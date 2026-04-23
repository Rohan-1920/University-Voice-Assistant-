"""
Text Chunker
=============
Splits scraped page text into smaller overlapping chunks
suitable for embedding and retrieval.

Chunk size: ~400 words (good balance for voice responses)
Overlap:    50 words (context continuity between chunks)
"""

from typing import List, Dict


CHUNK_SIZE    = 400   # words per chunk
CHUNK_OVERLAP = 50    # words overlap between chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping word-based chunks."""
    words  = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        end   = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 50:   # skip tiny chunks
            chunks.append(chunk.strip())
        start += chunk_size - overlap  # slide with overlap

    return chunks


def chunk_pages(pages: List[Dict]) -> List[Dict]:
    """
    Convert scraped pages into a flat list of chunks.
    Handles both old format (source key) and new scraper format (url/type keys).
    """
    all_chunks = []

    for page in pages:
        chunks = chunk_text(page["text"])

        # Derive source from URL or use existing source key
        if "source" in page:
            source = page["source"]
        else:
            url = page.get("url", "")
            doc_type = page.get("type", "webpage")
            # Extract meaningful source name from URL
            if "programs" in url:    source = "programs"
            elif "fee" in url:       source = "fee"
            elif "admission" in url: source = "admissions"
            elif "scholar" in url:   source = "scholarship"
            elif "hostel" in url:    source = "hostel"
            elif "transport" in url: source = "transport"
            elif "faculty" in url:   source = "faculty"
            elif "faq" in url:       source = "faq"
            elif "contact" in url:   source = "contact"
            elif "about" in url:     source = "about"
            elif "facilit" in url:   source = "facilities"
            elif "news" in url:      source = "news"
            elif "event" in url:     source = "events"
            elif "prospectus" in url or doc_type == "pdf": source = "prospectus"
            elif "scholarship" in url: source = "scholarship"
            else:                    source = "general"

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source":  source,
                "title":   page.get("title", source),
                "content": chunk,
                "metadata": {
                    "url":          page.get("url", ""),
                    "chunk_index":  i,
                    "total_chunks": len(chunks),
                    "type":         page.get("type", "webpage"),
                }
            })

    return all_chunks


if __name__ == "__main__":
    # Quick test
    sample = {"source": "test", "title": "Test Page", "url": "http://test.com",
              "text": "word " * 1000}
    chunks = chunk_pages([sample])
    print(f"1000 words → {len(chunks)} chunks")
    print(f"First chunk: {chunks[0]['content'][:80]}...")
