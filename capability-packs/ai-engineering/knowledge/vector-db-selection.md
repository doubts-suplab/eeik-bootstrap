# Vector Database Selection Guide

**Type**: Architecture Decision Aid  
**Context**: Choosing a vector store for RAG, semantic search, or embeddings-based retrieval

---

## Decision Matrix

| | pgvector | OpenSearch | Pinecone | Weaviate | Chroma |
|---|---|---|---|---|---|
| **Hosting** | Self / RDS | AWS OpenSearch | Managed SaaS | Self / Cloud | Self |
| **Scale** | Medium | Large | Very large | Large | Small–Med |
| **Hybrid search** | ✅ (v0.7+) | ✅ | ✅ | ✅ | Limited |
| **Metadata filtering** | ✅ SQL | ✅ | ✅ | ✅ | ✅ |
| **AWS-native** | ✅ RDS/Aurora | ✅ | ❌ | ❌ | ❌ |
| **Existing SQL data** | ✅ co-locate | ❌ separate | ❌ separate | ❌ separate | ❌ |
| **Compliance (data residency)** | ✅ full control | ✅ full control | Limited | ✅ self-hosted | ✅ |
| **Cost at 10M vectors** | Low | Medium | High | Medium | Low |
| **Bedrock KB native** | ❌ | ✅ | ❌ | ❌ | ❌ |

---

## Decision Tree

```
Already using RDS PostgreSQL?
  YES → pgvector (zero additional infra, SQL joins with metadata)

Using AWS Bedrock Knowledge Bases?
  YES → OpenSearch Serverless (native Bedrock KB integration)

Need >50M vectors at SaaS scale?
  YES → Pinecone (purpose-built, best query performance at scale)

Regulated industry (data residency required)?
  YES → pgvector or OpenSearch on dedicated cluster (not SaaS)

Prototyping / local development?
  YES → Chroma (zero config, in-process or server mode)
```

---

## pgvector Setup (RDS Aurora PostgreSQL)

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create embeddings table
CREATE TABLE document_chunks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id),
    content     TEXT NOT NULL,
    embedding   vector(1536),              -- Titan Embed v1: 1536 dims; v2: 1024 dims
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index (approximate nearest neighbour — fast for large datasets)
CREATE INDEX ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);           -- lists = sqrt(row_count) is a good starting point

-- Cosine similarity search with metadata filter
SELECT content, metadata,
       1 - (embedding <=> $1::vector) AS similarity
FROM document_chunks
WHERE metadata->>'document_type' = 'policy'
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

```python
# Python with pgvector + SQLAlchemy
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, select, cast
from sqlalchemy.dialects.postgresql import JSONB

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id          = Column(UUID, primary_key=True, default=uuid4)
    content     = Column(Text, nullable=False)
    embedding   = Column(Vector(1024))      # Titan Embed v2 dimensions
    metadata_   = Column("metadata", JSONB)

async def similarity_search(
    session: AsyncSession,
    query_embedding: list[float],
    doc_type: str,
    limit: int = 5,
) -> list[DocumentChunk]:
    result = await session.execute(
        select(DocumentChunk)
        .where(DocumentChunk.metadata_["document_type"].astext == doc_type)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    return result.scalars().all()
```

---

## OpenSearch Serverless (Bedrock Knowledge Base)

OpenSearch Serverless is the native choice for Bedrock Knowledge Bases — no manual index management.

```python
import boto3

opensearch = boto3.client('opensearchserverless')

# Create vector search collection
response = opensearch.create_collection(
    name='my-vectors',
    type='VECTORSEARCH',
    description='RAG vector store',
)

# Index mapping (created automatically by Bedrock KB, or manually)
index_body = {
    "settings": {"index.knn": True},
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 1024,
                "method": {"name": "hnsw", "engine": "faiss"},
            },
            "text":     {"type": "text"},
            "metadata": {"type": "object"},
        }
    },
}
```

---

## Hybrid Search Pattern (Keyword + Semantic)

Pure vector search misses exact matches (product codes, names). Hybrid combines both:

```python
# OpenSearch hybrid query
hybrid_query = {
    "query": {
        "hybrid": {
            "queries": [
                {
                    "match": {
                        "text": {"query": user_query, "boost": 0.3}
                    }
                },
                {
                    "knn": {
                        "embedding": {
                            "vector": query_embedding,
                            "k": 10,
                            "boost": 0.7,
                        }
                    }
                }
            ]
        }
    },
    "size": 5,
}
```

---

## Embedding Model Selection

| Model | Dimensions | Max tokens | Cost/1M tokens | Best for |
|---|---|---|---|---|
| Amazon Titan Embed v2 | 1024 | 8192 | $0.02 | AWS-native, multilingual |
| Amazon Titan Embed v1 | 1536 | 8192 | $0.10 | Legacy Bedrock KB |
| Cohere Embed v3 | 1024 | 512 | $0.10 | Multilingual, code |
| OpenAI text-embedding-3-small | 1536 | 8191 | $0.02 | General purpose |

Use **Titan Embed v2** for all new AWS-based RAG systems — AWS-native, good multilingual support, competitive cost.
