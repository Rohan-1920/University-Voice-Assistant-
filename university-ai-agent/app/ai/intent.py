import requests
import time
from typing import Optional
from app.core.config import config
from app.core.logger import logger
from app.ai.prompts import INTENT_CLASSIFICATION_PROMPT

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_RETRIES = 3
RETRY_DELAY = 1
RETRY_BACKOFF = 2
RETRYABLE_CODES = {429, 500, 502, 503, 504}

# Valid intent categories — fallback if Groq returns garbage
VALID_INTENTS = {
    "admission_process", "programs", "fee", "eligibility",
    "documents", "dates", "scholarship", "hostel",
    "transport", "contact", "general"
}


class IntentClassifier:
    """Classify user intents using Groq — with retry logic"""

    def __init__(self):
        self.api_key = config.GROQ_API_KEY
        self.model = config.AI_MODEL

    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq with retry on transient errors"""
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
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                        "max_tokens": 50
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()

                if response.status_code in RETRYABLE_CODES:
                    wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                    logger.warning(
                        f"Intent classifier got {response.status_code} "
                        f"(attempt {attempt}/{MAX_RETRIES}) — retrying in {wait}s"
                    )
                    last_error = f"HTTP {response.status_code}"
                    time.sleep(wait)
                    continue

                logger.error(f"Intent classifier non-retryable error {response.status_code}")
                return None

            except requests.exceptions.Timeout:
                wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                logger.warning(f"Intent classifier timeout (attempt {attempt}/{MAX_RETRIES}) — retrying in {wait}s")
                last_error = "Timeout"
                time.sleep(wait)

            except requests.exceptions.ConnectionError as e:
                wait = RETRY_DELAY * (RETRY_BACKOFF ** (attempt - 1))
                logger.warning(f"Intent classifier connection error (attempt {attempt}/{MAX_RETRIES}): {e}")
                last_error = "ConnectionError"
                time.sleep(wait)

            except Exception as e:
                logger.error(f"Unexpected intent classifier error: {e}")
                last_error = str(e)
                break

        logger.error(f"Intent classification failed after {MAX_RETRIES} attempts. Last: {last_error}")
        return None

    def classify(self, query: str) -> str:
        """Classify user intent — returns 'general' if all retries fail"""
        try:
            prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
            result = self._call_groq(prompt)

            if result:
                # Sanitize — only accept known intents
                intent = result.lower().strip()
                if intent in VALID_INTENTS:
                    logger.info(f"Classified intent: {intent}")
                    return intent
                else:
                    logger.warning(f"Unknown intent returned: '{intent}' — defaulting to 'general'")
                    return "general"

            return "general"  # safe fallback

        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return "general"


intent_classifier = IntentClassifier()
