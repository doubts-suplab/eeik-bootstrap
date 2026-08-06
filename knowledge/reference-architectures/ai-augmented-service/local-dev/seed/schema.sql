-- AI-Augmented Service — local vector store schema.
-- Documents are chunked; each chunk carries a pgvector embedding for similarity retrieval.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          UUID PRIMARY KEY,
    title       TEXT        NOT NULL,
    source_uri  TEXT        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id          UUID PRIMARY KEY,
    document_id UUID        NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal     INT         NOT NULL,
    content     TEXT        NOT NULL,
    -- Titan Text Embeddings v2 default dimensionality.
    embedding   vector(1024)
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(document_id);
-- Approximate nearest-neighbour index for retrieval (cosine distance).
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING hnsw (embedding vector_cosine_ops);
