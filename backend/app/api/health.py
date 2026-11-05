"""
Health Check API Router (app/api/health.py).
Provides system health and readiness probes.
"""
from fastapi import APIRouter
from app.services.retrieval_service import retrieval_service
from app.services.faiss_service import faiss_service
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="General service health status")
async def health_check():
    is_ready = retrieval_service.is_ready()
    return {
        "status": "healthy" if is_ready else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "index_ready": is_ready,
        "total_chunks": len(faiss_service.metadata) if is_ready else 0,
        "llm_model": settings.LLM_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL
    }

