# e-GP Manual Assistant — Current Architecture

This document records the implementation found during the 2026-11-08 project audit. It describes current code paths, not the desired final-state pipeline. See [PROJECT_PLAN.md](./PROJECT_PLAN.md) for milestones and acceptance criteria.

## System overview

```text
React 19 / Vite UI
  ├─ Express server.ts (development/full-stack API and local fallback)
  ├─ FastAPI chat proxy when the backend is reachable
  ├─ screenshot input, browser OCR, and manual citations
  └─ local retrieval from bundled/IndexedDB chunks when offline

FastAPI
  ├─ POST /api/chat
  │    ├─ optional backend OCR for uploaded images
  │    ├─ retrieval_service: PDF FAISS + weighted keyword fusion, plus supplemental Q&A text search
  │    ├─ LLM service: HF/local/offline fallback
  │    └─ manual-page or Q&A module/question citations
  ├─ /api/manual/*: page chunks, page image, keyword search, PDF download
  └─ /api/sync/*: client chunk sync and mutation endpoints

Local corpus
  PDF (543 pages) -> existing processed chunks (1,188)
                   -> FAISS IndexFlatIP (1,188 x 1,024)
                   -> metadata.json (1,188 records)
                   -> frontend bundled chunks (1,170 records)

  data/raw/e-GP System Q&A.txt + optional .docx copy (1,000 numbered entries)
                   -> startup parser, deduplication, and sparse TF-IDF vector index
                   -> verbatim answer for a confident question match
```

## Application surfaces

### Frontend

- `frontend/src/App.tsx` and `frontend/src/components/` implement the chat UI, screenshot selection, previews, page/source citation display, and manual page viewer.
- `GovtOfficialSidebar.tsx` builds manual-based questions from meaningful section titles and key terms in the bundled corpus, filters suggestions as the user types, and links to the full-PDF download endpoint. Partial words and small spelling errors are supported; the suggestion count changes when the bundled data changes.
- `frontend/src/services/api.ts` sends chat requests to `/api/chat`, checks backend health, and falls back to IndexedDB/local retrieval when the request fails.
- `frontend/server.ts` runs an Express/Vite server. It first proxies chat to FastAPI when reachable; otherwise, it performs local retrieval and can call configured cloud providers.
- `frontend/src/data/allManualChunks.json` contains 1,170 records. `frontend/src/data/manualChunks.ts` combines bundled records with curated records for frontend features. Check `INITIAL_MANUAL_CHUNKS` directly rather than inferring its count from the JSON file.

### FastAPI backend

- `backend/app/main.py` registers chat, health, manual, and sync routers under `/api`.
- `backend/app/api/chat.py` is the active backend chat entry point. It sanitizes question/image input, runs optional OCR, calls `retrieval_service.retrieve`, returns confident supplemental Q&A answers verbatim, otherwise invokes the LLM service, and returns source citations.
- `backend/app/services/retrieval_service.py` searches the supplemental Q&A text separately from the PDF index, embeds a query when the semantic provider is available, retrieves dense FAISS candidates, ranks PDF keywords with domain expansions, and combines PDF scores using a weighted sum. It excludes pages 1–5 from dense results.
- `backend/app/services/qa_service.py` parses numbered `Question`/`Q:` blocks from the text and optional Word sources, deduplicates matching entries, and builds sparse TF-IDF vectors plus inverted term postings at startup. Q&A references use module and question number, never a fabricated PDF page. These text vectors are separate from the existing PDF FAISS index.
- `backend/app/services/hybrid_retriever.py` and `reranker.py` implement a separate retriever/reranker path; the active chat route does not call these services. RRF and a BGE reranker are not currently verified in the request path.
- `backend/app/services/llm_service.py` uses Qwen2.5-VL-3B-Instruct by default, optionally uses Liquid AI when explicitly selected, and falls back to offline extractive synthesis. `vision_service.py` uses available OCR libraries; image data is also sent to the selected vision-language model.
- `backend/app/api/manual.py` serves page chunks, page images, keyword search, and the complete source PDF at `/api/manual/download`. Page images fall back to rendering the local PDF when no extracted image exists. `citation_service.py` maps citation pages to image endpoints.

### Document and vector data

- Local source: `data/raw/egp_manual.pdf` (100,156,678 bytes; 543 pages). The PDF is present in the working tree but is not tracked by Git.
- Processed corpus: `data/processed/chunks.json` (1,188 records; current schema includes `chunk_id`, `source`, `page`, `text`, `image_path`, and `content_type`).
- Vector assets: `data/faiss_index/index.faiss` and `data/faiss_index/metadata.json`. The index contains 1,188 vectors at 1,024 dimensions; metadata has 1,188 records covering every page from 1 through 543.
- Supplemental Q&A sources: `data/raw/e-GP System Q&A.txt` and the optional `data/raw/e-GP System Q&A .docx` contain the same 1,000 numbered entries. The backend merges/deduplicates them and indexes question and answer text as sparse TF-IDF vectors; include the available source files in the backend deployment artifact.
- These checks establish count and page coverage only. They do not prove embedding provenance, normalization, semantic quality, or citation accuracy.
- Image assets exist under `data/extracted_images/`. A previous text scan found 10 image-heavy pages with fewer than 40 extracted characters (96, 98, 100, 102, 107, 108, 130, 365, 467, and 485); those pages remain OCR-review candidates. There is no verified OCR-by-page report or structured table output yet.
- The current backend chunk schema omits `section_title` and `screen_references`; the existing `validate_chunks.py` consequently reports zero screen references. The frontend build script derives headings/screens separately from chunk text.

## Ingestion and retrieval scripts

- `backend/scripts/ingest_documents.py` scans `data/raw/` for PDFs, extracts text with `pypdf`, extracts some embedded images, and chunks text.
- `backend/scripts/ingest_manual.py` uses `pdf_loader.py`, whose default/alternate filenames do not include the current `egp_manual.pdf`; use the scanning ingestion path only after validating it, or fix the path handling before using that script.
- `backend/scripts/build_faiss_index.py` is the script that calls `embed_chunks`, builds the FAISS index, and writes metadata. The other `backend/scripts/build_index.py` path should be checked before use because it calls a different service interface.
- `backend/scripts/validate_chunks.py` reports chunk page coverage and basic term/screen counts, but does not detect low-quality text, OCR gaps, or table integrity.

## Configuration and runtime

- Backend settings are loaded by `backend/app/core/config.py` from root `.env`; data paths default to `data/raw`, `data/processed/chunks.json`, and `data/faiss_index/`.
- Backend CORS origins are controlled by `CORS_ORIGINS`; the default permits local development origins. Netlify production and custom-domain origins must be explicitly configured on the backend.
- The embedding model defaults differ between configuration and the service implementation. Record and validate the model that created the checked-in index before reusing or rebuilding it.
- `.env.example` is a placeholder template. Put active credentials in the ignored root `.env`; never place them in client-side `VITE_*` variables or commit them.
- Check the active Python environment and installed optional packages before running PDF rendering or tests. The backend requirements declare PyMuPDF, but an environment may not have installed every dependency.
- At the 2026-11-08 audit, the frontend production build succeeded with a large-bundle warning; `npm run lint` reported pre-existing TypeScript errors. Re-run checks after code changes for current results.
- `.gitignore` excludes local environment files, frontend dependencies/build output, and Python virtualenv/cache artifacts. Some bytecode files are already tracked and are not removed by ignore rules.

## Known gaps before the target architecture is production-ready

1. Audit the current 1,188 chunks against the PDF, including empty/low-text pages, headings, tables, OCR, and stable IDs.
2. Confirm that excluding the introductory/TOC pages from offline frontend retrieval remains acceptable for the manual viewer and synchronization contract.
3. Confirm embedding model/provider, normalization, and build provenance; evaluate existing retrieval before any index rebuild.
4. Choose one active retrieval path and measure it. Add BM25/RRF/reranking only as validated changes to the path used by `/api/chat`.
5. Test screenshot processing, model/provider support, timeouts, rate limits, invalid files, and insufficient-context abstention.
6. Add reproducible evaluation and deployment documentation.

## API contract pointers

- Chat: `POST /api/chat`; health and chunk diagnostics: `/api/chat/health`, `/api/chat/chunks`.
- Manual viewer/download: `/api/manual/page/{page_num}`, `/api/manual/page/{page_num}/image`, `/api/manual/search`, `/api/manual/download`.
- Offline synchronization: `/api/sync/*`.
- Interactive API specification: FastAPI `/docs` when the backend is running.
- Netlify deployment steps and external backend requirements: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md).
