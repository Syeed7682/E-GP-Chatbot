"""
Structure-Aware PDF Chunker.
Splits extracted manual pages into semantic chunks while preserving:
- Section hierarchy and numbers
- Page start and page end
- Parent section ID
- Screen references
- Clean metadata mapping
"""
import re
from typing import Any, Dict, List
from app.chunking.token_chunker import chunk_text


def create_pdf_chunks(
    pages_data: List[Dict[str, Any]],
    chunk_size: int = 450,
    overlap: int = 60,
    document_id: str = "EGP_MANUAL_V1",
    source_file: str = "egp_manual.pdf",
) -> List[Dict[str, Any]]:
    """
    Creates structured chunks from parsed PDF pages data.
    Groups content by section and page, then applies token chunker.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_counter = 1

    section_map: Dict[str, str] = {}
    section_counter = 1

    for page_record in pages_data:
        page_num = page_record.get("page", 1)
        section = page_record.get("section", "General Overview")
        section_num = page_record.get("section_number", "0.0")
        text = page_record.get("text", "").strip()
        screens = page_record.get("screens", [])

        if not text:
            continue

        sec_key = f"{section_num}::{section}"
        if sec_key not in section_map:
            section_map[sec_key] = f"SECTION_{section_counter:03d}"
            section_counter += 1

        parent_id = section_map[sec_key]

        # Break text into paragraphs
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        page_chunk_texts: List[str] = []

        current_para_group: List[str] = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para.split())
            if current_len + para_len > chunk_size and current_para_group:
                page_chunk_texts.append("\n\n".join(current_para_group))
                # keep last para for overlap
                current_para_group = [current_para_group[-1], para] if len(current_para_group) > 1 else [para]
                current_len = sum(len(p.split()) for p in current_para_group)
            else:
                current_para_group.append(para)
                current_len += para_len

        if current_para_group:
            page_chunk_texts.append("\n\n".join(current_para_group))

        # If no paragraphs or single block, fall back to token_chunker
        if not page_chunk_texts:
            page_chunk_texts = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

        for chunk_idx, chunk_content in enumerate(page_chunk_texts):
            chunk_id = f"PDF_{chunk_counter:06d}"
            chunk_counter += 1

            # Detect screens in this specific chunk
            chunk_screens = [s for s in screens if s in chunk_content]
            if not chunk_screens and screens:
                chunk_screens = screens

            chunks.append({
                "chunk_id": chunk_id,
                "parent_id": parent_id,
                "document_id": document_id,
                "page_start": page_num,
                "page_end": page_num,
                "section": section,
                "section_number": section_num,
                "content_type": "text",
                "text": chunk_content,
                "screens": chunk_screens,
                "screen_reference": chunk_screens[0] if chunk_screens else None,
                "source": source_file,
                "source_type": "pdf",
            })

    return chunks

