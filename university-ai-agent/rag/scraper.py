"""
GIFT University Web Scraper
============================
Scrapes ALL pages from gift.edu.pk including:
- All PHP pages (programs, admissions, fees, etc.)
- PDFs (fee structure, prospectus, scholarships)
- Auto-discovers new pages by crawling links

Usage:
    python -m rag.scraper
"""

import requests
import time
import logging
import io
from bs4 import BeautifulSoup
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

BASE_URL = "https://gift.edu.pk"
HEADERS  = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Seed pages to start crawling from
SEED_PAGES = [
    "/",
    "/programs.php",
    "/admissions.php",
    "/scholarships.php",
    "/facilities.php",
    "/schools.php",
    "/faqs.php",
    "/contact.php",
    "/about-us.php",
    "/life-at-gift.php",
    "/downloads.php",
    "/fee-structure.php",
    "/hostel.php",
    "/transport.php",
    "/hallmarks.php",
    "/offices.php",
    "/centres.php",
    "/faculty.php",
    "/news.php",
    "/events.php",
    "/research.php",
    "/library.php",
    "/career.php",
]

# PDFs to always include
PDF_URLS = [
    "https://gift.edu.pk/downloads/fee/national-fee-structure.pdf",
    "https://gift.edu.pk/downloads/fee/international-fee-structure.pdf",
    "https://gift.edu.pk/downloads/programs/programs-offered.pdf",
    "https://gift.edu.pk/downloads/prospectus/prospectus.pdf",
    "https://gift.edu.pk/downloads/prospectus/general-brochure.pdf",
    "https://gift.edu.pk/downloads/scholarships/scholarship-policy.pdf",
    "https://gift.edu.pk/downloads/scholarships/scholarship-form.pdf",
]


def clean_text(text: str) -> str:
    """Remove extra whitespace."""
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and len(l) > 5]
    return "\n".join(lines)


def scrape_page(url: str) -> Dict:
    """Scrape a single HTML page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Remove nav, footer, scripts
        for tag in soup(["nav", "footer", "script", "style", "header", "noscript", "iframe"]):
            tag.decompose()

        # Get page title
        title = soup.find("title")
        title = title.get_text(strip=True) if title else url

        # Get main content
        main = (soup.find("main") or
                soup.find("div", class_=lambda c: c and "content" in c.lower()) or
                soup.find("div", id=lambda i: i and "content" in i.lower()) or
                soup.body)

        text = clean_text(main.get_text(separator="\n") if main else "")

        # Also find all internal links for crawling
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".php" in href and not href.startswith("http"):
                links.add(urljoin(BASE_URL, href))
            elif "gift.edu.pk" in href and ".php" in href:
                links.add(href)

        logger.info(f"Scraped {url} — {len(text)} chars")
        return {"url": url, "title": title, "text": text, "links": links, "type": "webpage"}

    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {e}")
        return None


def scrape_pdf(url: str) -> Dict:
    """Extract text from a PDF."""
    try:
        import pypdf

        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()

        reader = pypdf.PdfReader(io.BytesIO(r.content))
        text_parts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t.strip())

        text = clean_text("\n".join(text_parts))
        title = url.split("/")[-1].replace("-", " ").replace(".pdf", "").title()

        logger.info(f"Scraped PDF {url} — {len(text)} chars, {len(reader.pages)} pages")
        return {"url": url, "title": title, "text": text, "links": set(), "type": "pdf"}

    except ImportError:
        logger.warning("pypdf not installed — skipping PDF. Run: pip install pypdf")
        return None
    except Exception as e:
        logger.warning(f"Failed to scrape PDF {url}: {e}")
        return None


def scrape_all() -> List[Dict]:
    """
    Crawl GIFT University website:
    1. Start from seed pages
    2. Discover new pages from links
    3. Scrape all PDFs
    """
    visited: Set[str] = set()
    queue:   List[str] = [urljoin(BASE_URL, p) for p in SEED_PAGES]
    results: List[Dict] = []

    # Scrape HTML pages
    logger.info(f"Starting crawl from {len(queue)} seed pages...")
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        data = scrape_page(url)
        if data and len(data["text"]) > 100:
            results.append(data)
            # Add newly discovered links to queue (max 100 pages total)
            if len(visited) < 100:
                for link in data["links"]:
                    if link not in visited and BASE_URL in link:
                        queue.append(link)

        time.sleep(0.5)  # polite crawling

    logger.info(f"Scraped {len(results)} HTML pages")

    # Scrape PDFs
    logger.info("Scraping PDFs...")
    for pdf_url in PDF_URLS:
        data = scrape_pdf(pdf_url)
        if data and len(data["text"]) > 50:
            results.append(data)
        time.sleep(0.5)

    logger.info(f"Total documents scraped: {len(results)}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
    pages = scrape_all()
    print(f"\nTotal: {len(pages)} documents")
    for p in pages:
        print(f"  [{p['type'].upper()}] {p['title'][:60]} — {len(p['text'])} chars")
