"""
Manual Viewer API Router (app/api/manual.py).
Provides endpoints for browsing manual pages and serving high-resolution page screenshots.
"""
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, Response
from app.core.config import settings
from app.services.faiss_service import faiss_service

router = APIRouter(prefix="/manual", tags=["Manual"])

@router.get("/page/{page_num}", summary="Get manual page content and chunks")
async def get_page(page_num: int):
    """Returns chunks and details for a page in the active manual."""
    total_pages = _manual_page_count()
    if page_num < 1 or page_num > total_pages:
        raise HTTPException(status_code=404, detail=f"Page number must be between 1 and {total_pages}.")

    page_chunks = [c for c in faiss_service.metadata if c.get("page") == page_num or c.get("page_number") == page_num]
    
    # Check if page image exists
    has_image = (
        any(path.exists() for path in _page_image_candidates(page_num))
        or _manual_pdf_path().is_file()
    )

    return {
        "page_number": page_num,
        "total_pages": total_pages,
        "has_image": has_image,
        "image_url": f"/api/manual/page/{page_num}/image" if has_image else None,
        "chunks_count": len(page_chunks),
        "chunks": page_chunks
    }

@router.get("/page/{page_num}/image", summary="Get extracted screenshot image of manual page")
async def get_page_image(page_num: int):
    """Serves the extracted JPG screenshot for the requested manual page."""
    total_pages = _manual_page_count()
    if page_num < 1 or page_num > total_pages:
        raise HTTPException(status_code=404, detail=f"Page number must be between 1 and {total_pages}.")

    for image_path in _page_image_candidates(page_num):
        if image_path.exists():
            with image_path.open("rb") as image_file:
                signature = image_file.read(8)
            media_type = (
                "image/png"
                if signature.startswith(b"\x89PNG\r\n\x1a\n")
                else "image/jpeg"
                if signature.startswith(b"\xff\xd8\xff")
                else None
            )
            if media_type is None:
                raise HTTPException(status_code=415, detail=f"Unsupported image format for manual page {page_num}.")
            return FileResponse(image_path, media_type=media_type)

    pdf_path = _manual_pdf_path()
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail=f"Image for page {page_num} not found.")

    import pymupdf

    with pymupdf.open(pdf_path) as document:
        if page_num > len(document):
            raise HTTPException(status_code=404, detail=f"Page {page_num} does not exist in the manual PDF.")
        page_image = document[page_num - 1].get_pixmap(dpi=150, alpha=False).tobytes("png")

    return Response(
        content=page_image,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/chunk/{chunk_id}/image", summary="Get extracted screenshot image of a specific manual chunk")
async def get_chunk_image(chunk_id: str):
    """Serves the exact extracted diagram or portal screenshot mapped to this chunk."""
    import re
    cid = re.sub(r"^[a-zA-Z]+:", "", str(chunk_id)).strip()
    chunks_dir = settings.EXTRACTED_IMAGES_DIR / "chunks"

    if chunks_dir.exists():
        matches = list(chunks_dir.glob(f"chunk_{cid}_page_*.*"))
        if matches:
            img_path = matches[0]
            with img_path.open("rb") as f:
                sig = f.read(8)
            media_type = "image/png" if sig.startswith(b"\x89PNG") else "image/jpeg"
            return FileResponse(img_path, media_type=media_type)

    raise HTTPException(status_code=404, detail=f"No image mapped to chunk {chunk_id}.")


@router.get("/images/{filename:path}", summary="Get extracted image asset by filename")
async def get_manual_image(filename: str):
    """Serves any extracted chunk or portal screenshot by filename."""
    safe_name = Path(filename).name
    chunks_dir = settings.EXTRACTED_IMAGES_DIR / "chunks"
    candidate = chunks_dir / safe_name
    if not candidate.is_file():
        candidate = settings.EXTRACTED_IMAGES_DIR / safe_name
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"Image {filename} not found.")

    with candidate.open("rb") as f:
        sig = f.read(8)
    media_type = "image/png" if sig.startswith(b"\x89PNG") else "image/jpeg"
    return FileResponse(candidate, media_type=media_type)


def _page_image_candidates(page_num: int) -> List[Path]:
    chunks_dir = settings.EXTRACTED_IMAGES_DIR / "chunks"
    chunk_matches = list(chunks_dir.glob(f"chunk_*_page_{page_num}_*.*")) if chunks_dir.exists() else []
    embedded_matches = sorted(settings.EXTRACTED_IMAGES_DIR.glob(f"page_{int(page_num):02d}_image_*.*"))
    return chunk_matches + embedded_matches + [
        settings.EXTRACTED_IMAGES_DIR / f"page_{page_num}.jpg",
        settings.EXTRACTED_IMAGES_DIR / f"page_{page_num}.png",
    ]


def _manual_pdf_path() -> Path:
    return settings.DATA_RAW_DIR / "source" / "new_manual.pdf"


def _manual_page_count() -> int:
    """Returns the page count for the active new manual/index."""
    indexed_pages = [
        c.get("page", c.get("page_number", 0))
        for c in faiss_service.metadata
    ]
    max_indexed_page = max((int(page) for page in indexed_pages if page), default=0)
    if max_indexed_page:
        return max_indexed_page

    pdf_path = _manual_pdf_path()
    if pdf_path.is_file():
        try:
            import pymupdf
            with pymupdf.open(pdf_path) as document:
                return len(document)
        except Exception:
            pass
    return 1


@router.get("/download", summary="Download the complete e-GP manual")
async def download_manual():
    """Downloads the official PDF used by the manual viewer and retrieval pipeline."""
    pdf_path = _manual_pdf_path()
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail="The full manual PDF is not available.")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )


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
