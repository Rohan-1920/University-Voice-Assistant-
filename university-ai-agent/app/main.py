from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.core.config import config
from app.core.logger import logger
from app.call.handler import call_handler
from app.call.telnyx_webhook import router as telnyx_router
from app.demo.voice_demo import router as demo_router
from app.db.supabase import db

app = FastAPI(
    title="University AI Voice Agent",
    description="AI-powered voice assistant for university students",
    version="1.0.0"
)

@app.on_event("shutdown")
async def shutdown():
    """Close DB pool gracefully on app shutdown"""
    db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telnyx voice webhooks
app.include_router(telnyx_router)

# Voice demo API (STT + TTS)
app.include_router(demo_router)

class QueryRequest(BaseModel):
    user_id: str
    query: str

class QueryResponse(BaseModel):
    intent: str
    response: str
    status: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "University AI Voice Agent",
        "version": "1.0.0"
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process text query"""
    try:
        result = call_handler.handle_text_query(request.user_id, request.query)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 10):
    """Get user's call history — use 'all' for all logs"""
    try:
        if user_id == "all":
            history = db.get_user_history(limit=limit)
        else:
            history = db.get_user_history(user_id, limit)
        return {"user_id": user_id, "history": history}
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/student/{student_id}")
async def get_student(student_id: str):
    """Get student information"""
    try:
        info = db.get_student_info(student_id)
        if not info:
            raise HTTPException(status_code=404, detail="Student not found")
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Student info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )
