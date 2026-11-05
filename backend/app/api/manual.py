"""
Manual Viewer API Router (app/api/manual.py).
Provides endpoints for browsing manual pages and serving high-resolution page screenshots.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from app.core.config import settings
from app.services.faiss_service import faiss_service

router = APIRouter(prefix="/manual", tags=["Manual"])

@router.get("/page/{page_num}", summary="Get manual page content and chunks")
async def get_page(page_num: int):
    """Returns chunks and details for a specific page number in the 543-page manual."""
    if page_num < 1 or page_num > 543:
        raise HTTPException(status_code=404, detail="Page number must be between 1 and 543.")

    page_chunks = [c for c in faiss_service.metadata if c.get("page") == page_num or c.get("page_number") == page_num]
    
    # Check if page image exists
    img_path = settings.EXTRACTED_IMAGES_DIR / f"page_{page_num}.jpg"
    has_image = img_path.exists()

    return {
        "page_number": page_num,
        "total_pages": 543,
        "has_image": has_image,
        "image_url": f"/api/manual/page/{page_num}/image" if has_image else None,
        "chunks_count": len(page_chunks),
        "chunks": page_chunks
    }

@router.get("/page/{page_num}/image", summary="Get extracted screenshot image of manual page")
async def get_page_image(page_num: int):
    """Serves the extracted JPG screenshot for the requested manual page."""
    img_candidates = [
        settings.EXTRACTED_IMAGES_DIR / f"page_{page_num}.jpg",
        settings.EXTRACTED_IMAGES_DIR / "page_images" / f"page_{page_num}.jpg",
        settings.EXTRACTED_IMAGES_DIR / f"page_{page_num}_img_0.jpg",
    ]
    for p in img_candidates:
        if p.exists():
            return FileResponse(p, media_type="image/jpeg")

    raise HTTPException(status_code=404, detail=f"Image for page {page_num} not found.")

@router.get("/search", summary="Search manual by keyword")
async def search_manual(q: str = Query(..., min_length=2), limit: int = 10):
    """Fast keyword search across all indexed chunks."""
    q_lower = q.lower()
    matches = []
    for c in faiss_service.metadata:
        text = c.get("content", c.get("text", "")).lower()
        title = c.get("section_title", "").lower()
        if q_lower in title or q_lower in text:
            matches.append(c)
            if len(matches) >= limit:
                break

    return {
        "query": q,
        "count": len(matches),
        "results": matches
    }

