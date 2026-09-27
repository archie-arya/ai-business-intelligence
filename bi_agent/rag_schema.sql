CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS rag_documents (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding VECTOR(768),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(source, chunk_index)
);

CREATE INDEX IF NOT EXISTS rag_documents_embedding_idx
ON rag_documents
USING hnsw (embedding vector_cosine_ops);