from typing import Dict, Any
from datetime import datetime

class CallLog:
    """Call log data model"""

    @staticmethod
    def create(user_id: str, query: str, response: str, intent: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "query": query,
            "response": response,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }

class UserSession:
    """User session data model"""

    @staticmethod
    def create(user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "session_data": session_data,
            "started_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

class StudentInfo:
    """Student information data model"""

    @staticmethod
    def create(student_id: str, name: str, email: str, courses: list) -> Dict[str, Any]:
        return {
            "student_id": student_id,
            "name": name,
            "email": email,
            "courses": courses,
            "created_at": datetime.utcnow().isoformat()
        }
