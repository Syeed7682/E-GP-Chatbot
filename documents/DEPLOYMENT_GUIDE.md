# Deployment Guide

## Deployment layout

Deploy the Vite frontend as a static site on Netlify. Deploy FastAPI separately: Netlify's static build does not run `frontend/server.ts`, host the FAISS index as a query service, or provide the local source PDF.

The frontend can use bundled manual data for local fallback, but hosted model answers, server retrieval, full-PDF download, and PDF-rendered page images require the FastAPI backend and its data files to be available.

## Prepare the backend

Deploy the repository's `backend/` application to a Python service that can access:

- `data/faiss_index/index.faiss`
- `data/faiss_index/metadata.json`
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
| `HF_TOKEN` | Hugging Face token, if hosted model inference is required |
| `LLM_MODEL` | `Qwen/Qwen2.5-VL-3B-Instruct` |
| `ALT_VL_MODEL` | `LiquidAI/LFM2.5-VL-1.6B` (optional alternative) |
| `CORS_ORIGINS` | Comma-separated exact Netlify production and custom-domain origins, e.g. `https://example.netlify.app,https://assistant.example.org` |
| `DATA_RAW_DIR` | Directory containing the manual PDF; defaults to `data/raw` relative to the project root |
| `FAISS_INDEX_PATH` | FAISS index path; defaults to `data/faiss_index/index.faiss` |
| `FAISS_METADATA_PATH` | FAISS metadata path; defaults to `data/faiss_index/metadata.json` |

Keep all AI tokens on the backend. Do not configure provider credentials as `VITE_*` variables.

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