"""
RAG Auto-Refresh
=================
Runs in background — checks GIFT website for changes every N hours.
If changes detected, re-ingests updated data into knowledge base.

Usage (run once, keeps running):
    python -m rag.auto_refresh

Or import and call start_scheduler() in main.py for background refresh.
"""

import hashlib
import logging
import time
import threading
import requests
from typing import Dict

logger = logging.getLogger(__name__)

REFRESH_INTERVAL_HOURS = 12   # check every 12 hours
CHECK_URLS = [
    "https://gift.edu.pk/programs.php",
    "https://gift.edu.pk/admissions.php",
    "https://gift.edu.pk/scholarships.php",
    "https://gift.edu.pk/news.php",
    "https://gift.edu.pk/events.php",
    "https://gift.edu.pk/fee-structure.php",
]

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Store page hashes to detect changes
_page_hashes: Dict[str, str] = {}


def _get_hash(url: str) -> str:
    """Get MD5 hash of page content."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return hashlib.md5(r.content).hexdigest()
    except Exception:
        return ""


def _check_for_changes() -> bool:
    """Returns True if any page has changed since last check."""
    changed = False
    for url in CHECK_URLS:
        new_hash = _get_hash(url)
        old_hash = _page_hashes.get(url, "")
        if new_hash and new_hash != old_hash:
            logger.info(f"Change detected: {url}")
            _page_hashes[url] = new_hash
            changed = True
    return changed


def _run_ingest():
    """Run the full ingest pipeline."""
    try:
        logger.info("Starting RAG re-ingest due to website changes...")
        from rag.scraper  import scrape_all
        from rag.chunker  import chunk_pages
        from rag.embedder import store_chunks
        from app.core.config import config

        pages  = scrape_all()
        chunks = chunk_pages(pages)
        stored = store_chunks(chunks, config.DATABASE_URL)

        # Reload retriever pool
        from rag.retriever import preload
        preload(config.DATABASE_URL)

        logger.info(f"RAG re-ingest complete — {stored} chunks updated")
    except Exception as e:
        logger.error(f"RAG re-ingest failed: {e}")


def _refresh_loop():
    """Background loop — checks for changes and re-ingests if needed."""
    logger.info(f"RAG auto-refresh started — checking every {REFRESH_INTERVAL_HOURS}h")

    # Initialize hashes on first run
    for url in CHECK_URLS:
        _page_hashes[url] = _get_hash(url)

    while True:
        time.sleep(REFRESH_INTERVAL_HOURS * 3600)
        logger.info("Checking GIFT website for updates...")
        if _check_for_changes():
            _run_ingest()
        else:
            logger.info("No changes detected — RAG is up to date")


def start_scheduler():
    """Start auto-refresh in a background daemon thread."""
    t = threading.Thread(target=_refresh_loop, daemon=True)
    t.start()
    logger.info("RAG auto-refresh scheduler started in background")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
    _refresh_loop()
