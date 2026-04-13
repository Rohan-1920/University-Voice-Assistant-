"""
Browser Voice Demo
==================
Flow:
  Browser mic → audio blob → POST /demo/transcribe → Groq Whisper STT
  → AI brain → text response → POST /demo/speak → browser plays audio
"""

import io
import os
import requests
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import Optional
from app.core.config import config
from app.core.logger import logger
from app.ai.brain import ai_brain
from app.memory.context import context_manager
from app.db.supabase import db

router = APIRouter(prefix="/demo", tags=["Browser Demo"])

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_TTS_URL = "https://api.groq.com/openai/v1/audio/speech"


# ── STT via Groq Whisper ─────────────────────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Send audio to Groq Whisper — supports Urdu + English"""
    try:
        response = requests.post(
            GROQ_STT_URL,
            headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
            files={"file": (filename, audio_bytes, "audio/webm")},
            data={
                "model": "whisper-large-v3-turbo",
                "response_format": "text",
                "prompt": "This is a university helpdesk call. Student speaks Urdu or English only."
            },
            timeout=15
        )
        if response.status_code == 200:
            return response.text.strip()
        logger.error(f"Groq STT error: {response.status_code} {response.text}")
        return ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""


# ── TTS via Groq Orpheus ─────────────────────────────────────────────

def text_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech — warm, natural, clear voice"""
    try:
        # Keep under 400 chars for TTS
        tts_text = text[:400] if len(text) > 400 else text

        # Natural helpdesk tone — no direction tags needed for diana
        tts_input = tts_text

        response = requests.post(
            GROQ_TTS_URL,
            headers={
                "Authorization": f"Bearer {config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "canopylabs/orpheus-v1-english",
                "input": tts_input,
                "voice": "diana",   # stable, clear, natural
                "response_format": "wav"
            },
            timeout=20
        )
        if response.status_code == 200:
            return response.content
        logger.error(f"Groq TTS error: {response.status_code} {response.text}")
        return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


# ── API Routes ───────────────────────────────────────────────────────

@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    user_id: str = Form(default="demo_user")
):
    """Receive audio → transcribe → AI response"""
    try:
        audio_bytes = await audio.read()

        # STT
        text = transcribe_audio(audio_bytes, audio.filename or "audio.webm")
        if not text:
            return {"transcript": "", "response": "Dobara bolein please.", "intent": "unknown"}

        logger.info(f"[{user_id}] Transcript: {text}")

        # AI
        ctx = context_manager.get(user_id)
        ctx.add_message("user", text)
        result = ai_brain.process_query(text, ctx.get_context_string())
        ctx.add_message("assistant", result["response"], result["intent"])

        # Save to DB (non-blocking)
        try:
            db.log_call(user_id, text, result["response"], result["intent"])
        except Exception as e:
            logger.error(f"DB log failed: {e}")

        return {
            "transcript": text,
            "response": result["response"],
            "intent": result["intent"]
        }

    except Exception as e:
        logger.error(f"Transcribe error: {e}")
        return {"transcript": "", "response": "Koi masla aa gaya, dobara try karein.", "intent": "unknown"}


@router.post("/speak")
async def speak(request: Request):
    """Convert AI response text → WAV audio"""
    try:
        body = await request.json()
        speak_text = body.get("text", "")

        if not speak_text:
            return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")

        audio_bytes = text_to_speech(speak_text)
        if audio_bytes:
            return StreamingResponse(
                io.BytesIO(audio_bytes),
                media_type="audio/wav",
                headers={"Content-Disposition": "inline; filename=response.wav"}
            )
    except Exception as e:
        logger.error(f"Demo speak error: {e}")

    return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")


@router.get("/", response_class=HTMLResponse)
async def demo_page():
    """Serve the browser demo UI"""
    html = open(
        os.path.join(os.path.dirname(__file__), "index.html"),
        encoding="utf-8"
    ).read()
    return HTMLResponse(content=html)
