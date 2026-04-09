from fastapi import FastAPI, Form, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from typing import Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="University Call Agent")


@app.get("/")
async def root():
    return {"status": "running"}


@app.post("/voice/incoming")
async def incoming_call():
    """Handle incoming call - prompt for speech"""
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/voice/process",
        method="POST",
        timeout=5,
        speech_timeout="auto",
        language="en-US"
    )

    gather.say("Hello! I'm your university assistant. How can I help you?", voice="Polly.Joanna")
    response.append(gather)

    response.say("I didn't hear anything. Goodbye!", voice="Polly.Joanna")
    response.hangup()

    return Response(content=str(response), media_type="application/xml")


@app.post("/voice/process")
async def process_speech(
    SpeechResult: Optional[str] = Form(None),
    From: Optional[str] = Form(None)
):
    """Process speech and return AI response"""
    response = VoiceResponse()

    # Handle empty input
    if not SpeechResult or not SpeechResult.strip():
        logger.warning(f"Empty input from {From}")
        response.say("I didn't catch that. Please call back.", voice="Polly.Joanna")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    try:
        logger.info(f"Processing: {SpeechResult[:50]}...")

        # Get AI response with retry
        ai_response = await get_ai_response(SpeechResult)

        # Return voice response
        response.say(ai_response, voice="Polly.Joanna")

        # Ask for more
        gather = Gather(
            input="speech",
            action="/voice/process",
            method="POST",
            timeout=5,
            speech_timeout="auto"
        )
        gather.say("Anything else?", voice="Polly.Joanna")
        response.append(gather)

        response.say("Thank you. Goodbye!", voice="Polly.Joanna")
        response.hangup()

        # Save conversation
        await save_conversation(From, SpeechResult, ai_response)

    except Exception as e:
        logger.error(f"Error: {e}")
        response.say("Sorry, there was an error. Please try again.", voice="Polly.Joanna")
        response.hangup()

    return Response(content=str(response), media_type="application/xml")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def get_ai_response(user_input: str) -> str:
    """Get AI response with retry logic"""
    text = user_input.lower()

    if "hours" in text or "open" in text:
        return "Our office hours are Monday through Friday, 9 AM to 5 PM."
    elif "register" in text or "enroll" in text:
        return "To register for classes, visit the student portal or contact the registrar."
    elif "tuition" in text or "payment" in text:
        return "For tuition information, contact the bursar's office at extension 1234."
    elif "transcript" in text:
        return "Request transcripts through the student portal or registrar's office."
    else:
        return "I can help with hours, registration, tuition, and transcripts. What do you need?"


async def save_conversation(caller: str, query: str, response: str):
    """Save conversation to database"""
    try:
        from supabase_memory import SupabaseMemory
        student_id = caller.replace("+", "").replace("-", "") if caller else "unknown"
        memory = SupabaseMemory()
        memory.save_conversation(student_id, query, response)
    except Exception as e:
        logger.error(f"Save failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
