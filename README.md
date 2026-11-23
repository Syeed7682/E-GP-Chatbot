# e-GP Assistant (user)
### Enterprise Multimodal AI Assistant for Bangladesh e-GP (Procuring Entities & Tenderers / Contractors)

An AI-powered document intelligence and procedural assistant that helps users understand and navigate the **Bangladesh Electronic Government Procurement (e-GP)** ecosystem under the Public Procurement Act (PPA 2006) and Public Procurement Rules (PPR 2008).

The platform serves both **Procuring Entities (PEs)** and **Tenderers / Contractors / Vendors**, providing contextual answers, statutory references, and visual diagram/portal screenshot alignments.

> **Official Authority Notice:** This assistant provides automated guidance grounded in the official Bangladesh e-GP User Manuals and BPPA / CPTU documentation. For legal disputes or formal decisions, consult the official portal at [eprocure.gov.bd](https://www.eprocure.gov.bd) or contact the **e-GP Helpdesk at 16575**.

---

## Key Features

- **Dual-Audience Scope:** Serves both Procuring Entities (APP planning, tender creation, opening, evaluation, NOA, contract signing) and Tenderers/Contractors (registration, e-Payment, e-BG mapping, tender purchasing, online bid preparation, joint venture setups).
- **Multi-Channel RAG Pipeline:** Combines dense semantic search (BGE-M3 1024-dim), sparse lexical ranking (BM25Okapi), visual screenshot matching (SigLIP 768-dim), and cross-encoder precision reranking (BGE-Reranker-v2-m3).
- **Interactive Action Pills on Every Response:**
  - ðŸ–¼ï¸ **`View Scenario â€” Screen / Page`**: Expandable modal/card rendering the exact manual diagram or portal screenshot mapped to the procedural step, with multi-page carousel navigation.
  - ðŸ“– **`Source Reference`**: Expandable citation block linking to official manual page numbers (e.g., `p. 199, p. 415`) and supplemental Q&A records.
  - ðŸ“ž **`Contact Helpdesk`**: Instant access to official BPPA / CPTU Helpdesk contact channels (Hotline `16575`, support numbers, and official emails).
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
| **Vector & Retrieval** | FAISS `IndexIDMap2(IndexFlatIP)`, `rank-bm25`, Reciuserl Rank Fusion ($k=60$) |
| **Embeddings & Reranking** | `BAAI/bge-m3` (1024-dim), `google/siglip-base-patch16-224` (768-dim), `BAAI/bge-reranker-v2-m3` |
| **Inference Models** | Groq `openai/gpt-oss-20b` (text), Groq `qwen/qwen3.8-27b` (multimodal/vision), Google Gemini Flash (fallback) |
| **Local / Browser Storage** | IndexedDB, SQLite (`metadata.db`) |
| **Deployment** | Netlify (Frontend), Render / Linux VM (Backend) |

---

## Knowledge Base Sources

1. **Current Official Manual**:
   - `csv_files/egp New Manual.csv` (27 page-level records for the current registration manual).
2. **Structured Retrieval Assets**:
   - `data/structured/indexes/pdf_manual.faiss`: Active FAISS vector index.
   - `data/structured/metadata/pdf_manual.json`: Matching cleaned page metadata.
   - `data/structured/indexes/registration_csv.faiss`: CSV embedding index.
   - `data/structured/images/`: Extracted manual images.
3. **Archived manuals and supplemental Q&A are not active retrieval sources.**


---

## Project Structure

```text
.
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ api/                 # Chat, health, manual, sync endpoints
â”‚   â”‚   â”œâ”€â”€ core/                # Configuration, security, database
â”‚   â”‚   â”œâ”€â”€ prompts/             # Dual-audience system prompts (system_prompt.txt)
â”‚   â”‚   â”œâ”€â”€ schemas/             # Pydantic request/response schemas
â”‚   â”‚   â”œâ”€â”€ services/            # Retrieval, embeddings, vision, citations, LLM
â”‚   â”‚   â””â”€â”€ main.py              # FastAPI application entry point
â”‚   â”œâ”€â”€ scripts/                 # Ingestion & index-building scripts (ingest_all.py, etc.)
â”‚   â”œâ”€â”€ tests/                   # Automated pytest suite (62 passing tests)
â”‚   â””â”€â”€ requirements.txt
â”‚
â”œâ”€â”€ csv_files/                   # Structured CSV data sources
â”‚   â”œâ”€â”€ egp_contractor_evaluation_dataset.csv
â”‚   â”œâ”€â”€ egp_manual_extracted.csv
â”‚   â””â”€â”€ egp_registration_manual_extracted.csv
â”‚
â”œâ”€â”€ data/
   structured/
       indexes/              # FAISS indexes and embedding artifacts
       metadata/             # JSON/SQLite metadata
       images/               # Extracted manual images
â”‚
â”œâ”€â”€ documents/                   # Architecture, API specs, deployment guides
â”‚   â”œâ”€â”€ INDEX.md                 # Documentation index
â”‚   â”œâ”€â”€ PROJECT_ARCHITECTURE.md  # Detailed architecture & component flows
â”‚   â”œâ”€â”€ API_DOCUMENTATION.md     # OpenAPI route documentation
â”‚   â”œâ”€â”€ DEPLOYMENT_GUIDE.md      # Deployment instructions (Local, Render, Netlify)
â”‚   â”œâ”€â”€ EMBEDDINGS.md            # Multi-channel embedding & indexing guide
â”‚   â””â”€â”€ PROJECT_PLAN.md          # Completed development phases (1â€“8)
â”‚
â”œâ”€â”€ frontend/
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ components/          # GovtChatArea, HelpdeskContactCard, Header, Sidebar
â”‚   â”‚   â”œâ”€â”€ services/            # API client and streaming handlers
â”‚   â”‚   â”œâ”€â”€ types/               # TypeScript interfaces
â”‚   â”‚   â””â”€â”€ App.tsx              # Main application shell
â”‚   â”œâ”€â”€ package.json
â”‚   â””â”€â”€ vite.config.ts
â”‚
â”œâ”€â”€ Nessery_dumpings/            # Archived scratch scripts & developer utility files
â”‚
â”œâ”€â”€ .env.example                 # Environment configuration template
â”œâ”€â”€ netlify.toml                 # Netlify SPA routing rules
â”œâ”€â”€ requirements.txt             # Root requirements pointer
â””â”€â”€ run.bat                      # One-click Windows development launcher
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

### 3. Build the Structured Manual Index
The current 27-page CSV manual is already structured. Rebuild its cleaned embeddings directly into `data/structured/`.

**Bash:**
```bash
cd "/e/E-gp Project manual"
source .venv/Scripts/activate
python backend/scripts/build_csv_embeddings.py --offline
python backend/scripts/build_faiss_index.py --chunks data/structured/metadata/pdf_manual.json
```

**PowerShell:**
```powershell
& ".venv\Scripts\python.exe" backend\scripts\build_csv_embeddings.py --offline
& ".venv\Scripts\python.exe" backend\scripts\build_faiss_index.py --chunks data\structured\metadata\pdf_manual.json
```

Generated files are saved under `data/structured/indexes/` and `data/structured/metadata/`. Chat reports are saved under `documentation/interactions/`.

Execute the Windows launcher:
```powershell
.\run.bat
```
Or start manually:

**Terminal 1 â€” Backend:**
```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 â€” Frontend:**
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

- ðŸ“ž **e-GP Helpdesk Hotline:** `16575` *(from any mobile network in Bangladesh)*
- â˜Žï¸ **Telephone Support:** `+880 9609112233` / `+880 1762625528â€“31`
- âœ‰ï¸ **Email Support:** `helpdesk@eprocure.gov.bd` / `e-gphelpdesk@cptu.gov.bd`
- ðŸŒ **Official Portal:** [eprocure.gov.bd](https://www.eprocure.gov.bd)
- ðŸ¢ **Authority:** Bangladesh Public Procurement Authority (BPPA) / CPTU, IMED, Ministry of Planning
