"""
RAG Retriever — Optimized for speed
=====================================
- Embedding model preloaded at startup (not per-query)
- DB connection reused (no reconnect per query)
- Async-friendly design
"""

import logging
from typing import List, Dict, Optional
import psycopg2
import psycopg2.extras
import psycopg2.pool

logger = logging.getLogger(__name__)

# ── Preloaded model (loaded once at startup) ─────────────────────
_model = None
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def preload(db_url: str):
    """
    Call this ONCE at app startup.
    Loads embedding model + DB pool into memory so queries are instant.
    """
    global _model, _pool

    # Load embedding model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dim, very fast
        logger.info("RAG embedding model loaded (all-MiniLM-L6-v2)")
    except Exception as e:
        logger.warning(f"Could not load embedding model: {e}")
        _model = None

    # DB connection pool
    try:
        _pool = psycopg2.pool.ThreadedConnectionPool(1, 5, db_url, connect_timeout=5)
        logger.info("RAG DB pool ready")
    except Exception as e:
        logger.warning(f"RAG DB pool failed: {e}")
        _pool = None


def _embed(text: str) -> Optional[List[float]]:
    """Embed text using preloaded model — fast because model is already in RAM."""
    if _model is None:
        return None
    try:
        vec = _model.encode(text, normalize_embeddings=True)
        # Pad 384-dim to 1536-dim to match schema
        padded = vec.tolist() + [0.0] * (1536 - len(vec))
        return padded
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None


def retrieve(query: str, top_k: int = 3) -> List[Dict]:
    """
    Find top-k relevant chunks for a query.
    Fast because model + DB pool are preloaded.
    """
    if _model is None or _pool is None:
        return []

    embedding = _embed(query)
    if not embedding:
        return []

    conn = None
    try:
        conn = _pool.getconn()
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM search_knowledge(%s::vector, %s, %s)",
                (str(embedding), top_k, 0.25)
            )
            results = [dict(r) for r in cur.fetchall()]
        logger.info(f"RAG: {len(results)} chunks for '{query[:40]}'")
        return results
    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        return []
    finally:
        if conn and _pool:
            _pool.putconn(conn)


def format_context(chunks: List[Dict]) -> str:
    """Format chunks into a concise context string for the LLM."""
    if not chunks:
        return ""
    parts = [f"[{c['source'].upper()}] {c['content']}" for c in chunks]
    return "\n---\n".join(parts)


def is_ready() -> bool:
    """Check if RAG is ready to use."""
    return _model is not None and _pool is not None
