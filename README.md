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
- **Multimodal AI Support:** Uses Qwen2.5-VL for hosted inference, with Liquid AI available as an optional alternative.
- **Manual Page Visualization:** View relevant manual pages alongside answers.
- **Offline Browser Support:** Includes local retrieval and IndexedDB storage for browser-based access when the backend is unavailable.
- **Suggested Questions:** Explore searchable, manual-based question suggestions.
- **Full Manual Access:** Download the complete 543-page PDF manual.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Development Server | Express.js |
| Vector Search | FAISS |
| Retrieval | Dense Semantic Search, Keyword Scoring |
| AI Models | Qwen2.5-VL-3B-Instruct, LiquidAI LFM2.5-VL-1.6B |
| Document Processing | PDF Processing, OCR, Vision |
| Browser Storage | IndexedDB |
| Deployment | Netlify, Python-compatible hosting |

## System Architecture

The application follows a frontend-backend architecture. The React frontend communicates with a separately hosted FastAPI backend for AI-powered question answering, document retrieval, and manual access.

### Question Answering Pipeline

1. **User Input:** Submit a text question or upload a screenshot.
2. **Document Retrieval:** Search the indexed manual using FAISS semantic similarity and domain-specific keyword ranking.
3. **Score Fusion:** Combine normalized retrieval scores to identify relevant document chunks.
4. **Context Selection:** Select the highest-ranked manual passages.
5. **AI Generation:** Generate a context-grounded response using the configured multimodal language model.
6. **Source Attribution:** Return relevant manual page references with the generated answer.

### Retrieval Strategy

The active backend chat pipeline uses two retrieval signals:

| Retrieval Component | Weight |
|---|---:|
| FAISS Semantic Search | 30% |
| Domain-Specific Keyword Ranking | 70% |

The normalized retrieval scores are combined using weighted score fusion when keyword results are available.

**Implementation note:** Although separate hybrid-retrieval and reranking modules exist in the repository, they are not currently integrated into the active chat request path. The current implementation does not use BM25, Reciprocal Rank Fusion (RRF), or a BGE reranker.

## AI Models

The application supports configurable hosted inference providers.

| Model | Purpose | Configuration |
|---|---|---|
| Qwen/Qwen2.5-VL-3B-Instruct | Primary multimodal model | Default |
| LiquidAI/LFM2.5-VL-1.6B | Alternative multimodal model | Optional |

The primary model is used by default. The alternative provider is activated only when explicitly selected.

An optional Hugging Face access token enables hosted inference. When no provider is configured, the backend can use its available local or extractive fallback.

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # Chat, health, manual, sync endpoints
│   │   ├── core/                # Configuration and security
│   │   ├── prompts/             # AI system prompts
│   │   ├── schemas/             # API request/response schemas
│   │   ├── services/            # Retrieval, embeddings, vision, citations
│   │   └── main.py              # FastAPI entry point
│   ├── scripts/                 # Ingestion and index-building scripts
│   ├── tests/                   # Backend tests
│   └── requirements.txt
│
├── data/
│   ├── raw/                     # Original PDF (not tracked)
│   ├── processed/               # Extracted and chunked content
│   ├── faiss_index/             # FAISS index and metadata
│   └── extracted_images/        # Optional manual page images
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
├── scripts/                     # Root-level utilities
├── .env.example                 # Environment configuration template
├── netlify.toml                 # Netlify configuration
├── run.bat                      # Windows development launcher
├── run.sh                       # Linux/macOS development launcher
└── README.md
```

## Getting Started

### Prerequisites

Ensure the following are installed:

- Node.js and npm
- Python and pip
- Git
- The authorized e-GP manual PDF
- Project FAISS index and metadata files

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_DIRECTORY>
```

### 2. Configure Environment Variables

Create a local environment file:

```powershell
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Configure the required backend settings in `.env`.

To enable hosted Hugging Face inference, configure:

```env
HF_TOKEN=your_huggingface_token
```

Keep API credentials on the backend. Never expose provider tokens through frontend `VITE_*` environment variables or commit `.env` to Git.

Refer to `.env.example` and `backend/app/core/config.py` for supported configuration options.

### 3. Install Backend Dependencies

From the project root:

```bash
python -m pip install -r backend/requirements.txt
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 5. Configure Manual Data

Place the authorized source PDF at:

```text
data/raw/egp_manual.pdf
```

Ensure the processed document chunks, FAISS index, and corresponding metadata are available:

```text
data/
├── raw/
│   └── egp_manual.pdf
├── processed/
│   └── chunks.json
└── faiss_index/
    ├── index.faiss
    └── metadata.json
```

The index and metadata must correspond to the same processed document version.

## Running the Application
## System workflow

```text
                 ┌───────────────────────────────────┐
                 │ ❓ Question + optional screenshot │
                 └───────────────┬─────────────── ───┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
        ┌───────────▼──────────┐  ┌──────────▼───────────┐
        │ 🔎 FAISS semantic    │  │  🔑 Domain keyword  │
        │    search            │  │    ranking           │
        └───────────┬──────────┘  └──────────┬───────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ ⚖️ Weighted score fusion │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ 📚 Top-k manual chunks  │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────────────┐
                    │ 🧠 Grounded model answer       │
                    │    + page citations             │
                    └─────────────────────────────────┘
```
### Option A: Windows

Run the launcher from the project root:

```powershell
.\run.bat
```

Select the full-stack development option.

### Option B: Linux / macOS

```bash
bash run.sh
```

The launcher starts the backend and frontend services.

### Option C: Start Services Separately

**Backend — Terminal 1**

From the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Alternatively, use your active Python executable:

```bash
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

**Frontend — Terminal 2**

```bash
cd frontend
npm run dev
```

### Local Development URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://127.0.0.1:8000 |
| API Documentation | http://127.0.0.1:8000/docs |

The Vite development server proxies `/api` requests to the local FastAPI backend.

The backend must be running for server-based chat, PDF downloads, and PDF-rendered page images. Frontend offline fallback functionality is available when the backend cannot be reached.

## Production Deployment

The application uses a separate deployment strategy for the frontend and backend.

| Component | Deployment |
|---|---|
| Frontend | Netlify |
| Backend | Python-compatible hosting |
| Manual PDF | Backend-accessible storage |
| FAISS Index | Backend-accessible storage |
| Metadata | Backend-accessible storage |

### Frontend Configuration

Set the following environment variable in Netlify:

```env
VITE_API_BASE_URL=https://your-backend-host.com
```

Use the backend's public origin without appending `/api`.

### Backend Configuration

Configure the backend environment variable:

```env
CORS_ORIGINS=https://your-netlify-site.netlify.app
```

Use your exact deployed frontend origin.

Ensure the backend deployment includes access to:

- The authorized source manual PDF.
- The processed manual chunks.
- The FAISS vector index.
- The corresponding chunk metadata.
- Any required extracted page images.

After configuring the environment variables, redeploy both services as required.

**Important:** The frontend is a static application. Hosting it on Netlify does not automatically deploy or host the FastAPI backend.

For detailed deployment instructions, see [Deployment Guide](documents/DEPLOYMENT_GUIDE.md).

## Build and Validation

### Frontend Build

```bash
cd frontend
npm run build
```

### Frontend Type Checking

```bash
npm run lint
```

The lint script currently runs TypeScript compilation using `tsc --noEmit`.

### Backend Tests

From the project root:

```bash
python -m pytest backend/tests -q
```

Ensure pytest is installed in the selected Python environment.

Build and test results should be verified against the current project state before deployment.

## Data Management

The project uses both backend document storage and frontend-bundled manual data.

| File | Description |
|---|---|
| `data/raw/egp_manual.pdf` | Original 543-page manual |
| `data/processed/chunks.json` | Extracted and processed document chunks |
| `data/faiss_index/index.faiss` | FAISS vector index |
| `data/faiss_index/metadata.json` | Vector-to-chunk metadata |
| `data/extracted_images/` | Optional extracted page images |
| `frontend/src/data/allManualChunks.json` | Bundled manual data for frontend features |

The original PDF is not tracked by Git.

**Data integrity:** Always ensure that the PDF, processed chunks, FAISS index, and metadata belong to the same manual version before rebuilding or deploying the retrieval system.

## Known Limitations

- Responses depend on the quality and coverage of the indexed manual.
- Retrieval results may not include every relevant provision or procedural exception.
- The current chat pipeline uses weighted semantic and keyword score fusion rather than BM25 or a dedicated reranking stage.
- Offline browser retrieval may produce different results from backend-powered inference.
- Screenshot interpretation depends on image quality and OCR/vision performance.
- Hosted model availability and response quality depend on the configured inference provider.
- The application does not replace official procurement instructions, legal interpretation, or professional judgment.

## Documentation

Additional technical documentation is available in the `documents/` directory.

| Document | Description |
|---|---|
| [Documentation Index](documents/INDEX.md) | Overview of project documentation |
| [Project Architecture](documents/PROJECT_ARCHITECTURE.md) | Architecture, request paths, and implementation limitations |
| [Project Plan](documents/PROJECT_PLAN.md) | Implementation roadmap and validation checklist |
| [API Documentation](documents/API_DOCUMENTATION.md) | Backend endpoints and request/response formats |
| [Deployment Guide](documents/DEPLOYMENT_GUIDE.md) | Netlify and backend deployment instructions |

## Contributing

Contributions, bug reports, and suggestions are welcome.

When contributing:

1. Review the existing project architecture and documentation.
2. Keep retrieval and citation behavior consistent with the indexed manual.
3. Avoid exposing API keys, credentials, or sensitive configuration.
4. Test frontend and backend changes before submitting.
5. Update relevant documentation when implementation behavior changes.

## License

Specify the applicable project license here before distributing or reusing the source code.

---

**e-GP Manual Assistant**  
*Making Bangladesh e-GP documentation easier to explore through AI-assisted information retrieval.*