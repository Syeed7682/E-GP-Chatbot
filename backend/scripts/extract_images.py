"""
Image Extraction Script (backend/scripts/extract_images.py).
Renders manual pages and extracts portal screenshots into data/extracted_images/.
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings

def run_image_extraction():
    print("=== Extracting High-Resolution Page Images from Manual ===")
    pdf_path = settings.DATA_RAW_DIR / "e-GP System User Manual - Procuring Entity User 1 February 2026.pdf"
    if not pdf_path.exists():
        pdf_path = settings.DATA_RAW_DIR / "egp_official_manual.pdf"

    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        return

    out_dir = settings.EXTRACTED_IMAGES_DIR / "page_images"
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        print(f"Opened PDF with {len(doc)} pages. Exporting page images...")
        for i in range(len(doc)):
            page_num = i + 1
            out_file = out_dir / f"page_{page_num}.jpg"
            if not out_file.exists():
                page = doc[i]
                pix = page.get_pixmap(dpi=150)
                pix.save(str(out_file))
        doc.close()
        print("Page image extraction finished successfully.")
    except Exception as e:
        print(f"Image extraction notice: {e}")

if __name__ == "__main__":
    run_image_extraction()

