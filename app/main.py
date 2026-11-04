"""
FastAPI Application Entry Point.
Starts the e-GP Manual Chatbot REST API server.
"""
import os
import sys

# Ensure project root is in sys.path even when running 'python app/main.py' directly
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.chat import router as chat_router
from app.services.retrieval_service import retrieval_service

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler: runs on startup and shutdown.
    Attempts to load the FAISS index when the server starts up.
    """
    print("[main] Starting e-GP Manual Chatbot API Server...")
    loaded = retrieval_service.load_index_if_needed()
    if loaded:
        print("[main] FAISS index loaded and ready for questions.")
    else:
        print("[main] Notice: FAISS index not found yet. Please run ingestion and index building scripts.")
    yield
    print("[main] Shutting down e-GP Manual Chatbot API Server...")

app = FastAPI(
    title="e-GP Manual Chatbot API",
    description="Intelligent RAG assistant for electronic Government Procurement (e-GP) manuals and guidelines.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Streamlit, web dashboards, or testing tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api
app.include_router(chat_router, prefix="/api")

# Serve static files (favicon, etc.)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serves the favicon to prevent browser 404 errors."""
    icon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/x-icon")
    return FileResponse(status_code=204)

@app.get("/", summary="Root status")
async def root():
    """Root endpoint welcoming users and providing useful links."""
    return {
        "app": "e-GP Manual Chatbot",
        "version": "1.0.0",
        "docs_url": "/docs",
        "chat_endpoint": "/api/chat",
        "health_endpoint": "/api/chat/health"
    }

if __name__ == "__main__":
    import uvicorn
    # Allow running directly with 'python app/main.py'
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

