Ok chec@echo off
cd /d "D:\Calling Agent for Uni Students\university-ai-agent"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
