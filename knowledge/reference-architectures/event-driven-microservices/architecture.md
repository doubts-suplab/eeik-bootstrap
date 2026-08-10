# Reference Architecture — Event-Driven Microservices (Kafka + saga/outbox on Spring Boot)

> Java/Spring Boot microservices over an Apache Kafka backbone. Cross-service consistency without
> distributed transactions: the **transactional outbox** removes dual-writes, **sagas** coordinate
> multi-service workflows with compensations, and **CQRS** projections serve reads. Schema Registry
> governs event contracts; each service owns its database.

- **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) — validates + resolves to
  `core, architecture, aws, containers, delivery, governance, java`.
- **Maturity:** production.
- **Deploy:** [`cdk/`](cdk/) (AWS + MSK) · **Run locally:** [`local-dev/`](local-dev/) (Kafka + Schema Registry + Postgres).

---

## Overview

```
        (north-south)                         (east-west, async)
Client ─▶ API Gateway ─▶ Command Service ──┐
                          │  DB tx: state   │  publish
                          │  + outbox row   ▼
                          └────────▶ [outbox] ──relay──▶ Kafka ──▶ Query Service (CQRS projection)
                                                          │  │
                                                          │  └──▶ Saga Orchestrator ──▶ compensations
                                                          ▼
                                                  Schema Registry (Avro, compat-checked)
```

## Components

| Component | Tech | Responsibility |
|---|---|---|
| API Gateway | Spring Cloud Gateway | North-south entry: auth, routing, rate limiting |
| Command services | Spring Boot (per context) | Own their write model; emit events via the outbox |
| Transactional outbox | Outbox table + relay (Debezium/poller) | State + event in one tx; reliable publish |
| Kafka + Schema Registry | Amazon MSK + Confluent | Event backbone; versioned, compatibility-checked contracts |
| Saga orchestrator | Spring state machine | Multi-service workflows with compensating actions |
| Query services (CQRS) | Spring Boot + projections | Read-optimised views built from events |

## Key design decisions

1. **Transactional outbox, never dual-write.** Writing to the DB and publishing to Kafka in two steps
   loses events on a crash between them. Instead, persist the state change and an `outbox` row in **one
   DB transaction**; a relay publishes committed rows and marks them published. Exactly-once *effect*
   from at-least-once delivery.
2. **Sagas over distributed transactions.** No 2PC across services. A saga is a sequence of local
   transactions; each step has a **compensating action** that undoes it if a later step fails.
3. **Schema Registry enforces contracts.** Events are Avro with registered schemas; compatibility checks
   mean an additive change never breaks a consumer. The event *is* the contract.
4. **Database-per-service.** No shared schema, no cross-service joins — services integrate only through
   events/APIs, so they can evolve and deploy independently.
5. **Idempotent consumers.** Delivery is at-least-once; consumers dedupe by event id (`processed_events`)
   so a redelivery is harmless. Never assume exactly-once delivery.

## Consistency & failure model

- **At-least-once delivery** end to end; idempotency makes it safe.
- **Ordering** is per-partition — key events by aggregate id so a single aggregate's events stay ordered.
- **A failed saga step** triggers compensations in reverse; the workflow reaches a consistent terminal
  state (completed or fully compensated), never a partial one.
- **Poison messages** go to a dead-letter topic after bounded retries, with an alert — never an infinite
  retry loop.

## Observability

- **End-to-end tracing** across the async hops (propagate trace context in event headers) — the single
  most valuable signal in an EDA.
- `outbox_unpublished_age` — the relay's lag; a rising value means events aren't reaching Kafka.
- `consumer_lag` per group; `saga_compensation_rate`; `dlq_depth` (alarm on any sustained non-zero).

## Limitations

- Eventual consistency is a feature, not a bug — the UX must tolerate read-after-write lag on projections.
- Debugging async flows needs the tracing above; without it, causality is hard to reconstruct.
- Schema evolution discipline is mandatory — a breaking event change is an outage across consumers.

See [`runbook.md`](runbook.md) for operations (outbox lag, consumer lag, saga failures, DLQ).
