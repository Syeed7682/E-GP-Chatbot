# e-GP Manual Assistant
### AI-Powered Question Answering for the Bangladesh e-GP Procuring Entity User Manual

An AI-powered document assistant that helps users explore and understand the **Bangladesh Electronic Government Procurement (e-GP) Procuring Entity User Manual** through natural-language questions.

Built with React, FastAPI, FAISS, and multimodal AI, the application combines semantic retrieval, domain-specific keyword ranking, and grounded language generation to provide contextual answers with manual page references.

> **Disclaimer:** This is an informational project assistant, not an official procurement authority. Its responses are based on the indexed manual and configured AI provider. Always verify procurement decisions against the applicable regulations, official e-GP guidance, and authorized sources.

---

## Key Features

- **AI-Powered Question Answering:** Ask natural-language questions about the e-GP manual.
- **Retrieval-Augmented Generation (RAG):** Combines FAISS semantic search with domain-specific keyword ranking.
- **Source-Grounded Responses:** Provides references to relevant manual pages to support generated answers.
- **Screenshot-Based Questions:** Upload screenshots for OCR and vision-based question processing.
- **Multimodal AI Support:** Uses Groq‑hosted GPT‑OSS for E1 text answers and Qwen for E2 and screenshot answers.
- **Manual Page Visualization:** View relevant manual pages alongside answers.
- **Offline Browser Support:** Includes local retrieval and IndexedDB storage for browser‑based access when the backend is unavailable.
- **Suggested Questions:** Explore searchable, manual‑based question suggestions.
- **Full Manual Access:** Download the complete 543‑page PDF manual.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Development Server | Express.js |
| Vector Search | FAISS |
| Retrieval | Dense Semantic Search, Keyword Scoring |
| AI Models | Groq `openai/gpt-oss-20b`, Groq `qwen/qwen3.8-27b` |
| Document Processing | PDF Processing, OCR, Vision |
| Browser Storage | IndexedDB |
| Deployment | Netlify, Python‑compatible hosting |

## System Architecture

The application follows a frontend‑backend architecture. The React frontend communicates with a separately hosted FastAPI backend for AI‑powered question answering, document retrieval, and manual access.

### Question Answering Pipeline

1. **User Input:** Submit a text question or upload a screenshot.
2. **Document Retrieval:** Search the indexed manual using FAISS semantic similarity and domain‑specific keyword ranking.
3. **Score Fusion:** Combine normalized retrieval scores to identify relevant document chunks.
4. **Context Selection:** Select the highest‑ranked manual passages.
5. **AI Generation:** Generate a context‑grounded response using the configured multimodal language model.
6. **Source Attribution:** Return relevant manual page references with the generated answer.

### Retrieval Strategy

| Retrieval Component | Weight |
|---|---:|
| FAISS Semantic Search | 30% |
| Domain‑Specific Keyword Ranking | 70% |

The normalized scores are fused linearly (default `0.7 * dense + 0.3 * bm25`). Adjust in `HybridRetriever._fuse` if needed.

**Note:** The repository contains separate hybrid‑retrieval and reranking modules, but the active chat path currently uses the weighted fusion above rather than BM25, RRF, or a BGE reranker.

## AI Models

| Model | Purpose | Configuration |
|---|---|---|
| `openai/gpt-oss-20b` | Groq E1 text answers | Default |
| `qwen/qwen3.8-27b` | Groq E2 and screenshot answers | Default |

Set `GROQ_API_KEY` on the backend host. `GROQ_TEXT_MODEL` and `GROQ_VISION_MODEL` can override the defaults. Gemini is an optional fallback.

When no hosted provider is configured, the backend falls back to an offline grounded synthesis routine.

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # Chat, health, manual, sync endpoints
│   │   ├── core/                # Configuration and security
│   │   ├── prompts/             # System prompts
│   │   ├── schemas/             # Request/response schemas
│   │   ├── services/            # Retrieval, embeddings, vision, citations
│   │   └── main.py              # FastAPI entry point
│   ├── scripts/                 # Ingestion and index‑building scripts
│   ├── tests/                   # Backend tests
│   └── requirements.txt
│
├── data/
│   ├── raw/                     # Original PDF (not tracked)
│   ├── processed/               # Extracted and chunked content
│   ├── faiss_index/             # FAISS index and metadata
│   └── extracted_images/        # Optional page images
│
├── documents/
│   ├── INDEX.md
│   ├── PROJECT_ARCHITECTURE.md
│   ├── PROJECT_PLAN.md
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
│
├── frontend/
│   ├── public/                  # Static assets and logo
│   └── src/
│       ├── components/          # React components
│       ├── data/                # Bundled manual data
│       ├── services/             # Backend API client
│       ├── types/                # TypeScript definitions
│       └── utils/                # Offline retrieval and storage
│
├── scripts/                     # Root‑level utilities
├── .env.example                 # Environment template
├── netlify.toml                 # Netlify configuration
├── run.bat                      # Windows development launcher
├── run.sh                       # Linux/macOS launcher
└── README.md
```

## Getting Started

### Prerequisites

- Node.js and npm
- Python and pip
- Git
- The authorized e‑GP manual PDF
- FAISS index and metadata files

### 1️⃣ Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

### 2️⃣ Configure Environment Variables

Create a local `.env` file (copy from `.env.example`):

```powershell
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` with your backend configuration (e.g., `GROQ_API_KEY`, model names, `USE_LOCAL_LLM`).

### 3️⃣ Install Backend Dependencies

```bash
python -m pip install -r backend/requirements.txt
```

### 4️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5️⃣ Prepare Manual Data

Place the official PDF at:

```
data/raw/egp_manual.pdf
```

Ensure the processed chunks, FAISS index, and metadata exist:

```
data/
├── raw/egp_manual.pdf
├── processed/chunks.json
└── faiss_index/index.faiss
   └── metadata.json
```

If you need to regenerate the index:

```bash
python -m app.services.embedding_service --build-index
```

---

## Embedding & FAISS Index

The `embedding_service` script splits the PDF into ~500‑word chunks, computes BGE‑M3 embeddings, and builds a flat FAISS index. Metadata (page numbers, chunk IDs) is stored alongside the index for citation generation.

---

## Hybrid Retrieval Pipeline

1. **Pre‑process query** – stop‑word removal, synonym expansion (see `retrieval_service.py`).
2. **Dense search** – FAISS inner‑product similarity.
3. **Sparse search** – BM25 via `BM25Retriever`.
4. **Score fusion** – weighted linear combination (default `0.7 * dense + 0.3 * bm25`).
5. **Post‑process** – filter TOC pages (`page ≤ 5`) and stitch fragmented sentences.

The top‑k chunks are formatted by `LLMService._build_context` into a numbered list with page citations (`combined_text`).

---

## LLM Configuration

- **Local mode** – Loads `Qwen/Qwen2.5-VL-3B-Instruct` via Hugging Face Transformers when `USE_LOCAL_LLM=true`.
- **Groq fallback** – Calls `GROQ_TEXT_MODEL` for text and `GROQ_VISION_MODEL` for images.
- **Vision auto‑shift** – If an image is supplied, the backend automatically routes the request to the vision model (E2) regardless of the toggle.

The UI includes an **E1/E2 toggle**; toggling sends `use_alt_model` in the `/chat` payload, forcing the vision model.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/chat` | Main QA endpoint (text + optional image). |
| `GET` | `/api/questions` | List supplemental Q&A entries for suggestions. |
| `GET` | `/api/health` | System health and index status. |
| `GET` | `/api/chunks` | Inspect a sample of indexed manual chunks. |
| `POST` | `/api/retrieve` *(optional)* | Return raw retrieved chunks (text, page, screenshots) without LLM processing. |

---

## Running the Application

### Option A: Windows (run.bat)

```powershell
.\run.bat
```
Select the full‑stack development option.

### Option B: Linux / macOS (run.sh)

```bash
bash run.sh
```

### Option C: Manual start

**Backend**
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
**Frontend**
```bash
cd frontend
npm run dev   # http://localhost:5173
```

### URLs

- Frontend: `http://localhost:3000` (or `5173` depending on Vite config)
- Backend API: `http://127.0.0.1:8000`
- OpenAPI docs: `http://127.0.0.1:8000/docs`

---

## Production Deployment

| Component | Deployment |
|---|---|
| Frontend | Netlify |
| Backend | Python‑compatible host |
| Manual PDF & FAISS index | Backend storage |

### Frontend (Netlify)

Add environment variable:
```env
VITE_API_BASE_URL=https://<your‑backend>.com
```

### Backend

Set CORS origin:
```env
CORS_ORIGINS=https://<your‑netlify‑site>.netlify.app
```
Ensure the backend has access to the PDF, processed chunks, FAISS index, and metadata.

See `documents/DEPLOYMENT_GUIDE.md` for full instructions.

---

## Build & Validation

**Frontend build**
```bash
cd frontend
npm run build
```

**Frontend lint / type‑check**
```bash
npm run lint   # runs tsc --noEmit
```

**Backend tests**
```bash
python -m pytest backend/tests -q
```
Run these before committing or deploying.

---

## Data Management

| File | Description |
|---|---|
| `data/raw/egp_manual.pdf` | Original 543‑page manual |
| `data/raw/e‑GP System Q&A.txt` | Supplemental Q&A source |
| `data/processed/chunks.json` | Extracted document chunks |
| `data/faiss_index/index.faiss` | FAISS vector index |
| `data/faiss_index/metadata.json` | Chunk metadata |
| `data/extracted_images/` | Optional page images |
| `frontend/src/data/allManualChunks.json` | Bundled data for offline UI |

Keep the PDF out of version control; only store processed artifacts.

---

## Known Limitations

- Answer quality depends on manual coverage and index quality.
- Retrieval may miss edge‑case provisions.
- Current pipeline uses weighted dense + keyword scores; no BM25‑only or reranker path.
- Offline browser mode may yield different results than the server.
- Vision performance relies on OCR/vision model accuracy.
- Hosted model limits are imposed by the provider.
- This tool does **not** replace official procurement guidance.

---

## Documentation

Additional docs are in the `documents/` folder:

- `INDEX.md` – Overview of documentation
- `PROJECT_ARCHITECTURE.md` – Detailed architecture
- `PROJECT_PLAN.md` – Roadmap & validation checklist
- `API_DOCUMENTATION.md` – Backend API spec
- `DEPLOYMENT_GUIDE.md` – Netlify & backend deployment steps

---

## Contributing

1. Fork the repo and create a feature branch.
2. Keep retrieval and citation behavior consistent with the indexed manual.
3. Do **not** commit any secret keys.
4. Run both frontend lint and backend tests.
5. Update documentation when behavior changes.


## License

Specify your project’s license here (e.g., MIT, Apache‑2.0).
