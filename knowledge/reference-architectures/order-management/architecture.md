# Reference Architecture — Order Management Microservice

**Stack:** Spring Boot 3 · Java 21 · Aurora PostgreSQL · Kafka (MSK) · ECS Fargate · AWS CDK
**Maturity:** Production · **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) (schema-valid)
**Resolves to packs:** `core · architecture · aws · delivery · java`

A proven blueprint for an order lifecycle service: capture an order, reserve stock, take payment, and
settle — reliably, under at-least-once event delivery, without dual-write inconsistency or double charges.

---

## 1. Context

```
                        ┌──────────────────────────── AWS account (eu-west-1) ────────────────────────────┐
                        │                                                                                 │
   Storefront / BFF ───▶│  API Gateway ──▶ Order API (Fargate) ──┐                                        │
                        │                                        │ (1) order + event in ONE tx            │
   Ops / Support ──────▶│  API Gateway ──▶ Order Read Model ◀─┐  ▼                                        │
                        │                                     │  Aurora (writer)  ──outbox poller──▶ Kafka │
                        │                                     │       │                              (MSK) │
                        │                    Aurora (replica)─┘       │                                │   │
                        │                                             ▼                                ▼   │
                        │                                  Inventory Svc (Fargate)          Payment Svc    │
                        │                                       │  ▲                          │  ▲         │
                        │                                       └──┴──────── Kafka topics ─────┴──┘         │
                        └─────────────────────────────────────────────────────────────────────────────────┘
```

**Actors:** the storefront/BFF issues commands; ops/support read status via the query side. **Boundaries:**
three services (Order, Inventory, Payment), each owning its data; no shared database, no cross-service joins.

---

## 2. Bounded contexts (DDD)

| Context | Aggregate(s) | Owns | Emits |
|---|---|---|---|
| **Order** | `Order`, `OrderLine` | order state machine, pricing snapshot | `OrderPlaced`, `OrderCancelled` |
| **Inventory** | `StockItem`, `Reservation` | available-to-promise, reservations | `StockReserved`, `StockRejected` |
| **Payment** | `Payment`, `Charge` | settlement, refunds, idempotency ledger | `PaymentSettled`, `PaymentFailed` |

Order is the saga initiator. Inventory and Payment are participants. Each context is a separately
deployable service with its own Aurora schema and its own CDK stack.

---

## 3. The reliability spine

### 3.1 Transactional outbox (no dual-write)
The Order API writes the `Order` row **and** an `outbox` row in a **single database transaction**. A poller
(or Debezium CDC) tails the outbox and publishes to Kafka. The service never writes to the DB and to Kafka
in two separate steps — so a crash between them cannot lose or duplicate the event's *intent*.

```
BEGIN;
  INSERT INTO orders (...) VALUES (...);
  INSERT INTO outbox (aggregate_id, type, payload) VALUES (...);
COMMIT;                       -- atomic; the poller publishes after commit
```

### 3.2 Choreographed saga (place → reserve → settle)
```
OrderPlaced ─▶ Inventory: reserve
                 ├─ StockReserved ─▶ Payment: charge
                 │                     ├─ PaymentSettled ─▶ Order: CONFIRMED
                 │                     └─ PaymentFailed  ─▶ Inventory: release  ─▶ Order: FAILED
                 └─ StockRejected ─▶ Order: FAILED
```
Compensations (release reservation, void charge) are themselves events — the happy and unhappy paths use
the same backbone. No distributed 2-phase commit.

### 3.3 Idempotency (at-least-once safe)
Every consumer is idempotent. Payment keys each charge by `orderId + attempt`; a redelivered
`StockReserved` re-uses the prior charge result rather than charging twice. Consumers track processed
event ids (inbox) to drop duplicates.

### 3.4 CQRS read model
The query side (`Order Read Model`) projects events into a denormalised view on an **Aurora read
replica**, so heavy status/history queries never contend with the order write path.

---

## 4. Non-functional targets

| Concern | Target | How |
|---|---|---|
| Availability | 99.9% | Multi-AZ Aurora + Fargate across 3 AZs; MSK 3-broker |
| Order-place P99 | < 200 ms | Single-tx write; async saga off the request path |
| Throughput | 500 orders/s | Partitioned topics keyed by `orderId`; horizontal Fargate scaling |
| Consistency | eventual, no double-charge | Outbox + idempotency keys + inbox de-dup |
| RPO / RTO | ≤ 1 min / ≤ 10 min | Aurora continuous backup + PITR; IaC redeploy |

---

## 5. Why these choices

- **Outbox over dual-write** — the single most common source of lost/duplicate events in event-driven
  systems; the outbox makes state and event atomic. *(See ADR in the EEIK event-driven standard.)*
- **Choreography over an orchestrator** — fewer moving parts for a 3-step saga; each service stays
  autonomous. An orchestrator (Step Functions) is the right call once the saga exceeds ~5 steps or needs
  central visibility — revisit then.
- **CQRS on a replica** — read/write isolation without a second datastore; upgrade to a dedicated
  projection store (DynamoDB/OpenSearch) only when query shapes diverge sharply from the write model.
- **Kafka over SQS here** — ordered, partitioned, replayable event log with a schema registry; SQS/SNS is
  simpler when you don't need ordering or replay.

---

## 6. Adopt it

```bash
# validate + see the packs this architecture activates
eeik validate knowledge/reference-architectures/order-management/project-manifest.yaml
eeik resolve-packs # (via the SDK) → core, architecture, aws, delivery, java

# or scaffold from the preset manifest
cp knowledge/reference-architectures/order-management/project-manifest.yaml ./project-manifest.yaml
eeik activate --apply           # materialise the resolved packs into .claude/
```

Golden rules enforced by the resolved packs apply: constructor injection, `jakarta.*`, no `SELECT *`,
parameterised queries, SLF4J, Conventional Commits. See [`runbook.md`](runbook.md) for operations.
