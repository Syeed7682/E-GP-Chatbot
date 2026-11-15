"""
Ingestion module for e-GP Manual RAG System.
Handles document extraction, rendering, OCR, and Q&A parsing.
"""
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.page_renderer import render_pages
from app.ingestion.table_extractor import extract_tables_from_page
from app.ingestion.image_extractor import extract_images_from_pdf
from app.ingestion.ocr_processor import process_ocr
from app.ingestion.qa_parser import parse_qa_corpus

__all__ = [
    "parse_pdf",
    "render_pages",
    "extract_tables_from_page",
    "extract_images_from_pdf",
    "process_ocr",
    "parse_qa_corpus",
]

