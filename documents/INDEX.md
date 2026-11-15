# e-GP Manual Assistant Documentation Index

This directory contains the technical documentation, architectural specifications, and operational guides for the **Bangladesh e-GP Official Manual Assistant**.

---

## Documentation Directory

| Document | Description |
|---|---|
| [`PROJECT_ARCHITECTURE.md`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_ARCHITECTURE.md) | High-level system architecture, multi-channel RAG pipeline (BGE-M3 + BM25 + SigLIP + RRF + BGE-Reranker), inference failover, and structured chunk image data flow. |
| [`PROJECT_ARCHITECTURE.puml`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_ARCHITECTURE.puml) | **PlantUML architecture diagram specification** defining the complete system components, data flow, endpoints, and multi-channel retrieval pipelines. |
| [`SIMPLE_ARCHITECTURE.puml`](file:///e:/E-gp%20Project%20manual/documents/SIMPLE_ARCHITECTURE.puml) | **Simplified PlantUML sequence diagram** showing end-to-end user query lifecycle, failover chain, and Helpdesk fallback. |
| [`API_DOCUMENTATION.md`](file:///e:/E-gp%20Project%20manual/documents/API_DOCUMENTATION.md) | Complete OpenAPI endpoint specifications, request/response JSON schemas, chunk image streaming routes, diagnostic APIs, and Helpdesk contact escalation. |
| [`DEPLOYMENT_GUIDE.md`](file:///e:/E-gp%20Project%20manual/documents/DEPLOYMENT_GUIDE.md) | Operational guide for local execution (`run.bat`), Render persistent disk configuration (`/var/data`), Netlify frontend deployment, and zero-downtime index migration. |
| [`EMBEDDINGS.md`](file:///e:/E-gp%20Project%20manual/documents/EMBEDDINGS.md) | Dense & sparse embedding mechanics, versioned FAISS index structure (`v001`/`active_version.json`), SQLite metadata store, and index validation scripts. |
| [`PROJECT_PLAN.md`](file:///e:/E-gp%20Project%20manual/documents/PROJECT_PLAN.md) | Implementation milestones, audit results, completed phases (1–7), acceptance criteria, and future roadmap items. |
| [`havedone.txt`](file:///e:/E-gp%20Project%20manual/documents/havedone.txt) | Detailed chronological log of implemented modules, verified test results, and bug fixes. |
| [`thinking_process.txt`](file:///e:/E-gp%20Project%20manual/documents/thinking_process.txt) | Engineering design rationale, architectural trade-offs, and fallback strategies. |
| [`INDEX.md`](file:///e:/E-gp%20Project%20manual/documents/INDEX.md) | This master documentation index. |
