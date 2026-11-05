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
    parser.add_argument("--chunks", default="data/processed/chunks.json", help="Path to processed chunks.json")
    parser.add_argument("--index-path", default="data/faiss_index/index.faiss", help="Path to save index.faiss")
    parser.add_argument("--metadata-path", default="data/faiss_index/metadata.json", help="Path to save metadata.json")
    args = parser.parse_args()

    print("========================================")
    print(" e-GP Manual Chatbot: Build FAISS Index")
    print("========================================")
    
    # 1. Load chunks
    if not os.path.exists(args.chunks):
        print(f"[!] Chunks file not found at: {args.chunks}")
        print("    Please run 'python scripts/ingest_documents.py' first.")
        sys.exit(1)

    chunks = load_chunks(args.chunks)
    if not chunks:
        print("[!] Chunks file is empty. Ingest valid documents first.")
        sys.exit(1)

    print(f"1. Loaded {len(chunks)} chunks from: {args.chunks}")

    # 2. Compute Multimodal Vector Embeddings (Text + Screenshots)
    print("2. Generating multimodal embeddings (Text + Images) using BGE-Visualized-M3...")
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
    print("   streamlit run frontend/streamlit_app.py")
    print("========================================")

if __name__ == "__main__":
    main()

