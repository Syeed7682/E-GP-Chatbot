"""
Chat API Router (app/api/chat.py).
Handles chat queries with OCR vision extraction, hybrid retrieval, and grounded Qwen LLM answering.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument, HealthResponse
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import (
    llm_service,
    LLM_MODEL,
    is_procedure_steps_request,
    is_vague_steps_request,
)
from app.services.embedding_service import EMBEDDING_MODEL
from app.services.faiss_service import faiss_service
from app.services.vision_service import vision_service
from app.services.citation_service import citation_service
from app.core.security import sanitize_user_query, sanitize_image_base64

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Ask a question about e-GP manuals")
async def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Accepts a question and optional portal screenshot, retrieves relevant manual sections,
    and returns a cited answer grounded strictly in the 543-page official e-GP PE manual.
    """
    raw_question = request.question.strip() if request.question else ""
    question = sanitize_user_query(raw_question)
    previous_question = sanitize_user_query(request.previous_question or "")[:500]

    img_data = sanitize_image_base64(request.image_base64 or request.image)

    if not question and not img_data:
        raise HTTPException(status_code=400, detail="Either a question or an image must be provided.")

    # 1. OCR Extraction if image attached
    ocr_text = ""
    if img_data:
        ocr_text = vision_service.extract_text_from_base64(img_data)

    # Resolve short follow-ups against the immediately preceding user question.
    answer_question = question
    has_followup_topic = bool(previous_question and not is_vague_steps_request(previous_question))
    if not img_data and is_vague_steps_request(question) and has_followup_topic:
        answer_question = f"Provide concise numbered steps for: {previous_question}"

    # 2. Precision Hybrid Retrieval
    if not img_data and is_vague_steps_request(question) and not has_followup_topic:
        context, raw_sources = "No relevant context found in manuals.", []
    else:
        effective_query = f"{answer_question} {ocr_text}".strip() or "e-GP portal procedure"
        context, raw_sources = retrieval_service.retrieve(
            effective_query,
            top_k=request.top_k or 5,
            image=img_data,
            include_page_context=is_procedure_steps_request(answer_question),
        )

    # 3. Generate Answer: Auto-shift to Vision Engine if an image is provided
    answer = llm_service.generate_answer(
        answer_question or "Portal Screenshot Analysis",
        context,
        image=img_data,
        use_alt_model=request.use_alt_model,
        image_mime=request.image_mime or "image/png",
    )
    if not answer or not answer.strip():
        answer = llm_service._offline_answer_generator(answer_question, context)

    # 4. Format Sources with Screenshot URLs
    sources = []
    portal_screens = set()
    for s in raw_sources:
        page = s["page"]
        img_url = citation_service.resolve_screenshot_path(page)
        
        # Collect screen references
        snippet = s["snippet"]
        import re
        sc_matches = re.findall(r'Screen\s*[-–—:]\s*[A-Za-z0-9_.]+', snippet, re.IGNORECASE)
        for sc in sc_matches:
            portal_screens.add(sc)

        sources.append(
            SourceDocument(
                source=s["source"],
                page=page,
                chunk_id=s["chunk_id"],
                score=s["score"],
                snippet=snippet,
                screen_reference=sc_matches[0] if sc_matches else None,
                image_path=img_url
            )
        )

    # Determine which model label to show
    model_label = f"{LLM_MODEL} (e-GP Grounded)"
    if request.use_alt_model:
        from app.services.llm_service import ALT_VL_MODEL
        model_label = f"{ALT_VL_MODEL} (Optional Liquid AI)"

    return ChatResponse(
        question=question or "Portal Screenshot Diagnostic",
        answer=answer,
        sources=sources,
        portal_screens=list(portal_screens),
        model_used=model_label,
        was_offline=False
    )

@router.get("/health", response_model=HealthResponse, summary="System health and vector index status")
async def health_check() -> HealthResponse:
    """Returns the operational status of the chatbot and vector store."""
    is_ready = retrieval_service.is_ready()
    chunk_count = len(faiss_service.metadata) if is_ready else 0

    return HealthResponse(
        status="healthy" if is_ready else "index_not_loaded",
        system="e-GP Official Manual Assistant",
        index_loaded=is_ready,
        total_chunks=chunk_count,
        llm_model=LLM_MODEL,
        embedding_model=EMBEDDING_MODEL,
        hf_configured=bool(llm_service.token),
        gemini_configured=False
    )

@router.get("/chunks", summary="Inspect indexed manual chunks")
async def get_indexed_chunks(limit: int = Query(10, ge=1, le=50)) -> Dict[str, Any]:
    """Returns a preview of the chunks currently loaded in the vector database."""
    if not retrieval_service.is_ready():
        retrieval_service.load_index_if_needed()

    chunks = faiss_service.metadata[:limit]
    return {
        "total_indexed": len(faiss_service.metadata),
        "showing": len(chunks),
        "chunks": chunks
    }
