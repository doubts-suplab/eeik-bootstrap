# Runbook — Order Management Microservice

Operational guide for the [Order Management reference architecture](architecture.md). Service names are
placeholders — replace with your deployment's actual names.

---

## Health & key signals

| Signal | Where | Healthy |
|---|---|---|
| Order-place P99 latency | CloudWatch `OrderAPI/latency` | < 200 ms |
| Outbox lag (rows unpublished) | `SELECT count(*) FROM outbox WHERE published_at IS NULL` | < 1000, draining |
| Saga completion rate | `PaymentSettled / OrderPlaced` (5-min) | > 0.98 |
| Consumer lag per topic | MSK / Kafka consumer group lag | < 10k, not growing |
| DLQ depth | `orders.DLT`, `payments.DLT` | 0 |

## SLOs

- **Availability** 99.9% (order-place success). **Latency** P99 < 200 ms. Error budget: 43 min/month.

---

## Common incidents

### Outbox lag climbing / events not flowing
1. Is the outbox poller / Debezium connector running? (`ECS service`, connector status.)
2. Kafka reachable? Broker health, topic exists, ACLs.
3. If the poller is stuck on a poison row: inspect the head outbox row; move to a parking table, alert, continue.
   **Never** delete outbox rows to "unblock" — that loses events.

### Saga stalls (orders stuck in `PENDING`)
1. Which step? Compare `OrderPlaced` vs `StockReserved` vs `PaymentSettled` counts.
2. Inventory or Payment consumer down / lagging → scale the consumer, check its DLQ.
3. A stuck order is *safe* (no partial charge) — the saga resumes when the participant recovers; redelivery
   is idempotent.

### Suspected double charge
1. Payment is keyed by `orderId + attempt`; query the idempotency ledger for that order.
2. A true duplicate charge means the idempotency key was not honoured — page Payment on-call, freeze the
   charge path (feature flag), reconcile from the ledger. This is a **P1**.

### Kafka consumer lag spike
1. Traffic surge vs stuck consumer? Check per-partition lag.
2. Scale consumers up to the partition count (no benefit beyond it). Verify no hot partition (key skew on `orderId`).

---

## Routine operations

- **Deploy:** CDK per service stack; blue/green on Fargate; run Flyway migrations **before** the new task set.
- **Schema evolution:** Avro via the schema registry — **backward-compatible** changes only (add optional
  fields; never remove/rename). Breaking change → new topic version + dual-consume during cutover.
- **Replay:** to rebuild a read model, reset the projection consumer group to earliest on the read-model topics.
  The write path is unaffected.
- **Backup/restore:** Aurora PITR; rehearse restore quarterly (RTO ≤ 10 min).

## Escalation
P1 (double charge, data loss, order-place down) → Payments/Commerce on-call. P2 (elevated lag, single-AZ
degradation) → platform on-call. Attach: order id(s), topic + partition, consumer group, the 5-min signal panel.
