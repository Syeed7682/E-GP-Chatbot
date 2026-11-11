# Project Architecture

This document describes the high‑level architecture of the **e‑GP Manual Assistant** as it stands today (November 2026).

## 1. Overview
- **Frontend** – Vite + React 19 UI, deployed as a static site (Netlify). It talks to the FastAPI backend via the `/api` namespace.
- **Backend** – FastAPI serving:
  - **Hybrid Retrieval** – FAISS dense vectors (BGE‑M3) + BM25 keyword search.
  - **Multimodal LLM** – Qwen 2.5‑VL‑3B‑Instruct loaded locally when a GPU is available (`USE_LOCAL_LLM=true`). When not available the system falls back to Groq hosted models (`GROQ_TEXT_MODEL` / `GROQ_VISION_MODEL`) and finally to a deterministic offline synthesiser.
  - **Vision & OCR** – When an image is supplied, the backend runs Tesseract OCR (in‑memory) and passes the extracted text to the retrieval pipeline. If the model supports vision, the image is also sent to the vision model.
  - **Citation Service** – Maps FAISS IDs back to PDF page numbers and optional screenshot URLs.
- **Data Layer** – `data/` folder containing the raw PDF, processed JSON chunks, and the FAISS index.

## 2. Data Flow (RAG)
```mermaid
flowchart TD
    A[User UI] -->|question / optional image| B[FastAPI /chat]
    B -->|OCR (if image)| C[Vision Service]
    C --> D[Retrieval Service]
    D -->|FAISS vectors| E[FAISS Index]
    D -->|BM25 keywords| F[BM25 Retriever]
    E & F -->|score fusion| G[Hybrid Retriever]
    G -->|top‑k chunks| H[LLM Service]
    H -->|prompt + context| I[Qwen 2.5‑VL‑3B‑Instruct]
    I -->|answer with citations| J[FastAPI response]
    J --> A
```

## 3. Model Selection Logic
- **Text‑only query** – Use local Qwen if `USE_LOCAL_LLM=true`; otherwise Groq text model.
- **Image present** – Always route to the vision model (`GROQ_VISION_MODEL` or local Qwen). The UI toggle `use_alt_model` forces the vision model even for text‑only queries.
- **Fallback** – If all remote providers fail, the offline synthesiser produces a deterministic answer based on the retrieved chunks.

## 4. Deployment Units
| Component | Deployable unit |
|-----------|-----------------|
| Frontend  | Netlify static site |
| Backend   | Python service (Docker, Render, Fly.io, etc.) |
| Data      | Mounted volume or persistent storage containing `data/` |

