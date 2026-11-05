"""
Script: Ingest Documents
Reads PDF manuals from data/raw/, extracts text, chunks it, and saves data/processed/chunks.json.

Usage:
    python scripts/ingest_documents.py
"""
import os
import sys
import argparse

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.document_loader import load_all_documents
from app.services.text_chunker import chunk_documents, save_chunks

def main():
    parser = argparse.ArgumentParser(description="Ingest e-GP manual PDFs into text chunks.")
    parser.add_argument("--raw-dir", default="data/raw", help="Folder containing raw PDF files")
    parser.add_argument("--output", default="data/processed/chunks.json", help="Path to save chunks.json")
    parser.add_argument("--chunk-size", type=int, default=450, help="Character size per chunk")
    parser.add_argument("--overlap", type=int, default=80, help="Character overlap between chunks")
    args = parser.parse_args()

    print("========================================")
    print(" e-GP Manual Chatbot: Ingest Documents")
    print("========================================")
    print(f"1. Scanning for PDFs in: {args.raw_dir}")
    documents = load_all_documents(args.raw_dir)
    if not documents:
        print("[!] No documents found. Please place PDF files in data/raw/ and try again.")
        sys.exit(1)

    print(f"2. Chunking {len(documents)} page(s) (size={args.chunk_size}, overlap={args.overlap})...")
    chunks = chunk_documents(documents, chunk_size=args.chunk_size, chunk_overlap=args.overlap)

    print(f"3. Saving processed chunks to: {args.output}")
    save_chunks(chunks, args.output)

    print("========================================")
    print(f" Success! Created {len(chunks)} chunks.")
    print(" Next step: Run 'python scripts/build_faiss_index.py'")
    print("========================================")

if __name__ == "__main__":
    main()

