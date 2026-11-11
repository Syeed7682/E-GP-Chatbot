# Project Plan

## Goal
Create a production‑ready **e‑GP Manual Assistant** that:
1. Ingests the official 543‑page e‑GP Procuring Entity manual.
2. Generates dense BGE‑M3 embeddings and builds a FAISS index.
3. Provides hybrid FAISS + BM25 retrieval with domain‑specific query expansion.
4. Answers user questions using the multimodal **Qwen 2.5‑VL‑3B‑Instruct** model (local GPU preferred, Groq fallback).
5. Supports screenshot‑based queries (OCR + vision model) and automatic model‑shift.
6. Exposes a clean FastAPI API and a Netlify‑hosted React UI.
7. Includes offline fallback synthesis and IndexedDB caching.

## Completed Milestones (Nov 2026)
- ✅ Directory standardisation for backend, frontend, scripts, docs.
- ✅ Full‑text and multimodal embedding pipeline (BGE‑M3 + image embeddings).
- ✅ FAISS index generation and metadata persistence.
- ✅ Hybrid retrieval (FAISS + BM25) with weighted score fusion (0.7 dense, 0.3 BM25).
- ✅ Vision auto‑shift: image uploads trigger Qwen‑VL model.
- ✅ UI redesign with professional header/sidebar, citation cards, and E1/E2 toggle.
- ✅ Offline synthesis path with deterministic answer generation.
- ✅ Comprehensive documentation (README, API docs, Deployment guide, Architecture, Project plan).
- ✅ Automated test suite (10 passing tests).
- ✅ Netlify static deployment and backend containerisation instructions.

## Current Status
- **Backend** runs locally with GPU; the Qwen model loads successfully.
- **FAISS index** is loaded at startup; health endpoint reports `index_ready: true`.
- **API** endpoints (`/api/chat`, `/api/manual/*`, `/api/health`) are functional.
- **Frontend** connects to the backend, displays citations, and handles image uploads.

## Next Steps (Q4 2026)
| Item | Description | Owner | Target |
|------|-------------|-------|--------|
| Dockerisation | Create Dockerfile for backend, CI/CD pipeline. | Backend lead | 2026‑12‑05 |
| Production Hosting | Deploy backend to Render/Fly.io, configure CORS. | DevOps | 2026‑12‑10 |
| Monitoring | Add Prometheus metrics and alerting for model latency. | Ops | 2026‑12‑15 |
| Accessibility | Ensure UI meets WCAG AA standards. | Frontend | 2026‑12‑20 |
| Documentation Polish | Add Mermaid diagrams to README, improve language. | Docs | Ongoing |

## Risks & Mitigations
- **GPU Availability** – fallback to Groq when no GPU.
- **Provider Rate Limits** – monitor usage, enable exponential back‑off.
- **Manual Updates** – re‑run ingestion scripts and redeploy backend.
- **Security** – keep all tokens in backend env, enforce strict CORS.

