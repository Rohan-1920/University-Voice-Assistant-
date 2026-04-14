# Project Architecture — GIFT University AI Helpdesk

Complete structure of every file and folder with purpose explained.

---

## System Flow Diagram

```
Student opens browser
        │
        ▼
┌─────────────────────┐
│   React Frontend    │  localhost:3000
│   university-ui/    │
└────────┬────────────┘
         │ HTTP (Vite proxy)
         ▼
┌─────────────────────┐
│   FastAPI Backend   │  localhost:8000
│ university-ai-agent │
└────────┬────────────┘
         │
    ┌────┴────────────────────────┐
    │                             │
    ▼                             ▼
┌──────────┐              ┌──────────────┐
│ Groq API │              │  Supabase DB │
│ LLaMA 4  │              │  PostgreSQL  │
│ Whisper  │              │  + pgvector  │
│ Orpheus  │              └──────────────┘
└──────────┘
```

---

## Voice Call Flow

```
User speaks
    │
    ▼
Browser MediaRecorder (audio/webm)
    │
    ▼
POST /demo/transcribe
    │
    ├─► Groq Whisper STT ──► transcript text
    │
    ├─► Intent Classifier (Groq LLaMA) ──► intent label
    │
    ├─► RAG Retriever
    │       │
    │       ├─► Embed query (sentence-transformers)
    │       └─► Supabase pgvector search ──► relevant chunks
    │
    ├─► Groq LLaMA 4 ──► AI response text
    │
    └─► Save to call_logs (Supabase)
    │
    ▼
POST /demo/speak
    │
    └─► Groq Orpheus TTS ──► WAV audio
    │
    ▼
Browser plays audio
```

---

## Root Directory

```
/
├── README.md              ← Project overview and quick start
├── ARCHITECTURE.md        ← This file — full structure diagram
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
│
├── app/                   ← Main application package
│   ├── main.py            ← FastAPI app entry point, routes registered here
│   │
│   ├── ai/                ← AI processing layer
│   │   ├── brain.py       ← Core AI: intent → RAG/DB → Groq → response
│   │   ├── intent.py      ← Classifies user query into categories
│   │   └── prompts.py     ← System prompt + GIFT University knowledge base
│   │
│   ├── call/              ← Call handling
│   │   ├── handler.py     ← Text query handler, per-user context management
│   │   └── telnyx_webhook.py ← Telnyx TeXML webhooks (future phone calls)
│   │
│   ├── core/              ← Shared utilities
│   │   ├── config.py      ← Loads .env, builds DB URL with encoding
│   │   ├── logger.py      ← Logging setup
│   │   └── utils.py       ← Helper functions (sanitize, truncate, etc.)
│   │
│   ├── db/                ← Database layer
│   │   ├── supabase.py    ← PostgreSQL connection pool, all DB queries
│   │   └── models.py      ← Data models (CallLog, UserSession, StudentInfo)
│   │
│   ├── demo/              ← Browser voice demo API
│   │   └── voice_demo.py  ← /demo/transcribe (STT+AI) and /demo/speak (TTS)
│   │
│   ├── memory/            ← Conversation context
│   │   └── context.py     ← Per-user isolated context manager (no mixing)
│   │
│   └── voice/             ← Local voice processing (optional)
│       ├── stt.py         ← faster-whisper local STT (Urdu+English)
│       └── tts.py         ← ElevenLabs TTS (fallback)
│
├── rag/                   ← RAG (Retrieval Augmented Generation) pipeline
│   ├── schema.sql         ← Supabase: creates knowledge_base table + pgvector
│   ├── scraper.py         ← Scrapes GIFT University website pages
│   ├── chunker.py         ← Splits scraped text into overlapping chunks
│   ├── embedder.py        ← Generates embeddings, stores in Supabase
│   ├── retriever.py       ← Finds relevant chunks for a query (fast, preloaded)
│   └── ingest.py          ← One-time pipeline: scrape → chunk → embed → store
│
└── database/              ← Supabase SQL files
    ├── schema.sql         ← Creates all tables (programs, fees, call_logs, etc.)
    └── seed_data.sql      ← Fills tables with GIFT University data
```

---

## Frontend: `university-ui/`

```
university-ui/
│
├── package.json           ← Dependencies (React, Vite, React Router)
├── vite.config.js         ← Vite config + proxy (/demo, /history → :8000)
├── tailwind.config.js     ← Tailwind theme (navy, gold colors)
├── index.html             ← HTML entry point
│
├── public/                ← Static assets served directly
│   ├── gift-logo.png      ← GIFT University official logo
│   └── gift-campus.jpg    ← Campus building photo (background)
│
└── src/
    ├── main.jsx           ← React entry point, BrowserRouter setup
    ├── App.jsx            ← Navbar (Home/Call/Statistics), theme toggle, routes
    ├── index.css          ← Global styles, Google Fonts, animations
    │
    ├── pages/             ← Full page components
    │   ├── HomePage.jsx   ← Landing page: hero, features, how it works, about
    │   ├── CallPage.jsx   ← Voice agent: VAD, STT, TTS, chat bubbles
    │   └── LogsPage.jsx   ← Admin dashboard: real-time logs, stats, filters
    │
    └── components/        ← Reusable UI components
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
programs            ← All GIFT programs (BS, MS, PhD, AD)
fee_structure       ← Fee per semester by category
admission_requirements ← Eligibility, documents per program
admission_dates     ← Semester start/end dates
faqs                ← Common questions and answers
contact_info        ← Department contacts
call_logs           ← Every conversation (user_id, query, response, intent, timestamp)
user_sessions       ← Session data per user
knowledge_base      ← RAG chunks with vector embeddings (pgvector)
```

---

## API Endpoints

```
GET  /                    ← Health check
POST /query               ← Text query (returns intent + response)
GET  /history/{user_id}   ← Call history (use "all" for all logs)
POST /demo/transcribe     ← Audio → STT → AI → response (main voice endpoint)
POST /demo/speak          ← Text → TTS → WAV audio
POST /telnyx/incoming     ← Telnyx webhook (future phone calls)
POST /telnyx/process      ← Telnyx speech processing
```

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Per-user context isolation | Multiple students can call simultaneously without mixing history |
| Connection pooling (psycopg2) | Handles concurrent requests without reconnecting each time |
| RAG preloaded at startup | Embedding model loaded once — queries are fast (~50ms) |
| Browser TTS fallback | If Groq TTS rate-limited, browser speaks instantly |
| Groq over OpenAI | 10x faster, generous free tier, supports Urdu via Whisper |
| Vite proxy | No CORS issues in development — all API calls go through :3000 |
