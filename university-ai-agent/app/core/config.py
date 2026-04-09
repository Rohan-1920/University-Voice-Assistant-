import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def _build_db_url() -> str:
    """Build properly encoded DATABASE_URL from components"""
    raw = os.getenv("DATABASE_URL", "")
    if not raw:
        return ""
    # If URL has special chars in password, encode them
    try:
        # Extract password between : and @ and encode it
        prefix = "postgresql://postgres:"
        suffix_start = raw.index("@db.")
        password = raw[len(prefix):suffix_start]
        host_part = raw[suffix_start:]
        encoded_password = quote_plus(password)
        return f"{prefix}{encoded_password}{host_part}"
    except Exception:
        return raw

class Config:
    """Application configuration"""

    # Database
    DATABASE_URL = _build_db_url()

    # AI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_MODEL = os.getenv("AI_MODEL", "gpt-3.5-turbo")

    # Voice
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()
