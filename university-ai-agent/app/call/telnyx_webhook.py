"""
Telnyx TeXML Voice Webhook
==========================
Flow:
  Tumhara phone → Telnyx number pe call
  → POST /telnyx/incoming  (bot greet karta hai, speech sunta hai)
  → POST /telnyx/process   (speech → AI → voice response)
"""

from fastapi import APIRouter, Form, Response
from typing import Optional
from app.core.logger import logger
from app.ai.brain import ai_brain
from app.memory.context import context_manager
from app.db.supabase import db

router = APIRouter(prefix="/telnyx", tags=["Telnyx Voice"])

VOICE = "Polly.Joanna"          # Amazon Polly via Telnyx (English)
VOICE_UR = "Polly.Zeynep"       # Closest Urdu-friendly voice on Telnyx


def texml(content: str) -> Response:
    """Wrap content in TeXML Response tags"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
{content}
</Response>"""
    return Response(content=xml, media_type="application/xml")


@router.post("/incoming")
async def incoming_call():
    """
    Step 1 — Telnyx calls this when someone dials the bot number.
    Bot greets and starts listening.
    """
    logger.info("Incoming call received via Telnyx")

    body = """
  <Say voice="Polly.Joanna">
    Assalam o Alaikum! GIFT University mein khush aamdeed.
    Main aapka admission assistant hoon.
    Aap admission, programs, fees, ya kisi bhi cheez ke baare mein pooch sakte hain.
    Batayein, main aapki kya madad kar sakta hoon?
  </Say>
  <Gather input="speech" action="/telnyx/process" method="POST"
          timeout="5" speechTimeout="auto" language="ur-PK">
  </Gather>
  <Say voice="Polly.Joanna">Koi awaaz nahi aayi. Meherbani kar ke dobara call karein.</Say>
  <Hangup/>"""

    return texml(body)


@router.post("/process")
async def process_speech(
    SpeechResult: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
):
    """
    Step 2 — Telnyx sends transcribed speech here.
    Bot processes it with AI and responds.
    """
    caller_id = From or "unknown"
    logger.info(f"Call from {caller_id} | Speech: {SpeechResult}")

    # Empty input
    if not SpeechResult or not SpeechResult.strip():
        body = """
  <Say voice="Polly.Joanna">Mujhe kuch sunai nahi diya. Meherbani kar ke dobara bolein.</Say>
  <Gather input="speech" action="/telnyx/process" method="POST"
          timeout="5" speechTimeout="auto" language="ur-PK">
  </Gather>
  <Hangup/>"""
        return texml(body)

    # Farewell check
    farewell = ["goodbye", "khuda hafiz", "allah hafiz", "shukriya", "bye"]
    if any(w in SpeechResult.lower() for w in farewell):
        body = """
  <Say voice="Polly.Joanna">
    Shukriya GIFT University ko call karne ka. Allah Hafiz, aur aapka future bright ho!
  </Say>
  <Hangup/>"""
        return texml(body)

    # Get per-caller context
    ctx = context_manager.get(caller_id)
    ctx.add_message("user", SpeechResult)

    # AI response
    result = ai_brain.process_query(SpeechResult, ctx.get_context_string())
    ai_response = result["response"]
    intent = result["intent"]

    ctx.add_message("assistant", ai_response, intent)
    db.log_call(caller_id, SpeechResult, ai_response, intent)

    # Respond with voice + keep listening
    import xml.sax.saxutils as saxutils
    safe_response = saxutils.escape(ai_response)

    body = f"""
  <Say voice="Polly.Joanna">{safe_response}</Say>
  <Gather input="speech" action="/telnyx/process" method="POST"
          timeout="5" speechTimeout="auto" language="ur-PK">
    <Say voice="Polly.Joanna">Kuch aur poochna chahte hain?</Say>
  </Gather>
  <Say voice="Polly.Joanna">Shukriya. Allah Hafiz!</Say>
  <Hangup/>"""

    return texml(body)
