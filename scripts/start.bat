@echo off
title Echo Development Environment

echo ===========================================
echo         Starting Echo Development
echo ===========================================
echo.

REM Move to project root (start.bat is inside scripts/)
cd /d "%~dp0.."

REM Start ngrok
echo Starting ngrok...
start "Ngrok" cmd /k "ngrok http 1244"

REM Wait for ngrok to initialize
timeout /t 3 >nul

REM Start Echo Backend
echo Starting Echo Backend...
start "Echo Backend" cmd /k "call .venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 1244 --reload"

echo.
echo ===========================================
echo Echo Development Environment Started
echo ===========================================
echo.
echo Backend : http://127.0.0.1:1244
echo Docs    : http://127.0.0.1:1244/docs
echo Ngrok UI: http://127.0.0.1:4040
echo.
pause