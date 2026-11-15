# e-GP Manual Assistant: Project Plan & Implementation Status

## Objective

Build and maintain an enterprise-grade multimodal Retrieval-Augmented Generation (RAG) assistant for the Bangladesh e-GP (Electronic Government Procurement) system, preserving full citation provenance, structured diagram associations, and high-availability inference with fallback escalation.

---

## Phases & Current Implementation Status

### Phase 1 — Baseline Audit & Integrity Verification
- **Status**: **Complete** ✅
- **Delivered**:
  - Validated source manual `data/raw/egp_manual.pdf` (543 pages).
  - Verified 1,188 existing chunks and 1,000 supplemental Q&A records.
  - Confirmed L2-normalized 1,024-dimensional embeddings.

---

### Phase 2 — Retrieval Evaluation & Smoke Benchmarking
- **Status**: **Complete** ✅
- **Delivered**:
  - Evaluation framework in `backend/scripts/evaluate_retrieval.py`.
  - Smoke benchmark dataset in `backend/data/retrieval_eval.json`.
  - Legacy pipeline benchmark: Hit@5 **1.000**, MRR@5 **0.917**.
  - New RAG service evaluation flag `--rag-version v001` added for automated regression testing.

---

### Phase 3 — Ingestion & Structure-Aware Processing Pipeline
- **Status**: **Complete** ✅
- **Delivered**:
  - `pdf_parser.py`: Docling engine with PyMuPDF dynamic fallback.
  - `page_renderer.py`: High-resolution 120/150 DPI page renderer.
  - `table_extractor.py`: Markdown table extraction with repeating headers.
  - `qa_parser.py`: Structured parser for 1,000 Q&A records across procurement modules.
  - `structure_chunker.py`: Preserves hierarchy, statutory section titles, and page provenance.

---

### Phase 4 — Versioned Index Architecture & Manifest Management
- **Status**: **Complete** ✅
- **Delivered**:
  - Immutable versioned index directory: `data/indexes/v001/`.
  - Atomic pointer: `data/indexes/active_version.json`.
  - Multi-index store: `pdf_text.faiss`, `bm25.pkl`, `metadata.db`.
  - Provenance manifest with cryptographic SHA-256 hashes and build metadata (`manifest.json`).
  - Validation engine: `backend/scripts/validate_indexes.py` running 9 automated integrity checks.

---

### Phase 5 — Multi-Channel Retrieval, RRF Fusion & Reranking
- **Status**: **Complete** ✅
- **Delivered**:
  - Dense semantic channel: BGE-M3 (1024-dim IndexIDMap2).
  - Lexical sparse channel: BM25Okapi (`rank-bm25`).
  - Rank fusion: Reciprocal Rank Fusion (RRF, $k=60$).
  - Cross-encoder reranker: BGE-Reranker-v2-m3 (`FlagEmbedding`).
  - Grounded context builder: `backend/app/retrieval/context_builder.py`.
  - Dynamic module loading (`importlib`) to prevent static IDE interpreter warnings.

---

### Phase 6 — Structured Chunk-Image Architecture & Vision API
- **Status**: **Complete** ✅
- **Delivered**:
  - Rebuilt all 1,096 manual images from the PDF to `data/extracted_images/chunks/`.
  - Saved files using structured schema: `chunk_{chunk_id}_page_{page}_{order}_{slug}.png`.
  - Central manifest: `data/extracted_images/images_manifest.json`.
  - Synchronized 580 verified multimodal chunks across `chunks.json`, `metadata.json`, and `metadata.db`.
  - Deleted 537 legacy indiscriminate `page_*.jpg` files and empty folders.
  - Endpoints: `GET /api/manual/chunk/{chunk_id}/image`, `GET /api/manual/images/{filename}`, and `POST /api/chat/vision`.

---

### Phase 7 — User Experience, Resilience & Deployment
- **Status**: **Complete** ✅
- **Delivered**:
  - Prompt overhaul in `system_prompt.txt`: Synthesizes descriptive answers in its own words; removed rigid disclaimers.
  - Helpdesk fallback: Automatically provides official Bangladesh e-GP Helpdesk contact channels (Hotline: `16575`, Phone: `+880 9609112233`, Email: `helpdesk@eprocure.gov.bd`).
  - Q&A Suggestion deduplication: `qaQuestionSuggestions.ts` single-escaped normalization collapses procedural question families into 1 entry per type.
  - Production launchers: Fixed Windows `run.bat` and added `backend\run.bat` for one-click startup.
  - Render deployment resilience: `_resolve_data_dir()` in `backend/app/config.py` safely catches `PermissionError` when `/var/data` is unmounted and gracefully defaults to local repository data.
  - Architecture modeling: Authored complete and simplified PlantUML diagrams (`PROJECT_ARCHITECTURE.puml`, `SIMPLE_ARCHITECTURE.puml`).

---

## Upcoming Enhancements (Phase 8 Roadmap)

1. **Full Docling v002 Re-Tokenization**: Run end-to-end extraction through Docling to populate deep table structures and section hierarchies for `v002`.
2. **Bengali (Bangla) Multilingual Expansion**: Expand retrieval and prompt templates to support native Bangla inquiries with official Bengali procurement terms.
3. **Advanced Visual Similarity Matching**: Benchmark visual embeddings (SigLIP) on end-to-end user photo uploads against the 1,096 cropped chunk diagrams.
