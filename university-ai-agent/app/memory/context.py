from typing import List, Dict
from datetime import datetime
from app.core.logger import logger

class ConversationContext:
    """Manage conversation context and history"""

    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []
        self.max_history = max_history
        self.session_start = datetime.utcnow()

    def add_message(self, role: str, content: str, intent: str = ""):
        """Add message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.history.append(message)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        logger.info(f"Added {role} message to context")

    def get_context_string(self) -> str:
        """Get formatted context string"""
        if not self.history:
            return "No previous context."

        context_parts = []
        for msg in self.history[-5:]:
            context_parts.append(f"{msg['role']}: {msg['content']}")

        return "\n".join(context_parts)

    def clear(self):
        """Clear conversation history"""
        self.history.clear()
        logger.info("Cleared conversation context")

    def get_last_intent(self) -> str:
        """Get the last detected intent"""
        for msg in reversed(self.history):
            if msg.get("intent"):
                return msg["intent"]
        return "unknown"

context_manager = ConversationContext()
