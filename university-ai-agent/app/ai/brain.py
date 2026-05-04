"""
AI Brain
=========
Fast query processing:
  1. Intent classify (Groq, fast)
  2. RAG retrieve (preloaded model, ~50ms)
  3. Groq generate (120 tokens max, ~1s)
Total target: < 2 seconds
"""

import time
import logging
from typing import Dict, Optional

import requests

from app.core.config import config
from app.ai.intent import intent_classifier
from app.ai.language import detect_reply_language
from app.ai.prompts import SYSTEM_PROMPT, RESPONSE_GENERATION_PROMPT
from app.db.supabase import db

logger = logging.getLogger(__name__)

GROQ_API_URL    = "https://api.groq.com/openai/v1/chat/completions"
MAX_RETRIES     = 2          # reduced for speed
RETRY_DELAY     = 0.5
RETRY_BACKOFF   = 2
RETRYABLE_CODES = {429, 500, 502, 503, 504}


class AIBrain:
    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        self.model   = config.AI_MODEL

    def _call_groq(self, messages: list, max_tokens: int = 120) -> Optional[str]:
        """Call Groq with retry. max_tokens=120 keeps responses short and fast."""
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                r = requests.post(
                    GROQ_API_URL,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"model": self.model, "messages": messages, "temperature": 0.1, "max_tokens": max_tokens},
                    timeout=20,
                )
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"].strip()
                if r.status_code in RETRYABLE_CODES:
                    wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                    logger.warning(f"Groq {r.status_code} — retry {attempt} in {wait}s")
                    last_error = f"HTTP {r.status_code}"
                    time.sleep(wait)
                    continue
                logger.error(f"Groq {r.status_code}: {r.text[:150]}")
                return None
            except requests.exceptions.Timeout:
                logger.warning(f"Groq timeout attempt {attempt}")
                last_error = "Timeout"
                time.sleep(RETRY_DELAY)
            except Exception as e:
                logger.error(f"Groq error: {e}")
                last_error = str(e)
                break

        logger.error(f"Groq failed after {MAX_RETRIES} attempts: {last_error}")
        return None

    def process_query(self, query: str, context: str = "", lang: Optional[str] = None) -> Dict[str, str]:
        """
        Process query — target < 2s total.
        lang: None = auto (mirror student's language); 'ur' / 'en' = force reply language
        """
        t0 = time.time()

        effective_lang = lang if lang is not None else detect_reply_language(query)

        # Step 1: Intent
        intent = intent_classifier.classify(query)

        # Step 2: Context — RAG if ready, else DB
        try:
            from rag.retriever import retrieve, format_context, is_ready
            if is_ready():
                chunks    = retrieve(query, top_k=3)
                knowledge = format_context(chunks)
            else:
                knowledge = db.get_relevant_data(intent)
        except Exception:
            knowledge = db.get_relevant_data(intent)

        # Step 3: Language instruction (must match effective_lang — default used to wrongly force English)
        lang_instruction = (
            "IMPORTANT: The student spoke in URDU. Reply ONLY in Urdu script or Roman Urdu — never English or Hindi/Devanagari. "
            "If Additional data / database context below is in English, translate those facts into Urdu in your answer."
            if effective_lang == "ur"
            else "IMPORTANT: The student spoke in ENGLISH. You MUST reply in English only."
        )

        # Step 4: Generate
        prompt = RESPONSE_GENERATION_PROMPT.format(
            db_context=knowledge,
            context=context,
            query=query,
        ) + f"\n\n{lang_instruction}"

        ai_response = self._call_groq([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ])

        elapsed = round(time.time() - t0, 2)
        logger.info(f"Query processed in {elapsed}s | intent={intent} | lang={effective_lang}")

        if ai_response:
            return {"intent": intent, "response": ai_response, "status": "success"}

        fallback = (
            "Maafi chahta hoon, abhi kuch masla aa gaya. 055-111-GIFT-00 pe rabta karein."
            if effective_lang == "ur"
            else "Sorry, something went wrong. Please call 055-111-GIFT-00."
        )
        return {"intent": intent, "response": fallback, "status": "error"}


ai_brain = AIBrain()
