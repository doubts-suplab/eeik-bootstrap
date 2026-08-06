# Data Platform — CDK

Deployable infrastructure for the [Data Platform](../architecture.md) reference architecture: the
medallion lakehouse buckets (bronze/silver/gold + Athena results), a Glue catalog database with a
crawler per zone, an Athena workgroup, and the MSK ingestion backbone. See
[`lib/data-platform-stack.ts`](lib/data-platform-stack.ts).

> This stack is the durable **substrate**. Compute — Glue Spark jobs, the dbt project (silver→gold), and
> the Airflow/MWAA orchestration — is deployed on top and references these buckets + catalog. The Glue
> crawler role ARN is a placeholder; create the service role first.

## Deploy

```bash
npm install
npx cdk bootstrap
npx cdk deploy DataPlatform
```

| Construct | Purpose |
|---|---|
| `Bronze/Silver/Gold` (S3) | medallion zones — raw → conformed → curated marts |
| `LakehouseDb` + crawlers (Glue) | schema catalog, one crawler per zone |
| `AnalyticsWorkgroup` (Athena) | SQL over gold; results encrypted to their own bucket |
| `IngestBackbone` (MSK) | streaming ingestion into bronze |

Local iteration without AWS: [`../local-dev/`](../local-dev/).
