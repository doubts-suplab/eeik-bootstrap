# Event-Driven Microservices — Local Dev

Run the event backbone + a service store on a laptop, no AWS account needed.

```bash
docker compose up -d       # Kafka (KRaft) + Schema Registry + Postgres (with outbox schema)
docker compose down -v      # tear down
```

## What runs

| Service | Purpose | Port |
|---|---|---|
| `kafka` | Kafka in KRaft mode (no ZooKeeper) — the event backbone | 9092 |
| `schema-registry` | Confluent Schema Registry — event-contract compatibility | 8081 |
| `postgres` | A service's write store, seeded with `orders` + `outbox` + `processed_events` | 5432 |

## The patterns, locally

- **Transactional outbox** — your service writes the state change and the `outbox` row in one DB
  transaction; a relay (Debezium, or a simple poller of `idx_outbox_unpublished`) publishes committed
  rows to Kafka and stamps `published_at`. No dual-write, so no lost or phantom events.
- **Idempotent consumers** — dedupe by event id via `processed_events`; delivery is at-least-once.
- **Schema Registry** — register Avro schemas at `http://localhost:8081`; producers/consumers check
  compatibility so an additive change never breaks a consumer.

Point your Spring Boot services at `localhost:9092` (Kafka), `localhost:8081` (registry), and
`jdbc:postgresql://localhost:5432/orders`.
