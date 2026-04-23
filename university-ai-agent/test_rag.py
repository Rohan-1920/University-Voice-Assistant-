from rag.retriever import preload, retrieve, format_context
from app.core.config import config
import time

preload(config.DATABASE_URL)
time.sleep(2)

queries = [
    "BS Data Science available hai GIFT mein?",
    "What programs does GIFT offer?",
    "scholarship policy GIFT",
]

for q in queries:
    print(f"\nQuery: {q}")
    chunks = retrieve(q, top_k=3)
    print(f"Chunks found: {len(chunks)}")
    for c in chunks:
        sim = round(c['similarity'], 2)
        src = c['source']
        txt = c['content'][:120]
        print(f"  [{src}] sim={sim} | {txt}")
