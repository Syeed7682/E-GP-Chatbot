"""
RAG Status and Admin Index Validation API Router.
Provides GET /api/rag/status and POST /api/admin/index/validate.
"""
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query
from app.indexing.index_manager import IndexManager
from app.config import INDEX_DIR
from app.services.rag_service import load_rag_service

router = APIRouter(tags=["RAG Admin"])


@router.get("/rag/status", summary="Get active RAG index status and version info")
async def get_rag_status() -> Dict[str, Any]:
    """Returns the current active index version, vector counts, and manifest."""
    mgr = IndexManager(INDEX_DIR)
    active_version = mgr.get_active_version()
    validation = mgr.validate_version(active_version)
    manifest = mgr.load_manifest(active_version)

    return {
        "status": "ready" if validation["passed"] else "degraded",
        "active_version": active_version,
        "available_versions": mgr.list_versions(),
        "stats": validation.get("stats", {}),
        "manifest": manifest,
        "warnings": validation.get("warnings", []),
    }


@router.post("/admin/index/validate", summary="Validate a specific index version before activation")
async def validate_index_version(version: str = Query(..., description="Version name e.g. v001, v002")) -> Dict[str, Any]:
    """Performs integrity and dimensionality checks on an index bundle."""
    mgr = IndexManager(INDEX_DIR)
    checks = mgr.validate_version(version)
    return checks

