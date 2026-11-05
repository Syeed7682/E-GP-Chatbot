# e-GP Manual Chatbot & Multimodal RAG — Documents & Specifications

This directory contains the system documentation, user manuals, design decisions, and tracking notes for the **e-GP Manual Chatbot**.

---

## 📁 Document Inventory

| Document | Description | Location |
| :--- | :--- | :--- |
| **Official PE Manual (PDF)** | 543-page electronic Government Procurement (e-GP) Procuring Entity manual (1 Feb 2026 edition) | `data/raw/e-GP System User Manual - Procuring Entity User 1 February 2026.pdf` |
| **Architecture Guide** | Overview of system architecture, vector pipeline, offline sync engine, and REST APIs | `documents/PROJECT_ARCHITECTURE.md` |
| **Thinking Process & Design Log** | Design and implementation reasoning for multimodal RAG, chunking strategies, and offline-first sync | `documents/thinking_process.txt` |
| **Milestone Log** | Completed tasks, verification steps, and changelog | `documents/havedone.txt` |

---

## 🏛️ System Core Modules

1. **Frontend (`frontend/`)**: Modern React 19 + Tailwind CSS + Lucide + Vite interface with portal screenshot diagnostics, verified citations, offline sync status, and responsive modal screens. Also includes Streamlit UI in `frontend/streamlit/`.
2. **Backend (`backend/`)**: FastAPI REST API providing `/api/chat`, `/api/chat/health`, `/api/sync/*`, document chunking, and FAISS vector retrieval.
3. **AI Models (`ai_models/`)**: Model definitions and registries for BGE-M3 (multimodal embeddings) and Gemini 2.0 Flash / Qwen2.5-VL / Local Synthesizer.
4. **Data (`data/`)**: Raw PDFs (`data/raw/`), preprocessed chunks (`data/processed/chunks.json`), extracted screenshots (`data/extracted_images/`), and FAISS vector index (`data/faiss_index/`).

