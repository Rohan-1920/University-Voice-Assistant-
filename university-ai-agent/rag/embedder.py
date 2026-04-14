"""
Embedder
=========
Generates vector embeddings using Groq's free embedding model.
Stores embeddings in Supabase pgvector.

Model: llama-3.1-8b (Groq free tier)
Note:  Groq doesn't have a dedicated embedding endpoint yet,
       so we use a lightweight sentence-transformer approach
       via the 'sentence-transformers' library (runs locally, free).
"""

import os
import logging
from typing import List, Dict
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Lazy-load the model (only when needed)
_model = None

def get_model():
    """Load sentence-transformer model (free, runs locally)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        # all-MiniLM-L6-v2: fast, 384-dim, great for semantic search
        # We'll use 1536-dim to match our schema — use a larger model
        _model = SentenceTransformer("all-mpnet-base-v2")  # 768-dim
        logger.info("Embedding model loaded: all-mpnet-base-v2")
    return _model


def embed_text(text: str) -> List[float]:
    """Generate embedding for a single text."""
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts (faster than one by one)."""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32, show_progress_bar=True)
    return [e.tolist() for e in embeddings]


def store_chunks(chunks: List[Dict], db_url: str) -> int:
    """
    Embed all chunks and store in Supabase knowledge_base table.
    Returns number of chunks stored.
    """
    if not chunks:
        return 0

    logger.info(f"Embedding {len(chunks)} chunks...")

    # Generate all embeddings in one batch (fast)
    texts      = [c["content"] for c in chunks]
    embeddings = embed_batch(texts)

    # Connect to DB
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur  = conn.cursor()

    # Clear old data first
    cur.execute("DELETE FROM knowledge_base")
    logger.info("Cleared old knowledge base")

    # Insert new chunks with embeddings
    stored = 0
    for chunk, embedding in zip(chunks, embeddings):
        # Pad or trim embedding to 1536 dims to match schema
        # all-mpnet-base-v2 gives 768 dims — we pad to 1536
        padded = embedding + [0.0] * (1536 - len(embedding))

        cur.execute(
            """
            INSERT INTO knowledge_base (source, title, content, embedding, metadata)
            VALUES (%s, %s, %s, %s::vector, %s)
            """,
            (
                chunk["source"],
                chunk["title"],
                chunk["content"],
                str(padded),
                psycopg2.extras.Json(chunk["metadata"]),
            )
        )
        stored += 1

    cur.close()
    conn.close()

    logger.info(f"Stored {stored} chunks in knowledge_base")
    return stored
