# e-GP Manual Assistant API Documentation

## Overview
The e-GP Official Manual Assistant REST API provides endpoints for multimodal Retrieval-Augmented Generation (RAG), statutory manual page browsing, portal screenshot diagnostics, and offline dataset synchronization.

- **Base URL:** `http://127.0.0.1:8000/api`
- **Specification:** OpenAPI 3.0 / Swagger UI at `http://127.0.0.1:8000/docs`
- **Grounding Corpus:** Official 543-page Bangladesh e-GP Procuring Entity User Manual (PPA 2006 / PPR 2008).

---

## 1. Chat Endpoints (`/api/chat`)

### `POST /api/chat`
Submits a user query and/or portal screenshot for grounded RAG analysis.

#### Request Body
```json
{
  "question": "what is debarment?",
  "image_base64": null,
  "top_k": 5
}
```

#### Response (200 OK)
```json
{
  "question": "what is debarment?",
  "answer": "Under Public Procurement Rules (PPR-2008 Rule 127) and Chapter 7 of the official e-GP manual...",
  "sources": [
    {
      "source": "Official e-GP Procuring Entity Manual",
      "page": 344,
      "chunk_id": 791,
      "score": 0.98,
      "snippet": "7.1.9 After approving the debarment by HOPE , the debarment details will be...",
      "screen_reference": "Screen - DEB-01",
      "image_path": "/api/manual/page/344/image"
    }
  ],
  "portal_screens": ["Screen - DEB-01", "Screen - DEB-02"],
  "model_used": "Qwen2.5-72B-Instruct (Grounded)",
  "was_offline": false
}
```

### `GET /api/chat/health`
Probes the health of the LLM pipeline and FAISS index.

#### Response (200 OK)
```json
{
  "status": "healthy",
  "system": "e-GP Official Manual Assistant",
  "index_loaded": true,
  "total_chunks": 1188,
  "llm_model": "Qwen/Qwen2.5-72B-Instruct",
  "embedding_model": "BAAI/bge-m3",
  "hf_configured": true,
  "gemini_configured": false
}
```

---

## 2. Manual Endpoints (`/api/manual`)

### `GET /api/manual/page/{page_num}`
Returns chunks and metadata for a specific page (1 to 543).

### `GET /api/manual/page/{page_num}/image`
Serves the rendered JPEG page screenshot for visual reference.

### `GET /api/manual/search?q={query}&limit=10`
Performs rapid keyword search across all indexed chunks.

---

## 3. Synchronization Endpoints (`/api/sync`)

### `GET /api/sync/version`
Returns the current server manual version, chunk count, and dataset hash for client cache invalidation.

### `GET /api/sync/chunks`
Downloads full verified procedural manual chunks for local browser IndexedDB caching.

### `POST /api/sync/push`
Reconciles client offline mutations and audit logs.

---

## 4. Run Scripts
- **Windows (Full Stack):** Double-click `run.bat`
- **Linux / Mac:** Run `./run.sh`
- **Backend Only:** `uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` (from `backend/`)
- **Frontend Only:** `npm run dev` (from `frontend/`)

