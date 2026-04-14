-- ============================================================
-- RAG Vector Store for GIFT University
-- Run this in Supabase SQL Editor ONCE
-- ============================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge base table
-- Each row = one chunk of GIFT University data
CREATE TABLE IF NOT EXISTS knowledge_base (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source      TEXT NOT NULL,        -- e.g. "programs", "fees", "faculty"
    title       TEXT NOT NULL,        -- e.g. "BS Computer Science"
    content     TEXT NOT NULL,        -- actual text chunk
    embedding   vector(1536),         -- Groq embedding vector
    metadata    JSONB DEFAULT '{}',   -- extra info (url, category, etc.)
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx
    ON knowledge_base
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Function: find most similar chunks to a query embedding
CREATE OR REPLACE FUNCTION search_knowledge(
    query_embedding vector(1536),
    match_count     INT DEFAULT 5,
    min_similarity  FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    id         UUID,
    source     TEXT,
    title      TEXT,
    content    TEXT,
    metadata   JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        kb.id,
        kb.source,
        kb.title,
        kb.content,
        kb.metadata,
        1 - (kb.embedding <=> query_embedding) AS similarity
    FROM knowledge_base kb
    WHERE 1 - (kb.embedding <=> query_embedding) > min_similarity
    ORDER BY kb.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
