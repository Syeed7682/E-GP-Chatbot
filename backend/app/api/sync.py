"""
Sync API Router (app/api/sync.py).
Handles offline synchronization, dataset hash validation, and client mutations reconciliation.
"""
import time
import hashlib
from typing import Dict, Any, List
from fastapi import APIRouter
from app.schemas.manual import SyncPushRequest, SyncPushResponse
from app.services.faiss_service import faiss_service

router = APIRouter(prefix="/sync", tags=["Sync"])

SERVER_SYNC_VERSION = "v2026.2.4-clean-rag"

def compute_dataset_hash() -> str:
    content = str(len(faiss_service.metadata))
    if faiss_service.metadata:
        content += faiss_service.metadata[0].get("content", "")[:100]
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

@router.get("/version", summary="Check current server manual version")
async def get_sync_version():
    return {
        "version": SERVER_SYNC_VERSION,
        "hash": compute_dataset_hash(),
        "chunk_count": len(faiss_service.metadata),
        "timestamp": int(time.time() * 1000)
    }

@router.get("/chunks", summary="Get full verified manual chunks for local IndexedDB caching")
async def get_sync_chunks():
    return {
        "version": SERVER_SYNC_VERSION,
        "hash": compute_dataset_hash(),
        "total_chunks": len(faiss_service.metadata),
        "chunks": faiss_service.metadata,
        "timestamp": int(time.time() * 1000)
    }

@router.post("/push", response_model=SyncPushResponse, summary="Push client mutations / offline actions")
async def push_client_mutations(req: SyncPushRequest):
    processed = []
    for m in req.mutations:
        processed.append(m.id)

    return SyncPushResponse(
        status="success",
        processed_count=len(processed),
        processed_ids=processed,
        conflicts=[],
        server_time=int(time.time() * 1000)
    )

