# Deployment Guide

## Overview

This guide details how to deploy the **e‑GP Manual Assistant** – a FastAPI backend providing hybrid FAISS + BM25 retrieval and multimodal inference using **Qwen 2.5‑VL‑3B‑Instruct**, and a Vite/React frontend hosted on Netlify (or any static‑hosting provider).

## 1. Backend deployment

### 1.1 Prerequisites
- Python 3.10+ with `pip`.
- Access to the FAISS index (`data/faiss_index/index.faiss`) and its metadata (`metadata.json`).
- The original manual PDF (`data/raw/e‑GP System User Manual.pdf`).
- A server capable of running a persistent Python process (Render, Fly.io, Railway, VPS, Docker, etc.).

### 1.2 Repository layout
```
backend/
│   app/
│   ├── api/      # chat, health, manual, sync routes
│   ├── core/     # config, security, CORS
│   ├── prompts/  # system_prompt.txt
│   ├── schemas/  # Pydantic request/response models
│   └── services/ # retrieval, embeddings, vision, LLM, citations
│   main.py       # FastAPI entry point
│   requirements.txt
scripts/            # ingestion, index‑building utilities
```

### 1.3 Environment variables (`.env`)
```
# Core configuration
VECTOR_DB=faiss
EMBEDDING_MODEL=BAAI/bge-m3
USE_LOCAL_LLM=true                # Load Qwen2.5‑VL‑3B‑Instruct locally if GPU is present
LOCAL_LLM_MODEL=Qwen/Qwen2.5-VL-3B-Instruct

# Hosted inference (fallback when local unavailable)
GROQ_API_KEY=your_groq_key
GROQ_TEXT_MODEL=openai/gpt-oss-20b
GROQ_VISION_MODEL=Qwen/Qwen2.5-VL-3B-Instruct

# Optional Gemini fallback
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-flash-latest

# Data locations (relative to project root)
DATA_RAW_DIR=data/raw
FAISS_INDEX_PATH=data/faiss_index/index.faiss
FAISS_METADATA_PATH=data/faiss_index/metadata.json
QA_DATA_PATH=data/raw/e‑GP System Q&A.txt

# CORS – comma‑separated list of allowed origins
CORS_ORIGINS=https://my-frontend.netlify.app,https://mydomain.com
```
Never expose these secrets to the client side.

### 1.4 Install & start
```bash
# Clone and enter the repo
git clone <repo-url>
cd e‑gp‑project‑manual

# Virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\activate

# Install backend deps
pip install -r backend/requirements.txt

# Verify FAISS files exist
ls data/faiss_index/
# should show index.faiss and metadata.json

# Run the server (adjust host/port as needed)
uvicorn backend/app/main:app --host 0.0.0.0 --port ${PORT:-8000}
```
The API will be reachable at `http://<host>:8000/api`.

### 1.5 Health check
```bash
curl http://localhost:8000/api/health
```
You should receive a JSON payload with `status: "healthy"`, index readiness, and model names.

## 2. Frontend deployment (Netlify)

### 2.1 Prerequisites
- Node 22 (or latest LTS) and npm.
- Netlify account linked to the Git repository.

### 2.2 Netlify configuration (`netlify.toml`)
```toml
[build]
  base = "frontend"
  command = "npm install && npm run build"
  publish = "dist"

[context.production.environment]
  VITE_API_BASE_URL = "https://<backend‑host>"
```
Only the public API URL is stored here; no secrets.

### 2.3 Deploy steps
1. Push the repo to GitHub (or your VCS).
2. In Netlify, **Add new site → Import an existing project** and select the repo.
3. Netlify reads `netlify.toml`, installs dependencies, builds, and publishes `frontend/dist`.
4. After a successful build, add the Netlify site URL to the backend’s `CORS_ORIGINS` and redeploy the backend.

### 2.4 Runtime verification
- Open the site and ask a sample question.
- Verify citations, page images, and the vision model work when you upload a screenshot.

## 3. Operational notes
- **GPU requirement:** The local Qwen model needs a CUDA‑enabled GPU. If missing, set `USE_LOCAL_LLM=false` to fall back to Groq.
- **Rate limits:** Monitor 429 responses from Groq/Gemini and consider a higher plan if needed.
- **Index updates:** When the manual PDF changes, re‑run the ingestion scripts and redeploy the backend.
- **Security:** Keep all provider tokens (`GROQ_API_KEY`, `HF_TOKEN`, `GEMINI_API_KEY`) in the host’s secret manager, never in client‑side env.
- **Monitoring:** Use `/api/health` and `/api/chat/health` for liveness probes.


