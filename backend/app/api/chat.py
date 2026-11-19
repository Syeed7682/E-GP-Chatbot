"""
Chat API Router (app/api/chat.py).
Handles chat queries with OCR vision extraction, hybrid retrieval, and grounded Qwen LLM answering.
"""
import re
import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.schemas.chat import ChatRequest, ChatResponse, SourceDocument, HealthResponse
from app.services.retrieval_service import retrieval_service
from app.services.qa_service import qa_service
from app.services.llm_service import (
    llm_service,
    LLM_MODEL,
    GROQ_VISION_MODEL,
    get_gemini_api_key,
    get_groq_api_key,
    is_procedure_steps_request,
    is_vague_steps_request,
)
from app.services.embedding_service import EMBEDDING_MODEL, embedding_service
from app.services.faiss_service import faiss_service
from app.services.vision_service import vision_service
from app.services.citation_service import citation_service
from app.core.security import sanitize_user_query, sanitize_image_base64

router = APIRouter(prefix="/chat", tags=["Chat"])


def _chat_log(message: str) -> None:
    """Write chat pipeline progress immediately to the server terminal."""
    print(f"[chat] {message}", flush=True)

@router.get("/questions", summary="List supplemental e-GP Q&A questions")
async def list_question_suggestions() -> Dict[str, Any]:
    """Returns the question text and module for every indexed Q&A record."""
    questions = [
        {
            "question_number": record["question_number"],
            "module": record["module"],
            "question": record["question"],
        }
        for record in qa_service.records
    ]
    return {"total": len(questions), "questions": questions}

@router.post("", response_model=ChatResponse, summary="Ask a question about e-GP manuals")
async def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Accepts a question and optional portal screenshot, retrieves relevant manual sections,
    and returns a cited answer grounded strictly in the 543-page official e-GP PE manual.
    """
    started_at = time.perf_counter()
    _chat_log("========== QUESTION PROCESSING START ==========")
    _chat_log("Step 1/8: Validating and sanitizing request...")
    raw_question = request.question.strip() if request.question else ""
    question = sanitize_user_query(raw_question)
    previous_question = sanitize_user_query(request.previous_question or "")[:500]

    img_data = sanitize_image_base64(request.image_base64 or request.image)

    if not question and not img_data:
        raise HTTPException(status_code=400, detail="Either a question or an image must be provided.")

    _chat_log(f"Question received: {question or '[image-only request]'}")
    _chat_log(f"Image attached: {'yes' if img_data else 'no'}")
    _chat_log(f"Request validation completed in {time.perf_counter() - started_at:.2f}s")
    csv_qa_service = retrieval_service.csv_qa_service
    index = faiss_service.index
    _chat_log(
        "Retrieval stores: "
        f"FAISS='{faiss_service.index_path}' ({index.ntotal if index else 0} vectors), "
        f"metadata='{faiss_service.metadata_path}' ({len(faiss_service.metadata)} records); "
        f"embedding='{EMBEDDING_MODEL}' provider={embedding_service._mode}."
    )
    _chat_log(
        f"Supplemental Q&A: TXT='{qa_service.path}' ({len(qa_service.records)} records), "
        f"DOCX='{qa_service.docx_path or 'disabled'}'; "
        f"CSV='{csv_qa_service.csv_path if csv_qa_service else 'disabled'}' "
        f"({len(csv_qa_service.records) if csv_qa_service else 0} records)."
    )

    # 1. OCR Extraction if image attached
    ocr_text = ""
    if img_data:
        _chat_log("Step 2/8: Extracting text from attached image (OCR)...")
        ocr_text = vision_service.extract_text_from_base64(img_data)
        _chat_log(f"OCR extracted {len(ocr_text)} characters.")
    else:
        _chat_log("Step 2/8: OCR skipped; no image attached.")

    # Resolve short follow-ups against the immediately preceding user question.
    answer_question = question
    has_followup_topic = bool(previous_question and not is_vague_steps_request(previous_question))
    if not img_data and is_vague_steps_request(question) and has_followup_topic:
        answer_question = f"Provide concise numbered steps for: {previous_question}"
    _chat_log(
        f"Step 3/8: Follow-up handling completed; effective question: {answer_question or '[image analysis]'}"
    )

    # 2. Precision Hybrid Retrieval
    if not img_data and is_vague_steps_request(question) and not has_followup_topic:
        context, raw_sources = "No relevant context found in manuals.", []
        _chat_log("Step 4/8: Retrieval skipped for a vague question without a previous topic.")
    else:
        effective_query = f"{answer_question} {ocr_text}".strip() or "e-GP portal procedure"
        _chat_log(f"Step 4/8: Retrieving top {request.top_k or 2} passage(s)...")
        context, raw_sources = retrieval_service.retrieve(
            effective_query,
            top_k=request.top_k or 2,
            image=img_data,
            include_page_context=is_procedure_steps_request(answer_question),
        )

    _chat_log(f"Retrieved {len(raw_sources)} source(s); context has {len(context)} characters.")
    for rank, source in enumerate(raw_sources, start=1):
        _chat_log(
            f"Source {rank}: type={source.get('source_type', 'manual')}, "
            f"page={source.get('page')}, score={source.get('score')}, "
            f"document={source.get('source', 'unknown')}, "
            f"files={source.get('source_files', [])}"
        )

    # 3. Generate Answer: Auto-shift to Vision Engine if an image is provided
    direct_qa_source = next(
        (
            source for source in raw_sources
            if source.get("source_type") == "qa" and source.get("direct_match")
        ),
        None,
    ) if not img_data else None
    answer_qa_source = direct_qa_source
    if direct_qa_source:
        _chat_log("Step 5/8: Direct supplemental Q&A match found; LLM generation skipped.")
        answer = direct_qa_source["answer"]
        answer_model = "e-GP System Q&A.txt (verbatim)"
        was_offline = False
    else:
        primary_model = (
            llm_service.model_name
            if not request.use_alt_model and not img_data and llm_service._mode == "local_transformers"
            else GROQ_VISION_MODEL
            if request.use_alt_model or img_data
            else LLM_MODEL
        )
        preview = context[:2000]
        _chat_log(f"Step 5/8: Sending question and retrieved context to {primary_model}.")
        _chat_log(f"Context preview (up to 2000 of {len(context)} characters):\n{preview}")
        if len(context) > len(preview):
            _chat_log("Context preview truncated; remaining context was still sent to the model.")
        answer, answer_model, was_offline = llm_service.generate_answer_with_metadata(
            answer_question or "Portal Screenshot Analysis",
            context,
            image=img_data,
            use_alt_model=request.use_alt_model,
            image_mime=request.image_mime or "image/png",
            language=request.language,
        )
        if not answer or not answer.strip():
            answer = llm_service._offline_answer_generator(answer_question, context)
            answer_model = "Offline grounded synthesis"
            was_offline = True
        has_retrieval_header = re.search(
            r"\b(?:Supplemental Q&A|Manual)\s*:",
            answer,
            re.IGNORECASE,
        )
        has_question_answer_labels = (
            re.search(r"^\s*Q\s*:", answer, re.IGNORECASE | re.MULTILINE)
            and re.search(r"^\s*A\s*:", answer, re.IGNORECASE | re.MULTILINE)
        )
        if has_retrieval_header or has_question_answer_labels:
            manual_context = "\n\n---\n\n".join(
                block for block in context.split("\n\n---\n\n")
                if not re.search(r"^\s*\[Supplemental Q&A\s*:", block)
            )
            has_manual_source = any(
                source.get("source_type") != "qa" for source in raw_sources
            )
            if has_manual_source and manual_context:
                answer = llm_service._offline_answer_generator(answer_question, manual_context)
                answer_model = "Offline grounded synthesis"
                was_offline = True
            else:
                matched_qa = next(
                    (source for source in raw_sources if source.get("source_type") == "qa"),
                    None,
                )
                if matched_qa:
                    answer = matched_qa["answer"]
                    answer_qa_source = matched_qa
                    answer_model = "e-GP System Q&A.txt (verbatim)"
                    was_offline = False

    _chat_log(f"Step 6/8: Answer generation completed using {answer_model}; offline={was_offline}.")

    # 4. Format Sources with Screenshot URLs
    sources = []
    portal_screens = set()
    _chat_log("Step 7/8: Formatting citations and source references...")
    for s in raw_sources:
        page = s["page"]
        chunk_id = s.get("chunk_id")
        img_url = citation_service.resolve_chunk_image_path(chunk_id, page)
        
        # Collect screen references
        snippet = s["snippet"]
        sc_matches = re.findall(r'Screen\s*[-–—:]\s*[A-Za-z0-9_.]+', snippet, re.IGNORECASE)
        for sc in sc_matches:
            portal_screens.add(sc)

        sources.append(
            SourceDocument(
                source=s["source"],
                page=page,
                chunk_id=chunk_id,
                score=s["score"],
                snippet=snippet,
                screen_reference=sc_matches[0] if sc_matches else None,
                image_path=img_url,
                related_sentence=s.get("related_sentence"),
                source_type=s.get("source_type", "manual"),
                source_files=s.get("source_files", []),
                question_number=s.get("question_number"),
                module=s.get("module"),
            )
        )

    model_label = (
        answer_model
        if answer_qa_source or was_offline
        else f"{answer_model} (e-GP Grounded)"
    )

    _chat_log(
        f"Step 8/8: Response ready with {len(sources)} citation(s); "
        f"total time={time.perf_counter() - started_at:.2f}s."
    )
    _chat_log("========== QUESTION PROCESSING END ==========")

    return ChatResponse(
        question=question or "Portal Screenshot Diagnostic",
        answer=answer,
        sources=sources,
        portal_screens=list(portal_screens),
        model_used=model_label,
        was_offline=was_offline
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
        vision_model=GROQ_VISION_MODEL,
        embedding_model=EMBEDDING_MODEL,
        hf_configured=bool(llm_service.token),
        gemini_configured=bool(get_gemini_api_key()),
        groq_configured=bool(get_groq_api_key())
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
