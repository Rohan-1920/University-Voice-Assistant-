"""Quick test to start voice call with laptop mic"""
from app.call.handler import call_handler

if __name__ == "__main__":
    call_handler.start_call(user_id="test_user")
