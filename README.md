# e-GP Assistant (Proca)
### Enterprise Multimodal AI Assistant for Bangladesh e-GP (Procuring Entities & Tenderers / Contractors)

An AI-powered document intelligence and procedural assistant that helps users understand and navigate the **Bangladesh Electronic Government Procurement (e-GP)** ecosystem under the Public Procurement Act (PPA 2006) and Public Procurement Rules (PPR 2008).

The platform serves both **Procuring Entities (PEs)** and **Tenderers / Contractors / Vendors**, providing contextual answers, statutory references, and visual diagram/portal screenshot alignments.

> **Official Authority Notice:** This assistant provides automated guidance grounded in the official Bangladesh e-GP User Manuals and BPPA / CPTU documentation. For legal disputes or formal decisions, consult the official portal at [eprocure.gov.bd](https://www.eprocure.gov.bd) or contact the **e-GP Helpdesk at 16575**.

---

## Key Features

- **Dual-Audience Scope:** Serves both Procuring Entities (APP planning, tender creation, opening, evaluation, NOA, contract signing) and Tenderers/Contractors (registration, e-Payment, e-BG mapping, tender purchasing, online bid preparation, joint venture setups).
- **Multi-Channel RAG Pipeline:** Combines dense semantic search (BGE-M3 1024-dim), sparse lexical ranking (BM25Okapi), visual screenshot matching (SigLIP 768-dim), and cross-encoder precision reranking (BGE-Reranker-v2-m3).
- **Interactive Action Pills on Every Response:**
  - 🖼️ **`View Scenario — Screen / Page`**: Expandable modal/card rendering the exact manual diagram or portal screenshot mapped to the procedural step, with multi-page carousel navigation.
  - 📖 **`Source Reference`**: Expandable citation block linking to official manual page numbers (e.g., `p. 199, p. 415`) and supplemental Q&A records.
  - 📞 **`Contact Helpdesk`**: Instant access to official BPPA / CPTU Helpdesk contact channels (Hotline `16575`, support numbers, and official emails).
- **Automated Helpdesk Escalation:** If a user query falls outside the official manual records, the system politely clarifies the limitation and renders the complete Helpdesk contact block directly.
- **Multimodal Screenshot Diagnostics:** Upload portal screenshots to diagnose error codes, BOQ discrepancies, and verification screens via OCR and vision models.
- **CSV Data Source Integration:** Utilizes structured CSV extractions (`csv_files/`) alongside original manuals and 1,000 official Q&A records.
- **Offline Resilience:** Local vector engine and IndexedDB cache allow client-side assistance when offline.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.12, FastAPI, Uvicorn, PyMuPDF |
| **Vector & Retrieval** | FAISS `IndexIDMap2(IndexFlatIP)`, `rank-bm25`, Reciprocal Rank Fusion ($k=60$) |
| **Embeddings & Reranking** | `BAAI/bge-m3` (1024-dim), `google/siglip-base-patch16-224` (768-dim), `BAAI/bge-reranker-v2-m3` |
| **Inference Models** | Groq `openai/gpt-oss-20b` (text), Groq `qwen/qwen3.8-27b` (multimodal/vision), Google Gemini Flash (fallback) |
| **Local / Browser Storage** | IndexedDB, SQLite (`metadata.db`) |
| **Deployment** | Netlify (Frontend), Render / Linux VM (Backend) |

---

## Knowledge Base Sources

1. **Official User Manuals**:
   - `egp_manual.pdf` (543 pages — Comprehensive Procuring Entity & System Manual).
   - `eGP_NewUserRegManual_English.pdf` (27 pages — Contractor & User Registration Manual).
2. **Supplemental Q&A Datasets**:
   - `e-GP System Q&A.txt` / `.docx` (1,000 baseline procedural questions & answers).
3. **Structured CSV Layer (`csv_files/`)**:
   - `egp_manual_extracted.csv`: Structured 543-page manual records.
   - `egp_registration_manual_extracted.csv`: Structured 27-page registration records.
   - `egp_contractor_evaluation_dataset.csv`: 729 verified question-and-answer pairs covering contractor and evaluation workflows.

---

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/                 # Chat, health, manual, sync endpoints
│   │   ├── core/                # Configuration, security, database
│   │   ├── prompts/             # Dual-audience system prompts (system_prompt.txt)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── services/            # Retrieval, embeddings, vision, citations, LLM
│   │   └── main.py              # FastAPI application entry point
│   ├── scripts/                 # Ingestion & index-building scripts (ingest_all.py, etc.)
│   ├── tests/                   # Automated pytest suite (62 passing tests)
│   └── requirements.txt
│
├── csv_files/                   # Structured CSV data sources
│   ├── egp_contractor_evaluation_dataset.csv
│   ├── egp_manual_extracted.csv
│   └── egp_registration_manual_extracted.csv
│
├── data/
│   ├── raw/                     # Original PDF manuals & Q&A documents
│   ├── processed/               # Processed chunks (chunks.json)
│   ├── faiss_index/             # Dense FAISS vectors & metadata
│   ├── indexes/                 # Versioned index store (v001/) with active_version.json
│   └── extracted_images/        # 1,096 cropped chunk diagrams & screen images
│
├── documents/                   # Architecture, API specs, deployment guides
│   ├── INDEX.md                 # Documentation index
│   ├── PROJECT_ARCHITECTURE.md  # Detailed architecture & component flows
│   ├── API_DOCUMENTATION.md     # OpenAPI route documentation
│   ├── DEPLOYMENT_GUIDE.md      # Deployment instructions (Local, Render, Netlify)
│   ├── EMBEDDINGS.md            # Multi-channel embedding & indexing guide
│   └── PROJECT_PLAN.md          # Completed development phases (1–8)
│
├── frontend/
│   ├── src/
│   │   ├── components/          # GovtChatArea, HelpdeskContactCard, Header, Sidebar
│   │   ├── services/            # API client and streaming handlers
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx              # Main application shell
│   ├── package.json
│   └── vite.config.ts
│
├── Nessery_dumpings/            # Archived scratch scripts & developer utility files
│
├── .env.example                 # Environment configuration template
├── netlify.toml                 # Netlify SPA routing rules
├── requirements.txt             # Root requirements pointer
└── run.bat                      # One-click Windows development launcher
```

---

## Quick Start

### 1. Prerequisites
- **Python**: 3.10+ (tested on 3.12.10)
- **Node.js**: 20+ (tested on Node 22)

### 2. Environment Configuration
Copy `.env.example` to `.env` in the repository root and configure your inference keys:
```bash
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # Optional fallback
```

### 3. Launching the Application
Execute the Windows launcher:
```powershell
.\run.bat
```
Or start manually:

**Terminal 1 — Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

Visit `http://localhost:3000` to interact with the assistant.

---

## Testing & Quality Assurance

Run the automated backend test suite:
```powershell
python -m pytest backend/tests -q
```
*Current test result: **62 passed**.*

Verify frontend compilation:
```powershell
npm run build --prefix frontend
```
*Current build result: **0 TypeScript / Vite compilation errors**.*

---

## Official Helpdesk Escalation Contacts

- 📞 **e-GP Helpdesk Hotline:** `16575` *(from any mobile network in Bangladesh)*
- ☎️ **Telephone Support:** `+880 9609112233` / `+880 1762625528–31`
- ✉️ **Email Support:** `helpdesk@eprocure.gov.bd` / `e-gphelpdesk@cptu.gov.bd`
- 🌐 **Official Portal:** [eprocure.gov.bd](https://www.eprocure.gov.bd)
- 🏢 **Authority:** Bangladesh Public Procurement Authority (BPPA) / CPTU, IMED, Ministry of Planning
