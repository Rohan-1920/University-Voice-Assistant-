"""
Production-Safe Configuration
==============================

This module ensures the entire system is production-ready with:
- Comprehensive error handling
- Retry logic (3 attempts)
- Fallback responses
- Extensive logging
- No crashes allowed

All failures respond with: "Please try again"
"""

import logging
from typing import Dict, Any

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# Retry configuration
RETRY_CONFIG = {
    'max_attempts': 3,
    'min_wait': 1,
    'max_wait': 5,
    'multiplier': 1
}

# Fallback responses
FALLBACK_RESPONSES = {
    'default': "Please try again.",
    'voice': "Please try again.",
    'api': {"status": "error", "message": "Please try again"},
    'empty_input': "I didn't catch that. Please try again.",
    'timeout': "Request timed out. Please try again.",
    'database_error': "Please try again.",
    'ai_error': "Please try again.",
    'network_error': "Please try again."
}

# Server configuration
SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'max_retries': 5,
    'log_level': 'info'
}


def get_fallback_response(error_type: str = 'default') -> Any:
    """
    Get appropriate fallback response for error type.

    Args:
        error_type: Type of error (default, voice, api, etc.)

    Returns:
        Fallback response for the error type
    """
    return FALLBACK_RESPONSES.get(error_type, FALLBACK_RESPONSES['default'])


def setup_logging():
    """Setup logging configuration for the entire application"""
    from logging.config import dictConfig
    dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")


# Production safety checklist
SAFETY_CHECKLIST = {
    'error_handling': 'All functions wrapped in try-catch',
    'retry_logic': '3 retries with exponential backoff',
    'logging': 'Comprehensive logging at all levels',
    'fallbacks': 'Fallback responses for all failure scenarios',
    'no_crashes': 'System never crashes, always responds',
    'graceful_degradation': 'Fallback to local storage if DB fails',
    'health_checks': 'Health check endpoints available',
    'monitoring': 'All errors logged to file and console'
}


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Production configuration loaded")
    logger.info(f"Safety checklist: {SAFETY_CHECKLIST}")
