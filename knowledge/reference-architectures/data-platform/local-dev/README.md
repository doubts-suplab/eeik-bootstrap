# Data Platform — Local Dev

Run ingestion + lakehouse locally. Kafka carries events; MinIO stands in for the S3 medallion buckets
(`bronze` / `silver` / `gold`), created on startup with the bronze seed loaded.

```bash
docker compose up -d          # Kafka :9092 · MinIO :9000 (console :9001) · buckets + seed created
```

| Component | Local endpoint | Notes |
|---|---|---|
| Kafka (ingestion) | `localhost:9092` | producers land raw events |
| MinIO (lakehouse) | `http://localhost:9000` (console `:9001`) | user `lakehouse` / `lakehouse_dev` |
| Bronze seed | `s3://bronze/events/events.jsonl` | 5 raw events (incl. a duplicate) |

The seed (`seed/events.bronze.jsonl`) deliberately contains a **duplicate** `e-0002` so the
bronze→silver step demonstrates idempotent dedup, and an `order_cancelled` so gold aggregations exercise
late-arriving state. Point Spark/dbt at MinIO with the S3A/`AWS_*` env vars (endpoint
`http://localhost:9000`, path-style access). Tear down: `docker compose down -v`.
