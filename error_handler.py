import logging
from functools import wraps
from typing import Callable, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_execute(fallback_response: Any = "Please try again"):
    """
    Decorator to safely execute functions with comprehensive error handling.

    Args:
        fallback_response: Response to return if all retries fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=False
        )
        def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Executing {func.__name__}")
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return fallback_response
        return wrapper
    return decorator


def safe_execute_async(fallback_response: Any = "Please try again"):
    """
    Async version of safe_execute decorator.

    Args:
        fallback_response: Response to return if all retries fail
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=5),
            reraise=False
        )
        async def wrapper(*args, **kwargs):
            try:
                logger.debug(f"Executing async {func.__name__}")
                result = await func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in async {func.__name__}: {e}", exc_info=True)
                return fallback_response
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handling utility"""

    @staticmethod
    def log_and_return_fallback(error: Exception, context: str, fallback: Any = "Please try again") -> Any:
        """
        Log error and return fallback response.

        Args:
            error: The exception that occurred
            context: Context description for logging
            fallback: Fallback response to return

        Returns:
            The fallback response
        """
        logger.error(f"Error in {context}: {error}", exc_info=True)
        return fallback

    @staticmethod
    def safe_call(func: Callable, *args, fallback: Any = None, **kwargs) -> Any:
        """
        Safely call a function with error handling.

        Args:
            func: Function to call
            *args: Positional arguments
            fallback: Fallback value if function fails
            **kwargs: Keyword arguments

        Returns:
            Function result or fallback value
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error calling {func.__name__}: {e}", exc_info=True)
            return fallback

    @staticmethod
    async def safe_call_async(func: Callable, *args, fallback: Any = None, **kwargs) -> Any:
        """
        Safely call an async function with error handling.

        Args:
            func: Async function to call
            *args: Positional arguments
            fallback: Fallback value if function fails
            **kwargs: Keyword arguments

        Returns:
            Function result or fallback value
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error calling async {func.__name__}: {e}", exc_info=True)
            return fallback


# Example usage
if __name__ == "__main__":
    @safe_execute(fallback_response="Fallback response")
    def example_function(x: int) -> int:
        if x < 0:
            raise ValueError("Negative value not allowed")
        return x * 2

    # This will succeed
    print(example_function(5))  # Output: 10

    # This will fail and return fallback after 3 retries
    print(example_function(-5))  # Output: Fallback response
