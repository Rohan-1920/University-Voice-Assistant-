"""
Browser Voice + Chat Demo
==========================
Endpoints:
  POST /demo/transcribe  — audio → STT → language detect → AI → response
  POST /demo/speak       — text → TTS → WAV
  POST /demo/chat        — text message → AI → response (chat mode)
"""

import io
import re
import requests
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from typing import Optional

from app.core.config import config
from app.core.logger import logger
from app.ai.brain import ai_brain
from app.memory.context import context_manager
from app.db.supabase import db

router = APIRouter(prefix="/demo", tags=["Demo"])

GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

# Urdu Unicode range check
URDU_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')


def detect_language(text: str) -> str:
    """
    Detect if text is Urdu or English.
    Returns 'ur' for Urdu/Roman-Urdu, 'en' for English.
    """
    if not text:
        return 'en'

    # If Urdu script characters found → definitely Urdu
    if URDU_PATTERN.search(text):
        return 'ur'

    # Pure Roman Urdu words (NOT shared with English)
    roman_urdu_only = [
        'kya', 'hai', 'hain', 'mujhe', 'mera', 'meri', 'aap', 'ap',
        'kaise', 'kahan', 'kab', 'kyun', 'kaun', 'kitna', 'kitni',
        'chahiye', 'chahta', 'chahti', 'batao', 'bata',
        'nahi', 'nahin', 'hoga', 'hogi', 'wala', 'wali',
        'mein', 'se', 'ko', 'ne', 'par', 'pe', 'tak',
        'aur', 'ya', 'lekin', 'magar', 'phir', 'toh',
        'shukriya', 'shukria', 'meherbani', 'janab', 'sahib',
        'karo', 'karna', 'karein', 'karoon', 'karta', 'karti',
        'dena', 'dein', 'dijiye', 'batana', 'samjhao',
        'hona', 'hoti', 'hota', 'tha', 'thi', 'the',
        'woh', 'yeh', 'ye', 'is', 'us', 'in', 'un',
        'bhi', 'sirf', 'bas', 'abhi', 'phir', 'agar',
    ]

    words = text.lower().split()
    if not words:
        return 'en'

    urdu_count = sum(1 for w in words if w in roman_urdu_only)

    # Need at least 2 Urdu words OR >30% of words to be Urdu
    if urdu_count >= 2 or (len(words) > 0 and urdu_count / len(words) > 0.3):
        return 'ur'

    return 'en'


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> tuple[str, str]:
    """
    STT via Groq Whisper.
    Returns (transcript, detected_language)
    """
    try:
        response = requests.post(
            GROQ_STT_URL,
            headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
            files={"file": (filename, audio_bytes, "audio/webm")},
            data={
                "model": "whisper-large-v3-turbo",
                "response_format": "verbose_json",  # gives us language detection
                "prompt": (
                    "GIFT University Pakistan helpdesk. "
                    "Student speaks Pakistani Urdu or English. "
                    "If Urdu: transcribe in Urdu script (not Hindi/Devanagari). "
                    "If English: transcribe in English."
                ),
            },
            timeout=20
        )
        if response.status_code == 200:
            data = response.json()
            text = data.get("text", "").strip()
            # Whisper also returns detected language
            whisper_lang = data.get("language", "en")
            # Map to our codes
            lang = "ur" if whisper_lang in ("urdu", "ur", "hindi") else "en"
            # Override with our own detection if Urdu script found
            if URDU_PATTERN.search(text):
                lang = "ur"
            logger.info(f"STT: '{text[:60]}' | whisper_lang={whisper_lang} | final_lang={lang}")
            return text, lang
        logger.error(f"Groq STT error: {response.status_code}")
        return "", "en"
    except Exception as e:
        logger.error(f"STT error: {e}")
        return "", "en"


def text_to_speech(text: str) -> Optional[bytes]:
    """TTS via Groq Orpheus — diana voice."""
    try:
        tts_text = text[:400] if len(text) > 400 else text
        response = requests.post(
            GROQ_TTS_URL,
            headers={"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "canopylabs/orpheus-v1-english",
                "input": tts_text,
                "voice": "diana",
                "response_format": "wav"
            },
            timeout=20
        )
        if response.status_code == 200:
            return response.content
        logger.error(f"TTS error: {response.status_code} {response.text[:100]}")
        return None
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None


# ── Routes ───────────────────────────────────────────────────────────

@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    user_id: str = Form(default="demo_user")
):
    """Voice: audio → STT → language detect → AI → response"""
    try:
        audio_bytes = await audio.read()
        text, lang = transcribe_audio(audio_bytes, audio.filename or "audio.webm")

        if not text:
            msg = "Mujhe kuch sunai nahi diya, dobara bolein." if lang == "ur" else "I didn't catch that, please try again."
            return {"transcript": "", "response": msg, "intent": "unknown", "lang": lang}

        ctx    = context_manager.get(user_id)
        ctx.add_message("user", text)
        result = ai_brain.process_query(text, ctx.get_context_string(), lang=lang)
        ctx.add_message("assistant", result["response"], result["intent"])

        try:
            db.log_call(user_id, text, result["response"], result["intent"])
        except Exception as e:
            logger.error(f"DB log: {e}")

        return {
            "transcript": text,
            "response":   result["response"],
            "intent":     result["intent"],
            "lang":       lang,
        }
    except Exception as e:
        logger.error(f"Transcribe error: {e}")
        return {"transcript": "", "response": "Koi masla aa gaya.", "intent": "unknown", "lang": "en"}


@router.post("/chat")
async def chat(request: Request):
    """Text chat: message → language detect → AI → response"""
    try:
        body    = await request.json()
        message = body.get("message", "").strip()
        user_id = body.get("user_id", "chat_user")

        if not message:
            return {"response": "Please type a message.", "intent": "unknown", "lang": "en"}

        lang   = detect_language(message)
        ctx    = context_manager.get(user_id)
        ctx.add_message("user", message)
        result = ai_brain.process_query(message, ctx.get_context_string(), lang=lang)
        ctx.add_message("assistant", result["response"], result["intent"])

        try:
            db.log_call(user_id, message, result["response"], result["intent"])
        except Exception as e:
            logger.error(f"DB log: {e}")

        return {
            "response": result["response"],
            "intent":   result["intent"],
            "lang":     lang,
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {"response": "Koi masla aa gaya.", "intent": "unknown", "lang": "en"}


@router.post("/speak")
async def speak(request: Request):
    """Text → WAV audio"""
    try:
        body       = await request.json()
        speak_text = body.get("text", "")
        if not speak_text:
            return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")
        audio = text_to_speech(speak_text)
        if audio:
            return StreamingResponse(io.BytesIO(audio), media_type="audio/wav",
                                     headers={"Content-Disposition": "inline; filename=response.wav"})
    except Exception as e:
        logger.error(f"Speak error: {e}")
    return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")
