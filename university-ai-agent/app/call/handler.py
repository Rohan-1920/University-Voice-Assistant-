from typing import Dict
from app.core.logger import logger
from app.ai.brain import ai_brain
from app.voice.stt import stt
from app.voice.tts import tts
from app.memory.context import context_manager
from app.db.supabase import db

class CallHandler:
    """Handle voice call interactions"""

    def __init__(self):
        self.active = False

    def start_call(self, user_id: str = "guest"):
        """Start a voice call session"""
        logger.info(f"Starting call for user: {user_id}")
        self.active = True

        tts.speak("Hello! I'm your university AI assistant. How can I help you today?")

        while self.active:
            user_input = stt.listen()

            if not user_input:
                continue

            if "goodbye" in user_input.lower() or "exit" in user_input.lower():
                tts.speak("Goodbye! Have a great day!")
                self.stop_call()
                break

            context_manager.add_message("user", user_input)

            context = context_manager.get_context_string()
            result = ai_brain.process_query(user_input, context)

            response = result["response"]
            intent = result["intent"]

            context_manager.add_message("assistant", response, intent)

            db.log_call(user_id, user_input, response, intent)

            tts.speak(response)

    def stop_call(self):
        """Stop the call session"""
        logger.info("Stopping call")
        self.active = False
        context_manager.clear()

    def handle_text_query(self, user_id: str, query: str) -> Dict[str, str]:
        """Handle text-based query (for API)"""
        logger.info(f"Handling text query from user: {user_id}")

        context = context_manager.get_context_string()
        result = ai_brain.process_query(query, context)

        context_manager.add_message("user", query)
        context_manager.add_message("assistant", result["response"], result["intent"])

        db.log_call(user_id, query, result["response"], result["intent"])

        return result

call_handler = CallHandler()
