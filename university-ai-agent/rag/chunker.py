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

    Each chunk dict:
        source   : page category (e.g. "programs")
        title    : page title
        content  : chunk text
        metadata : url, chunk_index
    """
    all_chunks = []

    for page in pages:
        chunks = chunk_text(page["text"])

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source":  page["source"],
                "title":   page["title"],
                "content": chunk,
                "metadata": {
                    "url":         page["url"],
                    "chunk_index": i,
                    "total_chunks": len(chunks),
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
