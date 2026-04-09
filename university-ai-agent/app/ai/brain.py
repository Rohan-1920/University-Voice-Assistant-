import requests
from typing import Dict
from app.core.config import config
from app.core.logger import logger
from app.ai.prompts import SYSTEM_PROMPT, RESPONSE_GENERATION_PROMPT
from app.ai.intent import intent_classifier
from app.db.supabase import db

class AIBrain:
    """Core AI brain for GIFT University admission queries"""

    def __init__(self):
        self.api_key = config.OPENAI_API_KEY
        self.model = config.AI_MODEL

    def process_query(self, query: str, context: str = "") -> Dict[str, str]:
        """Process admission query and generate humanized response"""
        try:
            # Step 1: Classify intent
            intent = intent_classifier.classify(query)

            # Step 2: Fetch relevant data from DB based on intent
            db_context = db.get_relevant_data(intent)

            # Step 3: Build prompt with DB data + conversation context
            prompt = RESPONSE_GENERATION_PROMPT.format(
                db_context=db_context,
                context=context,
                query=query
            )

            # Step 4: Call OpenAI
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
                    "max_tokens": 300
                },
                timeout=30
            )

            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                logger.info(f"Response generated for intent: {intent}")
                return {
                    "intent": intent,
                    "response": ai_response,
                    "status": "success"
                }
            else:
                logger.error(f"OpenAI error: {response.status_code} - {response.text}")
                return {
                    "intent": intent,
                    "response": "Maafi chahta hoon, abhi kuch technical masla aa gaya hai. Kripya thodi der baad call karein ya 055-111-GIFT-00 pe rabta karein.",
                    "status": "error"
                }

        except Exception as e:
            logger.error(f"AI brain error: {e}")
            return {
                "intent": "unknown",
                "response": "Maafi chahta hoon, koi masla aa gaya. Admissions office se rabta karein: 055-111-GIFT-00",
                "status": "error"
            }

ai_brain = AIBrain()
