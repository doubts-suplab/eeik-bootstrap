# Order Management — CDK

Deployable infrastructure for the [Order Management](../architecture.md) reference architecture: an
ECS Fargate cluster running the four bounded-context services, an Aurora PostgreSQL cluster (order
aggregate + transactional outbox, with a reader for the CQRS query side), and an MSK (Kafka) event
backbone. See [`lib/order-management-stack.ts`](lib/order-management-stack.ts).

> Reference skeleton, not a turnkey deploy. Container images are `REPLACE_ME/...` placeholders and the
> stack uses production-shaped defaults (isolated DB subnets, encryption in transit, serverless-v2
> Aurora). Point the images at your ECR repos and review sizing before `cdk deploy`.

## Deploy

```bash
npm install
npx cdk bootstrap                 # once per account/region
npx cdk synth                     # render the CloudFormation template
npx cdk deploy OrderManagement    # provision
```

Region defaults to `eu-west-1` (override with `CDK_DEFAULT_REGION`).

## What it provisions

| Construct | Purpose |
|---|---|
| `Vpc` | 3 AZs · public (ALB) / private-egress (app) / isolated (data) tiers |
| `OrderStore` (Aurora PostgreSQL) | order aggregate + outbox; writer + auto-scaling reader for CQRS |
| `EventBackbone` (MSK) | domain-event transport, TLS in transit, 3 brokers |
| `Cluster` (ECS) | Order API (public, behind ALB) + Order Read Model / Inventory / Payment (internal) |

For local iteration without AWS, use [`../local-dev/`](../local-dev/).
