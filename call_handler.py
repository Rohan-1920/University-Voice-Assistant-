from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
from dotenv import load_dotenv
from typing import Optional
import logging
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('call_handler.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="University Call Agent")

# Twilio configuration
try:
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None
    if twilio_client:
        logger.info("Twilio client initialized successfully")
    else:
        logger.warning("Twilio credentials not found, client not initialized")
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {e}")
    twilio_client = None


@app.get("/")
async def root():
    try:
        logger.info("Root endpoint accessed")
        return {"status": "Call Agent API is running", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        return {"status": "error", "message": "Please try again"}


@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio call webhook"""
    try:
        logger.info("Incoming call received")
        response = VoiceResponse()

        # Gather speech input with timeout
        gather = Gather(
            input="speech",
            action="/voice/process",
            method="POST",
            timeout=5,
            speech_timeout="auto",
            language="en-US"
        )

        gather.say(
            "Hello! I'm your university assistant. How can I help you today?",
            voice="Polly.Joanna"
        )

        response.append(gather)

        # Fallback if no input
        response.say(
            "I didn't hear anything. Please call back when you're ready.",
            voice="Polly.Joanna"
        )
        response.hangup()

        logger.info("Incoming call handled successfully")
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error handling incoming call: {e}", exc_info=True)
        return _error_response("Sorry, there was an error. Please try again.")


@app.post("/voice/process")
async def process_speech(
    SpeechResult: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None),
    From: Optional[str] = Form(None)
):
    """Process speech input and return AI response"""
    try:
        # Handle empty input
        if not SpeechResult or SpeechResult.strip() == "":
            logger.warning(f"Empty speech input from {From}")
            return _empty_input_response()

        logger.info(f"Processing speech from {From}: {SpeechResult[:100]}...")

        # Get AI response with retry logic
        try:
            ai_response = await get_ai_response(SpeechResult, From)
        except Exception as e:
            logger.error(f"Failed to get AI response after retries: {e}", exc_info=True)
            return _error_response("Please try again.")

        # Create TwiML response
        response = VoiceResponse()

        # Speak AI response
        response.say(ai_response, voice="Polly.Joanna")

        # Ask if they need more help
        gather = Gather(
            input="speech",
            action="/voice/process",
            method="POST",
            timeout=5,
            speech_timeout="auto",
            language="en-US"
        )

        gather.say(
            "Is there anything else I can help you with?",
            voice="Polly.Joanna"
        )

        response.append(gather)

        # End call if no response
        response.say("Thank you for calling. Goodbye!", voice="Polly.Joanna")
        response.hangup()

        # Save conversation to database (non-blocking)
        try:
            await save_conversation_async(From, SpeechResult, ai_response)
        except Exception as e:
            logger.error(f"Failed to save conversation (non-critical): {e}")

        logger.info(f"Speech processed successfully for {From}")
        return Response(content=str(response), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error processing speech: {e}", exc_info=True)
        return _error_response("Please try again.")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True
)
async def get_ai_response(user_input: str, caller_id: Optional[str] = None) -> str:
    """Get AI response with retry logic"""
    try:
        logger.debug(f"Getting AI response for input: {user_input[:50]}...")

        # TODO: Replace with actual AI integration (OpenAI, Claude, etc.)
        # For now, return a simple response

        user_input_lower = user_input.lower()

        # Simple keyword-based responses
        if "hours" in user_input_lower or "open" in user_input_lower:
            response = "Our office hours are Monday through Friday, 9 AM to 5 PM."

        elif "register" in user_input_lower or "enroll" in user_input_lower:
            response = "To register for classes, please visit the student portal or contact the registrar's office."

        elif "tuition" in user_input_lower or "payment" in user_input_lower:
            response = "For tuition and payment information, please contact the bursar's office at extension 1234."

        elif "transcript" in user_input_lower:
            response = "You can request transcripts through the student portal or by visiting the registrar's office."

        elif "help" in user_input_lower or "support" in user_input_lower:
            response = "I can help you with office hours, registration, tuition, transcripts, and general university information."

        else:
            response = "I understand you're asking about university services. For specific assistance, please visit our website or contact the main office."

        logger.debug(f"Generated response: {response[:50]}...")
        return response

    except Exception as e:
        logger.error(f"Error getting AI response: {e}", exc_info=True)
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def save_conversation_async(caller_id: str, user_query: str, ai_response: str):
    """Save conversation to database asynchronously with retry"""
    try:
        from supabase_memory import SupabaseMemory

        # Extract student ID from caller (or use phone number)
        student_id = caller_id.replace("+", "").replace("-", "") if caller_id else "unknown"

        memory = SupabaseMemory()
        success = memory.save_conversation(student_id, user_query, ai_response)

        if success:
            logger.info(f"Conversation saved for {student_id}")
        else:
            logger.warning(f"Conversation save returned False for {student_id}")

    except Exception as e:
        logger.error(f"Failed to save conversation after retries: {e}", exc_info=True)
        # Don't raise - saving is non-critical


def _empty_input_response() -> Response:
    """Return TwiML for empty input"""
    try:
        response = VoiceResponse()

        gather = Gather(
            input="speech",
            action="/voice/process",
            method="POST",
            timeout=5,
            speech_timeout="auto",
            language="en-US"
        )

        gather.say(
            "I didn't catch that. Could you please repeat your question?",
            voice="Polly.Joanna"
        )

        response.append(gather)
        response.say("Thank you for calling. Goodbye!", voice="Polly.Joanna")
        response.hangup()

        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error creating empty input response: {e}", exc_info=True)
        return _fallback_error_response()


def _error_response(message: str) -> Response:
    """Return TwiML for error cases"""
    try:
        response = VoiceResponse()
        response.say(message, voice="Polly.Joanna")
        response.say("Goodbye!", voice="Polly.Joanna")
        response.hangup()

        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        logger.error(f"Error creating error response: {e}", exc_info=True)
        return _fallback_error_response()


def _fallback_error_response() -> Response:
    """Absolute fallback response if everything fails"""
    try:
        response = VoiceResponse()
        response.say("Please try again.", voice="Polly.Joanna")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        logger.critical(f"Critical error in fallback response: {e}", exc_info=True)
        # Return minimal valid TwiML
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Please try again.</Say><Hangup/></Response>',
            media_type="application/xml"
        )


@app.post("/voice/status")
async def call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle call status callbacks"""
    try:
        logger.info(f"Call {CallSid} status: {CallStatus}")
        return {"status": "received", "call_sid": CallSid, "call_status": CallStatus}
    except Exception as e:
        logger.error(f"Error handling call status: {e}", exc_info=True)
        return {"status": "error", "message": "Please try again"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "twilio_configured": twilio_client is not None
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=True)
        return {"status": "error", "message": "Please try again"}


if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting call handler server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.critical(f"Failed to start server: {e}", exc_info=True)
