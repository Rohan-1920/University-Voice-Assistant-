"""
RAG Ingestion Pipeline
=======================
One-time script to:
  1. Scrape GIFT University website
  2. Split into chunks
  3. Generate embeddings
  4. Store in Supabase

Run this once (or whenever GIFT website updates):
    cd university-ai-agent
    python -m rag.ingest
"""

import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def run():
    from rag.scraper  import scrape_all
    from rag.chunker  import chunk_pages
    from rag.embedder import store_chunks
    from app.core.config import config

    if not config.DATABASE_URL:
        logger.error("DATABASE_URL not set in .env")
        sys.exit(1)

    # ── Step 1: Scrape ──────────────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Step 1: Scraping GIFT University website...")
    pages = scrape_all()
    logger.info(f"Scraped {len(pages)} pages")

    if not pages:
        logger.error("No pages scraped. Check internet connection.")
        sys.exit(1)

    # ── Step 2: Chunk ───────────────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Step 2: Splitting into chunks...")
    chunks = chunk_pages(pages)
    logger.info(f"Created {len(chunks)} chunks")

    # ── Step 3: Embed + Store ───────────────────────────────────────
    logger.info("=" * 50)
    logger.info("Step 3: Generating embeddings and storing in Supabase...")
    stored = store_chunks(chunks, config.DATABASE_URL)

    # ── Done ────────────────────────────────────────────────────────
    logger.info("=" * 50)
    logger.info(f"✅ RAG ingestion complete! {stored} chunks stored.")
    logger.info("You can now run the agent — it will use RAG for answers.")


if __name__ == "__main__":
    run()
