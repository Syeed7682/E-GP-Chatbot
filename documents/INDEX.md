# e-GP Manual Assistant Documentation Index

This directory contains the technical documentation, architectural specifications, and operational guides for the **Bangladesh e-GP Official Manual Assistant (Proca)**.

The assistant is an enterprise-grade multimodal Retrieval-Augmented Generation (RAG) platform serving both **Procuring Entities (PEs)** and **Tenderers / Contractors / Vendors** across all stages of public procurement under Public Procurement Act (PPA 2006) and Public Procurement Rules (PPR 2008).

---

## Documentation Directory

| Document | Description |
|---|---|
| [`PROJECT_ARCHITECTURE.md`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_ARCHITECTURE.md) | High-level system architecture, dual-audience (PE & Tenderer) multi-channel RAG pipeline (BGE-M3 + BM25 + SigLIP + RRF + BGE-Reranker), CSV data pipeline, and interactive UI action components. |
| [`PROJECT_ARCHITECTURE.puml`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_ARCHITECTURE.puml) | **PlantUML architecture diagram specification** defining system components, dual-channel data flow, and multi-channel retrieval pipelines. |
| [`SIMPLE_ARCHITECTURE.puml`](file:///e:/E-gp%20Project%20manual/documents/SIMPLE_ARCHITECTURE.puml) | **Simplified PlantUML sequence diagram** showing end-to-end query lifecycle, failover chain, and Helpdesk contact escalation. |
| [`API_DOCUMENTATION.md`](file:///e:/E-gp%20Project%20manual/documents/API_DOCUMENTATION.md) | Complete OpenAPI endpoint specifications, request/response schemas, chunk image streaming routes, diagnostic APIs, and Helpdesk contact escalation. |
| [`DEPLOYMENT_GUIDE.md`](file:///e:/E-gp%20Project%20manual/documents/DEPLOYMENT_GUIDE.md) | Operational guide for local execution (`run.bat`), Render persistent disk configuration (`/var/data`), Netlify frontend deployment, and zero-downtime index migration. |
| [`EMBEDDINGS.md`](file:///e:/E-gp%20Project%20manual/documents/EMBEDDINGS.md) | Dense & sparse embedding mechanics, versioned FAISS index structure (`v001`/`active_version.json`), SQLite metadata store, and index validation scripts. |
| [`PROJECT_PLAN.md`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_PLAN.md) | Implementation milestones, audit results, completed phases (1–8), acceptance criteria, and roadmap. |
| [`INDEX.md`](file:///e:/E-gp%20Project%20manual/documents/INDEX.md) | This master documentation index. |

---

## Archived Developer Logs

Historical scratchpads, preliminary extraction scripts, and developer notes have been safely consolidated into:
- 📁 **[`Nessery_dumpings/`](file:///e:/E-gp%20Project%20manual/Nessery_dumpings)** (archived scratch utilities, `havedone.txt`, `thinking_process.txt`, and one-off extraction tools).
