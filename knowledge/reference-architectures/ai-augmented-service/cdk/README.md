# AI-Augmented Service — CDK

Deployable infrastructure for the [AI-Augmented Service](../architecture.md) reference architecture: a
RAG FastAPI service on ECS Fargate, an Aurora PostgreSQL + pgvector vector store, an encrypted
documents bucket, and **least-privilege Bedrock access** (only the two named models). See
[`lib/ai-augmented-service-stack.ts`](lib/ai-augmented-service-stack.ts).

> HALO governs every model call *inside* the service (confidence gate, tool allowlist, audit); the
> infra only supplies the vector store, corpus bucket, and scoped Bedrock IAM. Image is a
> `REPLACE_ME/...` placeholder.

## Deploy

```bash
npm install
npx cdk bootstrap
npx cdk deploy AiAugmentedService
```

| Construct | Purpose |
|---|---|
| `VectorStore` (Aurora pgvector) | embeddings + document chunks for retrieval |
| `Documents` (S3) | source corpus, versioned, private |
| `RagApi` (Fargate + ALB) | FastAPI RAG service; HALO-governed model calls |
| Bedrock IAM policy | `InvokeModel` scoped to the Claude + Titan-embed models only |

Local iteration without AWS: [`../local-dev/`](../local-dev/).
