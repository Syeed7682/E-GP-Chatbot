"""
CSV Data Loader Service (backend/app/services/csv_loader.py).
Responsible for loading structured manual pages and Q&A records directly from CSV files.
Acts as the authoritative, ultra-fast data source loader for the RAG and retrieval pipeline.
"""
import csv
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class CSVLoader:
    def __init__(
        self,
        manual_csv_path: Optional[Path] = None,
        reg_csv_path: Optional[Path] = None,
        eval_csv_path: Optional[Path] = None,
    ):
        self.manual_csv_path = manual_csv_path or settings.EGP_MANUAL_CSV
        self.reg_csv_path = reg_csv_path or settings.EGP_REG_MANUAL_CSV
        self.eval_csv_path = eval_csv_path or settings.EGP_EVAL_CSV

    def load_manual_pages(self, csv_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
        """
        Loads the 543 pages of the official PE manual from CSV.
        Returns a list of dicts with page_number, text, section, total_pages, etc.
        """
        path = Path(csv_path) if csv_path else self.manual_csv_path
        if not path.is_file():
            logger.warning("Manual CSV not found at: %s", path)
            return []

        pages: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total_pages = len(rows)
        for row in rows:
            p_num = int(row.get("page_number", 0))
            text = row.get("text_content", "").strip()
            section = row.get("detected_section", "General Overview").strip()
            source = row.get("source_file", "egp_manual.pdf").strip()

            pages.append({
                "page_number": p_num,
                "text": text,
                "section": section,
                "detected_section": section,
                "source_file": source,
                "total_pages": total_pages,
                "char_count": int(row.get("char_count") or len(text)),
                "word_count": int(row.get("word_count") or len(text.split())),
                "image_count": int(row.get("image_count") or 0),
            })

        logger.info("Loaded %d manual pages from CSV: %s", len(pages), path)
        return pages

    def load_registration_pages(self, csv_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
        """
        Loads the 27 pages of the official Tenderer Registration manual from CSV.
        """
        path = Path(csv_path) if csv_path else self.reg_csv_path
        if not path.is_file():
            logger.warning("Registration manual CSV not found at: %s", path)
            return []

        pages: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        total_pages = len(rows)
        for row in rows:
            p_num = int(row.get("page_number", 0))
            text = row.get("text_content", "").strip()
            section = row.get("detected_section", "Tenderer Registration").strip()
            source = row.get("source_file", "eGP_NewUserRegManual_English.pdf").strip()

            pages.append({
                "page_number": p_num,
                "text": text,
                "section": section,
                "detected_section": section,
                "source_file": source,
                "total_pages": total_pages,
                "char_count": int(row.get("char_count") or len(text)),
                "word_count": int(row.get("word_count") or len(text.split())),
                "image_count": int(row.get("image_count") or 0),
            })

        logger.info("Loaded %d registration pages from CSV: %s", len(pages), path)
        return pages

    def load_all_manual_pages(self) -> List[Dict[str, Any]]:
        """Combines PE manual and registration manual pages."""
        pe_pages = self.load_manual_pages()
        reg_pages = self.load_registration_pages()
        return pe_pages + reg_pages

    def load_qa_records(self, csv_path: Optional[Path | str] = None) -> List[Dict[str, Any]]:
        """
        Loads curated, deduplicated Q&A records from CSV.
        Returns normalized records compatible with both QAService and vector indexing.
        """
        path = Path(csv_path) if csv_path else self.eval_csv_path
        if not path.is_file():
            logger.warning("Evaluation / Q&A CSV not found at: %s", path)
            return []

        records: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                qid = row.get("id", f"EGP-{idx + 1:04d}").strip()
                # Parse numeric question number for indexing compatibility
                num_match = re.search(r"\d+", qid)
                q_num = int(num_match.group(0)) if num_match else idx + 1

                category = row.get("category", "General Procurement").strip()
                question = row.get("question", "").strip()
                ground_truth = row.get("ground_truth", "").strip()
                citation = row.get("expected_citation", "").strip()
                screen = row.get("expected_screen_reference", "").strip()
                legal = row.get("expected_legal_basis", "").strip()
                workflow = row.get("tenderer_workflow_guidance", "").strip()
                lang = row.get("language", "English").strip()

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
                    "expected_citation": citation,
                    "expected_screen_reference": screen,
                    "expected_legal_basis": legal,
                    "tenderer_workflow_guidance": workflow,
                    "language": lang,
                    "complexity": row.get("complexity", "Medium").strip(),
                    "answerability": row.get("answerability", "Answerable").strip(),
                    "retrieval_text": f"Category: {category}\nQuestion: {question}\nExpected Citation: {citation}",
                    "source_type": "qa",
                    "source": path.name,
                    "source_files": [path.name],
                })

        logger.info("Loaded %d Q&A records from CSV: %s", len(records), path)
        return records


csv_loader = CSVLoader()
