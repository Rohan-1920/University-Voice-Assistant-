import requests
from typing import Dict, List
from app.core.config import config
from app.core.logger import logger
from app.ai.prompts import SYSTEM_PROMPT, RESPONSE_GENERATION_PROMPT
from app.ai.intent import intent_classifier

class AIBrain:
    """Core AI brain for processing queries"""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.AI_MODEL

    def process_query(self, query: str, context: str = "") -> Dict[str, str]:
        """Process user query and generate response"""
        try:
            intent = intent_classifier.classify(query)

            prompt = RESPONSE_GENERATION_PROMPT.format(
                context=context,
                query=query
            )

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200
                }
            )

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                logger.info(f"Generated response for intent: {intent}")

                return {
                    "intent": intent,
                    "response": ai_response,
                    "status": "success"
                }
            else:
                logger.error(f"AI processing failed: {response.status_code}")
                return {
                    "intent": intent,
                    "response": "I'm having trouble processing that right now.",
                    "status": "error"
                }

        except Exception as e:
            logger.error(f"AI brain error: {e}")
            return {
                "intent": "unknown",
                "response": "Sorry, I encountered an error.",
                "status": "error"
            }

ai_brain = AIBrain()
