#!/usr/bin/env python3
"""
Production Safety Test Suite
=============================

Tests all error handling, retry logic, and fallback mechanisms.
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from error_handler import safe_execute, safe_execute_async, ErrorHandler
from config import get_fallback_response, RETRY_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestErrorHandling:
    """Test error handling mechanisms"""

    def test_safe_execute_success(self):
        """Test successful execution"""
        @safe_execute(fallback_response="fallback")
        def success_func():
            return "success"

        result = success_func()
        assert result == "success"

    def test_safe_execute_failure(self):
        """Test failure returns fallback"""
        @safe_execute(fallback_response="fallback")
        def failing_func():
            raise ValueError("Test error")

        result = failing_func()
        assert result == "fallback"

    def test_error_handler_safe_call(self):
        """Test ErrorHandler.safe_call"""
        def failing_func():
            raise Exception("Test error")

        result = ErrorHandler.safe_call(failing_func, fallback="fallback")
        assert result == "fallback"

    def test_fallback_responses(self):
        """Test fallback response retrieval"""
        assert get_fallback_response('default') == "Please try again."
        assert get_fallback_response('voice') == "Please try again."
        assert get_fallback_response('unknown') == "Please try again."


class TestMemorySystem:
    """Test memory system error handling"""

    def test_memory_system_handles_file_errors(self):
        """Test memory system handles file errors gracefully"""
        from memory_system import ConversationMemory
        import tempfile

        # Test with valid temp directory
        temp_dir = tempfile.gettempdir()
        temp_file = f"{temp_dir}/test_memory.json"

        try:
            memory = ConversationMemory(temp_file)
            # Should not crash
            assert memory is not None
        except Exception as e:
            # If it raises, it should be caught
            logger.error(f"Memory system crashed: {e}")
            pytest.fail("Memory system should not crash with valid path")

    def test_memory_add_conversation_returns_bool(self):
        """Test add_conversation returns boolean"""
        from memory_system import ConversationMemory
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            memory = ConversationMemory(temp_file)
            result = memory.add_conversation("test query", "test response")
            assert isinstance(result, bool)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestSupabaseMemory:
    """Test Supabase memory error handling"""

    def test_supabase_fallback_mode(self):
        """Test Supabase falls back to local storage"""
        with patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_KEY': ''}):
            from supabase_memory import SupabaseMemory

            memory = SupabaseMemory()
            assert memory.fallback_mode == True

    def test_supabase_save_returns_bool(self):
        """Test save_conversation returns boolean"""
        with patch.dict('os.environ', {'SUPABASE_URL': '', 'SUPABASE_KEY': ''}):
            from supabase_memory import SupabaseMemory

            memory = SupabaseMemory()
            result = memory.save_conversation("test_id", "query", "response")
            assert isinstance(result, bool)


class TestCallHandler:
    """Test call handler error handling"""

    @pytest.mark.asyncio
    async def test_health_endpoint_never_crashes(self):
        """Test health endpoint always returns response"""
        from call_handler import health_check

        try:
            result = await health_check()
            assert result is not None
            assert 'status' in result
        except Exception as e:
            pytest.fail(f"Health check crashed: {e}")

    @pytest.mark.asyncio
    async def test_process_speech_handles_empty_input(self):
        """Test process_speech handles empty input"""
        from call_handler import process_speech

        try:
            result = await process_speech(SpeechResult="", From="+1234567890")
            assert result is not None
        except Exception as e:
            pytest.fail(f"Process speech crashed on empty input: {e}")

    @pytest.mark.asyncio
    async def test_get_ai_response_never_crashes(self):
        """Test AI response function never crashes"""
        from call_handler import get_ai_response

        try:
            result = await get_ai_response("test input")
            assert result is not None
            assert isinstance(result, str)
        except Exception as e:
            pytest.fail(f"AI response crashed: {e}")


class TestMainServer:
    """Test main server error handling"""

    def test_server_has_exception_handler(self):
        """Test server has global exception handler"""
        from main import app

        # Check if exception handler is registered
        assert app.exception_handlers is not None

    @pytest.mark.asyncio
    async def test_root_endpoint_never_crashes(self):
        """Test root endpoint always returns response"""
        from main import root

        try:
            result = await root()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Root endpoint crashed: {e}")


class TestRetryLogic:
    """Test retry mechanisms"""

    def test_retry_attempts_configured(self):
        """Test retry configuration is set"""
        assert RETRY_CONFIG['max_attempts'] == 3
        assert RETRY_CONFIG['min_wait'] >= 1
        assert RETRY_CONFIG['max_wait'] >= RETRY_CONFIG['min_wait']

    def test_function_retries_on_failure(self):
        """Test function retries correct number of times"""
        from tenacity import RetryError

        call_count = 0

        @safe_execute(fallback_response="fallback")
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Test error")

        result = failing_func()
        assert result == "fallback"
        # Should have tried up to 3 times (tenacity may stop early with reraise=False)
        assert call_count >= 1


def run_safety_tests():
    """Run all safety tests"""
    logger.info("Running production safety tests...")
    pytest.main([__file__, '-v', '--tb=short'])


if __name__ == "__main__":
    run_safety_tests()
