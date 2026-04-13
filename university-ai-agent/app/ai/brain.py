import requests
import time
from typing import Dict, Optional
from app.core.config import config
from app.core.logger import logger
from app.ai.prompts import SYSTEM_PROMPT, RESPONSE_GENERATION_PROMPT
from app.ai.intent import intent_classifier
from app.db.supabase import db

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Retry config
MAX_RETRIES = 3
RETRY_DELAY = 1      # base seconds
RETRY_BACKOFF = 2    # multiplier per attempt  (1s → 2s → 4s)

# Status codes worth retrying (transient errors)
RETRYABLE_CODES = {429, 500, 502, 503, 504}


class AIBrain:
    """Core AI brain for GIFT University admission queries — powered by Groq"""

    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        self.model = config.AI_MODEL

    def _call_groq(self, messages: list, max_tokens: int = 300) -> Optional[str]:
        """
        Call Groq API with full retry logic:
        - 429 rate limit  → exponential backoff + retry
        - 5xx server error → retry
        - network timeout  → retry
        - 4xx client error → no retry (bad request, wrong key, etc.)
        """
        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": max_tokens
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()

                if response.status_code in RETRYABLE_CODES:
                    wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                    logger.warning(
                        f"Groq returned {response.status_code} "
                        f"(attempt {attempt}/{MAX_RETRIES}) — retrying in {wait}s"
                    )
                    last_error = f"HTTP {response.status_code}"
                    time.sleep(wait)
                    continue

                # Non-retryable 4xx (bad key, bad request, etc.)
                logger.error(f"Groq non-retryable error {response.status_code}: {response.text[:200]}")
                return None

            except requests.exceptions.Timeout:
                wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                logger.warning(f"Groq timeout (attempt {attempt}/{MAX_RETRIES}) — retrying in {wait}s")
                last_error = "Timeout"
                time.sleep(wait)

            except requests.exceptions.ConnectionError as e:
                wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                logger.warning(f"Groq connection error (attempt {attempt}/{MAX_RETRIES}) — retrying in {wait}s: {e}")
                last_error = "ConnectionError"
                time.sleep(wait)

            except Exception as e:
                logger.error(f"Unexpected Groq error on attempt {attempt}: {e}")
                last_error = str(e)
                break

        logger.error(f"Groq failed after {MAX_RETRIES} attempts. Last error: {last_error}")
        return None

    def process_query(self, query: str, context: str = "") -> Dict[str, str]:
        """Process admission query — fast parallel intent + response"""
        try:
            # Classify intent first (fast, small model call)
            intent = intent_classifier.classify(query)

            # Fetch DB data based on intent
            db_context = db.get_relevant_data(intent)

            prompt = RESPONSE_GENERATION_PROMPT.format(
                db_context=db_context,
                context=context,
                query=query
            )

            ai_response = self._call_groq([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ], max_tokens=120)  # short = fast TTS

            if ai_response:
                logger.info(f"Response generated for intent: {intent}")
                return {"intent": intent, "response": ai_response, "status": "success"}

            return {
                "intent": intent,
                "response": "Maafi chahta hoon, abhi kuch masla aa gaya. 055-111-GIFT-00 pe rabta karein.",
                "status": "error"
            }

        except Exception as e:
            logger.error(f"AI brain error: {e}")
            return {
                "intent": "unknown",
                "response": "Koi masla aa gaya. 055-111-GIFT-00 pe rabta karein.",
                "status": "error"
            }


ai_brain = AIBrain()
