# GIFT University AI Helpdesk Assistant

An AI-powered voice and chat helpdesk for GIFT University Gujranwala. Students can ask about admissions, programs, fees, scholarships, and more in **Urdu or English** and get instant accurate answers.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Student (Browser)                        │
│              http://localhost:3000                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP (Vite proxy)
          ┌────────────▼────────────┐
          │    React Frontend       │
          │    university-ui/       │
          │                         │
          │  / ──── Home Page       │
          │  /call ─ Voice Agent    │
          │  /chat ─ Chat Page      │
          │  /statistics ─ Logs     │
          └────────────┬────────────┘
                       │ REST API
          ┌────────────▼────────────┐
          │   FastAPI Backend       │
          │ university-ai-agent/    │
          │   localhost:8000        │
          └──┬──────────┬───────────┘
             │          │
    ┌────────▼──┐  ┌────▼──────────┐
    │ Groq API  │  │  Supabase DB  │
    │           │  │  PostgreSQL   │
    │ Whisper   │  │  + pgvector   │
    │ LLaMA 4   │  │               │
    │ Orpheus   │  │  call_logs    │
    └───────────┘  │  knowledge_base│
                   └───────────────┘
```

## Voice Call Flow

```
User speaks into mic
        │
        ▼
Browser MediaRecorder (audio/webm)
        │
        ▼
POST /demo/transcribe
        │
        ├─► Groq Whisper STT
        │       └─► transcript + language detection (ur/en)
        │
        ├─► Intent Classifier (Groq LLaMA, temp=0.0)
        │       └─► admission / fee / programs / scholarship / etc.
        │
        ├─► RAG Retriever
        │       ├─► Embed query (sentence-transformers all-mpnet-base-v2)
        │       └─► Supabase pgvector similarity search → top 3 chunks
        │
        ├─► Groq LLaMA 4 Scout (temp=0.1, max_tokens=120)
        │       └─► Response in same language as query (Urdu/English)
        │
        └─► Save to call_logs (Supabase)
                │
                ▼
        POST /demo/speak
                │
                └─► Groq Orpheus TTS → WAV audio → Browser plays
```

---

## Features

- 🎙️ **Voice conversations** — speak naturally, no typing needed
- 💬 **Text chat** — type questions in Urdu or English
- 🌐 **Auto language detection** — Urdu script, Roman Urdu, or English
- ⚡ **Fast responses** — under 2 seconds end-to-end
- 🤖 **RAG pipeline** — LLaMA 4 + real GIFT University data
- 📊 **Analytics dashboard** — real-time call logs with intent tracking
- 🔄 **Auto-refresh** — RAG updates every 12 hours from GIFT website
- 🗄️ **Supabase** — all conversations stored with timestamp

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + React Router |
| Backend | FastAPI (Python 3.13) |
| AI Model | Groq LLaMA 4 Scout (free tier) |
| STT | Groq Whisper Large v3 Turbo |
| TTS | Groq Orpheus v1 (diana voice) |
| RAG Embeddings | sentence-transformers all-mpnet-base-v2 |
| Vector Search | Supabase pgvector |
| Database | Supabase PostgreSQL |
| Connection Pool | psycopg2 ThreadedConnectionPool |
| Web Scraping | BeautifulSoup4 + pypdf |

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- Supabase account (free)
- Groq API key (free — [console.groq.com](https://console.groq.com))

### 1. Backend

```powershell
cd university-ai-agent
pip install -r requirements.txt
python -m app.main
# Runs on http://localhost:8000
```

### 2. Frontend

```powershell
cd university-ui
npm install
npm run dev
# Runs on http://localhost:3000
```

### 3. One-click start (Windows)

Double-click `start.bat` in the root folder.

---

## Environment Variables

Edit `university-ai-agent/.env`:

```env
GROQ_API_KEY=gsk_...          # From console.groq.com (free)
DATABASE_URL=postgresql://... # From Supabase → Settings → Database → URI
SUPABASE_URL=https://...
SUPABASE_KEY=sb_...
```

---

## RAG Setup (One-time)

```powershell
cd university-ai-agent

# 1. Run schema in Supabase SQL Editor:
#    rag/schema.sql

# 2. Install extra dependencies
pip install sentence-transformers beautifulsoup4 pypdf

# 3. Ingest GIFT University website + PDFs
python -m rag.ingest
```

This scrapes 40+ pages and 7 PDFs from gift.edu.pk, chunks them, generates embeddings, and stores in Supabase. Takes ~10 minutes once.

After that, RAG auto-refreshes every 12 hours.

---

## Pages

| Route | Description |
|---|---|
| `/` | Home — landing page with features and info |
| `/call` | Voice agent — talk to the AI |
| `/chat` | Text chat — type questions |
| `/statistics` | Admin dashboard — call logs and analytics |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/demo/transcribe` | Audio → STT → AI → response |
| POST | `/demo/speak` | Text → TTS → WAV |
| POST | `/demo/chat` | Text message → AI → response |
| GET | `/history/{user_id}` | Call history (use `all` for all) |

---

## Project Structure

See `ARCHITECTURE.md` for complete file-by-file breakdown.

---

## Contact

GIFT University Gujranwala · 055-111-GIFT-00 · [gift.edu.pk](https://gift.edu.pk)
