---
applyTo: "**/pipelines/**/*.py, **/jobs/**/*.py, **/dags/**/*.py, **/consumers/**/*.py, **/producers/**/*.py, **/models/**/*.sql, **/dbt/**/*.sql"
---

## Context

This instruction file applies to data pipeline code: Kafka producers and consumers, Apache Spark PySpark jobs, dbt SQL models, and Airflow / AWS Step Functions DAG definitions. The guiding principle is **idempotency** — every pipeline step must be safe to re-run without producing duplicate or corrupted output. All pipeline code must emit observability metrics and route unprocessable records to a Dead-Letter Queue (DLQ).

---

## Coding Standards

- **Idempotency first:** Every step must use UPSERT/MERGE, partition overwrite, or deduplication keys — never plain INSERT
- **Manual Kafka commit:** `enable.auto.commit=false`; commit only after successful downstream write
- **Dead-letter everything:** Unprocessable records go to DLQ with full metadata — never silently drop
- **Schema contracts:** All data crossing a system boundary has a registered, versioned Avro/JSON Schema Registry schema
- **`logging` not `print()`:** `logging.getLogger(__name__)` in every module; structured fields
- **DataFrame API only:** PySpark DataFrame API exclusively in new code — never RDD API
- **No business logic in dbt staging:** Staging models rename columns only; transformations go in intermediate layer
- **Observability metrics:** Emit `records_read`, `records_written`, `records_failed`, `duration_seconds` for every job run

---

## Preferred Patterns

### Kafka Producer (idempotent, Schema Registry)

```python
# ✅ CORRECT — idempotent producer with Avro serialisation
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

registry = SchemaRegistryClient({"url": settings.schema_registry_url})
serialiser = AvroSerializer(registry, ORDER_AVRO_SCHEMA)

producer = Producer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "acks": "all",
    "enable.idempotence": True,
    "max.in.flight.requests.per.connection": 5,
})

def publish_order_event(event: OrderPlacedEvent) -> None:
    producer.produce(
        topic="orders.placed",
        key=event.order_id,
        value=serialiser(event.to_dict(), SerializationContext("orders.placed", MessageField.VALUE)),
        on_delivery=_delivery_callback,
    )
    producer.flush()
```

### Kafka Consumer (manual commit, DLQ)

```python
# ✅ CORRECT — manual commit, DLQ routing
consumer = Consumer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": "order-processor",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})

while True:
    msg = consumer.poll(timeout=1.0)
    if msg is None:
        continue
    try:
        event = deserialise(msg.value())
        processor.handle(event)
        consumer.commit(message=msg)
    except ProcessingError as exc:
        logger.error("Processing failed; routing to DLQ", exc_info=True)
        dlq_producer.produce(topic="orders.placed.dlq", value=msg.value(), headers=_error_headers(exc))
        consumer.commit(message=msg)

# ❌ WRONG — auto-commit loses records on failure
Consumer({"enable.auto.commit": True})
```

### PySpark Job (DataFrame API, explicit schema)

```python
# ✅ CORRECT — explicit schema, partition overwrite, observability
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

ORDER_SCHEMA = StructType([
    StructField("order_id", StringType(), nullable=False),
    StructField("customer_id", StringType(), nullable=False),
    StructField("created_at", TimestampType(), nullable=False),
])

spark = SparkSession.builder.appName("OrderEnrichmentJob").getOrCreate()

raw_df = spark.read.schema(ORDER_SCHEMA).parquet(input_path)
enriched_df = raw_df.join(customer_df, on="customer_id", how="left")
enriched_df.write.mode("overwrite").partitionBy("created_date").parquet(output_path)

logger.info("records_read=%d records_written=%d", raw_df.count(), enriched_df.count())

# ❌ WRONG — inferred schema, RDD API, no observability
rdd = spark.sparkContext.textFile(input_path)
```

### dbt Layered Models

```sql
-- ✅ CORRECT: staging model — rename only, no business logic
-- models/staging/stg_orders.sql
select
    order_id,
    cust_id       as customer_id,
    order_ts      as placed_at,
    total_amt_gbp as total_amount_gbp
from {{ source('raw', 'orders') }}

-- ✅ CORRECT: intermediate model — business logic here
-- models/intermediate/int_orders_with_status.sql
select
    o.order_id,
    o.customer_id,
    o.placed_at,
    o.total_amount_gbp,
    case when s.fulfilled_at is not null then 'FULFILLED' else 'PENDING' end as status
from {{ ref('stg_orders') }} o
left join {{ ref('stg_fulfilments') }} s using (order_id)

-- ❌ WRONG: business logic in staging model
select order_id,
    case when total_amt_gbp > 1000 then 'HIGH_VALUE' else 'STANDARD' end as tier
from raw.orders
```

---

## Anti-Patterns — Do NOT Generate

```python
# WRONG: auto-commit on Kafka consumer — loses messages on crash [BLOCKER]
Consumer({"enable.auto.commit": True})

# WRONG: silently dropping failed records [BLOCKER]
try:
    process(record)
except Exception:
    pass  # record silently lost

# WRONG: RDD API in new PySpark code [MAJOR]
rdd = sc.textFile(path).map(lambda x: x.split(","))

# WRONG: inferred schema in Spark — breaks on empty partitions [MAJOR]
df = spark.read.parquet(path)  # no explicit schema

# WRONG: plain INSERT — not idempotent [MAJOR]
cursor.execute("INSERT INTO orders VALUES (%s, %s)", (order_id, amount))

# WRONG: print() in pipeline code [MAJOR]
print(f"Processed {count} records")

# WRONG: business logic in dbt staging model [MINOR]
-- stg_orders.sql
select *, total_amt_gbp * 0.2 as vat_amount from raw.orders
```

---

## Dependencies & Versions

| Technology | Version | Notes |
|-----------|---------|-------|
| confluent-kafka | 2.x | `acks=all`, `enable.idempotence=True` for producers |
| apache-spark (PySpark) | 3.5+ | DataFrame API only; use `SparkSession.builder` |
| dbt-core | 1.7+ | `staging → intermediate → mart` layer convention |
| great-expectations | 0.18+ | Data quality suite; `checkpoint.run()` in CI |
| apache-airflow | 2.8+ | Task-level idempotency; use `execution_date` as partition key |
| boto3 | 1.34+ | AWS Step Functions, S3 access; use `waiters` for polling |

---

## Test Conventions

- Unit test pipeline functions with mocked Kafka client (`MagicMock`) and in-memory DataFrames
- Integration test Kafka consumers with `testcontainers-python` Kafka container
- Test idempotency: run the pipeline twice on the same input; verify output row count does not double
- Test DLQ routing: inject a record that will fail processing and verify it appears in the DLQ topic
- For dbt, use `dbt test` with `not_null`, `unique`, `relationships` tests on every mart model
- Verify observability metrics are emitted: assert `records_read`, `records_written` counters in test output
