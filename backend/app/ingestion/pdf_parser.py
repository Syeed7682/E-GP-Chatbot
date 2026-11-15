"""
PDF Parser for e-GP Manual.
Extracts structured text, tables, screenshots, headings, and page provenance.
Uses Docling when available, with PyMuPDF (fitz) fallback.
"""
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def parse_pdf_with_docling(pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
    """Parse PDF using Docling for structured multi-modal representation."""
    import importlib
    docling_mod = importlib.import_module("docling.document_converter")
    DocumentConverter = getattr(docling_mod, "DocumentConverter")

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))

    # Save structured JSON
    doc_json_path = output_dir / "document.json"
    result.document.save_as_json(doc_json_path)

    # Save Markdown
    markdown = result.document.export_to_markdown()
    (output_dir / "document.md").write_text(markdown, encoding="utf-8")

    return {
        "engine": "docling",
        "json_path": str(doc_json_path),
        "markdown_path": str(output_dir / "document.md"),
        "page_count": len(result.document.pages) if hasattr(result.document, "pages") else 0,
    }


def _get_fitz():
    import importlib
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except Exception:
            pass
    raise ImportError("PyMuPDF / fitz is required for PDF parsing. Install with: pip install PyMuPDF")


def parse_pdf_with_fitz(pdf_path: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Fallback high-precision PDF extraction using PyMuPDF.
    Preserves page provenance, detects Screen codes, headings, and tables.
    """
    fitz = _get_fitz()

    doc = fitz.open(str(pdf_path))
    pages_data: List[Dict[str, Any]] = []
    full_markdown_lines: List[str] = []

    screen_pattern = re.compile(r"Screen\s*[–—-]\s*([A-Za-z0-9_.-]+)", re.IGNORECASE)
    section_pattern = re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)$")

    current_section = "General Overview"
    current_section_num = "0.0"

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        text = page.get_text("text")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        page_headings = []
        page_screens = []

        for line in lines:
            # Check for Screen references
            screen_match = screen_pattern.search(line)
            if screen_match:
                page_screens.append(screen_match.group(0))

            # Check for Section headings
            sec_match = section_pattern.match(line)
            if sec_match:
                current_section_num = sec_match.group(1)
                current_section = sec_match.group(2).strip()
                page_headings.append(f"{current_section_num} {current_section}")

        page_record = {
            "page": page_num,
            "section": current_section,
            "section_number": current_section_num,
            "headings": page_headings,
            "screens": list(set(page_screens)),
            "text": text.strip(),
            "has_images": len(page.get_images()) > 0,
        }
        pages_data.append(page_record)

        # Markdown representation
        full_markdown_lines.append(f"\n\n<!-- PAGE {page_num} -->\n## Page {page_num} — {current_section}\n\n")
        full_markdown_lines.append(text)

    doc.close()

    doc_json_path = output_dir / "document.json"
    doc_json_path.write_text(json.dumps(pages_data, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = output_dir / "document.md"
    md_path.write_text("\n".join(full_markdown_lines), encoding="utf-8")

    return {
        "engine": "pymupdf",
        "json_path": str(doc_json_path),
        "markdown_path": str(md_path),
        "page_count": len(pages_data),
        "pages": pages_data,
    }


def parse_pdf(pdf_path: str | Path, output_dir: str | Path) -> Dict[str, Any]:
    """
    Main entry point for PDF parsing.
    Attempts Docling first; falls back to PyMuPDF if Docling is unavailable.
    """
    pdf_p = Path(pdf_path)
    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    if not pdf_p.exists():
        raise FileNotFoundError(f"PDF file not found at: {pdf_p}")

    try:
        import importlib
        importlib.import_module("docling")
        logger.info("Parsing PDF with Docling: %s", pdf_p)
        return parse_pdf_with_docling(pdf_p, out_p)
    except (ImportError, Exception) as exc:
        logger.info("Docling unavailable or encountered error (%s); falling back to PyMuPDF.", exc)
        return parse_pdf_with_fitz(pdf_p, out_p)

