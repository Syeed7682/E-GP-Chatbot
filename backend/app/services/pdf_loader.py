"""
PDF Loader Service (app/services/pdf_loader.py).
Extracts text, page metadata, and dimensions from the official 543-page e-GP manual.
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.core.config import settings

class PDFLoader:
    def __init__(self, pdf_path: Optional[str] = None):
        self.pdf_path = pdf_path or str(settings.DATA_RAW_DIR / "e-GP System User Manual - Procuring Entity User 1 February 2026.pdf")
        if not os.path.exists(self.pdf_path):
            # Check alternative name
            alt_path = str(settings.DATA_RAW_DIR / "egp_official_manual.pdf")
            if os.path.exists(alt_path):
                self.pdf_path = alt_path

    def load_pages(self, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Extracts text per page using PyMuPDF (fitz) or pypdf."""
        pages = []
        if not os.path.exists(self.pdf_path):
            print(f"[pdf_loader] Manual PDF not found at: {self.pdf_path}")
            return pages

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(self.pdf_path)
            total = len(doc)
            last = end_page if end_page and end_page <= total else total
            
            for page_idx in range(start_page - 1, last):
                page = doc[page_idx]
                text = page.get_text("text")
                pages.append({
                    "page_number": page_idx + 1,
                    "text": text.strip(),
                    "total_pages": total,
                    "width": page.rect.width,
                    "height": page.rect.height
                })
            doc.close()
            return pages
        except ImportError:
            print("[pdf_loader] PyMuPDF not installed, falling back to pypdf...")
            try:
                from pypdf import PdfReader
                reader = PdfReader(self.pdf_path)
                total = len(reader.pages)
                last = end_page if end_page and end_page <= total else total
                for idx in range(start_page - 1, last):
                    page = reader.pages[idx]
                    text = page.extract_text() or ""
                    pages.append({
                        "page_number": idx + 1,
                        "text": text.strip(),
                        "total_pages": total
                    })
                return pages
            except Exception as e:
                print(f"[pdf_loader] Extraction error: {e}")
                return pages

pdf_loader = PDFLoader()

