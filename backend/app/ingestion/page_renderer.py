"""
Page Renderer for e-GP Manual.
Renders PDF pages containing screenshots, diagrams, and tables at 120-150 DPI.
Saves rendered pages to images/pages/page_XXXX.png for visual verification and multimodal retrieval.
"""
import logging
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


def _get_fitz():
    import importlib
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except Exception:
            pass
    raise ImportError("PyMuPDF / fitz is required for page rendering. Install with: pip install PyMuPDF")


def render_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 120,
    page_numbers: Optional[List[int]] = None,
    only_visual: bool = False,
) -> List[Path]:
    """
    Renders pages of the given PDF to PNG images.
    
    Args:
        pdf_path: Path to the e-GP manual PDF
        output_dir: Directory where rendered images will be saved
        dpi: Target resolution (120-150 DPI recommended)
        page_numbers: Specific 1-based page numbers to render (or None for all)
        only_visual: If True, only render pages that contain images or Screen references
        
    Returns:
        List of Paths to rendered PNG images
    """
    fitz = _get_fitz()

    pdf_p = Path(pdf_path)
    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    if not pdf_p.exists():
        raise FileNotFoundError(f"PDF file does not exist: {pdf_p}")

    doc = fitz.open(str(pdf_p))
    rendered_files: List[Path] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    target_pages: Set[int] = set(page_numbers) if page_numbers else set(range(1, len(doc) + 1))

    for idx in range(len(doc)):
        page_num = idx + 1
        if page_num not in target_pages:
            continue

        page = doc[idx]

        if only_visual:
            has_img = len(page.get_images()) > 0
            text = page.get_text("text").lower()
            has_screen = "screen" in text or "table" in text or "figure" in text
            if not (has_img or has_screen):
                continue

        out_file = out_p / f"page_{page_num:04d}.png"
        # Skip if already rendered
        if out_file.exists() and out_file.stat().st_size > 0:
            rendered_files.append(out_file)
            continue

        pix = page.get_pixmap(matrix=matrix, alpha=False)
        pix.save(str(out_file))
        rendered_files.append(out_file)

    doc.close()
    logger.info("Rendered %d pages to %s", len(rendered_files), out_p)
    return rendered_files

