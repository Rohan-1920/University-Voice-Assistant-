@echo off
title GIFT University AI Agent
color 0A

echo.
echo  ==========================================
echo   GIFT University AI Agent - Starting...
echo  ==========================================
echo.

:: Start Backend
echo  [1/2] Backend starting (port 8000)...
start "GIFT Backend" /min cmd /c "cd /d D:\Calling Agent for Uni Students\university-ai-agent && python -m app.main"

:: Wait for backend
timeout /t 4 /nobreak > nul

:: Start Frontend  
echo  [2/2] Frontend starting (port 3000)...
start "GIFT Frontend" /min cmd /c "cd /d D:\Calling Agent for Uni Students\university-ui && npm run dev"

:: Wait then open browser
timeout /t 5 /nobreak > nul

echo.
echo  Opening browser...
start http://localhost:3000

echo.
echo  ==========================================
echo   Ready! http://localhost:3000
echo  ==========================================
echo.
pause
