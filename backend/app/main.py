"""
FastAPI Application Entry Point (backend/app/main.py).
Starts the e-GP Manual Chatbot REST API server with all routers.
"""
import os
import sys
from pathlib import Path

# Ensure project root and backend dir are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
for p in [str(BACKEND_DIR), str(ROOT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.manual import router as manual_router
from app.api.sync import router as sync_router
from app.services.retrieval_service import retrieval_service
from app.core.config import settings

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    print(f"[main] Starting {settings.PROJECT_NAME} API Server...")
    loaded = retrieval_service.load_index_if_needed()
    if loaded:
        print("[main] FAISS index loaded and ready for questions.")
    else:
        print("[main] Notice: FAISS index not found yet. Please run ingestion script.")
    yield
    print(f"[main] Shutting down {settings.PROJECT_NAME} API Server...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Multimodal RAG assistant for electronic Government Procurement (e-GP) manuals and guidelines.",
    version=settings.VERSION,
    lifespan=lifespan
)

# Enable CORS for React frontend, mobile browsers, or local dev tools
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers under /api
app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(manual_router, prefix="/api")
app.include_router(sync_router, prefix="/api")

# Serve static files (favicon, etc.)
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/x-icon")
    return FileResponse(status_code=204)

@app.get("/", summary="Root status")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "chat_endpoint": "/api/chat",
        "health_endpoint": "/api/health",
        "manual_endpoint": "/api/manual",
        "sync_endpoint": "/api/sync"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
