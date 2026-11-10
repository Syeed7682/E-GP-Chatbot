# e-GP Manual Assistant: Implementation Plan

## Objective

Deliver a reliable assistant grounded in the official 543-page Bangladesh e-GP Procuring Entity User Manual. It should answer text questions, explain user-provided portal screenshots, and provide verifiable manual-page citations.

## Current audit snapshot (2026-11-08)

- The working tree contains a React 19/Vite/Express frontend and a FastAPI backend. The frontend proxies chat to FastAPI when available and has an offline local-search fallback.
- The current local PDF at `data/raw/egp_manual.pdf` has **543 pages**.
- `data/processed/chunks.json` and `data/faiss_index/metadata.json` each contain **1,188 records**. The FAISS index has **1,188 vectors at 1,024 dimensions**; metadata covers all 543 page numbers. This confirms count/alignment, not embedding quality or retrieval accuracy.
- The browser bundle `frontend/src/data/allManualChunks.json` contains **1,170 records**. Its 18 omitted IDs are `0`–`17`, the introductory/TOC chunks from pages 1–5; the bundle-generation script intentionally filters these pages, matching the backend's procedural retrieval exclusion.
- A source-text scan found 10 image-heavy pages with fewer than 40 extracted characters (96, 98, 100, 102, 107, 108, 130, 365, 467, and 485). These are OCR-review candidates, not yet individually OCR-verified.
- Existing backend retrieval uses a dense search plus weighted keyword fusion. A separate hybrid retriever and reranker also exist, but the chat route currently uses `retrieval_service`; RRF and the reranker are not established as part of the active chat path.
- Screenshot upload, browser-side OCR, backend OCR, a vision-model path, manual page image endpoints, and clickable source citations are present. Their end-to-end accuracy, upload limits, timeout behavior, and error handling still need verification.
- The ingestion code has PDF text extraction and chunking, but no verified OCR pass or structured table extraction. `PDFLoader` does not recognize the current `egp_manual.pdf` filename; the separate document-loader ingestion path does scan PDFs in `data/raw/`.
- The existing index dimensions/count are verified, but its exact embedding-model provenance and vector quality are not. Do not overwrite or rebuild it before a retrieval evaluation.
- The API configuration and `.env.example` use different embedding-model names. The checked-in `.env.example` previously contained a credential; its value has been removed. Revoke/rotate that credential because deleting it from the current file does not erase Git history.
- E1/E2 answer generation uses Groq models: `openai/gpt-oss-20b` for text and `qwen/qwen3.8-27b` for vision. Hosted inference requires `GROQ_API_KEY` in the backend deployment environment; Gemini is an optional fallback.
- The sidebar now has searchable manual-derived question suggestions and a link to download the full source PDF. The download requires the PDF in `data/raw/` and the FastAPI backend to be running.
- README, architecture, plan, and API documentation describe the current implementation; ingestion, evaluation, and deployment documentation remain open work.
- Root `.gitignore` now excludes local virtual environments and Python caches. Some cache files are already tracked; ignore rules do not untrack them.
- `data/raw/egp_manual.pdf` is present locally but is not tracked by Git. Keep the official PDF local or distribute it through an approved artifact location; do not commit credentials or large source PDFs by accident.
- Environment and validation results vary by Python installation. The earlier audit used Python 3.14.6; the `python` command in the latest check used Python 3.12 and did not have pytest installed. An earlier backend run passed 11 tests, but that result predates later changes. The frontend build has passed, while `npm run lint` reports existing TypeScript errors. Repeat checks with the intended environment before release.

## Phases and acceptance criteria

### Phase 1 — Audit and environment

Status: **Audit completed; environment/security follow-ups remain.**

- [x] Map frontend, backend, API routes, and ingestion/retrieval entry points.
- [x] Verify local PDF page count and FAISS vector/metadata counts and dimensions.
- [x] Identify the frontend/backend chunk-count discrepancy and stale documentation.
- [x] Remove the credential from `.env.example` and add local Python artifacts to `.gitignore`.
- [ ] Revoke/rotate the exposed credential and confirm all required secrets are supplied locally through `.env`.
- [x] Run an initial offline backend test suite (11 passed at the earlier audit) and build the frontend production bundle.
- [ ] Resolve the current frontend TypeScript errors; `npm run lint` is not clean.
- [ ] Decide where the large official PDF is to be stored/distributed.

### Phase 2 — PDF extraction and preprocessing

Status: **Existing 543-page coverage found; page-quality review remains.**

- Audit the 543-page source against extracted page records before regenerating anything. Existing chunks cover all 543 pages and have no empty text records.
- OCR-review the 10 low-text/image-heavy candidates; retain source images and page numbering.
- Account for every page, flag empty/low-text pages, then OCR only pages needing it.
- Preserve printed/PDF page numbering and identify repeated headers/footers.
- Extract tables as structured row/column data where feasible; retain a page-linked text fallback.
- Record extraction status, OCR status, and errors per page.

Acceptance: every PDF page has a traceable extraction record; OCR/table exceptions are explicit and reviewable.

### Phase 3 — Structure-aware chunks

Status: **Existing 1,188 chunks need schema/quality validation.**

- Normalize the chunk schema and stable IDs (including source, page, section, subsection, text, and image/table references).
- Prefer section-aware boundaries; preserve procedural steps and table context.
- Verify that excluding the 18 introductory/TOC chunks (IDs 0–17, pages 1–5) from the browser bundle is intentional and safe for offline/manual-viewer behavior.
- Add section and screen metadata where derivable; the current backend chunk schema does not include `section_title` or `screen_references`.
- Produce a chunking report with page coverage, sizes, overlap, and exceptional pages.

Acceptance: stable IDs, full page coverage, consistent schemas, and manually reviewed procedural/table edge cases.

### Phase 4 — Embeddings and FAISS

Status: **Index exists; provenance and retrieval behavior are unverified.**

- Fix and document one embedding model/provider configuration before building.
- Generate normalized embeddings in batches (use Colab GPU if local memory is insufficient).
- Persist index metadata/config including model, dimension, normalization, corpus hash, and build time.
- Validate index vector count, dimension, metadata order, and reload behavior.

Acceptance: vectors and metadata match exactly; rebuilds are reproducible; known queries return expected pages.

### Phase 5 — Hybrid retrieval and reranking

Status: **Basic weighted dense/keyword retrieval is active; login-query noise is fixed and covered by regression tests.**

- Measure a baseline before further changing ranking.
- [x] Constrain general login-procedure retrieval to relevant login pages and avoid duplicate-page citations.
- Add BM25 and Reciprocal Rank Fusion (RRF) if evaluation supports it.
- Integrate a reranker in the active chat path, not only as an unused service.
- Preserve exact identifiers and terms; exclude cover/TOC pages only when justified by the manual.

Acceptance: a versioned test set reports Recall@5/10, MRR, and citation-page accuracy, including exact IDs, menus, dates, methods, and procedure names.

### Phase 6 — Hosted multimodal model

Status: **Groq E1/E2 routing is implemented; hosted credentials must be configured and verified on the deployment.**

- [x] Route E1 text requests through Groq `openai/gpt-oss-20b` and E2/screenshot requests through `qwen/qwen3.8-27b`.
- [x] Include screenshot image payloads and MIME types in Groq chat requests.
- [x] Keep provider credentials in backend secret settings and report Groq readiness through health endpoints.
- [x] Use Gemini as an optional fallback, followed by grounded offline synthesis.
- Pass the question, screenshot, OCR text, and retrieved manual context with clear trust boundaries.
- Validate hosted inference, rate limits, invalid-image handling, and provider availability after deploying the configured key.
- Require the assistant to distinguish screenshot observations from manual-backed rules and abstain when context is insufficient.

Acceptance: text-only, correct screenshot, unrelated screenshot, malformed image, missing context, provider failure, and rate-limit cases behave as expected.

### Phase 7 — Frontend

Status: **Upload, preview, offline fallback, source citations, searchable manual suggestions, and the PDF download link exist; end-to-end verification is pending.**

- Verify image type/size validation, preview/removal, and API error/loading behavior.
- Ensure citation pages open the matching PDF/manual page and source snippets remain visible.
- Reconcile the 1,170 browser chunks with the 1,188 backend chunks.
- Keep cloud-provider secrets on the server; do not expose them in Vite/client variables.

Acceptance: screenshot and text journeys work on the online backend and offline fallback, with accurate and clickable citations.

### Phase 8 — Evaluation, deployment, and documentation

Status: **Current implementation documentation is available; evaluation and deployment are not validated.**

- Build a 30–50 question gold dataset with expected pages and screenshot scenarios.
- Report retrieval and citation metrics; record known limitations.
- Validate API failures, invalid uploads, and production CORS/configuration.
- Document ingestion, index building, model setup, API, evaluation, and deployment.

Acceptance: reproducible evaluation and deployment instructions; no secrets in source or client bundles.

## Project checklist

- [x] Audit existing React and FastAPI code
- [ ] Validate extraction for all 543 PDF pages
- [ ] Identify and OCR scanned/low-text pages
- [ ] Extract and preserve tables
- [ ] Validate structured chunks and metadata
- [ ] Confirm BGE-M3 embedding provenance and generate/reuse verified embeddings
- [ ] Build and validate FAISS index
- [ ] Implement/validate BM25 + hybrid retrieval
- [ ] Integrate and validate reranking
- [ ] Verify hosted text and vision-language inference
- [ ] Verify screenshot upload and analysis in React
- [ ] Verify manual page citations and viewer links
- [ ] Evaluate 30–50 questions
- [ ] Validate backend and frontend deployment
- [x] Document current architecture, API, project status, and local setup
- [ ] Complete ingestion, RAG evaluation, and deployment documentation

## Immediate next milestone

Produce a validated, page-aware `chunks.json` for all 543 pages by auditing the existing data first. Do not re-embed or rebuild FAISS until the chunk schema, frontend dataset discrepancy, embedding provenance, and retrieval baseline are understood.
