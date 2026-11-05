#!/usr/bin/env bash
# =========================================================
# e-GP Official Manual Assistant Launcher (Unix/macOS)
# =========================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

if [ -f ".venv/bin/python" ]; then
    PY_EXE=".venv/bin/python"
else
    PY_EXE="python3"
fi

echo "========================================================="
echo "   Bangladesh e-GP Official Manual Multimodal Assistant"
echo "========================================================="
echo "Starting FastAPI Backend (Port 8000) & React Frontend (Port 3000)..."

cd backend
../$PY_EXE -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
