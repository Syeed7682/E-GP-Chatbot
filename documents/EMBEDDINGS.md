# Embeddings Documentation

This guide explains **how to generate embeddings for the e‑GP manual** and how the **question‑answering (QA) pipeline consumes those embeddings**.

---

## 1. Overview
| Component | Purpose |
|-----------|---------|
| **Raw Manual** | PDF file containing the official e‑GP Procuring Entity User Manual (usually `data/raw/e‑GP System User Manual.pdf`). |
| **Chunking** | The PDF is split into ~500‑word text chunks so that each chunk can be embedded individually. |
| **Embedding Service** (`backend/app/services/embedding_service.py`) | Uses the **BGE‑M3** model (or any configured model) to create a 1024‑dimensional vector for each chunk. |
| **FAISS Index** (`data/faiss_index/index.faiss`) | Stores all chunk vectors for fast similarity search. |
| **QA Retrieval** (`backend/app/services/retrieval_service.py`) | Looks up the nearest vectors in the FAISS index and returns the original text chunks to the LLM. |

---

## 2. Prerequisites
1. **Python 3.10+** with the project's virtual environment activated.
2. **`requirements.txt`** installed (`pip install -r backend/requirements.txt`).
3. **GPU (optional)** – needed for the local `Qwen2.5‑VL‑3B‑Instruct` model; otherwise the system falls back to the Groq API.
4. **Environment variables** set in `.env` (see `DEPLOYMENT_GUIDE.md`). At a minimum:
   ```dotenv
   VECTOR_DB=faiss
   EMBEDDING_MODEL=BAAI/bge-m3
   USE_LOCAL_LLM=true
   LOCAL_LLM_MODEL=Qwen/Qwen2.5-VL-3B-Instruct
   ```

---

## 3. Preparing the Raw Manual
1. Place the official PDF inside the **raw data folder**:
   ```text
   e:/E-gp Project manual/data/raw/e‑GP System User Manual.pdf
   ```
2. Verify the file name matches the path referenced in `embedding_service.py` (the script looks for `*.pdf` files under `data/raw`).
3. (Optional) If you have multiple PDFs, put each in `data/raw/` – the service will process all of them.

---

## 4. Generating Chunk Files
Run the **chunking utility** which extracts text and creates `chunks.json`:
```bash
python -m app.services.text_chunker --input data/raw --output data/processed/chunks.json
```
*What happens:* 
- The PDF is read page‑by‑page using `pypdf`. 
- Text is cleaned (whitespace normalization, removal of TOC pages ≤ 5). 
- Overlapping windows (default 200 tokens) are applied to preserve context. 
- Each chunk gets a unique `chunk_id`, source PDF name, page number, and the raw text snippet.

The resulting file (`data/processed/chunks.json`) looks like:
```json
[{
  "chunk_id": "c001",
  "source": "e‑GP System User Manual.pdf",
  "page": 12,
  "text": "...excerpt..."
}, ...]
```

---

## 5. Creating Embeddings
The **embedding service** reads `chunks.json` and writes two outputs:
- `data/faiss_index/index.faiss` – the binary FAISS index.
- `data/faiss_index/metadata.json` – a mapping from FAISS vector IDs to the original chunk metadata.

Run the script:
```bash
python -m app.services.embedding_service --build-index
```
### What the script does
1. **Load the BGE‑M3 model** (or the model specified in `EMBEDDING_MODEL`).
2. Iterate over each chunk and compute a **1024‑dim L2‑normalized** vector.
3. Insert vectors into a **FAISS `IndexFlatIP`** (inner‑product) index – this behaves as cosine similarity because vectors are normalized.
4. Persist the index (`index.faiss`) and accompanying metadata (`metadata.json`).

> **Tip:** If you change the embedding model, delete the existing `faiss_index/` folder first to avoid mixing vectors of different dimensionalities.

---

## 6. How QA Consumes the Embeddings
When a user asks a question, the following flow occurs (see `retrieval_service.py`):
1. **Question Embedding** – The same embedding model is used to embed the incoming query.
2. **FAISS Search** – The query vector is compared against the stored vectors; the top‑k nearest chunk IDs are returned.
3. **Hybrid Fusion (optional)** – If keyword‑based BM25 results are also requested, their scores are linearly combined (`0.7 * dense + 0.3 * bm25`).
4. **Chunk Retrieval** – Using `metadata.json`, the service fetches the original text snippets for the selected chunk IDs.
5. **Context Assembly** – The snippets are concatenated into a numbered list with page citations, then passed to the LLM (`llm_service.py`).
6. **Answer Generation** – The LLM generates a grounded answer, appending the source references.

The **frontend** simply displays the answer and the cited pages; no additional processing is required on the client side.

---

## 7. Re‑building the Index (e.g., after PDF updates)
If the manual PDF changes, repeat steps **3–5**. A convenient one‑click option exists in the UI (Streamlit or React) under **“Re‑Index Manuals”**, which internally runs the same command.

---

## 8. Troubleshooting
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `RuntimeError: Model dimension mismatch` | Index was built with a different model than the current one. | Delete `data/faiss_index/` and rebuild the index with the desired model. |
| No results returned from `/api/chat` | FAISS index file missing or corrupted. | Verify `data/faiss_index/index.faiss` exists; run `embedding_service --build-index` again. |
| Slow response (>5 s) | GPU not available and the system falls back to Groq, hitting rate limits. | Set `USE_LOCAL_LLM=false` and ensure a valid `GROQ_API_KEY` is present, or upgrade the Groq plan. |

---

## 9. References
- **BGE‑M3** model documentation: https://huggingface.co/BAAI/bge-m3
- **FAISS**: https://github.com/facebookresearch/faiss
- **Qwen 2.5‑VL‑3B‑Instruct**: https://github.com/QwenLM/Qwen2.5

---

*End of document*
