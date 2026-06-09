# Data Pipeline Engineering Standard

Version: Spark 3.5 | AWS Glue 4.0 | dbt 1.7+ | Kafka 3.x | Airflow 2.7+

---

## Architecture: Medallion / Lakehouse

```
Raw (Bronze)          → exactly as received; never modified; partitioned by ingestion date
Standardised (Silver) → typed, deduplicated, null-handled; schema enforced
Curated (Gold)        → business-ready aggregates, joined dimensions, serving layer

Storage: Delta Lake (preferred) or Apache Iceberg
Format:  Parquet (batch) | Avro (streaming with Schema Registry)
```

---

## Naming Conventions

| Layer | Table prefix | Example |
|-------|-------------|---------|
| Raw | `raw_` | `raw_orders` |
| Staging (dbt) | `stg_` | `stg_orders` |
| Intermediate | `int_` | `int_orders_with_customer` |
| Fact | `fct_` | `fct_orders` |
| Dimension | `dim_` | `dim_customers` |
| Mart | `mart_` | `mart_revenue_by_region` |

Partitioning:
- Temporal: `PARTITIONED BY (year INT, month INT, day INT)` or `event_date DATE`
- High-cardinality: hash partition by business key (never by random UUID)

---

## Pipeline Non-Negotiables

| # | Rule |
|---|------|
| P01 | Every pipeline is idempotent — re-runnable without duplicates |
| P02 | Schema defined in code (Spark StructType, Avro schema, dbt source YAML) |
| P03 | PII columns tagged in catalog before data is processed |
| P04 | DLQ / error table for every pipeline — failed records never silently dropped |
| P05 | No `SELECT *` — explicit column lists everywhere |
| P06 | Watermarks on all streaming pipelines — handle late data |
| P07 | Incremental loads preferred — document why a full reload is needed |
| P08 | Data quality checks run as part of pipeline, not as afterthought |
| P09 | Lineage metadata written: `source_system`, `pipeline_name`, `loaded_at` |
| P10 | Sensitive data encrypted at rest and masked in non-production |

---

## dbt Project Structure

```
dbt_project.yml
models/
├── staging/          ← 1:1 with source tables; light renaming/casting only
│   ├── _sources.yml  ← source definitions + freshness checks
│   └── stg_*.sql
├── intermediate/     ← joins, business logic, not for direct consumption
│   └── int_*.sql
├── marts/            ← domain-specific curated tables
│   ├── finance/
│   ├── operations/
│   └── customers/
└── _schema.yml       ← model-level tests and documentation
tests/
macros/
seeds/                ← reference data only (currencies, country codes)
```

### Mandatory dbt tests (in `_schema.yml`)
```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [not_null, unique]
      - name: customer_id
        tests: [not_null, relationships: { to: ref('dim_customers'), field: customer_id }]
      - name: amount
        tests: [not_null, dbt_utils.accepted_range: { min_value: 0 }]
```

---

## AWS Glue Best Practices

- Always enable job bookmarks for incremental processing
- Use Glue Data Catalog as the single schema registry for batch data
- Set `--TempDir` and `--spark-event-logs-path` for every job
- Use `DynamicFrame.fromDF` / `toDF` sparingly — stay in DynamicFrame or pure Spark, not both
- Timeout: set explicit timeout (default is 48h — always too long)
- Worker type: G.1X for most jobs; G.2X only for memory-intensive wide transformations

---

## Kafka / Streaming Standards

- Topic naming: `{domain}.{entity}.{event}.v{n}` e.g. `orders.order.placed.v1`
- Always use Schema Registry (Confluent or AWS Glue Schema Registry)
- Consumer groups: `{service}-{env}` e.g. `invoicing-service-prod`
- Always set `enable.auto.commit=false` — commit after successful processing
- Poison pill handling: after 3 retries, publish to `{topic}.dlq`
- Retention: minimum 7 days for audit; 30 days for replayability

---

## Data Quality SLAs

| Metric | Target |
|--------|--------|
| Freshness | Data available within SLA window (define per pipeline) |
| Completeness | 0% null on primary keys; document acceptable null rates for others |
| Uniqueness | 0 duplicates on business keys in Gold layer |
| Row count variance | Alert if ±20% vs 7-day moving average |
| Schema drift | Alert and halt pipeline; never silently coerce |
