"""
Vision Chat and Screenshot Upload API Router.
Accepts portal screenshots, validates image headers, performs OCR and visual embedding,
retrieves grounded evidence, and synthesizes step-by-step guidance.
"""
import io
import logging
from typing import Any, Dict
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from PIL import Image

from app.schemas.chat import ChatResponse, SourceDocument
from app.services.llm_service import llm_service
from app.services.rag_service import load_rag_service
from app.ingestion.ocr_processor import process_ocr
from app.core.security import sanitize_user_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Vision Chat"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _verify_image_signature(data: bytes) -> bool:
    """Verifies image file magic numbers/signatures."""
    if len(data) < 8:
        return False
    # PNG signature: 89 50 4E 47 0D 0A 1A 0A
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    # JPEG signature: FF D8 FF
    if data.startswith(b"\xff\xd8\xff"):
        return True
    # WebP signature: RIFF....WEBP
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return True
    return False


@router.post("/vision", response_model=ChatResponse, summary="Screenshot-based multimodal procurement consultation")
async def vision_chat(
    question: str = Form(..., description="User question or error query"),
    screenshot: UploadFile = File(..., description="Uploaded portal screenshot or error image"),
) -> ChatResponse:
    """
    Multimodal endpoint: Accepts question + portal screenshot, executes OCR + visual retrieval,
    and returns cited procedure grounded in official e-GP manual.
    """
    clean_query = sanitize_user_query(question)
    if not clean_query:
        clean_query = "Analyze this portal screenshot and explain the required e-GP procedure or error resolution."

    # Validate MIME type
    if screenshot.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {screenshot.content_type}. Allowed: JPEG, PNG, WebP.",
        )

    # Read and validate size
    data = await screenshot.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds maximum permitted size of 5 MB.",
        )

    # Validate magic bytes
    if not _verify_image_signature(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format: file contents do not match header signature.",
        )

    try:
        pil_image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not decode image: {e}",
        )

    # 1. OCR Extraction
    ocr_text = process_ocr(pil_image)
    combined_query = clean_query
    if ocr_text:
        combined_query += f"\n[OCR Text from Screen]: {ocr_text[:300]}"

    # 2. Multimodal Retrieval via RAG Service
    rag = load_rag_service()
    if rag is not None:
        visual_vec = rag.visual_embedder.encode_image(pil_image)
        context, sources_raw, portal_screens = rag.retrieve(
            query=combined_query,
            screenshot_vector=visual_vec,
            top_k=7,
        )
    else:
        context = ""
        sources_raw = []
        portal_screens = []

    # 3. LLM Synthesis
    import base64
    b64_img = base64.b64encode(data).decode("utf-8")
    answer, model_used, was_offline = llm_service.generate_answer_with_metadata(
        clean_query,
        context,
        image=b64_img,
        use_alt_model=True,
        image_mime=screenshot.content_type or "image/png",
    )

    sources = [
        SourceDocument(
            page=s.get("page", 1),
            chunk_id=s.get("chunk_id", ""),
            score=s.get("score", 0.0),
            snippet=s.get("snippet", ""),
            screen_reference=s.get("screen_reference"),
            source=s.get("source", "egp_manual.pdf"),
            section=s.get("section", ""),
            source_type=s.get("source_type", "pdf"),
            question_number=s.get("question_number"),
            module=s.get("module"),
        )
        for s in sources_raw
    ]

    return ChatResponse(
        question=clean_query,
        answer=answer,
        sources=sources,
        portal_screens=portal_screens,
        model_used=model_used,
        was_offline=was_offline,
    )

