# GIFT University AI Helpdesk Assistant

An AI-powered voice helpdesk for GIFT University Gujranwala — students can ask about admissions, programs, fees, scholarships, and more in **Urdu or English**, and get instant accurate answers.

---

## Live Demo

```
http://localhost:3000
```

---

## Features

- 🎙️ **Voice conversations** — speak naturally, no typing needed
- 🌐 **Bilingual** — Urdu and English, auto-detected
- ⚡ **Fast responses** — under 2 seconds
- 🤖 **Groq AI + RAG** — LLaMA 4 with retrieval from real GIFT data
- 📊 **Analytics dashboard** — real-time call logs with intent tracking
- 🗄️ **Supabase** — all conversations stored with timestamp

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| AI Model | Groq LLaMA 4 Scout |
| STT | Groq Whisper Large v3 Turbo |
| TTS | Groq Orpheus v1 |
| RAG | sentence-transformers + pgvector |
| Database | Supabase PostgreSQL |
| Styling | Inline CSS + Playfair Display font |

---

## Quick Start

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

Copy `university-ai-agent/.env.example` to `.env` and fill in:

```env
GROQ_API_KEY=gsk_...          # From console.groq.com (free)
DATABASE_URL=postgresql://... # From Supabase dashboard
SUPABASE_URL=https://...
SUPABASE_KEY=sb_...
```

---

## RAG Setup (One-time)

```powershell
cd university-ai-agent
pip install sentence-transformers beautifulsoup4

# Run schema in Supabase SQL Editor first:
# rag/schema.sql

# Then ingest GIFT University website data:
python -m rag.ingest
```

---

## Project Structure

See `ARCHITECTURE.md` for a detailed diagram of every file and folder.

---

## Pages

| Route | Description |
|---|---|
| `/` | Home — landing page with features and info |
| `/call` | Voice agent — talk to the AI |
| `/statistics` | Admin dashboard — call logs and analytics |

---

## Contact

GIFT University Gujranwala · 055-111-GIFT-00 · [gift.edu.pk](https://gift.edu.pk)
