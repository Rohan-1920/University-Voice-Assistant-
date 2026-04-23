"""
RAG Ingestion Pipeline
=======================
Scrapes GIFT University website + PDFs, chunks, embeds, stores in Supabase.

Run this ONCE to set up, then auto_refresh.py keeps it updated.

    cd university-ai-agent
    python -m rag.ingest
"""

import logging
import sys
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

    logger.info("=" * 55)
    logger.info("GIFT University RAG Ingestion Pipeline")
    logger.info("=" * 55)

    # Step 1: Scrape
    logger.info("Step 1/3 — Scraping GIFT University website + PDFs...")
    pages = scrape_all()
    logger.info(f"  Scraped {len(pages)} documents")

    if not pages:
        logger.error("No pages scraped. Check internet connection.")
        sys.exit(1)

    # Step 2: Chunk
    logger.info("Step 2/3 — Splitting into chunks...")
    chunks = chunk_pages(pages)
    logger.info(f"  Created {len(chunks)} chunks")

    # Step 3: Embed + Store
    logger.info("Step 3/3 — Generating embeddings and storing in Supabase...")
    stored = store_chunks(chunks, config.DATABASE_URL)

    logger.info("=" * 55)
    logger.info(f"Done! {stored} chunks stored in knowledge_base")
    logger.info("Bot will now use RAG for accurate answers.")
    logger.info("=" * 55)


if __name__ == "__main__":
    run()
