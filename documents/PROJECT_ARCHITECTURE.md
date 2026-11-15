# Project Architecture: Enterprise Multimodal RAG Assistant

This document details the production architecture of the **Bangladesh e-GP Official Manual Assistant**.

---

## 1. System Architecture Overview

A complete PlantUML source file is available at [`PROJECT_ARCHITECTURE.puml`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_ARCHITECTURE.puml).

```mermaid
flowchart TD
    subgraph Client [Client Presentation Layer - Netlify]
        UI[React 19 + Tailwind CSS Frontend]
        SB[GovtOfficialSidebar: Deduplicated Q&A Suggestions]
        CA[GovtChatArea: Markdown Tables, Citations, Chunk Images]
    end

    subgraph API [FastAPI Service Layer :8000]
        Router[API Gateway / CORS / Validation]
        ChatAPI["/api/chat & /api/chat/vision"]
        ManualAPI["/api/manual (Pages & Chunk Images)"]
        RagAPI["/api/rag & /health"]
    end

    subgraph RAG [Retrieval & Ranking Engine]
        QR[Query Router]
        Dense[BGE-M3 Dense Retriever - 1024-dim]
        Sparse[BM25Okapi Lexical Retriever]
        Vision[SigLIP Visual Feature Retriever - 768-dim]
        RRF[Reciprocal Rank Fusion k=60]
        Reranker[BGE-Reranker-v2-m3 Cross-Encoder]
        ContextBuilder[Context & Citation Assembly]
    end

    subgraph Inference [Multimodal LLM Layer]
        GroqText["Groq: openai/gpt-oss-20b"]
        GroqVision["Groq: qwen/qwen3.8-27b"]
        GeminiFB["Google Gemini Flash Fallback"]
        OfflineSyn["Offline Grounded Synthesizer + Helpdesk Info"]
    end

    subgraph Storage [Data & Versioned Index Layer]
        ActivePtr[active_version.json]
        V001["Version v001 Index Store"]
        FAISS[(pdf_text.faiss - 1188 vectors)]
        BM25[(bm25.pkl)]
        SQLite[(metadata.db SQLite)]
        ChunkImages["data/extracted_images/chunks/ (1096 images)"]
        RawDocs["egp_manual.pdf (543 pages) + 1000 Q&A"]
    end

    UI --> Router
    Router --> ChatAPI & ManualAPI & RagAPI
    ChatAPI --> QR
    QR --> Dense & Sparse & Vision
    Dense & Sparse & Vision --> RRF
    RRF --> Reranker
    Reranker --> ContextBuilder
    ContextBuilder --> GroqText & GroqVision
    GroqText -.->|Failover| GeminiFB
    GeminiFB -.->|Failover| OfflineSyn
    ContextBuilder -.-> SQLite & FAISS & BM25
    ManualAPI --> ChunkImages
    V001 --- FAISS & BM25 & SQLite
    ActivePtr --> V001
```

---

## 2. Core Architectural Layers

### 2.1 Presentation Layer (Frontend)
- **Framework**: React 19 with Vite, Tailwind CSS, and Lucide icons.
- **Q&A Suggestion Deduplication**: `qaQuestionSuggestions.ts` hashes procedural question families using single-escaped normalization, reducing duplicate "Procedure Part 1–N" suggestions into a single representative question per procurement family.
- **Contextual Image Display**: Automatically resolves `/api/manual/chunk/{chunk_id}/image` so that the exact screenshot explaining the retrieved step is rendered inline with statutory citations.

### 2.2 API & Serving Layer (Backend)
- **Framework**: FastAPI (asynchronous ASGI, Python 3.12).
- **Security**: Strict image magic-byte verification (`verify_image_signature`), payload sanitation, and CORS origin controls.
- **Lifespan Management**: `load_rag_service()` loads versioned indexes and models once on startup, persisting memory across requests.

### 2.3 Multi-Channel Retrieval & RAG Pipeline
- **Dense Channel**: FAISS `IndexIDMap2(IndexFlatIP)` with BGE-M3 1024-dimensional normalized vectors.
- **Sparse Channel**: BM25Okapi inverted index covering procurement clauses, statutory rules (e.g. PPR-2008), and specific menu labels.
- **Visual Channel**: SigLIP 768-dimensional visual vectors matching user portal screenshots to manual diagrams.
- **Fusion**: Reciprocal Rank Fusion ($k=60$) combines channel scores without dimension bias.
- **Reranker**: BGE-Reranker-v2-m3 evaluates token interactions between query and fused passages.

### 2.4 Structure-Aware Image Ingestion & Storage
- **Image Extraction**: 1,096 images extracted from the 543-page manual via PyMuPDF C++ bindings.
- **Chunk Alignment**: Each image is bounded and linked to its owning `chunk_id`, `page`, `screen_reference`, and `related_sentence`.
- **Filesystem Convention**: `chunk_{chunk_id}_page_{page}_{order}_{slug}.png`.
- **Data Integrity**: 580 chunks in `chunks.json` and `metadata.db` are explicitly flagged as multimodal with verified screenshots; remaining chunks are cleanly designated as pure text.

### 2.5 Inference & Official Helpdesk Fallback
- **Primary LLM**: Groq-hosted `openai/gpt-oss-20b` (text) and `qwen/qwen3.8-27b` (multimodal vision).
- **Secondary LLM**: Google Gemini (`gemini-flash-latest`) automatic failover.
- **Synthesis Prompting**: Strictly synthesizes retrieved data into structured, professional prose (Markdown tables for fees, numbered lists for procedures, bold values).
- **Helpdesk Escalation**: If no supporting passage is found in manual records, the system politely declines to invent facts and immediately provides official Bangladesh e-GP Helpdesk contact channels (Hotline: `16575`, Phone: `+880 9609112233`, Email: `helpdesk@eprocure.gov.bd`).

---

## 3. Data Flow Comparison: Text Query vs. Vision Query

| Stage | Text Chat Query (`POST /api/chat`) | Screenshot Upload Query (`POST /api/chat/vision`) |
|---|---|---|
| **Input** | String query | Binary image file + optional prompt |
| **Validation** | String sanitation, character bounds | Magic-byte signature verification (PNG/JPEG/WEBP) |
| **Pre-Processing** | Query tokenization & routing | In-memory OCR + SigLIP visual embedding |
| **Retrieval** | Dense FAISS + Sparse BM25 + RRF | Visual SigLIP FAISS + OCR term retrieval |
| **Context** | Top-k chunks + citations + chunk images | Closest manual screen + verified step context |
| **Model** | `openai/gpt-oss-20b` | `qwen/qwen3.8-27b` |
| **Output** | Synthesized steps, tables, chunk screenshot link | Visual diagnostic, highlighted discrepancies, manual page reference |
