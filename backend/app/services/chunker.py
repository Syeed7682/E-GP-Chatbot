"""
Chunker Service (app/services/chunker.py).
Splits manual pages into indexed semantic chunks preserving page citations and headings.
"""
from typing import List, Dict, Any
from app.services.document_parser import document_parser

class Chunker:
    @staticmethod
    def chunk_page(page_data: Dict[str, Any], chunk_size: int = 800, overlap: int = 150) -> List[Dict[str, Any]]:
        page_num = page_data["page_number"]
        text = page_data["text"]
        if not text.strip():
            return []

        screens = document_parser.extract_screen_references(text)
        title = document_parser.extract_section_title(text, page_num)
        
        words = text.split()
        if len(words) <= chunk_size:
            return [{
                "page_number": page_num,
                "section_title": title,
                "content": text,
                "screen_references": screens,
                "category": "statutory" if "ppr" in text.lower() else "procedural"
            }]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_text = " ".join(words[start:end])
            chunk_screens = document_parser.extract_screen_references(chunk_text) or screens
            chunks.append({
                "page_number": page_num,
                "section_title": title,
                "content": chunk_text,
                "screen_references": chunk_screens,
                "category": "statutory" if "ppr" in chunk_text.lower() else "procedural"
            })
            if end == len(words):
                break
            start += (chunk_size - overlap)
        return chunks

chunker = Chunker()

