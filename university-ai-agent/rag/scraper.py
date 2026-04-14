"""
GIFT University Web Scraper
============================
Scrapes all relevant pages from gift.edu.pk and returns
structured data chunks ready for embedding.

Usage:
    python -m rag.scraper
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import logging

logger = logging.getLogger(__name__)

# All pages to scrape
PAGES = [
    {"url": "https://gift.edu.pk/about-us.php",      "source": "about",       "title": "About GIFT University"},
    {"url": "https://gift.edu.pk/programs.php",       "source": "programs",    "title": "Programs Overview"},
    {"url": "https://gift.edu.pk/admissions.php",     "source": "admissions",  "title": "Admissions Process"},
    {"url": "https://gift.edu.pk/scholarships.php",   "source": "scholarship", "title": "Scholarships & Financial Aid"},
    {"url": "https://gift.edu.pk/facilities.php",     "source": "facilities",  "title": "Campus Facilities"},
    {"url": "https://gift.edu.pk/schools.php",        "source": "schools",     "title": "Schools & Departments"},
    {"url": "https://gift.edu.pk/faqs.php",           "source": "faq",         "title": "Frequently Asked Questions"},
    {"url": "https://gift.edu.pk/contact.php",        "source": "contact",     "title": "Contact Information"},
    {"url": "https://gift.edu.pk/hallmarks.php",      "source": "hallmarks",   "title": "Hallmarks of Excellence"},
    {"url": "https://gift.edu.pk/life-at-gift.php",   "source": "campus_life", "title": "Life at GIFT"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def clean_text(text: str) -> str:
    """Remove extra whitespace and empty lines."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l and len(l) > 3]
    return "\n".join(lines)


def scrape_page(url: str, source: str, title: str) -> Dict:
    """Scrape a single page and return structured data."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove nav, footer, scripts, styles
        for tag in soup(["nav", "footer", "script", "style", "header", "noscript"]):
            tag.decompose()

        # Get main content
        main = soup.find("main") or soup.find("div", class_="container") or soup.body
        text = clean_text(main.get_text(separator="\n") if main else "")

        logger.info(f"Scraped {url} — {len(text)} chars")
        return {
            "url":    url,
            "source": source,
            "title":  title,
            "text":   text,
        }

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None


def scrape_all() -> List[Dict]:
    """Scrape all GIFT University pages."""
    results = []
    for page in PAGES:
        data = scrape_page(page["url"], page["source"], page["title"])
        if data and data["text"]:
            results.append(data)
        time.sleep(1)  # be polite to the server

    logger.info(f"Scraped {len(results)}/{len(PAGES)} pages successfully")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pages = scrape_all()
    for p in pages:
        print(f"✓ {p['title']} — {len(p['text'])} chars")
