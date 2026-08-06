# AI-Augmented Service — Local Dev

Run the vector store locally. Postgres + `pgvector` stands in for Aurora pgvector; the schema and a
tiny seed corpus load on first boot.

```bash
docker compose up -d          # Postgres + pgvector on :5432
```

| Component | Local endpoint | Notes |
|---|---|---|
| Vector store | `postgres://rag:rag_dev@localhost:5432/knowledge` | `vector` extension + HNSW index |
| Corpus | seeded: `Refund Policy`, `Shipping SLA` | embeddings NULL until ingested |

**Bedrock has no local emulator.** Two options for the model calls:
1. Point the service at real Bedrock with AWS credentials (set `BEDROCK_MODEL_ID` / `BEDROCK_EMBED_MODEL_ID`).
2. Stub HALO's LLM + embedding ports with a deterministic fake — the ports make this a one-liner, and
   the confidence gate / audit still exercise unchanged.

Compute embeddings for the seed chunks via the service's ingestion path (`POST /ingest`). Tear down
with `docker compose down -v`.
