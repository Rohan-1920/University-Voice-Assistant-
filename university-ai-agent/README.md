# University AI Voice Agent

Production-ready AI voice assistant for university students.

## Features

- Voice-to-text and text-to-voice capabilities
- Intent classification and intelligent responses
- Conversation context management
- Supabase database integration
- RESTful API with FastAPI
- Comprehensive logging

## Setup

### 1. Create Virtual Environment

```bash
cd university-ai-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env` and fill in your credentials:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the Application

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Health check
- `POST /query` - Process text query
- `GET /history/{user_id}` - Get user history
- `GET /student/{student_id}` - Get student info

## Project Structure

```
university-ai-agent/
├── app/
│   ├── core/          # Configuration, logging, utilities
│   ├── ai/            # AI brain, intent classification, prompts
│   ├── voice/         # Speech-to-text and text-to-speech
│   ├── memory/        # Conversation context management
│   ├── db/            # Supabase integration and models
│   ├── call/          # Call handling logic
│   └── main.py        # FastAPI application
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md         # Documentation
```

## Usage

### Voice Call Mode

```python
from app.call.handler import call_handler

call_handler.start_call(user_id="student123")
```

### API Mode

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student123", "query": "What are my courses?"}'
```

## Development

- All imports are properly connected
- Logging configured for production
- Error handling implemented
- Database models defined
- Ready for deployment
