import requests
from typing import Dict
from app.core.config import config
from app.core.logger import logger
from app.ai.prompts import INTENT_CLASSIFICATION_PROMPT

class IntentClassifier:
    """Classify user intents"""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.AI_MODEL

    def classify(self, query: str) -> str:
        """Classify user intent"""
        try:
            prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 50
                }
            )

            if response.status_code == 200:
                intent = response.json()["choices"][0]["message"]["content"].strip()
                logger.info(f"Classified intent: {intent}")
                return intent
            else:
                logger.error(f"Intent classification failed: {response.status_code}")
                return "unknown"

        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return "unknown"

intent_classifier = IntentClassifier()
