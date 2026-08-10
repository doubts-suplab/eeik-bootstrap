# Runbook — Event-Driven Microservices (Kafka + saga/outbox)

Operating the platform. In an EDA most incidents are about **flow** — events not being published,
consumed, or completing a saga — not a single service being down.

## Key signals

| Signal | Meaning | Healthy |
|---|---|---|
| `outbox_unpublished_age` p95 | Oldest unpublished outbox row (relay lag) | seconds, flat |
| `consumer_lag` per group | Unprocessed records behind the head | bounded, draining |
| `saga_compensation_rate` | Share of sagas ending in compensation | low, stable |
| `dlq_depth` | Dead-letter topic backlog | **0** (alarm on sustained non-zero) |
| schema-registry compat failures | Rejected incompatible schema registrations | 0 |

## SLOs

- **Event freshness:** p95 `outbox → consumed` within target for the business flow.
- **DLQ:** `dlq_depth == 0` sustained; any growth is a P2.
- **Saga completion:** ≥ target % of sagas reach a terminal state within the workflow SLA.

## Common incidents

### Outbox lag climbing — events not reaching Kafka
The relay (Debezium/poller) is stuck or Kafka is unreachable. Check the relay's health and its Kafka
connectivity; the state changes are safe in the DB (that's the point of the outbox) and will publish when
the relay recovers. Do not manually re-publish — the relay is the single publisher.

### Consumer lag growing
Consumers can't keep up or are erroring. Check the consumer group's error rate; scale consumers (add
partitions + instances) if it's throughput, fix the handler if it's errors. Because consumers are
idempotent, a restart/replay is safe.

### DLQ filling up (poison messages)
Messages failed past the retry bound. Inspect a sample: bad payload, a downstream dependency down, or a
schema mismatch. Fix the cause, then replay the DLQ back onto the source topic (consumers dedupe, so
replay is safe). Never drop the DLQ silently.

### Saga stuck / compensation spike
A workflow can't progress or is rolling back a lot. Find the failing step from the saga's audit trail;
a spike usually means a downstream service is unhealthy. The saga should compensate to a consistent
terminal state — verify no aggregate is left half-updated.

### Schema-registry compatibility failure on deploy
A producer tried to register an incompatible event schema. This is the guardrail working — do **not**
force-override compatibility. Make the change additive/optional, or introduce a new event version and
migrate consumers first.

### Partition hot-spotting / ordering issues
Events for one aggregate landed on different partitions (wrong/rotating key), breaking per-aggregate
order. Confirm events are keyed by aggregate id; re-key the producer if not.

## Routine operations

- **Add an event type:** register the Avro schema (compat-checked), publish from the outbox, add
  idempotent consumers.
- **Replay a topic:** reset the consumer group's offset; idempotency makes reprocessing safe.
- **Add a service:** its own DB schema + outbox; subscribe to the events it needs. No shared schema.

## Escalation

1. Platform on-call (flow: outbox, consumers, DLQ, sagas).
2. Owning service team (a specific service's handler or schema).
3. Cloud/infra on-call (MSK, Aurora, Fargate capacity).
