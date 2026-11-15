"""
Master Ingestion & Index Pipeline (backend/scripts/ingest_all.py).
Single entry point for the full e-GP manual ingestion and versioned indexing pipeline:
1. Validate source files (PDF and Q&A)
2. Extract PDF structured content
3. Extract and normalize Q&A pairs
4. Generate structured text chunks
5. Extract and render visual regions
6. Build text embeddings and FAISS index
7. Build Q&A FAISS index
8. Build visual embeddings index
9. Build BM25 lexical index
10. Populate SQLite metadata store
11. Validate index bundle
12. Publish new version atomically
"""
import argparse
import hashlib
import json
import logging
import os
import sys
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import (
    DATA_DIR, RAW_DIR, PROCESSED_DIR, INDEX_DIR, IMAGE_DIR,
    TEXT_MODEL, VISUAL_MODEL, TEXT_DIM, VISUAL_DIM,
)
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.qa_parser import parse_qa_corpus
from app.ingestion.page_renderer import render_pages
from app.ingestion.image_extractor import extract_images_from_pdf
from app.chunking.structure_chunker import create_pdf_chunks
from app.chunking.qa_chunker import prepare_qa_records
from app.embeddings.text_embedder import TextEmbedder, embed_in_batches
from app.embeddings.visual_embedder import VisualEmbedder
from app.indexing.faiss_builder import build_faiss_index
from app.indexing.metadata_store import MetadataStore
from app.indexing.bm25_builder import build_bm25_index
from app.indexing.index_manager import IndexManager

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger("ingest_all")


def compute_file_hash(path: Path) -> str:
    """Computes SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="e-GP Manual End-to-End Ingestion Pipeline")
    parser.add_argument("--version", type=str, default=None, help="Target version name (e.g. v002)")
    parser.add_argument("--activate", action="store_true", help="Automatically activate the new version if valid")
    parser.add_argument("--batch-size", type=int, default=8, help="Batch size for embedding models")
    parser.add_argument("--render-pages", action="store_true", help="Render all visual PDF pages to PNG")
    args = parser.parse_args()

    logger.info("=== Starting e-GP Manual Ingestion Pipeline ===")

    # 1. Validate Source Documents
    pdf_candidates = [
        RAW_DIR / "egp_manual.pdf",
        DATA_DIR / "raw" / "egp_manual.pdf",
        BACKEND_DIR.parent / "data" / "raw" / "egp_manual.pdf",
    ]
    pdf_path = next((p for p in pdf_candidates if p.exists()), None)
    if not pdf_path:
        logger.error("Could not find egp_manual.pdf in any raw directory!")
        sys.exit(1)

    qa_txt_candidates = [
        RAW_DIR / "e-GP System Q&A.txt",
        DATA_DIR / "raw" / "e-GP System Q&A.txt",
        BACKEND_DIR.parent / "data" / "raw" / "e-GP System Q&A.txt",
    ]
    qa_txt_path = next((p for p in qa_txt_candidates if p.exists()), None)

    qa_docx_candidates = [
        RAW_DIR / "e-GP System Q&A .docx",
        DATA_DIR / "raw" / "e-GP System Q&A .docx",
        BACKEND_DIR.parent / "data" / "raw" / "e-GP System Q&A .docx",
    ]
    qa_docx_path = next((p for p in qa_docx_candidates if p.exists()), None)

    logger.info("Found source PDF: %s (Size: %.2f MB)", pdf_path, pdf_path.stat().st_size / (1024 * 1024))
    if qa_txt_path:
        logger.info("Found supplemental Q&A: %s", qa_txt_path)

    # 2. Setup Version Target Directory
    mgr = IndexManager(INDEX_DIR)
    if args.version:
        target_version = args.version
        target_dir = mgr.get_version_dir(target_version)
    else:
        target_version, target_dir = mgr.create_next_version_dir()

    logger.info("Target index version: %s (Directory: %s)", target_version, target_dir)

    # 3. Extract PDF Content
    logger.info("Phase 1: Extracting structured PDF content...")
    pdf_parse_result = parse_pdf(pdf_path, PROCESSED_DIR)
    pages_data = pdf_parse_result.get("pages", [])
    if not pages_data and (PROCESSED_DIR / "document.json").exists():
        try:
            pages_data = json.loads((PROCESSED_DIR / "document.json").read_text(encoding="utf-8"))
        except Exception:
            pass

    logger.info("Parsed %d pages from manual", len(pages_data))

    # 4. Extract and Normalize Q&A
    logger.info("Phase 2: Extracting supplemental Q&A pairs...")
    raw_qa_records = parse_qa_corpus(qa_txt_path, qa_docx_path)
    qa_chunks = prepare_qa_records(raw_qa_records)
    logger.info("Prepared %d Q&A chunks", len(qa_chunks))

    # 5. Generate Text Chunks
    logger.info("Phase 3: Generating structure-aware text chunks...")
    pdf_chunks = create_pdf_chunks(pages_data)
    logger.info("Generated %d PDF text chunks", len(pdf_chunks))

    # Save chunks to processed
    (PROCESSED_DIR / "pdf_chunks.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in pdf_chunks), encoding="utf-8"
    )
    (PROCESSED_DIR / "qa_chunks.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in qa_chunks), encoding="utf-8"
    )

    # 6. Extract / Render Visual Images
    if args.render_pages:
        logger.info("Phase 4: Rendering visual pages at 120 DPI...")
        page_images_dir = IMAGE_DIR / "pages"
        render_pages(pdf_path, page_images_dir, dpi=120, only_visual=True)

    crops_dir = IMAGE_DIR / "crops"
    extract_images_from_pdf(pdf_path, crops_dir)

    # 7. Initialize SQLite Metadata Store
    logger.info("Phase 5: Populating SQLite metadata store in %s...", target_dir)
    db_path = target_dir / "metadata.db"
    if db_path.exists():
        db_path.unlink()
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
    logger.info("Stored %d records in SQLite metadata.db", len(all_records))

    # 8. Build Text Embeddings & FAISS Index
    logger.info("Phase 6: Computing BGE-M3 text embeddings (batch_size=%d)...", args.batch_size)
    text_embedder = TextEmbedder()
    pdf_texts = [c.get("text", "") for c in pdf_chunks]
    pdf_vectors = embed_in_batches(pdf_texts, text_embedder, batch_size=args.batch_size)

    pdf_faiss_path = target_dir / "pdf_text.faiss"
    pdf_ids = np.array([c["vector_id"] for c in pdf_chunks], dtype=np.int64)
    build_faiss_index(pdf_vectors, records=pdf_chunks, output_path=pdf_faiss_path, ids=pdf_ids)

    # 9. Build Q&A FAISS Index
    if qa_chunks:
        logger.info("Phase 7: Computing Q&A text embeddings...")
        qa_texts = [c.get("retrieval_text") or c.get("question", "") for c in qa_chunks]
        qa_vectors = embed_in_batches(qa_texts, text_embedder, batch_size=args.batch_size)
        qa_faiss_path = target_dir / "qa.faiss"
        qa_ids = np.array([c["vector_id"] for c in qa_chunks], dtype=np.int64)
        build_faiss_index(qa_vectors, records=qa_chunks, output_path=qa_faiss_path, ids=qa_ids)

    # 10. Build BM25 Index
    logger.info("Phase 8: Building BM25 lexical keyword index...")
    bm25_path = target_dir / "bm25.pkl"
    build_bm25_index(all_records, output_path=bm25_path)

    # 11. Write Manifest
    manifest_data = {
        "version": target_version,
        "source_pdf": str(pdf_path.name),
        "source_pdf_hash": compute_file_hash(pdf_path),
        "text_model": TEXT_MODEL,
        "visual_model": VISUAL_MODEL,
        "text_dimension": TEXT_DIM,
        "visual_dimension": VISUAL_DIM,
        "pdf_chunks_count": len(pdf_chunks),
        "qa_chunks_count": len(qa_chunks),
        "total_records": len(all_records),
    }
    mgr.write_manifest(target_version, manifest_data)
    logger.info("Manifest created for %s", target_version)

    # 12. Validate Version
    logger.info("Phase 9: Validating index bundle...")
    validation = mgr.validate_version(target_version)
    if not validation["passed"]:
        logger.error("Validation failed! Errors: %s", validation["errors"])
        sys.exit(1)
    logger.info("Validation passed successfully! Stats: %s", validation["stats"])

    # 13. Activate if requested
    if args.activate:
        mgr.activate_version(target_version)
        logger.info("Successfully activated version: %s as active production index!", target_version)
    else:
        logger.info("Version %s is ready for evaluation (active version remains %s).", target_version, mgr.get_active_version())

    logger.info("=== Ingestion Pipeline Completed Successfully ===")


if __name__ == "__main__":
    import numpy as np
    main()

