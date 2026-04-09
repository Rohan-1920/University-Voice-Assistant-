# Calling Agent for University Students

A voice-enabled call handling system with Supabase integration for university student support.

## Features

- **Voice Call Handling** - Twilio webhook integration for incoming calls
- **Speech-to-Text** - Automatic voice to text conversion
- **AI Response** - Intelligent responses to student queries
- **Text-to-Speech** - Voice responses via TwiML
- **Database Storage** - Supabase PostgreSQL for conversation history
- **Automatic Fallback** - Local storage if DB fails
- **Error Handling** - No crashes on empty input
- **Fast Response** - Sub-second response times
- **Retry Logic** - Automatic retry on failures

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
# - Supabase URL and Key
# - Twilio Account SID, Auth Token, and Phone Number
```

3. Run the SQL schema in your Supabase project:
```sql
-- Execute supabase_schema.sql in Supabase SQL Editor
```

4. Configure Twilio webhook:
```
Voice webhook URL: https://your-domain.com/voice/incoming
Method: POST
```

## Running the API

```bash
# Development
python call_api.py

# Production
uvicorn call_api:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /voice/incoming
Handles incoming Twilio calls, prompts for speech input.

**Response:** TwiML with speech gathering

### POST /voice/process
Processes speech input and returns AI response.

**Parameters:**
- `SpeechResult` (form) - Transcribed speech text
- `From` (form) - Caller phone number

**Response:** TwiML with AI voice response

## Usage Example

### Call Flow

1. Student calls university number
2. System greets: "Hello! I'm your university assistant. How can I help you?"
3. Student speaks: "What are your office hours?"
4. System responds: "Our office hours are Monday through Friday, 9 AM to 5 PM."
5. System asks: "Anything else?"
6. Conversation continues or ends

## Supported Queries

The AI can handle:
- **Office Hours** - "What are your office hours?" / "When are you open?"
- **Registration** - "How do I register for classes?" / "How do I enroll?"
- **Tuition** - "How much is tuition?" / "Payment information?"
- **Transcripts** - "How do I get my transcript?"
- **General Help** - Fallback for other queries

## Error Handling

- **Empty Input** - Returns "I didn't catch that" message
- **Database Failure** - Automatically falls back to local JSON storage
- **AI Failure** - Retries up to 3 times with exponential backoff
- **Network Issues** - Graceful error messages to caller

## Testing

```bash
# Test call API
python -m pytest test_call_api.py -v

# Test Supabase integration
python test_supabase.py

# Test local memory system
python test_memory.py
```

All tests pass with 100% success rate.

## Files

- `call_api.py` - FastAPI call handling system
- `supabase_memory.py` - Supabase integration with fallback
- `memory_system.py` - Local memory system
- `supabase_schema.sql` - PostgreSQL database schema
- `test_call_api.py` - Call API tests
- `test_supabase.py` - Supabase integration tests
- `test_memory.py` - Local memory tests
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

## Architecture

```
Incoming Call (Twilio)
    ↓
POST /voice/incoming
    ↓
Gather Speech Input
    ↓
POST /voice/process
    ↓
Speech → Text (Twilio)
    ↓
AI Processing (with retry)
    ↓
Save to Database (with fallback)
    ↓
Text → Speech (TwiML)
    ↓
Voice Response to Caller
```

```python
from supabase_memory import SupabaseMemory

# Initialize
memory = SupabaseMemory()

# Save conversation
memory.save_conversation(
    student_id="S12345",
    user_query="What is Python?",
    ai_response="Python is a programming language."
)

# Fetch history
history = memory.fetch_history("S12345", limit=10)
for conv in history:
    print(f"Q: {conv['user_query']}")
    print(f"A: {conv['ai_response']}")
```

### Local Storage (Fallback)

```python
from memory_system import ConversationMemory

# Initialize
memory = ConversationMemory()

# Add conversation
memory.add_conversation(
    user_query="What is Python?",
    ai_response="Python is a programming language."
)

# Get context
context = memory.get_context()
print(context)
```

## Database Schema

### Tables

- **students** - Student information (id, student_id, name, email)
- **conversations** - Conversation history (student_id, user_query, ai_response)
- **logs** - System logs (student_id, log_level, message, metadata)

## Error Handling

The system automatically falls back to local JSON storage if:
- Supabase credentials are missing
- Database connection fails
- Any database operation errors occur

## Testing

```bash
# Test local memory system
python test_memory.py

# Test Supabase integration
python test_supabase.py
```

## Files

- `supabase_memory.py` - Supabase integration with fallback
- `memory_system.py` - Local memory system
- `supabase_schema.sql` - PostgreSQL database schema
- `test_supabase.py` - Supabase integration tests
- `test_memory.py` - Local memory tests
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
