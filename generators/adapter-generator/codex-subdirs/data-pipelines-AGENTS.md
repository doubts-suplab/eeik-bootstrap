# AGENTS.md — Data Pipelines Directory

> **Deploy to**: `data-pipelines/AGENTS.md` or `pipelines/AGENTS.md`
> Codex CLI reads this when working in pipeline files (PySpark, Glue, dbt, Airflow).

---

You are working in the **data engineering** directory.

## Stack

- PySpark 3.5 / AWS Glue 4.0 for batch processing
- Apache Kafka + Confluent Schema Registry for streaming
- dbt 1.7+ for SQL transformations (Medallion architecture)
- Apache Airflow 2.7+ for orchestration
- Delta Lake or Apache Iceberg for the lakehouse layer

## Architecture: Medallion

```
Bronze (raw)   → exact copy of source; never modified; partitioned by ingestion date
Silver (clean) → typed, deduped, null-handled; schema enforced
Gold (curated) → business-ready aggregates and joins; serves analytics and applications
```

## Non-Negotiable Rules

1. **Idempotent pipelines** — re-running must produce the same result; use `overwrite` with partition filter
2. **Schema first** — define `StructType` or Avro schema before writing a line of pipeline code
3. **No `SELECT *`** — explicit column lists in all Spark and dbt SQL
4. **PII tagged in catalog** — classify PII columns before data lands in Silver
5. **Dead-letter queue** — failed records go to error table/S3 path, never silently dropped
6. **Watermarks on streams** — always set `withWatermark()` for late data handling
7. **Incremental by default** — full reload only when schema change requires; document why
8. **Data quality checks** — `not_null`, `unique`, `accepted_range` on every key column
9. **Partition strategy upfront** — never change partition key after data grows
10. **Lineage metadata** — write `_source_system`, `_pipeline_name`, `_loaded_at` to every table

## Key Patterns

### Idempotent Spark write
```python
(df.write
   .format("delta")
   .mode("overwrite")
   .option("replaceWhere", f"event_date = '{run_date}'")
   .partitionBy("event_date")
   .saveAsTable("silver.orders"))
```

### dbt incremental model
```sql
{{ config(materialized='incremental', unique_key='order_id') }}
SELECT * FROM {{ ref('stg_orders') }}
{% if is_incremental() %}
WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Mandatory dbt tests
```yaml
columns:
  - name: order_id
    tests: [not_null, unique]
  - name: amount
    tests: [not_null, dbt_utils.accepted_range: {min_value: 0}]
```

## Before Writing a Pipeline

1. Define schema with types and nullability
2. Identify PII columns → apply masking strategy
3. Choose partition key and document rationale
4. Define SLA (freshness, row count expectations)
5. Define DLQ path for bad records
6. Write unit test for transformation logic first

## Standards Reference

Full standard: `capability-packs/data-engineering/standards/data-pipeline-standard.md`  
Lakehouse patterns: `capability-packs/data-engineering/knowledge/lakehouse-patterns.md`
