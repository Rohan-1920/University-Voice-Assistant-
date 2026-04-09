import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConversationMemory:
    def __init__(self, memory_file: str = "conversation_memory.json", max_conversations: int = 3):
        try:
            self.memory_file = Path(memory_file)
            self.max_conversations = max_conversations

            # Validate path before creating file
            if not self.memory_file.parent.exists():
                logger.warning(f"Parent directory does not exist: {self.memory_file.parent}")
                # Try to create parent directory
                try:
                    self.memory_file.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    logger.error(f"Cannot create parent directory: {e}")
                    raise ValueError(f"Invalid memory file path: {memory_file}")

            self._ensure_file_exists()
            logger.info(f"ConversationMemory initialized: {memory_file}")
        except Exception as e:
            logger.error(f"Failed to initialize ConversationMemory: {e}")
            raise

    def _ensure_file_exists(self):
        try:
            if not self.memory_file.exists():
                self._save_data([])
                logger.info(f"Created new memory file: {self.memory_file}")
        except Exception as e:
            logger.error(f"Failed to create memory file: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _load_data(self) -> List[Dict]:
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Loaded {len(data)} conversations from {self.memory_file}")
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Failed to load data, returning empty list: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _save_data(self, data: List[Dict]):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                logger.debug(f"Saved {len(data)} conversations to {self.memory_file}")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            raise

    def add_conversation(self, user_query: str, ai_response: str) -> bool:
        try:
            conversations = self._load_data()

            new_conversation = {
                "timestamp": datetime.now().isoformat(),
                "user_query": user_query,
                "ai_response": ai_response
            }

            conversations.append(new_conversation)

            # Keep only last N conversations
            if len(conversations) > self.max_conversations:
                conversations = conversations[-self.max_conversations:]

            self._save_data(conversations)
            logger.info(f"Added conversation: {user_query[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")
            return False

    def get_context(self) -> str:
        try:
            conversations = self._load_data()

            if not conversations:
                return "No previous conversations."

            context_parts = []
            for i, conv in enumerate(conversations, 1):
                context_parts.append(f"Conversation {i} ({conv['timestamp']}):")
                context_parts.append(f"User: {conv['user_query']}")
                context_parts.append(f"AI: {conv['ai_response']}")
                context_parts.append("")

            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return "No previous conversations."

    def clear(self) -> bool:
        try:
            self._save_data([])
            logger.info("Memory cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False


# Example usage
if __name__ == "__main__":
    memory = ConversationMemory()

    # Add conversations
    memory.add_conversation("What is Python?", "Python is a programming language.")
    memory.add_conversation("How do I use lists?", "Lists are created with square brackets.")
    memory.add_conversation("What about dictionaries?", "Dictionaries use curly braces with key-value pairs.")
    memory.add_conversation("Explain loops", "Loops iterate over sequences using for or while.")

    # Get context (only last 3 will be stored)
    print(memory.get_context())
