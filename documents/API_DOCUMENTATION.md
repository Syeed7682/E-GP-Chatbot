# API Documentation

The Bangladesh e-GP Manual Assistant backend is powered by FastAPI. All endpoints return JSON or binary image streams and are documented interactively in OpenAPI / Swagger UI at `http://127.0.0.1:8000/docs`.

---

## 1. Service Configuration

- **Base URL (Local)**: `http://127.0.0.1:8000`
- **CORS**: Configured via `CORS_ORIGINS` (defaults to `http://localhost:3000,http://127.0.0.1:3000`).
- **Interactive Docs**: `http://127.0.0.1:8000/docs` (Swagger) and `http://127.0.0.1:8000/redoc` (ReDoc).

---

## 2. Health & Diagnostic Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Core system health, service name, and version (`2.0.0`). |
| `GET` | `/api/health` | Service health, vector index readiness, and active text/vision models. |
| `GET` | `/api/chat/health` | Chat subsystem health check. |
| `GET` | `/api/rag/status` | Active index version (`v001`), total indexed vectors, and RAG status. |
| `POST` | `/api/admin/index/validate` | Validates active index files, SQLite schema, and query retrieval integrity. |

---

## 3. Chat & Vision Endpoints

### 3.1 `POST /api/chat`
Standard conversation endpoint for text queries and optional base64 screenshots.

**Request Payload:**
```json
{
  "question": "How do I create a tender in e-GP?",
  "previous_question": null,
  "image_base64": null,
  "image_mime": "image/png",
  "top_k": 5,
  "use_alt_model": false
}
```

**Parameters:**
- `question` *(string, required)*: User query text.
- `previous_question` *(string, optional)*: Previous query for multi-turn topic continuity.
- `image_base64` *(string, optional)*: Base64-encoded image string for screenshot queries.
- `image_mime` *(string, optional)*: MIME type (`image/png`, `image/jpeg`). Default: `image/png`.
- `top_k` *(int, optional)*: Number of source chunks to retrieve (1–20, default 5).
- `use_alt_model` *(bool, optional)*: Forces multimodal model (`qwen/qwen3.8-27b`) for inference.

**Response (JSON):**
```json
{
  "question": "How do I create a tender in e-GP?",
  "answer": "Here is the official procedure for a Procuring Entity (PE) to create and place a new tender...\n\n1. Navigate to Tender >> Create Tender...\n2. Search and select approved APP package...",
  "sources": [
    {
      "source": "e-GP System User Manual - Procuring Entity User 1 February 2026.pdf",
      "page": 54,
      "chunk_id": 145,
      "score": 0.88,
      "snippet": "published on e-GP Portal). (As shown in Screen – D1)...",
      "screen_reference": "Screen – D1",
      "image_path": "/api/manual/chunk/145/image",
      "related_sentence": "(As shown in Screen – D1) Screen – D1 4.1.2 “Steps for tender Preparation” button...",
      "source_type": "manual",
      "source_files": [],
      "question_number": null,
      "module": null
    }
  ],
  "portal_screens": ["Screen – D1"],
  "model_used": "openai/gpt-oss-20b (e-GP Grounded)",
  "was_offline": false
}
```

---

### 3.2 `POST /api/chat/vision`
Dedicated multipart file upload endpoint for portal screenshot diagnostics.

**Request:** `multipart/form-data`
- `file`: Binary image file (`PNG`, `JPEG`, `WEBP`, max 10MB).
- `question` *(optional text field)*: Question or diagnostic instructions. Defaults to `"Analyze this portal screenshot against the e-GP manual."`.

**Features:**
- Verifies image magic-byte signatures (prevents arbitrary file uploads).
- Runs OCR and dense visual feature matching against manual screenshots.
- Returns grounded analysis, matching manual steps, and citation links.

---

### 3.3 `GET /api/chat/questions`
Returns all 1,000 supplemental Q&A question suggestions categorized by procurement module.

**Response (JSON):**
```json
{
  "total": 1000,
  "questions": [
    {
      "question_number": 1,
      "module": "Portal Access, Account Registration, NID & OTP Security Controls",
      "question": "How to Verify National ID (NID) for PE and Vendor User Accounts?"
    }
  ]
}
```

---

## 4. Manual Viewing & Chunk Image Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/manual/page/{page_num}` | Page metadata, chunk list, and rendered image link for a manual page (1–543). |
| `GET` | `/api/manual/page/{page_num}/image` | Serves high-resolution page render (cached or on-the-fly via PyMuPDF). |
| `GET` | `/api/manual/chunk/{chunk_id}/image` | **Serves the exact cropped diagram or portal screenshot mapped to this chunk.** |
| `GET` | `/api/manual/images/{filename}` | Serves any extracted image asset directly by filename from `data/extracted_images/chunks/`. |
| `GET` | `/api/manual/download` | Streams the complete official 543-page PDF (`egp_manual.pdf`). |
| `GET` | `/api/manual/search?q={query}&limit=10` | Non-semantic substring search across manual chunk text. |

---

## 5. Offline Cache & Synchronization Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/sync/version` | Returns active index version hash and total chunk count for client-side cache invalidation. |
| `GET` | `/api/sync/chunks` | Returns full metadata array for all 1,188 chunks for IndexedDB offline storage. |
| `POST` | `/api/sync/push` | Accepts client mutation audit events. |

---

## 6. Official Helpdesk Fallback Information

When a user query cannot be answered from the official manual passages or supplemental Q&A records, the system responds with a clear statement and provides the **official Bangladesh e-GP Helpdesk contact channels**:

- 📞 **e-GP Helpdesk Hotline:** `16575` *(from any mobile network in Bangladesh)*
- ☎️ **Telephone Support:** `+880 9609112233` / `+880 1762625528–31`
- ✉️ **Email Support:** `helpdesk@eprocure.gov.bd` / `e-gphelpdesk@cptu.gov.bd`
- 🌐 **Official Portal:** [eprocure.gov.bd](https://www.eprocure.gov.bd)
- 🏢 **Authority:** Bangladesh Public Procurement Authority (BPPA) / CPTU, IMED, Ministry of Planning
