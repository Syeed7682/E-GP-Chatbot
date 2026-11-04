"""
Chat API Router.
Provides endpoints for querying the e-GP Manual Chatbot and checking system status.
"""
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Query
from app.schemas.chat_schema import ChatRequest, ChatResponse, SourceDocument, HealthResponse
from app.services.retrieval_service import retrieval_service
from app.services.llm_service import llm_service, LLM_MODEL
from app.services.embedding_service import EMBEDDING_MODEL
from app.services.faiss_service import faiss_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Ask a question about e-GP manuals")
async def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Accepts a question, retrieves the most relevant manual sections via FAISS,
    and returns a cited answer using Qwen2.5-VL-72B-Instruct.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Retrieve context & sources from FAISS (supports text and/or image)
    context, raw_sources = retrieval_service.retrieve(question, top_k=request.top_k or 3, image=request.image)

    # 2. Generate answer via LLM (Qwen2.5-VL-72B-Instruct supports multimodal vision)
    answer = llm_service.generate_answer(question, context, image=request.image)

    # 3. Format source documents with screenshot images
    sources = [
        SourceDocument(
            source=s["source"],
            page=s["page"],
            chunk_id=s["chunk_id"],
            score=s["score"],
            snippet=s["snippet"],
            image_path=s.get("image_path")
        )
        for s in raw_sources
    ]

    return ChatResponse(
        question=question,
        answer=answer,
        sources=sources
    )

@router.get("/health", response_model=HealthResponse, summary="System health and vector index status")
async def health_check() -> HealthResponse:
    """Returns the operational status of the chatbot and vector store."""
    is_ready = retrieval_service.is_ready()
    chunk_count = len(faiss_service.metadata) if is_ready else 0

    return HealthResponse(
        status="healthy" if is_ready else "index_not_loaded",
        index_loaded=is_ready,
        total_chunks=chunk_count,
        llm_model=LLM_MODEL,
        embedding_model=EMBEDDING_MODEL
    )

@router.get("/chunks", summary="Inspect indexed manual chunks")
async def get_indexed_chunks(limit: int = Query(10, ge=1, le=50)) -> Dict:
    """Returns a preview of the chunks currently loaded in the vector database."""
    if not retrieval_service.is_ready():
        retrieval_service.load_index_if_needed()

    chunks = faiss_service.metadata[:limit]
    return {
        "total_indexed": len(faiss_service.metadata),
        "showing": len(chunks),
        "chunks": chunks
    }

