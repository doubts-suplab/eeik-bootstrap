# Reference Architecture — Data Platform (streaming + lakehouse)

**Stack:** Kafka (MSK) · Spark/Glue · dbt · Airflow (MWAA) · S3 lakehouse · Glue Catalog · Athena · CDK
**Maturity:** Production · **Manifest:** [`project-manifest.yaml`](project-manifest.yaml) (schema-valid)
**Resolves to packs:** `core · architecture · aws · data-engineering · delivery · python`

A blueprint for a data platform that ingests events and files, refines them through a **medallion**
lakehouse, and serves analytics — reproducibly, idempotently, and with data-quality gates between stages.

---

## 1. Context

```
   Producers ──▶ Kafka (MSK) ──sink──▶  ┌──────────────── S3 lakehouse (Glue Catalog) ───────────────┐
                                        │  bronze (raw, immutable) ──Spark/Glue──▶ silver (conformed) │
   Batch files ──▶ S3 landing ──────────┤                                             │ dbt           │
                                        │                                             ▼               │
                                        │                                   gold (business models) ───┼──▶ Athena ──▶ BI
                                        └──────────────────────────────────▲──────────────────────────┘
                                                Airflow (MWAA): schedules · deps · retries · backfills · DQ gates
```

- **Bronze** — raw landing, append-only, source-faithful (schema + keys preserved). Never edited.
- **Silver** — cleaned, deduped, conformed; the reliable base for modelling.
- **Gold** — business-level marts (dbt models) consumed by Athena/BI.

---

## 2. The reliability spine

### 2.1 Idempotent ingestion (re-runs are safe)
Streaming lands to bronze partitioned by ingest date + Kafka key; batch lands to a dated prefix. Every
downstream stage writes with **partitioned overwrite** (or Iceberg MERGE) keyed by a natural/business key —
so re-processing a partition **replaces** it rather than appending duplicates. Backfills are just re-runs.

### 2.2 Schema evolution (backward-compatible)
Streaming payloads carry an Avro schema from the registry; only **backward-compatible** changes (add
optional fields) flow through. A breaking change is a **new topic/dataset version** with dual-write during
cutover — never an in-place breaking edit that silently corrupts silver.

### 2.3 Data-quality gates (promotion is earned)
Between silver → gold, **dbt tests** (unique, not-null, accepted-values, relationships) and/or Great
Expectations run as an Airflow task. A failed expectation **fails the DAG** and blocks promotion — bad data
does not reach gold. Row-count and freshness checks alert on drift.

### 2.4 Reproducibility
Gold is a pure function of silver; silver of bronze. Because bronze is immutable, **the whole platform can
be rebuilt from raw** — a transformation bug is fixed by correcting code and re-running, not by patching data.

---

## 3. Orchestration (Airflow)

```
ingest_sensor ─▶ bronze_to_silver (Spark/Glue) ─▶ dq_gate_silver ─▶ dbt_run (silver→gold)
                                                        │(fail → stop, alert)   │
                                                        ▼                       ▼
                                                    backfill on demand      dq_gate_gold ─▶ publish/refresh Athena views
```
DAGs are idempotent and **re-entrant**: a retried task produces the same partition. Backfills parameterise
the date range and re-run the same tasks.

---

## 4. Non-functional targets

| Concern | Target | How |
|---|---|---|
| Freshness (streaming → silver) | < 15 min | micro-batch Spark; MSK retention buffers spikes |
| Reprocessing | full rebuild from bronze | immutable raw + deterministic transforms |
| Correctness | no dupes, DQ-gated | partitioned overwrite + dbt/GE tests |
| Cost | bounded scan | Parquet + partition pruning; Athena workgroup limits |
| Lineage | end-to-end | Glue Catalog + dbt docs; column-level lineage in dbt |

---

## 5. Why these choices

- **Medallion over ad-hoc pipelines** — immutable raw + layered refinement makes the platform
  *reproducible* and debuggable; a bad transform never destroys the source of truth.
- **dbt for the gold layer** — transformations, tests, and docs as version-controlled code; the DQ gate is
  part of the model, not a bolt-on.
- **Athena/S3 (lakehouse) over a warehouse-first design** — decoupled storage/compute, pay-per-scan, open
  formats (Parquet/Iceberg). Move hot marts to Redshift/Snowflake only when query latency/concurrency demands.
- **Kafka for streaming, Spark/Glue for batch** — the same lakehouse serves both; one catalog, one gold layer.

---

## 6. Adopt it

```bash
eeik validate knowledge/reference-architectures/data-platform/project-manifest.yaml
# resolves to: core, architecture, aws, data-engineering, delivery, python
cp knowledge/reference-architectures/data-platform/project-manifest.yaml ./project-manifest.yaml
eeik activate --apply
```

The `data-engineering` pack's standards (idempotency, schema evolution, DLQ, pipeline conventions) apply.
See [`runbook.md`](runbook.md) for operations (DAG health, DQ failures, backfills).
