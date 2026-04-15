from typing import Dict
from app.core.logger import logger
from app.ai.brain import ai_brain
from app.memory.context import context_manager
from app.db.supabase import db


class CallHandler:
    """Handle voice call interactions"""

    def start_call(self, user_id: str = "guest"):
        """Start a voice call session — loads STT/TTS only when needed"""
        # Lazy import so server starts fast without downloading Whisper model
        from app.voice.stt import stt
        from app.voice.tts import tts

        logger.info(f"Starting call for user: {user_id}")
        ctx = context_manager.get(user_id)

        tts.speak(
            "Assalam o Alaikum! Gift University mein khush aamdeed. "
            "Main aapka admission assistant hoon. Aap mujhse admission, "
            "programs, fees, ya kisi bhi cheez ke baare mein pooch sakte hain. "
            "Batayein, main aapki kya madad kar sakta hoon?"
        )

        active = True
        while active:
            user_input = stt.listen()

            if not user_input:
                continue

            farewell_words = ["goodbye", "exit", "khuda hafiz", "shukriya", "allah hafiz"]
            if any(word in user_input.lower() for word in farewell_words):
                tts.speak("Shukriya GIFT University ko call karne ka. Allah Hafiz, aur aapka future bright ho!")
                context_manager.clear(user_id)
                active = False
                break

            ctx.add_message("user", user_input)
            result = ai_brain.process_query(user_input, ctx.get_context_string())

            response = result["response"]
            intent = result["intent"]

            ctx.add_message("assistant", response, intent)
            db.log_call(user_id, user_input, response, intent)
            tts.speak(response)

    def handle_text_query(self, user_id: str, query: str) -> Dict[str, str]:
        """Handle text-based query (for API) — each user has isolated context"""
        logger.info(f"Handling text query from user: {user_id}")

        ctx = context_manager.get(user_id)
        result = ai_brain.process_query(query, ctx.get_context_string())

        ctx.add_message("user", query)
        ctx.add_message("assistant", result["response"], result["intent"])
        db.log_call(user_id, query, result["response"], result["intent"])

        return result


call_handler = CallHandler()
