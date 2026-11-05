"""
Manual Ingestion Script (backend/scripts/ingest_manual.py).
Extracts all pages from the 543-page e-GP Procuring Entity User Manual.
"""
import os
import sys
import json
from pathlib import Path

# Setup sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings
from app.services.pdf_loader import pdf_loader
from app.services.chunker import chunker

def run_ingestion():
    print(f"=== Starting e-GP Manual Ingestion from '{pdf_loader.pdf_path}' ===")
    pages = pdf_loader.load_pages()
    print(f"Extracted text from {len(pages)} pages.")

    all_chunks = []
    chunk_counter = 1
    for page in pages:
        page_chunks = chunker.chunk_page(page)
        for c in page_chunks:
            c["chunk_id"] = chunk_counter
            c["source"] = "Official e-GP Procuring Entity Manual"
            all_chunks.append(c)
            chunk_counter += 1

    out_file = settings.PROCESSED_DATA_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Ingestion complete: Generated {len(all_chunks)} chunks saved to {out_file}")

if __name__ == "__main__":
    run_ingestion()

