import logging
import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    try:
        logger.info("Server starting up...")
        yield
    except Exception as e:
        logger.error(f"Error during lifespan: {e}", exc_info=True)
        raise
    finally:
        logger.info("Server shutting down...")


app = FastAPI(title="Calling Agent API", lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Please try again"
            }
        )


@app.get("/")
async def root():
    """Root endpoint"""
    try:
        logger.info("Root endpoint accessed")
        return {"message": "Calling Agent for Uni Students API", "status": "running"}
    except Exception as e:
        logger.error(f"Root endpoint error: {e}", exc_info=True)
        return {"status": "error", "message": "Please try again"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler - catch all unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Please try again"}
    )


def run_server():
    """Run the FastAPI server with auto-restart on crash"""
    max_retries = 5
    retry_count = 0

    while True:
        try:
            logger.info(f"Starting server (attempt {retry_count + 1}/{max_retries})")
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            break
        except Exception as e:
            retry_count += 1
            logger.error(f"Server crashed: {e}", exc_info=True)

            if retry_count >= max_retries:
                logger.critical(f"Max retries ({max_retries}) reached. Exiting.")
                sys.exit(1)

            wait_time = min(2 ** retry_count, 60)
            logger.info(f"Restarting in {wait_time} seconds...")
            time.sleep(wait_time)


if __name__ == "__main__":
    try:
        logger.info("Initializing server...")
        run_server()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
