# Deployment Guide

## Deployment layout

Deploy the Vite frontend as a static site on Netlify. Deploy FastAPI separately: Netlify's static build does not run `frontend/server.ts`, host the FAISS index as a query service, or provide the local source PDF.

The frontend can use bundled manual data for local fallback, but hosted model answers, server retrieval, full-PDF download, and PDF-rendered page images require the FastAPI backend and its data files to be available.

## Prepare the backend

Deploy the repository's `backend/` application to a Python service that can access:

- `data/faiss_index/index.faiss`
- `data/faiss_index/metadata.json`
- `data/raw/e-GP System Q&A.txt` and, if available, `data/raw/e-GP System Q&A .docx` for supplemental question-and-answer retrieval.
- The official manual PDF under `data/raw/` if PDF download or PDF-rendered page images are required.
- Any extracted page images used by the manual viewer.

The PDF and some data files are not tracked by Git. Ensure they are present in the backend deployment artifact or mounted from approved persistent storage. The current backend uses local filesystem paths; ephemeral storage must be restored on each deploy/start or replaced with persistent storage.

Install `backend/requirements.txt`. Configure the host to start FastAPI on its provided port, for example:

```sh
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port "${PORT:-8000}"
```

Set these backend environment variables in the backend host's secret/configuration settings:

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | Required for hosted E1/E2 answer generation; add the secret in the backend host's environment settings |
| `GROQ_TEXT_MODEL` | E1 text model; defaults to `openai/gpt-oss-20b` |
| `GROQ_VISION_MODEL` | E2 vision model and E1 image-question model; defaults to `qwen/qwen3.8-27b` |
| `HF_TOKEN` | Optional Hugging Face token for embedding generation; not used for answer generation |
| `LOCAL_LLM_MODEL` | Optional local Transformers model name; used only when `USE_LOCAL_LLM=true` |
| `GEMINI_API_KEY` | Optional fallback for text and screenshot answers if Groq inference fails |
| `GEMINI_MODEL` | Optional Gemini model name; defaults to `gemini-flash-latest` |
| `CORS_ORIGINS` | Comma-separated exact Netlify production and custom-domain origins, e.g. `https://example.netlify.app,https://assistant.example.org` |
| `DATA_RAW_DIR` | Directory containing the manual PDF; defaults to `data/raw` relative to the project root |
| `QA_DATA_PATH` | Supplemental Q&A text path; defaults to `data/raw/e-GP System Q&A.txt` |
| `QA_DOCX_PATH` | Optional Word copy of the supplemental Q&A; defaults to `data/raw/e-GP System Q&A .docx` |
| `FAISS_INDEX_PATH` | FAISS index path; defaults to `data/faiss_index/index.faiss` |
| `FAISS_METADATA_PATH` | FAISS metadata path; defaults to `data/faiss_index/metadata.json` |

Keep all AI tokens on the backend. Do not configure provider credentials as `VITE_*` variables.

E1 uses the configured Groq text model for text questions and the Groq vision model when a screenshot is attached. E2 always uses the Groq vision model. If Groq inference fails and `GEMINI_API_KEY` is configured, Gemini is tried as a fallback; otherwise, the backend uses manual-grounded offline synthesis. The `/api/chat/health` and `/api/health` endpoints report whether Groq is configured and the active default model names. Set `GROQ_API_KEY` in Render's backend environment variables and redeploy; setting it in Netlify or a local `.env` does not configure Render.

Hugging Face embedding-provider access is separate from answer-model credentials; without embedding access, retrieval switches to keyword-only mode.

The Q&A text and optional Word copy are parsed into numbered question/answer records at backend startup, deduplicated by question number and question text, and indexed as sparse TF-IDF vectors with term postings. If both files contain the same records, the text-file wording is retained and both filenames are recorded. The PDF continues to use its existing FAISS vector index. A clear Q&A match returns its answer verbatim; citations identify its module and question number, not a PDF page. Include the source files in the backend deployment artifact or configure the paths above.

Before connecting Netlify, verify:

- `GET https://<backend-host>/api/health` reports the retrieval index ready.
- `GET https://<backend-host>/api/manual/download` downloads the PDF if the file is configured.
- The backend allows the exact public Netlify origin in `CORS_ORIGINS`.

## Deploy the frontend to Netlify

1. Push the repository to the Git provider connected to Netlify. Keep `.env`, tokens, and private data out of Git.
2. Create a Netlify site from the repository. The root `netlify.toml` configures the `frontend` base directory, `npm run build`, `dist` publish directory, Node.js 22, and SPA fallback to `index.html`.
3. In **Site configuration → Environment variables**, add:

   ```text
   VITE_API_BASE_URL=https://<backend-host>
   ```

   Use the backend origin only, without a trailing slash and without `/api`. This value is public and embedded in the frontend bundle; never put secrets in it.
4. Trigger a new deploy. Vite reads `VITE_API_BASE_URL` at build time, so changing it requires a new build/deploy.
5. Add the final Netlify site URL and any custom domain to backend `CORS_ORIGINS`, then restart/redeploy the backend if needed.
6. Test the live site:
   - Ask a manual question and confirm a grounded backend response.
   - Confirm references and manual page images load.
   - Confirm **Download Full Manual** downloads a PDF.
   - Upload an image and verify the backend/model behavior.
   - Check the browser console and network panel for CORS or failed API requests.

API requests go directly from the browser to the configured FastAPI origin; they are not proxied through Netlify. Deploy previews have distinct origins. Add preview origins to `CORS_ORIGINS` only if they need backend access, using an intentional controlled list.

## Operational checks and limitations

- FastAPI `/docs` is useful for diagnostics but should be restricted or disabled if required by the deployment.
- During local development, the frontend can fall back to local retrieval if the backend is unavailable. This does not provide hosted model inference or server-only PDF functions.
- In production, chat requests fail visibly instead of silently returning a lower-quality offline answer when the API is missing or unreachable.
- Re-run `npm run build` and the backend test suite before release. A successful static build does not test backend model credentials, data availability, CORS, or provider availability.