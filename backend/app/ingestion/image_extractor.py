"""
Image Extractor for e-GP Manual.
Extracts embedded images, portal screenshots, and diagrams from PDF pages.
Maintains coordinates, bounding boxes, chunk associations, and related sentence captions.
"""
import io
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image

logger = logging.getLogger(__name__)


def _get_fitz():
    import importlib
    for name in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(name)
        except Exception:
            pass
    raise ImportError("PyMuPDF / fitz is required for image extraction. Install with: pip install PyMuPDF")


def _clean_slug(text: str, max_words: int = 5) -> str:
    s = re.sub(r"[^\w\s-]", " ", text.lower())
    words = [w for w in s.split() if len(w) > 1 and w not in {"the", "and", "for", "with", "from", "this", "that"}][:max_words]
    slug = "_".join(words)
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return slug[:40] if slug else "img"


def _find_related_sentence(text: str, screen_ref: Optional[str] = None) -> str:
    raw_lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_text = " ".join(raw_lines)
    sentences = re.split(r"(?<=[.!?])\s+", full_text)
    cleaned = [re.sub(r"\s+", " ", s).strip() for s in sentences if len(s.strip()) > 10 and not s.strip().isdigit()]
    if not cleaned:
        return text[:120].strip()

    if screen_ref:
        norm_ref = re.sub(r"[\s–—_-]", "", screen_ref.lower())
        for s in cleaned:
            if norm_ref in re.sub(r"[\s–—_-]", "", s.lower()):
                return s

    for s in cleaned:
        if re.search(r"\bScreen\s*[-–—:]\s*[A-Za-z0-9_.]+", s, re.I):
            return s

    action_pattern = re.compile(
        r"\b(?:click|select|choose|navigate|enter|fill|verify|displays?|shown\s+in|button|tab|window|dialog|screen)\b",
        re.I,
    )
    for s in cleaned:
        if action_pattern.search(s):
            return s

    return cleaned[0]


def extract_images_from_pdf(
    pdf_path: str | Path,
    output_dir: str | Path,
    min_width: int = 100,
    min_height: int = 80,
    chunks: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Extracts embedded raster images and screenshots from the PDF,
    organizing them by chunk ID, page ID, and related sentence.
    """
    fitz = _get_fitz()

    pdf_p = Path(pdf_path)
    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_p))
    image_records: List[Dict[str, Any]] = []

    # Map chunks by page if provided
    chunks_by_page: Dict[int, List[Dict[str, Any]]] = {}
    if chunks:
        for c in chunks:
            p = c.get("page")
            if p is not None:
                chunks_by_page.setdefault(p, []).append(c)

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]
        image_list = page.get_images(full=True)
        if not image_list:
            continue

        page_text = page.get_text()
        page_screens = re.findall(r"Screen\s*[-–—:]\s*[A-Za-z0-9_.]+", page_text, re.I)

        valid_images = []
        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
                w, h = base_image["width"], base_image["height"]
                if w < min_width or h < min_height:
                    continue

                rects = page.get_image_rects(xref)
                y0 = rects[0].y0 if rects else float(img_idx * 100)

                valid_images.append({
                    "img_idx": img_idx,
                    "xref": xref,
                    "bytes": base_image["image"],
                    "ext": base_image["ext"],
                    "width": w,
                    "height": h,
                    "y0": y0,
                })
            except Exception as e:
                logger.debug("Could not process image xref %d on page %d: %s", xref, page_num, e)

        if not valid_images:
            continue

        valid_images.sort(key=lambda item: item["y0"])
        page_chunk_list = chunks_by_page.get(page_num, [])

        for img_order, img_data in enumerate(valid_images):
            screen_ref = page_screens[img_order] if img_order < len(page_screens) else None

            chosen_chunk = None
            if page_chunk_list:
                if len(page_chunk_list) == 1:
                    chosen_chunk = page_chunk_list[0]
                else:
                    if screen_ref:
                        norm_ref = re.sub(r"[\s–—_-]", "", screen_ref.lower())
                        for c in page_chunk_list:
                            if norm_ref in re.sub(r"[\s–—_-]", "", c.get("text", "").lower()):
                                chosen_chunk = c
                                break
                    if not chosen_chunk:
                        chunk_idx = min(img_order, len(page_chunk_list) - 1)
                        chosen_chunk = page_chunk_list[chunk_idx]

            chunk_id = chosen_chunk["chunk_id"] if chosen_chunk else f"p{page_num}"
            chunk_text = chosen_chunk.get("text", page_text) if chosen_chunk else page_text
            related_sentence = _find_related_sentence(chunk_text, screen_ref=screen_ref)

            slug_source = screen_ref if screen_ref else related_sentence
            slug = _clean_slug(slug_source)
            ext = "png" if img_data["ext"] in ("png", "x-png") else "jpg"
            filename = f"chunk_{chunk_id}_page_{page_num}_{img_order}_{slug}.{ext}"
            save_path = out_p / filename

            if not save_path.exists():
                try:
                    pil_img = Image.open(io.BytesIO(img_data["bytes"]))
                    if pil_img.mode in ("RGBA", "P") and ext == "jpg":
                        pil_img = pil_img.convert("RGB")
                    pil_img.save(str(save_path))
                except Exception:
                    save_path.write_bytes(img_data["bytes"])

            image_records.append({
                "image_id": f"chunk_{chunk_id}_page_{page_num}_img_{img_order}",
                "chunk_id": chunk_id,
                "page": page_num,
                "filename": filename,
                "path": str(save_path),
                "related_sentence": related_sentence,
                "screen_reference": screen_ref,
                "width": img_data["width"],
                "height": img_data["height"],
                "format": ext,
            })

    doc.close()
    logger.info("Extracted %d structured chunk images from PDF to %s", len(image_records), out_p)
    return image_records
