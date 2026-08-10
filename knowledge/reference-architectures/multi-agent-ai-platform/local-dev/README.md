# Multi-Agent AI Platform — Local Dev

Run the platform's stateful dependencies on a laptop, no AWS account needed.

```bash
docker compose up          # DynamoDB Local + create the checkpoint/audit tables + the platform API
docker compose down -v     # tear down (in-memory tables are discarded)
```

## What runs

| Service | Purpose |
|---|---|
| `dynamodb` | DynamoDB Local (in-memory) — stands in for the checkpoint + audit tables |
| `seed` | One-shot: creates `agent-platform-checkpoints` + `agent-platform-audit`, then exits |
| `platform-api` | Placeholder for your FastAPI + LangGraph image (points at DynamoDB Local) |

## Bedrock offline

Bedrock has no local emulator. Two options for the model port:

- **Real Bedrock** — set AWS credentials in the `platform-api` environment and remove the
  `DYNAMODB_ENDPOINT` override for anything that should hit AWS.
- **Offline** — inject HALO's `StubLlm` as the `LlmPort` (a one-liner). Every agent still runs on the
  full HALO governance path (confidence gate, tool registry, audit, human review) — only the model
  responses are canned. This is exactly how the platform's tests run.
