"""
Q&A Parser for e-GP System.
Parses master operational Q&A pairs from TXT and DOCX files.
Normalizes question number, module category, question text, and step-by-step answers.
"""
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_QUESTION_HEADER = re.compile(r"^Question\s+(\d+)\s*:\s*(.*?)\s*$", re.IGNORECASE)
_MODULE_HEADER = re.compile(r"^Module\s+\d+\s*:\s*(.*?)\s*$", re.IGNORECASE)
_QUESTION_LINE = re.compile(r"^Q\s*:\s*(.*?)\s*$", re.IGNORECASE)


def parse_qa_text(text: str) -> List[Dict[str, Any]]:
    """Parse numbered Question/Q&A blocks without altering answer text."""
    records: List[Dict[str, Any]] = []
    current_module: Optional[str] = None
    blocks: List[tuple[int, str, List[str], str]] = []
    active_number: Optional[int] = None
    active_title = ""
    active_lines: List[str] = []

    def finish_block() -> None:
        if active_number is not None:
            blocks.append((
                active_number,
                active_title,
                active_lines.copy(),
                current_module or "General Procurement",
            ))

    for line in text.lstrip("\ufeff").splitlines():
        mod_match = _MODULE_HEADER.match(line.strip())
        if mod_match:
            finish_block()
            active_number = None
            active_title = ""
            active_lines = []
            current_module = mod_match.group(1).strip()
            continue

        q_match = _QUESTION_HEADER.match(line.strip())
        if q_match:
            finish_block()
            active_number = int(q_match.group(1))
            active_title = q_match.group(2).strip()
            active_lines = []
            continue

        if active_number is not None:
            active_lines.append(line)

    finish_block()

    seen_numbers = set()
    for number, title, lines, module in blocks:
        if number in seen_numbers:
            continue
        seen_numbers.add(number)

        question_idx = next(
            (idx for idx, line in enumerate(lines) if _QUESTION_LINE.match(line.strip())),
            None,
        )

        if question_idx is not None:
            q_match = _QUESTION_LINE.match(lines[question_idx].strip())
            question = q_match.group(1).strip() if q_match else title
            answer = "\n".join(l.rstrip() for l in lines[question_idx + 1:]).strip()
        else:
            question = title
            answer = "\n".join(l.rstrip() for l in lines).strip()

        records.append({
            "id": f"QA_{number:04d}",
            "question_number": number,
            "category": module,
            "module": module,
            "title": title,
            "question": question,
            "answer": answer,
            "retrieval_text": f"Category: {module}\nQuestion: {question}\nTitle: {title}",
            "source_type": "qa",
        })

    return records


def parse_qa_from_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """
    Parses Q&A records directly from the evaluation CSV dataset.
    """
    import csv

    records: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            qid = row.get("id", f"EGP-{idx + 1:04d}").strip()
            num_match = re.search(r"\d+", qid)
            q_num = int(num_match.group(0)) if num_match else idx + 1

            category = row.get("category", "General Procurement").strip()
            question = row.get("question", "").strip()
            ground_truth = row.get("ground_truth", "").strip()

            if not question or not ground_truth:
                continue

            records.append({
                "id": qid,
                "question_number": q_num,
                "category": category,
                "module": category,
                "title": question,
                "question": question,
                "answer": ground_truth,
                "expected_citation": row.get("expected_citation", "").strip(),
                "retrieval_text": f"Category: {category}\nQuestion: {question}",
                "source_type": "qa",
                "source_file": csv_path.name,
            })

    logger.info("Loaded %d Q&A records from CSV %s", len(records), csv_path)
    return records


def parse_qa_corpus(
    txt_path: Optional[Path] = None,
    docx_path: Optional[Path] = None,
    csv_path: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """
    Parses Q&A records. Checks CSV dataset first; falls back to TXT or DOCX files.
    """
    # 1. Check CSV data source first
    target_csv = csv_path or Path("csv_files/egp_contractor_evaluation_dataset.csv")
    if target_csv and target_csv.is_file():
        return parse_qa_from_csv(target_csv)

    records: List[Dict[str, Any]] = []

    if txt_path and txt_path.exists():
        try:
            content = txt_path.read_text(encoding="utf-8-sig")
            parsed = parse_qa_text(content)
            for r in parsed:
                r["source_file"] = txt_path.name
            records.extend(parsed)
            logger.info("Loaded %d Q&A records from %s", len(parsed), txt_path)
            return records
        except Exception as e:
            logger.warning("Error reading QA text file %s: %s", txt_path, e)

    if docx_path and docx_path.exists():
        try:
            from docx import Document
            doc = Document(docx_path)
            full_text = "\n".join(p.text for p in doc.paragraphs)
            parsed = parse_qa_text(full_text)
            for r in parsed:
                r["source_file"] = docx_path.name
            records.extend(parsed)
            logger.info("Loaded %d Q&A records from %s", len(parsed), docx_path)
        except Exception as e:
            logger.warning("Error reading QA docx file %s: %s", docx_path, e)

    return records

