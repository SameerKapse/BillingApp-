@echo off
title Billing System - Development Mode
echo ==================================================
echo   Starting Billing System in Development Mode
echo ==================================================

start "Billing Backend (Flask)" cmd /k "cd backend && python app.py"
start "Billing Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo Both Backend and Frontend are starting in separate windows.
echo Backend API: http://127.0.0.1:5000
echo Frontend UI:  http://127.0.0.1:5173
echo.
pause
