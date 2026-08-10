# Event-Driven Microservices — CDK

The architecture from [`../reference.yaml`](../reference.yaml) as deployable AWS infrastructure.

```bash
npm install
npx cdk synth
npx cdk diff
npx cdk deploy      # needs AWS credentials + CDK bootstrap
```

## What it provisions

| Construct | Purpose |
|---|---|
| `Vpc` | 3-AZ network for broker + service resilience |
| `EventBackbone` (MSK) | 3-broker Kafka cluster, TLS in transit + at rest — the event backbone |
| `ServiceStore` (Aurora PostgreSQL) | Per-service private write store (outbox lives here) |
| `Edge` (Fargate + ALB) | Spring Cloud Gateway — north-south entry, health at `/actuator/health` |

The Command/Query/Saga services are deployed per bounded context (one Fargate service each, omitted here
for brevity); they attach to the same MSK backbone and their own schema in `ServiceStore`. Add a Schema
Registry (Confluent/Glue) alongside MSK to govern event-contract compatibility.
