# Architecture — GIFT University AI Helpdesk

Complete structure of every file and folder with purpose explained.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Student (Browser)                        │
│              http://localhost:3000                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP (Vite proxy — no CORS issues)
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

---

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
        ├─► Groq Whisper STT (verbose_json)
        │       └─► transcript + language (ur/en)
        │
        ├─► detect_language()
        │       ├─► Urdu script check (Unicode range)
        │       └─► Roman Urdu keyword check
        │
        ├─► Intent Classifier (Groq LLaMA, temp=0.0)
        │       └─► admission / fee / programs / scholarship / etc.
        │
        ├─► RAG Retriever
        │       ├─► Embed query (all-mpnet-base-v2, 768-dim → pad 1536)
        │       └─► pgvector cosine similarity → top 3 chunks
        │
        ├─► Groq LLaMA 4 Scout (temp=0.1, max_tokens=120)
        │       ├─► System prompt + GIFT knowledge
        │       ├─► RAG context chunks
        │       └─► Language instruction (reply in Urdu OR English)
        │
        └─► Save to call_logs (Supabase)
                │
                ▼
        POST /demo/speak
                │
                └─► Groq Orpheus TTS → WAV → Browser plays
                    (fallback: browser SpeechSynthesis)
```

---

## RAG Pipeline

```
GIFT University Website (gift.edu.pk)
        │
        ▼
rag/scraper.py
  ├─► Crawls 40+ PHP pages (programs, fees, admissions, etc.)
  └─► Downloads 7 PDFs (fee structure, prospectus, scholarships)
        │
        ▼
rag/chunker.py
  └─► Splits text into 400-word overlapping chunks (50-word overlap)
        │
        ▼
rag/embedder.py
  └─► sentence-transformers all-mpnet-base-v2 → 768-dim vectors
      Padded to 1536-dim → stored in Supabase knowledge_base
        │
        ▼
rag/retriever.py (preloaded at startup)
  └─► Query → embed → pgvector cosine search → top 3 chunks

rag/auto_refresh.py (background thread)
  └─► Every 12 hours: check website for changes → re-ingest if changed
```

---

## Root Directory

```
/
├── README.md              ← Project overview, quick start, API docs
├── ARCHITECTURE.md        ← This file — full structure and flow diagrams
├── start.bat              ← Windows: double-click to start both servers
├── university-ai-agent/   ← Python FastAPI backend
└── university-ui/         ← React frontend
```

---

## Backend: `university-ai-agent/`

```
university-ai-agent/
│
├── .env                   ← API keys (GROQ, Supabase) — never commit
├── .env.example           ← Template for .env
├── requirements.txt       ← Python dependencies
├── start_bot.bat          ← Start backend only
├── install_service.ps1    ← Install as Windows Service (24/7)
├── nssm.exe               ← Windows Service Manager binary
├── check_rag.py           ← Debug: check RAG chunks in DB
├── test_rag.py            ← Debug: test RAG retrieval queries
│
├── app/                   ← Main application package
│   ├── main.py            ← FastAPI app: routes registered, RAG preloaded at startup
│   │
│   ├── ai/                ← AI processing layer
│   │   ├── brain.py       ← Core: intent → RAG → Groq → response (with lang param)
│   │   ├── intent.py      ← Classifies query into categories (temp=0.0)
│   │   └── prompts.py     ← System prompt + GIFT University knowledge base
│   │
│   ├── call/              ← Call handling
│   │   ├── handler.py     ← Text query handler, per-user context management
│   │   └── telnyx_webhook.py ← Telnyx TeXML webhooks (future phone calls)
│   │
│   ├── core/              ← Shared utilities
│   │   ├── config.py      ← Loads .env, encodes special chars in DB URL
│   │   ├── logger.py      ← Logging setup
│   │   └── utils.py       ← Helper functions
│   │
│   ├── db/                ← Database layer
│   │   ├── supabase.py    ← ThreadedConnectionPool, all DB queries
│   │   └── models.py      ← Data models (CallLog, UserSession)
│   │
│   ├── demo/              ← Browser voice + chat API
│   │   └── voice_demo.py  ← /transcribe (STT+lang+AI), /speak (TTS), /chat (text)
│   │
│   ├── memory/            ← Conversation context
│   │   └── context.py     ← Per-user isolated context (no mixing between users)
│   │
│   └── voice/             ← Local voice (optional fallback)
│       ├── stt.py         ← faster-whisper local STT (Urdu+English)
│       └── tts.py         ← ElevenLabs TTS
│
├── rag/                   ← RAG pipeline
│   ├── schema.sql         ← Supabase: knowledge_base table + pgvector index
│   ├── scraper.py         ← Crawls gift.edu.pk pages + PDFs
│   ├── chunker.py         ← Splits text into overlapping chunks
│   ├── embedder.py        ← Generates embeddings, stores in Supabase
│   ├── retriever.py       ← Fast similarity search (preloaded model + pool)
│   ├── auto_refresh.py    ← Background thread: re-ingest on website changes
│   └── ingest.py          ← One-time pipeline: scrape → chunk → embed → store
│
└── database/              ← Supabase SQL
    ├── schema.sql         ← All tables (programs, fees, call_logs, etc.)
    └── seed_data.sql      ← GIFT University data (programs, FAQs, contacts)
```

---

## Frontend: `university-ui/`

```
university-ui/
│
├── package.json           ← Dependencies (React, Vite, React Router)
├── vite.config.js         ← Proxy: /demo/* and /history/* → localhost:8000
├── tailwind.config.js     ← Theme colors (navy, gold)
├── index.html             ← HTML entry point
│
├── public/                ← Static assets
│   ├── gift-logo.png      ← GIFT University official logo
│   └── gift-campus.jpg    ← Campus building photo (background)
│
└── src/
    ├── main.jsx           ← React entry, BrowserRouter
    ├── App.jsx            ← Navbar (Home/Call/Chat/Statistics), theme, routes
    ├── index.css          ← Global styles, Playfair Display + Inter fonts
    │
    ├── pages/
    │   ├── HomePage.jsx   ← Landing: hero, stats, features, how it works, about
    │   ├── CallPage.jsx   ← Voice agent: VAD, STT, TTS, chat bubbles
    │   ├── ChatPage.jsx   ← Text chat: message input, suggestions, history
    │   └── LogsPage.jsx   ← Admin: real-time logs, stats cards, filters, pagination
    │
    └── components/
        ├── Icons.jsx      ← All SVG icons (no emojis)
        ├── Avatar.jsx     ← Animated avatar with ripple rings
        ├── CallControls.jsx ← Start/End/Mute buttons
        ├── ChatBubble.jsx ← Message bubbles (user/bot)
        ├── StatusBadge.jsx ← Listening/Thinking/Speaking badge
        └── Waveform.jsx   ← Animated audio waveform bars
```

---

## Database Tables (Supabase)

```
programs              ← All GIFT programs (BS, MS, PhD, AD)
fee_structure         ← Fee per semester by category
admission_requirements ← Eligibility, documents per program
admission_dates       ← Semester start/end dates
faqs                  ← Common questions and answers
contact_info          ← Department contacts
call_logs             ← Every conversation (user_id, query, response, intent, timestamp)
user_sessions         ← Session data per user
knowledge_base        ← RAG chunks with 1536-dim vector embeddings (pgvector)
```

---

## API Endpoints

```
GET  /                    ← Health check
POST /demo/transcribe     ← Audio → Whisper STT → lang detect → AI → response
POST /demo/speak          ← Text → Orpheus TTS → WAV audio
POST /demo/chat           ← Text message → lang detect → AI → response
GET  /history/{user_id}   ← Call logs (use "all" for all users)
POST /telnyx/incoming     ← Telnyx webhook (future phone integration)
POST /telnyx/process      ← Telnyx speech processing
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Per-user context isolation | Multiple students simultaneously — no history mixing |
| Connection pooling (psycopg2) | Handles concurrent requests without reconnecting |
| RAG preloaded at startup | Model in RAM — queries ~50ms instead of ~3s |
| Browser TTS fallback | If Groq TTS rate-limited, browser speaks instantly |
| Groq over OpenAI | 10x faster, generous free tier, Whisper supports Urdu |
| temperature=0.0 for intent | Deterministic classification — same query, same intent |
| temperature=0.1 for response | Consistent + slightly natural (pure 0 = too rigid) |
| Vite proxy | No CORS issues in dev — all API calls through :3000 |
| Auto-refresh every 12h | RAG stays updated when GIFT website changes |
| Language instruction in prompt | Forces LLM to reply in same language as student |
