import psycopg2
import psycopg2.extras
from typing import Dict, List, Any
from app.core.config import config
from app.core.logger import logger
from app.db.models import CallLog, UserSession


class SupabaseDB:
    """Database interface using direct PostgreSQL connection"""

    def __init__(self):
        self.conn = None

    def connect(self):
        """Initialize PostgreSQL connection"""
        if not config.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in .env file")
        self.conn = psycopg2.connect(config.DATABASE_URL)
        self.conn.autocommit = True
        logger.info("PostgreSQL connected")

    def _get_conn(self):
        if not self.conn or self.conn.closed:
            self.connect()
        return self.conn

    def _execute(self, query: str, params=None) -> List[Dict]:
        """Execute query and return results as list of dicts"""
        try:
            with self._get_conn().cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if cur.description:
                    return [dict(row) for row in cur.fetchall()]
                return []
        except Exception as e:
            logger.error(f"Query error: {e}")
            self.conn = None  # reset connection on error
            return []

    # ── Admission Data Queries ──────────────────────────────────────

    def get_programs(self, category: str = None) -> List[Dict]:
        if category:
            return self._execute("SELECT * FROM programs WHERE category=%s ORDER BY degree_type", (category,))
        return self._execute("SELECT * FROM programs ORDER BY degree_type")

    def get_fee_structure(self, category: str = None) -> List[Dict]:
        if category:
            return self._execute("SELECT * FROM fee_structure WHERE program_category=%s", (category,))
        return self._execute("SELECT * FROM fee_structure")

    def get_admission_requirements(self, category: str = None) -> List[Dict]:
        if category:
            return self._execute("SELECT * FROM admission_requirements WHERE program_category=%s", (category,))
        return self._execute("SELECT * FROM admission_requirements")

    def get_active_admission_dates(self) -> List[Dict]:
        return self._execute("SELECT * FROM admission_dates WHERE is_active=TRUE")

    def get_faqs(self, category: str = None) -> List[Dict]:
        if category:
            return self._execute("SELECT * FROM faqs WHERE category=%s", (category,))
        return self._execute("SELECT * FROM faqs")

    def get_contact_info(self) -> List[Dict]:
        return self._execute("SELECT * FROM contact_info")

    def get_relevant_data(self, intent: str) -> str:
        """Fetch relevant DB data based on intent"""
        try:
            data_parts = []

            if intent == "programs":
                programs = self.get_programs()
                if programs:
                    names = [f"{p['degree_type']} {p['name']}" for p in programs]
                    data_parts.append("Available Programs:\n" + "\n".join(names))

            elif intent == "fee":
                fees = self.get_fee_structure()
                for f in fees:
                    data_parts.append(
                        f"{f['program_category'].title()} programs: "
                        f"Rs. {f['fee_per_semester']:,}/semester, "
                        f"Rs. {f['annual_fee']:,}/year. "
                        f"Admission fee: Rs. {f['admission_fee']:,}"
                    )

            elif intent in ("eligibility", "documents", "admission_process"):
                reqs = self.get_admission_requirements()
                for r in reqs:
                    docs = ", ".join(r.get("required_documents") or [])
                    data_parts.append(
                        f"{r['program_category'].title()}: "
                        f"Min {r['min_percentage']}% marks. "
                        f"Documents: {docs}"
                    )

            elif intent == "dates":
                dates = self.get_active_admission_dates()
                for d in dates:
                    data_parts.append(
                        f"{d['semester']} {d['year']}: "
                        f"Admissions {d['admission_start']} to {d['admission_end']}. "
                        f"Classes start {d['classes_start']}"
                    )

            elif intent == "contact":
                contacts = self.get_contact_info()
                for c in contacts:
                    data_parts.append(f"{c['department']}: {c['phone']} | {c['email']} | {c['timings']}")

            elif intent in ("scholarship", "hostel", "transport"):
                faqs = self.get_faqs(intent)
                for f in faqs:
                    data_parts.append(f"Q: {f['question']}\nA: {f['answer']}")

            else:
                faqs = self.get_faqs()
                for f in faqs[:5]:
                    data_parts.append(f"Q: {f['question']}\nA: {f['answer']}")

            return "\n\n".join(data_parts) if data_parts else "No specific data found."

        except Exception as e:
            logger.error(f"Failed to get relevant data: {e}")
            return ""

    # ── Logging ─────────────────────────────────────────────────────

    def log_call(self, user_id: str, query: str, response: str, intent: str) -> bool:
        try:
            data = CallLog.create(user_id, query, response, intent)
            self._execute(
                "INSERT INTO call_logs (user_id, query, response, intent, timestamp, created_at) VALUES (%s,%s,%s,%s,%s,%s)",
                (data["user_id"], data["query"], data["response"], data["intent"], data["timestamp"], data["created_at"])
            )
            logger.info(f"Logged call for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to log call: {e}")
            return False

    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        return self._execute(
            "SELECT * FROM call_logs WHERE user_id=%s ORDER BY created_at DESC LIMIT %s",
            (user_id, limit)
        )

    def save_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        try:
            import json
            data = UserSession.create(user_id, session_data)
            self._execute(
                "INSERT INTO user_sessions (user_id, session_data, started_at, last_activity) VALUES (%s,%s,%s,%s)",
                (data["user_id"], json.dumps(data["session_data"]), data["started_at"], data["last_activity"])
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False


db = SupabaseDB()
