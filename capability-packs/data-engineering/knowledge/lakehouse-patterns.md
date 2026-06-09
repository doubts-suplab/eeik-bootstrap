# Lakehouse Architecture Patterns

**Type**: Reference Architecture  
**Applicability**: Any project using Delta Lake, Iceberg, or Databricks on AWS/Azure

---

## Pattern 1: Delta Live Tables (DLT) Pipeline

Best for: Databricks-first organizations needing declarative pipelines with built-in quality.

```python
import dlt
from pyspark.sql import functions as F

@dlt.table(comment="Raw orders from S3 landing zone")
def raw_orders():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("s3://bucket/raw/orders/"))

@dlt.table
@dlt.expect_or_drop("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
def silver_orders():
    return (dlt.read_stream("raw_orders")
            .select("order_id", "customer_id",
                    F.col("amount").cast("double"),
                    F.to_timestamp("created_at").alias("created_at")))

@dlt.table(comment="Daily order aggregations for reporting")
def gold_daily_revenue():
    return (dlt.read("silver_orders")
            .groupBy(F.to_date("created_at").alias("date"))
            .agg(F.sum("amount").alias("total_revenue"),
                 F.count("order_id").alias("order_count")))
```

**Pros**: Automatic lineage, built-in quality constraints, managed checkpoints  
**Cons**: Databricks-only, higher cost than raw Spark

---

## Pattern 2: Auto Loader + Delta (AWS)

Best for: High-throughput S3 ingestion with exactly-once semantics.

```python
def ingest_orders(spark: SparkSession, source_bucket: str, checkpoint_dir: str) -> None:
    (spark.readStream
     .format("cloudFiles")
     .option("cloudFiles.format", "parquet")
     .option("cloudFiles.schemaLocation", f"{checkpoint_dir}/schema")
     .option("cloudFiles.inferColumnTypes", "true")
     .load(f"s3://{source_bucket}/orders/")
     .withColumn("_ingested_at", F.current_timestamp())
     .withColumn("_source_file", F.input_file_name())
     .writeStream
     .format("delta")
     .outputMode("append")
     .option("checkpointLocation", f"{checkpoint_dir}/orders")
     .option("mergeSchema", "true")
     .partitionBy("year", "month", "day")
     .table("bronze.orders"))
```

---

## Pattern 3: MERGE (Upsert) for CDC

Best for: Change Data Capture from operational databases.

```python
from delta.tables import DeltaTable

def apply_cdc(spark: SparkSession, changes_df, target_table: str) -> None:
    target = DeltaTable.forName(spark, target_table)
    (target.alias("t")
     .merge(changes_df.alias("s"), "t.id = s.id")
     .whenMatchedUpdate(
         condition="s.op = 'UPDATE'",
         set={"name": "s.name", "updated_at": "s.ts"}
     )
     .whenNotMatchedInsert(
         condition="s.op = 'INSERT'",
         values={"id": "s.id", "name": "s.name", "created_at": "s.ts"}
     )
     .whenMatchedDelete(condition="s.op = 'DELETE'")
     .execute())
```

---

## Pattern 4: Schema Evolution Strategy

| Scenario | Delta behaviour | Action |
|----------|----------------|--------|
| New column added upstream | Blocked by default | Set `mergeSchema=true` for trusted sources |
| Column renamed | Breaking change | Version the topic/table; run migration job |
| Column type changed | Breaking change | New table version; dual-write period |
| Column removed | Blocked | Add to DLQ analysis; consult data consumers |

**Rule**: Schema changes must go through RFC process for Gold layer tables.
Silver and Bronze can auto-evolve with `mergeSchema=true` + alerting.

---

## Pattern 5: Data Vault 2.0 (Enterprise)

Used when: multiple source systems, audit requirements, historisation needed.

```
Hub_Customer   — business key (customer_id) + hash key + load_date + record_source
Sat_Customer   — descriptive attributes + hash diff for change detection
Link_Order_Customer — relationship between Order hub and Customer hub
```

Implement with dbt using `dbt_datavault4dbt` package. Only for regulated or complex multi-source environments — overkill for single-source reporting.

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `coalesce(1)` before write | Creates single huge file, kills parallelism | Use `repartition()` only when necessary; let Delta manage file sizes |
| Full reload daily | Wastes compute; misses late data | Incremental with watermark |
| No partition pruning | Full table scan on every query | Always filter on partition column |
| Collect to driver | OOM for large datasets | Aggregate in Spark, never `.collect()` on production data |
| String timestamps | Timezone ambiguity | Always use `TimestampType` with explicit UTC |
| UDFs for simple transforms | 10-100× slower than native functions | Use `pyspark.sql.functions` equivalents |
