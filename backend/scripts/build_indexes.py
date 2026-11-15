"""
Build Indexes Script (backend/scripts/build_indexes.py).
Constructs FAISS, BM25, and SQLite metadata indices from existing processed chunks.
"""
import argparse
import json
import logging
import sys
from pathlib import Path
import numpy as np

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import INDEX_DIR, PROCESSED_DIR
from app.embeddings.text_embedder import TextEmbedder, embed_in_batches
from app.indexing.faiss_builder import build_faiss_index
from app.indexing.metadata_store import MetadataStore
from app.indexing.bm25_builder import build_bm25_index
from app.indexing.index_manager import IndexManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("build_indexes")


def main():
    parser = argparse.ArgumentParser(description="Build FAISS and BM25 Indexes")
    parser.add_argument("--version", type=str, default="v001", help="Version name to build (e.g. v001, v002)")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for embeddings")
    args = parser.parse_args()

    mgr = IndexManager(INDEX_DIR)
    v_dir = mgr.get_version_dir(args.version)
    logger.info("Building indexes for version: %s in %s", args.version, v_dir)

    pdf_chunks_file = PROCESSED_DIR / "pdf_chunks.jsonl"
    qa_chunks_file = PROCESSED_DIR / "qa_chunks.jsonl"
    legacy_chunks_file = PROCESSED_DIR / "chunks.json"

    pdf_chunks = []
    qa_chunks = []

    if pdf_chunks_file.exists():
        pdf_chunks = [json.loads(line) for line in pdf_chunks_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif legacy_chunks_file.exists():
        pdf_chunks = json.loads(legacy_chunks_file.read_text(encoding="utf-8"))

    if qa_chunks_file.exists():
        qa_chunks = [json.loads(line) for line in qa_chunks_file.read_text(encoding="utf-8").splitlines() if line.strip()]

    logger.info("Loaded %d PDF chunks, %d QA chunks", len(pdf_chunks), len(qa_chunks))

    db_path = v_dir / "metadata.db"
    metadata_store = MetadataStore(db_path)

    all_records = []
    current_vid = 0
    for chunk in pdf_chunks:
        chunk["vector_id"] = current_vid
        chunk["namespaced_id"] = f"PDF:{current_vid}"
        all_records.append(chunk)
        current_vid += 1

    for chunk in qa_chunks:
        chunk["vector_id"] = current_vid
        chunk["namespaced_id"] = f"QA:{current_vid}"
        all_records.append(chunk)
        current_vid += 1

    metadata_store.insert_many(all_records)
    logger.info("Inserted %d records into SQLite metadata.db", len(all_records))

    text_embedder = TextEmbedder()

    # 1. PDF Text Index
    if pdf_chunks:
        pdf_texts = [c.get("text") or c.get("content", "") for c in pdf_chunks]
        pdf_vectors = embed_in_batches(pdf_texts, text_embedder, batch_size=args.batch_size)
        pdf_ids = np.array([c["vector_id"] for c in pdf_chunks], dtype=np.int64)
        build_faiss_index(pdf_vectors, records=pdf_chunks, output_path=v_dir / "pdf_text.faiss", ids=pdf_ids)

    # 2. QA Index
    if qa_chunks:
        qa_texts = [c.get("retrieval_text") or c.get("question", "") for c in qa_chunks]
        qa_vectors = embed_in_batches(qa_texts, text_embedder, batch_size=args.batch_size)
        qa_ids = np.array([c["vector_id"] for c in qa_chunks], dtype=np.int64)
        build_faiss_index(qa_vectors, records=qa_chunks, output_path=v_dir / "qa.faiss", ids=qa_ids)

    # 3. BM25 Index
    build_bm25_index(all_records, output_path=v_dir / "bm25.pkl")

    # 4. Manifest
    mgr.write_manifest(args.version, {
        "version": args.version,
        "pdf_chunks_count": len(pdf_chunks),
        "qa_chunks_count": len(qa_chunks),
        "total_records": len(all_records),
    })

    logger.info("Indexes built successfully for %s", args.version)


if __name__ == "__main__":
    main()

