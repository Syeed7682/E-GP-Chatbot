"""
Rebuild Chunk Images (backend/scripts/rebuild_chunk_images.py).
Extracts all diagrams, portal screenshots, and figures from the e-GP Manual PDF,
maps each image to its exact owning Chunk ID, Page ID, and Related Sentence,
and saves the images with structured filenames:
chunk_{chunk_id}_page_{page_id}_{slug}.png

Updates:
1. data/extracted_images/chunks/ (all extracted image files)
2. data/extracted_images/images_manifest.json (complete image registry)
3. data/processed/chunks.json (chunk records with image_path and related_sentence)
4. data/faiss_index/metadata.json (mirror of chunks.json)
5. data/indexes/v001/metadata.db (SQLite metadata store with image paths)
"""
import io
import json
import logging
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rebuild_images")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PDF_PATH = ROOT_DIR / "data" / "raw" / "egp_manual.pdf"
CHUNKS_PATH = ROOT_DIR / "data" / "processed" / "chunks.json"
LEGACY_META_PATH = ROOT_DIR / "data" / "faiss_index" / "metadata.json"
SQLITE_DB_PATH = ROOT_DIR / "data" / "indexes" / "v001" / "metadata.db"
OUTPUT_DIR = ROOT_DIR / "data" / "extracted_images" / "chunks"
MANIFEST_PATH = ROOT_DIR / "data" / "extracted_images" / "images_manifest.json"


def get_fitz():
    import importlib
    for mod in ("pymupdf", "fitz"):
        try:
            return importlib.import_module(mod)
        except Exception:
            pass
    raise ImportError("pymupdf / fitz is required. Please install with: pip install pymupdf")


def clean_slug(text: str, max_words: int = 5) -> str:
    """Creates a clean, safe filename slug from a sentence or phrase."""
    # Remove screen prefix variations for cleaner slug
    s = re.sub(r"[^\w\s-]", " ", text.lower())
    words = [w for w in s.split() if len(w) > 1 and w not in {"the", "and", "for", "with", "from", "this", "that"}][:max_words]
    slug = "_".join(words)
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return slug[:40] if slug else "img"


def extract_sentences(text: str) -> List[str]:
    """Splits chunk text into sentences, cleaning OCR noise."""
    raw_lines = [l.strip() for l in text.split("\n") if l.strip()]
    full_text = " ".join(raw_lines)
    # Split on sentence boundaries
    sentences = re.split(r"(?<=[.!?])\s+", full_text)
    cleaned = []
    for s in sentences:
        s_clean = re.sub(r"\s+", " ", s).strip()
        if len(s_clean) > 10 and not s_clean.isdigit():
            cleaned.append(s_clean)
    return cleaned if cleaned else raw_lines


def find_best_sentence_for_image(
    chunk_text: str,
    screen_ref: Optional[str] = None,
) -> str:
    """Finds the most descriptive related sentence in the chunk text."""
    sentences = extract_sentences(chunk_text)
    if not sentences:
        return chunk_text[:120].strip()

    # 1. Look for explicit screen reference (e.g. Screen D1, Screen-A6)
    if screen_ref:
        norm_ref = re.sub(r"[\s–—_-]", "", screen_ref.lower())
        for s in sentences:
            s_norm = re.sub(r"[\s–—_-]", "", s.lower())
            if norm_ref in s_norm:
                return s

    # 2. Look for any Screen mention
    for s in sentences:
        if re.search(r"\bScreen\s*[-–—:]\s*[A-Za-z0-9_.]+", s, re.I):
            return s

    # 3. Look for procedural action verbs
    action_pattern = re.compile(
        r"\b(?:click|select|choose|navigate|enter|fill|verify|displays?|shown\s+in|button|tab|window|dialog|screen)\b",
        re.I,
    )
    for s in sentences:
        if action_pattern.search(s):
            return s

    # 4. Fallback to first substantive sentence
    return sentences[0]


def rebuild_images():
    fitz = get_fitz()
    if not PDF_PATH.exists():
        logger.error("Manual PDF not found at %s", PDF_PATH)
        sys.exit(1)

    if not CHUNKS_PATH.exists():
        logger.error("Chunks JSON not found at %s", CHUNKS_PATH)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Opening PDF: %s", PDF_PATH)
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    logger.info("PDF has %d pages.", total_pages)

    logger.info("Loading chunks: %s", CHUNKS_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    logger.info("Loaded %d chunks.", len(chunks))

    # Index chunks by page
    chunks_by_page: Dict[int, List[Dict[str, Any]]] = {}
    for c in chunks:
        p = c.get("page")
        if p is not None:
            chunks_by_page.setdefault(p, []).append(c)

    manifest_records: List[Dict[str, Any]] = []
    chunk_image_map: Dict[int, Dict[str, Any]] = {}  # chunk_id -> best image info

    total_extracted = 0

    for page_idx in range(total_pages):
        page_num = page_idx + 1
        page = doc[page_idx]
        image_list = page.get_images()
        if not image_list:
            continue

        # Extract text on page to find screen references
        page_text = page.get_text()
        page_screens = re.findall(r"Screen\s*[-–—:]\s*[A-Za-z0-9_.]+", page_text, re.I)

        # Filter raster images (ignore tiny icons/bullets)
        valid_images = []
        for img_idx, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_img = doc.extract_image(xref)
                w, h = base_img["width"], base_img["height"]
                if w < 100 or h < 80:
                    continue

                # Get bounding box if available
                rects = page.get_image_rects(xref)
                y0 = rects[0].y0 if rects else float(img_idx * 100)

                valid_images.append({
                    "img_idx": img_idx,
                    "xref": xref,
                    "bytes": base_img["image"],
                    "ext": base_img["ext"],
                    "width": w,
                    "height": h,
                    "y0": y0,
                })
            except Exception as e:
                logger.debug("Failed to extract image xref %d on page %d: %s", xref, page_num, e)

        if not valid_images:
            continue

        # Sort images on page from top to bottom
        valid_images.sort(key=lambda item: item["y0"])

        # Chunks for this page
        page_chunk_list = chunks_by_page.get(page_num, [])

        for img_order, img_data in enumerate(valid_images):
            # Screen reference for this image if available
            screen_ref = page_screens[img_order] if img_order < len(page_screens) else None

            # Pick matching chunk on this page
            chosen_chunk = None
            if page_chunk_list:
                if len(page_chunk_list) == 1:
                    chosen_chunk = page_chunk_list[0]
                else:
                    # If multiple chunks, check which chunk contains the screen_ref
                    if screen_ref:
                        norm_ref = re.sub(r"[\s–—_-]", "", screen_ref.lower())
                        for c in page_chunk_list:
                            if norm_ref in re.sub(r"[\s–—_-]", "", c["text"].lower()):
                                chosen_chunk = c
                                break

                    # If not matched by screen, distribute by vertical order
                    if not chosen_chunk:
                        chunk_idx = min(img_order, len(page_chunk_list) - 1)
                        chosen_chunk = page_chunk_list[chunk_idx]

            chunk_id = chosen_chunk["chunk_id"] if chosen_chunk else f"p{page_num}"
            chunk_text = chosen_chunk["text"] if chosen_chunk else page_text

            # Find related sentence
            related_sentence = find_best_sentence_for_image(chunk_text, screen_ref=screen_ref)

            # Build filename: chunk_{chunk_id}_page_{page_id}_{slug}.ext
            slug_source = screen_ref if screen_ref else related_sentence
            slug = clean_slug(slug_source)
            ext = "png" if img_data["ext"] in ("png", "x-png") else "jpg"
            filename = f"chunk_{chunk_id}_page_{page_num}_{img_order}_{slug}.{ext}"
            file_path = OUTPUT_DIR / filename

            # Save the image file
            try:
                # Normalize format through PIL
                pil_img = Image.open(io.BytesIO(img_data["bytes"]))
                if pil_img.mode in ("RGBA", "P") and ext == "jpg":
                    pil_img = pil_img.convert("RGB")
                pil_img.save(str(file_path))
            except Exception:
                file_path.write_bytes(img_data["bytes"])

            relative_image_path = f"data/extracted_images/chunks/{filename}"

            record = {
                "image_id": f"chunk_{chunk_id}_page_{page_num}_img_{img_order}",
                "chunk_id": chunk_id,
                "page": page_num,
                "filename": filename,
                "image_path": relative_image_path,
                "related_sentence": related_sentence,
                "screen_reference": screen_ref,
                "width": img_data["width"],
                "height": img_data["height"],
                "format": ext,
            }
            manifest_records.append(record)
            total_extracted += 1

            # Map chunk to its primary image
            if chosen_chunk and isinstance(chunk_id, int):
                if chunk_id not in chunk_image_map:
                    chunk_image_map[chunk_id] = record

    doc.close()
    logger.info("Extracted %d valid images across %d pages.", total_extracted, total_pages)

    # Save manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_records, f, indent=2, ensure_ascii=False)
    logger.info("Saved image manifest to %s (%d records)", MANIFEST_PATH, len(manifest_records))

    # Update chunks.json
    multimodal_count = 0
    for c in chunks:
        cid = c["chunk_id"]
        if cid in chunk_image_map:
            img_info = chunk_image_map[cid]
            c["image_path"] = img_info["image_path"]
            c["related_sentence"] = img_info["related_sentence"]
            c["content_type"] = "multimodal"
            c["screen_reference"] = img_info["screen_reference"]
            multimodal_count += 1
        else:
            c["image_path"] = None
            c["related_sentence"] = None
            c["content_type"] = "text"
            c["screen_reference"] = None

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info("Updated chunks.json: %d / %d chunks are multimodal with verified images.", multimodal_count, len(chunks))

    # Update legacy metadata.json
    if LEGACY_META_PATH.parent.exists():
        with open(LEGACY_META_PATH, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        logger.info("Updated legacy metadata.json: %s", LEGACY_META_PATH)

    # Update SQLite database
    if SQLITE_DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(SQLITE_DB_PATH))
            cur = conn.cursor()
            updated_db = 0
            for cid, img_info in chunk_image_map.items():
                cur.execute(
                    """
                    UPDATE chunks 
                    SET image_path = ?, content_type = 'multimodal'
                    WHERE chunk_id = ? OR chunk_id = ?
                    """,
                    (img_info["image_path"], str(cid), f"pdf:{cid}"),
                )
                if cur.rowcount > 0:
                    updated_db += cur.rowcount
            conn.commit()
            conn.close()
            logger.info("Updated SQLite metadata.db: %d rows updated with image paths.", updated_db)
        except Exception as e:
            logger.warning("Could not update SQLite DB: %e", e)

    print("\n=======================================================")
    print("           IMAGE REBUILD COMPLETE")
    print(f"Total images extracted : {total_extracted}")
    print(f"Chunks with images     : {multimodal_count} / {len(chunks)}")
    print(f"Image storage folder   : {OUTPUT_DIR}")
    print(f"Manifest file          : {MANIFEST_PATH}")
    print("=======================================================")


if __name__ == "__main__":
    rebuild_images()
