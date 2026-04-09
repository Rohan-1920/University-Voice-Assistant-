import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseMemory:
    def __init__(self):
        try:
            self.supabase_url = os.getenv("SUPABASE_URL")
            self.supabase_key = os.getenv("SUPABASE_KEY")
            self.client: Optional[Client] = None
            self.fallback_mode = False

            self._initialize_client()
            logger.info("SupabaseMemory initialized")
        except Exception as e:
            logger.error(f"Failed to initialize SupabaseMemory: {e}")
            self.fallback_mode = True
            self.client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _initialize_client(self):
        try:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("Missing Supabase credentials")

            self.client = create_client(self.supabase_url, self.supabase_key)
            self.fallback_mode = False
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.warning(f"Supabase initialization failed: {e}")
            logger.info("Running in fallback mode (local storage)")
            self.fallback_mode = True
            self.client = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def save_conversation(self, student_id: str, user_query: str, ai_response: str) -> bool:
        if self.fallback_mode:
            return self._save_conversation_fallback(student_id, user_query, ai_response)

        try:
            # Get student UUID
            student_uuid = self._get_or_create_student(student_id)
            if not student_uuid:
                logger.warning(f"Could not get student UUID for {student_id}, using fallback")
                return self._save_conversation_fallback(student_id, user_query, ai_response)

            # Insert conversation
            data = {
                "student_id": student_uuid,
                "user_query": user_query,
                "ai_response": ai_response
            }

            response = self.client.table("conversations").insert(data).execute()

            self._log("INFO", f"Conversation saved for student {student_id}", {"student_id": student_id})
            logger.info(f"Conversation saved for student {student_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            self._log("ERROR", f"Failed to save conversation: {e}", {"student_id": student_id})
            return self._save_conversation_fallback(student_id, user_query, ai_response)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def fetch_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        if self.fallback_mode:
            return self._fetch_history_fallback(student_id, limit)

        try:
            # Get student UUID
            student_uuid = self._get_student_uuid(student_id)
            if not student_uuid:
                logger.warning(f"Student UUID not found for {student_id}, using fallback")
                return self._fetch_history_fallback(student_id, limit)

            # Fetch conversations
            response = self.client.table("conversations")\
                .select("*")\
                .eq("student_id", student_uuid)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Fetched {len(response.data) if response.data else 0} conversations for {student_id}")
            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            self._log("ERROR", f"Failed to fetch history: {e}", {"student_id": student_id})
            return self._fetch_history_fallback(student_id, limit)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _get_or_create_student(self, student_id: str) -> Optional[str]:
        try:
            # Check if student exists
            response = self.client.table("students")\
                .select("id")\
                .eq("student_id", student_id)\
                .execute()

            if response.data:
                logger.debug(f"Student {student_id} found")
                return response.data[0]["id"]

            # Create new student
            data = {
                "student_id": student_id,
                "name": f"Student {student_id}",
                "email": f"{student_id}@university.edu"
            }

            response = self.client.table("students").insert(data).execute()
            logger.info(f"Created new student: {student_id}")
            return response.data[0]["id"] if response.data else None

        except Exception as e:
            logger.error(f"Failed to get/create student: {e}")
            return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def _get_student_uuid(self, student_id: str) -> Optional[str]:
        try:
            response = self.client.table("students")\
                .select("id")\
                .eq("student_id", student_id)\
                .execute()

            return response.data[0]["id"] if response.data else None

        except Exception as e:
            logger.error(f"Failed to get student UUID: {e}")
            return None

    def _log(self, level: str, message: str, metadata: Optional[Dict] = None):
        if self.fallback_mode:
            logger.log(getattr(logging, level, logging.INFO), message)
            return

        try:
            student_uuid = None
            if metadata and "student_id" in metadata:
                student_uuid = self._get_student_uuid(metadata["student_id"])

            data = {
                "student_id": student_uuid,
                "log_level": level,
                "message": message,
                "metadata": metadata
            }

            self.client.table("logs").insert(data).execute()

        except Exception as e:
            logger.error(f"Failed to write log to Supabase: {e}")

    def _save_conversation_fallback(self, student_id: str, user_query: str, ai_response: str) -> bool:
        try:
            from memory_system import ConversationMemory
            memory = ConversationMemory(f"fallback_{student_id}.json")
            success = memory.add_conversation(user_query, ai_response)
            if success:
                logger.info(f"Conversation saved to fallback for {student_id}")
            return success
        except Exception as e:
            logger.error(f"Fallback save failed: {e}")
            return False

    def _fetch_history_fallback(self, student_id: str, limit: int = 10) -> List[Dict]:
        try:
            from memory_system import ConversationMemory
            import json

            memory = ConversationMemory(f"fallback_{student_id}.json")
            conversations = memory._load_data()

            # Convert to Supabase format
            result = [
                {
                    "user_query": conv["user_query"],
                    "ai_response": conv["ai_response"],
                    "created_at": conv["timestamp"]
                }
                for conv in conversations[-limit:]
            ]
            logger.info(f"Fetched {len(result)} conversations from fallback for {student_id}")
            return result
        except Exception as e:
            logger.error(f"Fallback fetch failed: {e}")
            return []


# Example usage
if __name__ == "__main__":
    memory = SupabaseMemory()

    # Save conversation
    success = memory.save_conversation(
        student_id="S12345",
        user_query="What is machine learning?",
        ai_response="Machine learning is a subset of AI."
    )
    print(f"Save successful: {success}")

    # Fetch history
    history = memory.fetch_history("S12345", limit=5)
    print(f"Fetched {len(history)} conversations")
    for conv in history:
        print(f"- {conv['user_query'][:50]}...")
