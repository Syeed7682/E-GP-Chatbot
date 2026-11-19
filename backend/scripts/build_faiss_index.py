"""
Script: Build FAISS Index
Loads chunks from data/processed/chunks.json, generates embeddings via BGE-M3,
and creates the FAISS vector index (data/faiss_index/index.faiss and metadata.json).

Usage:
    python scripts/build_faiss_index.py
"""
import os
import sys
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.text_chunker import load_chunks
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service

def main():
    parser = argparse.ArgumentParser(description="Build FAISS vector index from chunks.json.")
    parser.add_argument("--chunks", default="data/faiss_index/metadata.json", help="Path to chunk records JSON")
    parser.add_argument("--index-path", default="data/faiss_index/index.faiss", help="Path to save index.faiss")
    parser.add_argument("--metadata-path", default="data/faiss_index/metadata.json", help="Path to save metadata.json")
    args = parser.parse_args()

    print("========================================")
    print(" e-GP Manual Chatbot: Build FAISS Index")
    print("========================================")

    if not embedding_service.semantic_search_available:
        raise RuntimeError(
            "Cannot build the semantic FAISS index while only offline fallback "
            "embeddings are available. Initialize the configured embedding model first."
        )
    
    # 1. Load chunks
    if not os.path.exists(args.chunks):
        print(f"[!] Chunks file not found at: {args.chunks}")
        print("    Please run 'python scripts/ingest_documents.py' first.")
        sys.exit(1)

    chunks = load_chunks(args.chunks)
    if not chunks:
        print("[!] Chunks file is empty. Ingest valid documents first.")
        sys.exit(1)

    for chunk in chunks:
        if "text" not in chunk:
            chunk["text"] = chunk.get("content", "")
        if "page" not in chunk:
            chunk["page"] = chunk.get("page_number", 0)

    print(f"1. Loaded {len(chunks)} chunks from: {args.chunks}")

    # 2. Compute Multimodal Vector Embeddings (Text + Screenshots)
    print(f"2. Generating text-only embeddings with '{embedding_service.model_name}'...")
    embeddings = embedding_service.embed_chunks(chunks)

    # 4. Build FAISS index
    print("3. Building FAISS IndexFlatIP (Cosine Similarity)...")
    faiss_service.build_index(embeddings, chunks)

    # 5. Save to disk
    print(f"4. Saving FAISS index to '{args.index_path}' and metadata to '{args.metadata_path}'...")
    faiss_service.save(args.index_path, args.metadata_path)

    print("========================================")
    print(" Index built and saved successfully!")
    print(f" Total indexed vectors: {len(chunks)}")
    print(" You can now launch the API server or frontend:")
    print("   uvicorn app.main:app --reload")
    print("   npm run dev --prefix frontend")
    print("========================================")

if __name__ == "__main__":
    main()

