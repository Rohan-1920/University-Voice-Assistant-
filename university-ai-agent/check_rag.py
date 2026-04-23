from app.core.config import config
import psycopg2

conn = psycopg2.connect(config.DATABASE_URL, connect_timeout=10)
cur = conn.cursor()

# Check total chunks
cur.execute("SELECT COUNT(*) FROM knowledge_base")
print('Total chunks:', cur.fetchone()[0])

# Check sources
cur.execute("SELECT source, COUNT(*) FROM knowledge_base GROUP BY source ORDER BY COUNT(*) DESC")
print('\nChunks by source:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Search for Data Science
cur.execute("SELECT title, content FROM knowledge_base WHERE content ILIKE '%data science%' LIMIT 3")
rows = cur.fetchall()
print(f'\nData Science mentions: {len(rows)}')
for r in rows:
    print(f'  [{r[0]}] {r[1][:100]}...')

# Search for BS programs
cur.execute("SELECT title, content FROM knowledge_base WHERE content ILIKE '%BS %' LIMIT 5")
rows = cur.fetchall()
print(f'\nBS program mentions: {len(rows)}')
for r in rows:
    print(f'  [{r[0]}] {r[1][:80]}...')

conn.close()
