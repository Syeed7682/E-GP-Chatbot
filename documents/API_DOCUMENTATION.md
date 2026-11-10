# API Documentation

The FastAPI application exposes chat, manual, health, and synchronization routes under `/api`.

- Local base URL: `http://127.0.0.1:8000/api`
- OpenAPI UI: `http://127.0.0.1:8000/docs`
- Implementation: `backend/app/api/`

The React development server on port 3000 proxies `/api` requests to FastAPI. Hosted frontends must be configured to use the deployed backend URL.
Set the backend's `CORS_ORIGINS` environment variable to a comma-separated list of exact frontend origins. The default allows local development origins only.

### `GET /api/health`

Returns general service status, retrieval-index readiness, chunk count, and configured model names.

## Chat

### `POST /api/chat`

Ask a question grounded in the e-GP manual and the supplemental Q&A text, optionally including a screenshot.

Request:

```json
{
  "question": "How do I create an Annual Procurement Plan?",
  "previous_question": null,
  "image_base64": null,
  "image_mime": "image/png",
  "image_name": null,
  "top_k": 5,
  "use_alt_model": false
}
```

`question` is required by the request schema. `previous_question` supports short follow-ups such as asking for steps. An image may be supplied in `image_base64` or the compatibility field `image`. `top_k` is between 1 and 20. `use_alt_model` selects the optional Liquid AI model; otherwise Qwen is used.

Successful responses contain `question`, `answer`, `sources`, `portal_screens`, `model_used`, and `was_offline`. Each source may include `source`, `source_files`, `page`, `chunk_id`, `score`, `snippet`, `screen_reference`, `image_path`, `source_type`, `module`, and `question_number`. Manual sources have a PDF page. Q&A sources identify their module and question number and have no PDF page. When a Q&A entry clearly matches the question, `answer` is returned verbatim from that entry. In the FastAPI chat route, `was_offline` is false; local fallback is handled by the frontend/Express paths.

### `GET /api/chat/health`

Returns whether the FAISS retrieval index is loaded, its available metadata count, model names, and whether a Hugging Face token is configured. This does not guarantee that the hosted provider is currently reachable.

### `GET /api/chat/chunks?limit=10`

Returns a preview of indexed metadata. `limit` is between 1 and 50.

## Manual

### `GET /api/manual/page/{page_num}`

Returns page metadata and chunks for a page from 1 to 543, plus whether an image can be served and its URL.

### `GET /api/manual/page/{page_num}/image`

Serves an extracted page image when one is available. Otherwise, renders that page from the local source PDF as PNG. PDF rendering requires the source file and PyMuPDF.

### `GET /api/manual/download`

Downloads the complete source PDF as an attachment. FastAPI looks in `data/raw/` for the supported manual filenames. Returns `404` when the PDF is unavailable.

### `GET /api/manual/search?q={query}&limit=10`

Performs case-insensitive substring matching against chunk titles and text. `q` must contain at least two characters. This is a simple keyword search, not semantic retrieval.

## Synchronization

### `GET /api/sync/version`

Returns the server dataset version, a hash, metadata count, and timestamp.

### `GET /api/sync/chunks`

Returns all currently loaded chunk metadata for client caching.

### `POST /api/sync/push`

Accepts client mutation records and returns their IDs as processed. The current FastAPI implementation does not persist these records or perform durable conflict resolution; do not treat the success response as an audit-log guarantee.

## Errors and operational notes

- Invalid manual page numbers return `404`.
- The PDF download endpoint returns `404` if no supported source PDF is present.
- Model/provider and vector-index readiness are separate concerns. Check provider configuration and server logs when a chat request fails despite a loaded index.
- Keep Hugging Face and other provider credentials on the server in the root `.env`; never expose them in client-side environment variables.
