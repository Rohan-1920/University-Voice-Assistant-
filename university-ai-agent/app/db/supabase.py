from supabase import create_client, Client
from typing import Dict, List, Any
from app.core.config import config
from app.core.logger import logger
from app.db.models import CallLog, UserSession

class SupabaseDB:
    """Supabase database interface"""

    def __init__(self):
        self.client: Client = None

    def connect(self):
        """Initialize Supabase connection"""
        if not config.SUPABASE_URL or config.SUPABASE_URL == "your_supabase_url_here":
            raise ValueError("SUPABASE_URL is not set in .env file")
        if not config.SUPABASE_KEY or config.SUPABASE_KEY == "your_supabase_key_here":
            raise ValueError("SUPABASE_KEY is not set in .env file")
        self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("Supabase client initialized")

    def _get_client(self) -> Client:
        """Get or create client"""
        if not self.client:
            self.connect()
        return self.client

    def log_call(self, user_id: str, query: str, response: str, intent: str) -> bool:
        """Log a call interaction"""
        try:
            data = CallLog.create(user_id, query, response, intent)
            result = self._get_client().table("call_logs").insert(data).execute()
            logger.info(f"Logged call for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to log call: {e}")
            return False

    def save_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Save user session"""
        try:
            data = UserSession.create(user_id, session_data)
            result = self._get_client().table("user_sessions").insert(data).execute()
            logger.info(f"Saved session for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get user's call history"""
        try:
            result = self._get_client().table("call_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            logger.info(f"Retrieved history for user: {user_id}")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []

    def get_student_info(self, student_id: str) -> Dict[str, Any]:
        """Get student information"""
        try:
            result = self._get_client().table("students")\
                .select("*")\
                .eq("student_id", student_id)\
                .single()\
                .execute()

            logger.info(f"Retrieved info for student: {student_id}")
            return result.data
        except Exception as e:
            logger.error(f"Failed to get student info: {e}")
            return {}

db = SupabaseDB()
