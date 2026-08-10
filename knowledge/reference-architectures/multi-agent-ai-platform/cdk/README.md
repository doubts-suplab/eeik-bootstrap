# Multi-Agent AI Platform — CDK

The architecture from [`../reference.yaml`](../reference.yaml) as deployable AWS infrastructure.

```bash
npm install
npx cdk synth       # render the CloudFormation template
npx cdk diff        # compare against the deployed stack
npx cdk deploy      # deploy (needs AWS credentials + CDK bootstrap)
```

## What it provisions

| Construct | Purpose |
|---|---|
| `Vpc` | Network isolation (2 AZs, 1 NAT) |
| `Checkpoints` (DynamoDB) | LangGraph checkpoint store — long, multi-step runs survive restarts |
| `AuditLog` (DynamoDB) | Append-only record of every governed agent decision (write-only grant) |
| `PlatformApi` (Fargate + ALB) | FastAPI + LangGraph supervisor and worker agents, all on HALO in-process |
| Bedrock IAM policy | Least-privilege `bedrock:InvokeModel` on `anthropic.*` only — the HALO LLM port |

## Governance is in the service, not the infra

The confidence gate, tool registry, audit, and human-review routing live in the **HALO runtime inside
the container** (`halo-agent-harness`). The infra's role is to grant the platform exactly what it needs
— its own tables and Bedrock inference — and nothing more. The supervisor holds no tools; only worker
agents act, and only through HALO's default-deny tool registry.
