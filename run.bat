@echo off
title e-GP Official Manual Assistant Launcher
echo =========================================================
echo    Bangladesh e-GP Official Manual Multimodal Assistant
echo    (Enterprise RAG + Offline-First Sync Architecture)
echo =========================================================
echo.

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    set "PY_EXE=.venv\Scripts\python.exe"
) ELSE (
    set "PY_EXE=python"
)

echo Select launch mode:
echo   [1] Start Full Stack (FastAPI Backend + React Frontend)
echo   [2] Start React Frontend Only (Port 3000)
echo   [3] Start FastAPI Python Backend Only (Port 8000)
echo.
set /p opt="Enter choice [1, 2, or 3] (default 1): "

if "%opt%"=="3" (
    echo Starting FastAPI Backend on http://127.0.0.1:8000...
    cd backend
    ..\%PY_EXE% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    goto end
)

if "%opt%"=="2" (
    echo Starting React Frontend on http://localhost:3000...
    cd frontend
    npm run dev
    goto end
)

:: Default: Full Stack
echo Starting Python FastAPI Backend in background...
start "e-GP FastAPI Backend" cmd /k "cd backend && ..\%PY_EXE% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting React Frontend...
cd frontend
npm run dev

:end
pause
