# API Documentation

The FastAPI backend exposes a small set of routes under `/api` that power the e‑GP Manual Assistant. All endpoints return JSON and are documented in the OpenAPI UI at `http://127.0.0.1:8000/docs`.

## Common configuration
- **Base URL (local)**: `http://127.0.0.1:8000/api`
- **CORS**: Controlled via the `CORS_ORIGINS` environment variable. By default only `http://localhost:3000` (Vite dev) is allowed.

## Health & status
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Returns overall service health, index readiness, and the names of the active text and vision models. |
| `GET` | `/api/chat/health` | Same as above but names the endpoint used by the chat UI. |

## Chat
### `POST /api/chat`
Accepts a question (or screenshot) and returns a grounded answer.
```json
{
  "question": "How do I create an Annual Procurement Plan?",
  "previous_question": null,
  "image_base64": null,
  "image_mime": "image/png",
  "top_k": 5,
  "use_alt_model": false
}
```
- **`question`** – mandatory text query.
- **`previous_question`** – optional short follow‑up (used for step‑by‑step clarification).
- **`image_base64` / `image`** – optional screenshot for OCR / vision processing.
- **`top_k`** – number of retrieved chunks (1‑20).
- **`use_alt_model`** – when `true` forces the vision model (`Qwen/Qwen2.5‑VL‑3B‑Instruct`) even for text‑only queries.

**Response** (JSON):
```json
{
  "question": "How do I create an Annual Procurement Plan?",
  "answer": "... grounded answer with citations ...",
  "sources": [
    {
      "source": "e‑GP System Manual",
      "page": 34,
      "chunk_id": 12,
      "score": 0.92,
      "snippet": "...",
      "screen_reference": "Screen A2",
      "image_path": "https://…/page34.png",
      "source_type": "manual",
      "source_files": [],
      "question_number": null,
      "module": null
    }
  ],
  "portal_screens": ["Screen A2"],
  "model_used": "Qwen/Qwen2.5‑VL‑3B‑Instruct (e‑GP Grounded)",
  "was_offline": false
}
```
- `model_used` reflects the actual model that generated the answer (text‑only, vision, Gemini fallback or offline synthesis).
- `was_offline` is `true` only when the answer came from the deterministic offline synthesizer.

## Manual handling
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/manual/page/{page_num}` | Returns page metadata, the list of chunks belonging to that page, and a URL for the rendered PNG image (generated on‑the‑fly if a pre‑extracted image is missing). |
| `GET` | `/api/manual/page/{page_num}/image` | Serves a pre‑extracted page image, falling back to on‑the‑fly rendering via PyMuPDF. |
| `GET` | `/api/manual/download` | Streams the original 543‑page PDF. |
| `GET` | `/api/manual/search?q={query}&limit=10` | Simple case‑insensitive substring search over chunk titles and text (non‑semantic). |

## Synchronisation (client cache)
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/sync/version` | Returns a hash, timestamp and total chunk count – useful for client‑side cache invalidation. |
| `GET` | `/api/sync/chunks` | Returns the full metadata list for all chunks (used by the offline IndexedDB cache). |
| `POST` | `/api/sync/push` | Accepts client‑side mutation records – **note:** the current implementation does not persist these records.

## Errors & operational notes
- 404 for invalid manual page numbers or missing PDF.
- 400 for malformed request bodies (e.g., missing `question`).
- Model‑provider errors are surfaced as a generic 500 with a short message; the UI falls back to the offline synthesizer when this occurs.
- Keep all provider tokens (`GROQ_API_KEY`, `HF_TOKEN`, `GEMINI_API_KEY`) in the backend `.env`; never expose them via `VITE_*` variables.
