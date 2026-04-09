import json
from typing import Any, Dict
from datetime import datetime

def format_timestamp() -> str:
    """Return current timestamp in ISO format"""
    return datetime.utcnow().isoformat()

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return text.strip().lower()

def parse_json_safe(data: str) -> Dict[str, Any]:
    """Safely parse JSON string"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    return text[:max_length] + "..." if len(text) > max_length else text
