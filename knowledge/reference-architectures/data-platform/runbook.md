# Runbook — Data Platform (streaming + lakehouse)

Operational guide for the [Data Platform reference architecture](architecture.md).

---

## Key signals

| Signal | Where | Healthy |
|---|---|---|
| Streaming lag (Kafka → bronze) | MSK consumer group lag | < 10k, not growing |
| Silver freshness | max(ingest_ts) age | < 15 min |
| DQ gate pass rate | Airflow `dq_gate_*` task | 100% (a fail blocks promotion by design) |
| DAG success rate | Airflow | > 0.98; retries recovering |
| Athena scan per query | Athena workgroup metrics | within budget; partitions pruned |
| Backfill status | Airflow DAG runs | completing; no overlapping writers on a partition |

## SLOs
- **Freshness** silver < 15 min. **Correctness** no duplicate business keys in gold. **Gold availability** 99.5%.

---

## Common incidents

### DQ gate failing (DAG stopped at silver→gold)
This is the platform **working as designed** — bad data was blocked.
1. Read the failed dbt test / expectation: which column, which rule (unique, not-null, accepted-values)?
2. Is it a **source** problem (upstream sent bad data) or a **transform** bug? Check bronze for the raw rows.
3. Fix at the earliest correct layer, then **re-run from that stage** (idempotent). Never hand-edit gold to
   "unblock" — that hides the defect and it recurs.

### Streaming lag climbing
1. Consumer/Spark micro-batch running? Scale consumers up to the partition count.
2. Hot partition (key skew)? Re-key or salt. A single hot key caps throughput regardless of scaling.
3. MSK retention long enough to absorb the backlog while you recover? (No data loss if within retention.)

### Duplicate rows in gold
1. Almost always a non-idempotent write (append instead of partitioned overwrite / MERGE). Identify the
   offending stage; switch to overwrite-by-partition or Iceberg MERGE keyed by the business key.
2. Rebuild the affected partitions from bronze (safe — raw is immutable).

### Schema change broke silver
1. A breaking upstream change slipped past compatibility. Pin the consumer to the last good schema version.
2. Treat the new shape as a **new dataset version**; dual-process during cutover; migrate gold models.

### Athena costs spiking
1. Full-table scans? Ensure queries filter on partition columns; enforce partition projection.
2. Set a per-query/data-scanned limit on the workgroup; convert hot marts to columnar + compacted Parquet.

---

## Routine operations

- **Backfill:** parameterise the date range; the DAG re-runs the same idempotent tasks — no special path.
- **Schema registry:** register new versions; CI checks backward compatibility before deploy.
- **Compaction:** schedule small-file compaction on bronze/silver (streaming produces many small files).
- **Catalog:** Glue crawler or explicit DDL keeps the catalog in sync; dbt docs publish lineage.
- **Deploy:** CDK for infra; dbt + DAGs via CI; migrations are forward-only.

## Escalation
P1 (gold wrong/unavailable, data loss beyond retention) → data-platform on-call. P2 (lag, DQ backlog,
cost spike) → platform on-call. Attach: DAG run id, stage, partition/date range, the failing DQ test.
