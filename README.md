# Bangladesh e-GP Official Manual Assistant

An enterprise-grade **Multimodal RAG (Retrieval-Augmented Generation) + Offline-First Synchronization System** for the official **543-page Bangladesh e-GP (electronic Government Procurement) Procuring Entity User Manual**.

Built in accordance with the Public Procurement Act (PPA 2006) and Public Procurement Rules (PPR 2008), this system answers queries with strict statutory grounding, page citations, portal screenshot diagnostics, and offline fallback.

---

## 🏛️ System Architecture

```
User Query (Text + optional portal screenshot)
                 │
                 ▼
     Multimodal Query Processor
      (OCR + Visual Layout Analysis)
                 │
         ┌───────┴───────┐
         ▼               ▼
   Text Embedding   Visual Understanding
  (BGE-M3 1024-dim)   (OCR / Qwen2.5-VL)
         │               │
         └───────┬───────┘
                 ▼
     Hybrid Retrieval Engine
   (FAISS IndexFlatIP + BM25)
                 │
                 ▼
      BGE Cross-Encoder Reranker
  (Filters TOC pages 1–5, boosts exact procedures)
                 │
                 ▼
     Grounded Context Builder
(Official manual passages + page citations + screens)
                 │
                 ▼
        LLM Inference Engine
(Qwen2.5-72B-Instruct / Gemini / Zero-Crash Synthesizer)
                 │
                 ▼
     e-GP Assistant Response
(Actionable steps + Page citations + Portal screen guidance)
                 │
                 ▼
   Offline Synchronization Layer
 (IndexedDB + Local vector cache + Reconciliation queue)
```

---

## 📁 Directory Structure

```
E:\E-gp Project manual\
│
├── frontend/
│   ├── public/
│   │   ├── assets/
│   │   ├── logo/
│   │   └── manual-preview/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/             # ChatWindow, ChatMessage, ChatInput, SourceCitation
│   │   │   ├── manual/           # ManualViewer, PageNavigator, ScreenshotViewer
│   │   │   ├── offline/          # OfflineIndicator, SyncManager, SyncInspector
│   │   │   └── layout/           # Header, Sidebar, Dashboard
│   │   ├── services/             # api.ts, chatService.ts, retrievalService.ts, syncService.ts
│   │   ├── data/                 # manualChunks.ts, portalScreens.ts, allManualChunks.json
│   │   ├── utils/                # indexedDB.ts, offlineVectorEngine.ts, encryption.ts, syncQueue.ts
│   │   ├── types/                # egp.ts
│   │   ├── App.tsx               # Primary application component
│   │   └── main.tsx              # React DOM entry point
│   ├── index.html
│   ├── vite.config.ts            # Vite config with /api proxy to FastAPI
│   ├── package.json
│   ├── tsconfig.json
│   ├── server.ts                 # Full-stack Node proxy & fallback engine
│   └── netlify.toml              # Netlify client deployment config
│
├── backend/
│   ├── app/
│   │   ├── api/                  # chat.py, health.py, manual.py, sync.py
│   │   ├── services/             # embedding_service.py, vector_store.py, hybrid_retriever.py,
│   │   │                         # reranker.py, vision_service.py, llm_service.py,
│   │   │                         # citation_service.py, pdf_loader.py, chunker.py
│   │   ├── prompts/              # system_prompt.py, system_prompt.txt
│   │   ├── schemas/              # chat.py, manual.py
│   │   ├── core/                 # config.py, security.py
│   │   └── main.py               # FastAPI application entry point
│   ├── scripts/                  # ingest_manual.py, extract_images.py, build_index.py, validate_chunks.py
│   ├── tests/                    # test_retrieval.py, test_chat.py, test_citations.py, test_offline.py
│   └── requirements.txt
│
├── ai_models/
│   ├── __init__.py
│   ├── models.py
│   └── model_config.py
│
├── data/
│   ├── raw/                      # e-GP System User Manual (543 pages)
│   ├── processed/                # chunks.json (1,188 chunks)
│   ├── extracted_images/         # page_images/ (pages 1 to 543)
│   ├── embeddings/
│   └── faiss_index/              # index.faiss & metadata.json
│
├── documents/
│   ├── INDEX.md
│   ├── PROJECT_ARCHITECTURE.md
│   ├── thinking_process.txt
│   ├── havedone.txt
│   └── API_DOCUMENTATION.md
│
├── .venv/
├── .env
├── .env.example
├── .gitignore
├── run.bat                       # One-click Windows launcher
├── run.sh                        # One-click Unix launcher
└── README.md
```

---

## 🚀 Quick Start

### Option 1: One-Click Full Stack Launcher
On Windows, double-click:
```cmd
run.bat
```
Select **`[1]`** to launch both the FastAPI Python Backend (`http://127.0.0.1:8000`) and React Frontend (`http://localhost:3000`).

### Option 2: Run Separately

#### 1. FastAPI Backend:
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation available at: `http://127.0.0.1:8000/docs`

#### 2. React Frontend:
```powershell
cd frontend
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## 🧪 Verification & Automated Tests

Run the Python verification test suites:
```powershell
.\.venv\Scripts\python.exe backend/tests/test_retrieval.py
.\.venv\Scripts\python.exe backend/tests/test_offline.py
```
Both tests verify:
1. **Debarment / Suspension** correctly retrieves statutory Chapter 7 (Pages 342–348, Rule 127).
2. **Tender Deletion** correctly retrieves Chapter 4 Cancellation Process (Page 178 / 191) with Table of Contents permanently excluded.
3. Offline synthesis executes zero-crash responses when disconnected.
