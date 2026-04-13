import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def _build_db_url() -> str:
    """Build properly encoded DATABASE_URL — handles special chars in password"""
    raw = os.getenv("DATABASE_URL", "")
    if not raw:
        return ""
    try:
        # Format: postgresql://user:password@host:port/db
        # Find user:password part
        after_scheme = raw[len("postgresql://"):]
        at_pos = after_scheme.rfind("@")  # last @ = host separator
        user_pass = after_scheme[:at_pos]
        host_part = after_scheme[at_pos:]  # @host:port/db

        colon_pos = user_pass.index(":")
        user = user_pass[:colon_pos]
        password = user_pass[colon_pos+1:]

        encoded_password = quote_plus(password)
        return f"postgresql://{user}:{encoded_password}{host_part}"
    except Exception:
        return raw

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = _build_db_url()

    # AI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # legacy, not used
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    AI_MODEL = os.getenv("AI_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

    # Voice
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()
