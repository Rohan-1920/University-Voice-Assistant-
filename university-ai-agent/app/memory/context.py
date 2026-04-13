from typing import List, Dict
from datetime import datetime
from app.core.logger import logger


class ConversationContext:
    """Conversation context for a single user session"""

    def __init__(self, user_id: str, max_history: int = 10):
        self.user_id = user_id
        self.history: List[Dict] = []
        self.max_history = max_history
        self.session_start = datetime.utcnow()

    def add_message(self, role: str, content: str, intent: str = ""):
        self.history.append({
            "role": role,
            "content": content,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat()
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context_string(self) -> str:
        if not self.history:
            return "No previous context."
        return "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in self.history[-5:]
        )

    def get_last_intent(self) -> str:
        for msg in reversed(self.history):
            if msg.get("intent"):
                return msg["intent"]
        return "unknown"

    def clear(self):
        self.history.clear()
        logger.info(f"Cleared context for user: {self.user_id}")


class ContextManager:
    """
    Per-user context store.
    Each user_id gets its own isolated ConversationContext.
    No more shared global state — 2 students calling simultaneously
    will never mix each other's history.
    """

    def __init__(self):
        self._sessions: Dict[str, ConversationContext] = {}

    def get(self, user_id: str) -> ConversationContext:
        """Get or create context for a user"""
        if user_id not in self._sessions:
            self._sessions[user_id] = ConversationContext(user_id)
            logger.info(f"New context created for user: {user_id}")
        return self._sessions[user_id]

    def clear(self, user_id: str):
        """Clear and remove context for a user after call ends"""
        if user_id in self._sessions:
            self._sessions[user_id].clear()
            del self._sessions[user_id]
            logger.info(f"Session removed for user: {user_id}")

    def active_sessions(self) -> int:
        return len(self._sessions)


# Single manager instance — but each user gets isolated context
context_manager = ContextManager()
