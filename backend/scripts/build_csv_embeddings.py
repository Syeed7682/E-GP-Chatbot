"""Build embeddings and a FAISS index for a page-level manual CSV."""
import argparse
import csv
import json
import os
import sys
import gc
from pathlib import Path

import numpy as np

if "--offline" in sys.argv:
    os.environ["EGP_FORCE_OFFLINE_EMBEDDINGS"] = "1"

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service
from app.services.text_cleaner import clean_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=PROJECT_ROOT / "csv_files" / "egp New Manual.csv", type=Path)
    parser.add_argument("--index", default=PROJECT_ROOT / "data" / "structured" / "indexes" / "registration_csv.faiss", type=Path)
    parser.add_argument("--metadata", default=PROJECT_ROOT / "data" / "structured" / "metadata" / "registration_csv.json", type=Path)
    parser.add_argument("--embeddings", default=PROJECT_ROOT / "data" / "structured" / "indexes" / "registration_csv.embeddings.npy", type=Path)
    parser.add_argument("--offline", action="store_true", help="Use the project's deterministic low-memory fallback")
    args = parser.parse_args()

    with args.csv.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"No records found in {args.csv}")

    records = []
    for row in rows:
        question = clean_text(row.get("question") or "")
        ground_truth = clean_text(row.get("ground_truth_answer") or "")
        source_text = row.get("text_content") or ""
        # Ground-truth rows contain the answer separately from the page excerpt.
        # Include both fields so retrieval can directly ground the LLM answer.
        text = clean_text(
            f"Question: {question}\nGround-truth answer: {ground_truth}\n{source_text}"
        )
        raw_pages = str(row.get("page_number") or "0")
        pages = [part.strip() for part in raw_pages.replace(",", ";").split(";") if part.strip().isdigit()]
        page_number = int(pages[0]) if pages else 0
        records.append({
            "chunk_id": f"ground_truth_{row.get('question_id') or len(records) + 1}",
            "question_id": row.get("question_id") or "",
            "question": question,
            "ground_truth_answer": ground_truth,
            "page": page_number,
            "page_number": page_number,
            "pages": [int(page) for page in pages],
            "source": row.get("source_file") or args.csv.name,
            "section_title": row.get("detected_section") or "",
            "text": text,
            "content": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "image_count": int(row.get("image_count") or 0),
            "source_type": "ground_truth_csv",
        })

    if args.offline:
        embedding_service._local_model = None
        embedding_service._mode = "offline_multimodal_fallback"
        gc.collect()
    print(f"Embedding {len(records)} CSV pages with {embedding_service.model_name} ({embedding_service._mode})")
    # Long manual pages can exhaust RAM when encoded as one batch. Encode one
    # page at a time and cap model input to a practical retrieval window.
    if embedding_service._local_model is not None:
        embedding_service._local_model.max_seq_length = 256
    encoded = []
    for number, record in enumerate(records, start=1):
        print(f"  page {number}/{len(records)}", end="\r")
        encoded.append(embedding_service.embed_text(record["text"]))
    vectors = np.vstack(encoded).astype(np.float32)
    print()
    vectors = np.asarray(vectors, dtype=np.float32)
    args.index.parent.mkdir(parents=True, exist_ok=True)
    faiss_service.build_index(vectors, records)
    faiss_service.save(str(args.index), str(args.metadata))
    np.save(args.embeddings, vectors)
    manifest = {
        "source_csv": str(args.csv),
        "records": len(records),
        "dimension": int(vectors.shape[1]),
        "embedding_model": embedding_service.model_name,
        "embedding_mode": embedding_service._mode,
        "text_cleaning": "NFKC normalization, mojibake repair, control-character removal, whitespace cleanup",
        "index": str(args.index),
        "metadata": str(args.metadata),
        "embeddings": str(args.embeddings),
    }
    args.metadata.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
