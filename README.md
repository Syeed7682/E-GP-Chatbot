# e-GP Manual Assistant

A React and FastAPI application for asking questions about the Bangladesh e-GP Procuring Entity User Manual. The interface supports manual-based question suggestions, screenshot questions, source references, and downloading the full manual PDF.

The application is a project assistant, not an official procurement authority. Answers depend on the indexed manual and configured AI provider; verify decisions against the applicable rules and official guidance.

## What is implemented

- React 19, Vite, Tailwind CSS, and an Express development server.
- FastAPI chat, manual, health, and synchronization endpoints.
- A local 543-page PDF, processed chunks, FAISS index, and metadata.
- Dense retrieval combined with keyword scoring in the active backend chat path. Separate hybrid-retriever and reranker modules exist but are not part of that path.
- Qwen/Qwen2.5-VL-3B-Instruct as the default hosted model; Liquid AI is an optional, explicitly selected alternative.
- Screenshot upload, OCR/vision processing, manual source citations, and page-image rendering.
- Local browser retrieval and IndexedDB storage for offline use. Offline responses may differ from backend responses.
- A searchable suggestion list built from the bundled manual data and a full-manual PDF download link.

See [Project Architecture](documents/PROJECT_ARCHITECTURE.md) for active request paths and known limitations.
For publishing the static frontend on Netlify and connecting a separately hosted FastAPI backend, follow the [Deployment Guide](documents/DEPLOYMENT_GUIDE.md).

## Requirements

- Node.js and npm.
- Python with pip, and the packages in `backend/requirements.txt`.
- The manual PDF and FAISS data files. The PDF is not tracked by Git; place the authorized manual at `data/raw/egp_manual.pdf`.
- An optional Hugging Face token for hosted model inference. Without a configured provider, the backend can use its local/extractive fallback where available.

## Setup

From the project root:

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python -m pip install -r backend/requirements.txt
Set-Location frontend
npm install
```

Set `HF_TOKEN` in the root `.env` to enable hosted Hugging Face inference. Keep credentials server-side; do not put provider tokens in frontend `VITE_*` variables or commit `.env`.

The primary model defaults to `Qwen/Qwen2.5-VL-3B-Instruct`. The optional alternate defaults to `LiquidAI/LFM2.5-VL-1.6B` and is used only when explicitly selected. Backend data paths and model options are documented in [`.env.example`](.env.example) and `backend/app/core/config.py`.

## Run locally

### Windows full stack

Run `run.bat` from the project root and choose the full-stack option. The backend runs at `http://127.0.0.1:8000`; the frontend runs at `http://localhost:3000`.

### Start services separately

Backend, from the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

If using a different Python executable, replace `.\.venv\Scripts\python.exe` with `python`.

Frontend, in a separate terminal:

```powershell
Set-Location frontend
npm run dev
```

The frontend development server proxies `/api` requests to `http://127.0.0.1:8000`. Start FastAPI for backend chat, PDF download, and PDF-rendered manual page images. The frontend also contains local fallback behavior when the backend cannot be reached.

The interactive API reference is available at `http://127.0.0.1:8000/docs`.

## Build and tests

```powershell
Set-Location frontend
npm run build
npm run lint
```

`npm run lint` runs the TypeScript compiler (`tsc --noEmit`). Backend tests use pytest:

```powershell
python -m pytest backend/tests -q
```

The test command requires pytest to be installed in the selected Python environment. Build/test status can change as the project evolves; consult the current command output rather than assuming the checks pass.

## Data and generated files

```text
data/
  raw/egp_manual.pdf             # local source manual; not tracked
  processed/chunks.json          # processed manual text
  faiss_index/index.faiss        # vector index
  faiss_index/metadata.json      # vector-to-chunk metadata
  extracted_images/              # optional extracted page images
frontend/src/data/
  allManualChunks.json           # bundled source for local UI/offline features
```

Current audit counts are documented in [Project Architecture](documents/PROJECT_ARCHITECTURE.md). Verify the PDF, chunks, index, and metadata together before rebuilding or replacing generated data.

## Documentation

- [Project documentation index](documents/INDEX.md)
- [Current architecture and limitations](documents/PROJECT_ARCHITECTURE.md)
- [Implementation plan and validation checklist](documents/PROJECT_PLAN.md)
- [API endpoints and payloads](documents/API_DOCUMENTATION.md)
- [Netlify and backend deployment](documents/DEPLOYMENT_GUIDE.md)
