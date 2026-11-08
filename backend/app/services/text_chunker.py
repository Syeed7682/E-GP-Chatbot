"""
Text Chunker Service.
Splits extracted document text into overlapping chunks suitable for semantic embedding.
"""
import json
import os
from typing import List, Dict

def split_text_with_overlap(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[str]:
    """
    Splits a single text string into overlapping chunks.
    Ensures that chunks break at whitespace when possible to keep words intact.
    
    Args:
        text: Input string.
        chunk_size: Target character count per chunk.
        chunk_overlap: Number of characters to overlap between adjacent chunks.
        
    Returns:
        List of text chunks.
    """
    if not text:
        return []

    # If the text is shorter than chunk_size, return it directly
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        
        # If we haven't reached the end of the text, try to find a natural boundary
        if end < text_length:
            # Look backwards from 'end' for a space or newline within the last 50 chars
            boundary = text.rfind(' ', start, end)
            if boundary == -1 or boundary <= start:
                boundary = text.rfind('\n', start, end)
            
            # If a boundary was found, snap to it
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward, stepping by (end - chunk_overlap)
        start = end - chunk_overlap
        if start < 0 or start >= text_length or (chunks and start <= (end - chunk_size)):
            start = end
        elif start > 0 and not text[start - 1].isspace() and not text[start].isspace():
            while start < text_length and not text[start].isspace():
                start += 1
            while start < text_length and text[start].isspace():
                start += 1

    return chunks

def chunk_documents(documents: List[Dict], chunk_size: int = 500, chunk_overlap: int = 100) -> List[Dict]:
    """
    Takes document pages and splits them into structured chunks with metadata.
    
    Args:
        documents: List of dicts with {"source": ..., "page": ..., "text": ...}
        chunk_size: Character size per chunk.
        chunk_overlap: Overlapping character count.
        
    Returns:
        List of chunk dicts:
        [
            {
                "chunk_id": 0,
                "source": "egp_user_manual.pdf",
                "page": 1,
                "text": "..."
            },
            ...
        ]
    """
    all_chunks = []
    chunk_counter = 0

    for doc in documents:
        source = doc.get("source", "unknown")
        page = doc.get("page", 1)
        raw_text = doc.get("text", "")
        img_path = doc.get("image_path")

        text_pieces = split_text_with_overlap(raw_text, chunk_size, chunk_overlap)
        for piece in text_pieces:
            all_chunks.append({
                "chunk_id": chunk_counter,
                "source": source,
                "page": page,
                "text": piece,
                "image_path": img_path,
                "content_type": "multimodal" if img_path else "text"
            })
            chunk_counter += 1

    print(f"[text_chunker] Created {len(all_chunks)} chunks from {len(documents)} page(s).")
    return all_chunks

def save_chunks(chunks: List[Dict], output_path: str = "data/processed/chunks.json") -> None:
    """Saves processed chunks to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"[text_chunker] Saved {len(chunks)} chunks to '{output_path}'.")

def load_chunks(input_path: str = "data/processed/chunks.json") -> List[Dict]:
    """Loads chunks from an existing JSON file."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Chunks file not found at: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"[text_chunker] Loaded {len(chunks)} chunks from '{input_path}'.")
    return chunks

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from app.services.document_loader import load_all_documents
    sample_docs = load_all_documents("data/raw")
    sample_chunks = chunk_documents(sample_docs, chunk_size=400, chunk_overlap=80)
    save_chunks(sample_chunks, "data/processed/chunks.json")
    print(f"Sample chunk: {sample_chunks[0]}")
