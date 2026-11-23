"""Extract embedded PDF image objects for the current structured manual."""
import hashlib
import json
import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "data" / "structured" / "source" / "new_manual.pdf"
OUT = ROOT / "data" / "structured" / "images"
CATALOG = ROOT / "data" / "structured" / "metadata" / "images.json"


def main() -> None:
    if not PDF.exists():
        raise FileNotFoundError(PDF)
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.iterdir():
        if path.is_file():
            path.unlink()

    document = fitz.open(PDF)
    seen = set()
    catalog = []
    for page_number, page in enumerate(document, start=1):
        for image_number, image in enumerate(page.get_images(full=True), start=1):
            xref = image[0]
            payload = document.extract_image(xref)
            data = payload["image"]
            digest = hashlib.sha256(data).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            extension = payload.get("ext", "png")
            filename = f"page_{page_number:02d}_image_{image_number:02d}.{extension}"
            destination = OUT / filename
            destination.write_bytes(data)
            catalog.append({
                "page": page_number,
                "image_number": image_number,
                "path": f"data/structured/images/{filename}",
                "width": payload.get("width"),
                "height": payload.get("height"),
                "format": extension,
                "sha256": digest,
            })

    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    first_image_by_page = {}
    for item in catalog:
        first_image_by_page.setdefault(item["page"], item["path"])
    for metadata_name in ("pdf_manual.json", "registration_csv.json"):
        metadata_path = ROOT / "data" / "structured" / "metadata" / metadata_name
        if not metadata_path.exists():
            continue
        records = json.loads(metadata_path.read_text(encoding="utf-8"))
        for record in records:
            record["image_path"] = first_image_by_page.get(record.get("page_number", record.get("page")))
        metadata_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {len(catalog)} unique embedded images from {len(document)} PDF pages")


if __name__ == "__main__":
    main()
