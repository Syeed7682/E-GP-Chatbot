"""
FAISS Index Builder Script (backend/scripts/build_index.py).
Embeds processed chunks with BGE-M3 and builds a FAISS IndexFlatIP index.
"""
import os
import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service

def run_build_index():
    print("=== Building FAISS Index with BGE-M3 Embeddings ===")
    chunks_path = settings.PROCESSED_DATA_PATH
    if not chunks_path.exists():
        print(f"Error: Processed chunks not found at {chunks_path}")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks. Generating embeddings...")
    faiss_service.build_and_save(chunks, embedding_service)
    print("Index build completed successfully.")

if __name__ == "__main__":
    run_build_index()

