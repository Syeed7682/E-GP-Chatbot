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
    from app.services.csv_loader import csv_loader

    print(f"=== Starting e-GP Manual Ingestion from CSV Data Sources ===")
    
    # 1. Load Procuring Entity Manual pages from CSV
    pe_pages = csv_loader.load_manual_pages()
    if not pe_pages:
        print("[ingest_manual] Fallback to pdf_loader for PE manual...")
        pe_pages = pdf_loader.load_pages()
    print(f"Loaded {len(pe_pages)} pages from Procuring Entity Manual CSV.")

    # 2. Load Tenderer Registration Manual pages from CSV
    reg_pages = csv_loader.load_registration_pages()
    print(f"Loaded {len(reg_pages)} pages from Tenderer Registration Manual CSV.")

    all_chunks = []
    chunk_counter = 1

    # Chunk PE manual pages
    for page in pe_pages:
        page_chunks = chunker.chunk_page(page)
        for c in page_chunks:
            c["chunk_id"] = chunk_counter
            c["source"] = "Official e-GP Procuring Entity Manual"
            all_chunks.append(c)
            chunk_counter += 1

    # Chunk Registration manual pages
    for page in reg_pages:
        page_chunks = chunker.chunk_page(page)
        for c in page_chunks:
            c["chunk_id"] = chunk_counter
            c["source"] = "Official e-GP Tenderer Registration Manual"
            all_chunks.append(c)
            chunk_counter += 1

    out_file = settings.PROCESSED_DATA_PATH
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Ingestion complete: Generated {len(all_chunks)} chunks saved to {out_file}")

if __name__ == "__main__":
    run_ingestion()

