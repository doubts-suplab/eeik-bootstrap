# Order Management — Local Dev

Run the architecture end-to-end on a laptop, no AWS. Postgres stands in for Aurora; a single-node
Kafka (KRaft) + Confluent Schema Registry stand in for MSK.

```bash
docker compose up -d          # Postgres :5432 · Kafka :9092 · Schema Registry :8081
./seed/seed.sh                # (optional) re-apply schema + seed data
```

The schema (`seed/schema.sql`) is applied automatically on first Postgres boot; `seed/seed.sql` loads
three orders across the saga states (`PLACED` / `RESERVED` / `PAID`) plus their outbox events.

| Service | Local endpoint | Notes |
|---|---|---|
| Postgres (order store + outbox) | `postgres://orders:orders_dev@localhost:5432/orders` | schema + seed auto-applied |
| Kafka (event backbone) | `localhost:9092` (PLAINTEXT) | topic-per-aggregate |
| Schema Registry | `http://localhost:8081` | Avro contracts |

Point each Spring Boot service at these with `SPRING_PROFILES_ACTIVE=local`. Tear down with
`docker compose down -v`.
