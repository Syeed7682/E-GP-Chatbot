@echo off
title e-GP Manual Chatbot
echo ===================================================
echo           e-GP Manual Chatbot Launcher
echo ===================================================
echo.

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    echo [OK] Using virtual environment Python...
    set "PY_EXE=.venv\Scripts\python.exe"
    set "ST_EXE=.venv\Scripts\streamlit.exe"
) ELSE (
    echo [INFO] Using system Python...
    set "PY_EXE=python"
    set "ST_EXE=streamlit"
)

echo Starting e-GP Manual Assistant Web UI...
echo The app will open in your default browser shortly.
echo (Press Ctrl+C in this window anytime to close)
echo.

"%ST_EXE%" run streamlit_app.py

pause

