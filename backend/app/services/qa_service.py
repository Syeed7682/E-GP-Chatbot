"""Loads and searches the supplemental e-GP question-and-answer text corpus."""
import logging
import math
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.core.config import settings

logger = logging.getLogger(__name__)

_QUESTION_HEADER = re.compile(r"^Question\s+(\d+)\s*:\s*(.*?)\s*$", re.IGNORECASE)
_MODULE_HEADER = re.compile(r"^Module\s+\d+\s*:\s*(.*?)\s*$", re.IGNORECASE)
_QUESTION_LINE = re.compile(r"^Q\s*:\s*(.*?)\s*$", re.IGNORECASE)
_SEARCH_NOISE = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can", "do",
    "does", "for", "from", "give", "how", "i", "in", "into", "is", "it",
    "me", "of", "on", "or", "please", "process", "provide", "question",
    "show", "step", "steps", "system", "tell", "the", "then", "to", "what",
    "when", "where", "which", "who", "why", "with", "you", "your", "exact",
    "instruction", "instructions", "operational", "procedure", "procedures",
    "workflow", "execute", "executing", "e", "gp", "portal", "user", "users",
    "concise", "numbered", "brief", "detailed",
}


def _canonical_token(token: str) -> str:
    if token in {"change", "changed", "changing", "replace", "replaced", "replacement", "replacing"}:
        return "replace"
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and token.endswith("s") and not token.endswith(("ss", "us")):
        return token[:-1]
    return token


def _search_tokens(text: str) -> Set[str]:
    text = re.sub(r"\b(?:log|sign)\s+in\b", "login", text.lower())
    return {
        _canonical_token(token)
        for token in re.findall(r"[a-z0-9]+", text)
        if token not in _SEARCH_NOISE and len(token) > 1
    }


def parse_qa_text(text: str) -> List[Dict]:
    """Parse numbered Question/Q&A blocks without altering answer text."""
    records: List[Dict] = []
    current_module: Optional[str] = None
    blocks: List[tuple[int, str, List[str], str]] = []
    active_number: Optional[int] = None
    active_title = ""
    active_lines: List[str] = []

    def finish_block() -> None:
        if active_number is not None:
            blocks.append((active_number, active_title, active_lines.copy(), current_module or "Unspecified module"))

    for line in text.lstrip("\ufeff").splitlines():
        module_match = _MODULE_HEADER.match(line.strip())
        if module_match:
            finish_block()
            active_number = None
            active_title = ""
            active_lines = []
            current_module = module_match.group(1).strip()
            continue

        question_match = _QUESTION_HEADER.match(line.strip())
        if question_match:
            finish_block()
            active_number = int(question_match.group(1))
            active_title = question_match.group(2).strip()
            active_lines = []
            continue

        if active_number is not None:
            active_lines.append(line)
    finish_block()

    malformed: List[str] = []
    seen_numbers: Set[int] = set()
    for number, title, lines, module in blocks:
        if number in seen_numbers:
            malformed.append(f"duplicate Question {number}")
            continue
        seen_numbers.add(number)

        question_index = next(
            (index for index, line in enumerate(lines) if _QUESTION_LINE.match(line.strip())),
            None,
        )
        if question_index is None:
            malformed.append(f"Question {number} has no Q: line")
            continue

        question_match = _QUESTION_LINE.match(lines[question_index].strip())
        question = question_match.group(1).strip() if question_match else ""
        answer = "\n".join(line.rstrip() for line in lines[question_index + 1:]).strip()
        if not title or not question or not answer:
            malformed.append(f"Question {number} is missing its title, question, or answer")
            continue

        records.append({
            "question_number": number,
            "module": module,
            "title": title,
            "question": question,
            "answer": answer,
        })

    if malformed:
        raise ValueError("Malformed Q&A entries: " + "; ".join(malformed[:10]))
    if not records:
        raise ValueError("No numbered Q&A records were found")
    return records


class QAService:
    def __init__(self, path: Optional[Path] = None):
        self.path = path or settings.QA_DATA_PATH
        self.records: List[Dict] = []
        self._record_tokens: List[Set[str]] = []
        self._load()

    def _load(self) -> None:
        if not self.path.is_file():
            logger.warning("Supplemental e-GP Q&A file is missing: %s", self.path)
            return

        text = self.path.read_text(encoding="utf-8-sig")
        self.records = parse_qa_text(text)
        self._record_tokens = [
            _search_tokens(f"{record['title']} {record['question']}")
            for record in self.records
        ]
        logger.info("Loaded %s supplemental e-GP Q&A records from %s", len(self.records), self.path)

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        query_tokens = _search_tokens(query)
        if len(query_tokens) < 2 or not self.records or limit < 1:
            return []

        document_frequency: Dict[str, int] = {}
        for tokens in self._record_tokens:
            for token in tokens:
                document_frequency[token] = document_frequency.get(token, 0) + 1

        def idf(token: str) -> float:
            count = document_frequency.get(token, 0)
            return 1.0 + math.log((len(self.records) + 1) / (count + 1))

        query_weight = sum(idf(token) for token in query_tokens)
        normalized_query = " ".join(sorted(query_tokens))
        matches = []
        for record, record_tokens in zip(self.records, self._record_tokens):
            common = query_tokens & record_tokens
            if not common:
                continue

            matched_weight = sum(idf(token) for token in common)
            candidate_weight = sum(idf(token) for token in record_tokens)
            coverage = matched_weight / query_weight if query_weight else 0.0
            precision = matched_weight / candidate_weight if candidate_weight else 0.0
            candidate_text = " ".join(sorted(record_tokens))
            similarity = SequenceMatcher(None, normalized_query, candidate_text).ratio()
            score = min(1.0, 0.72 * coverage + 0.18 * precision + 0.10 * similarity)
            direct_match = (
                len(query_tokens) >= 2
                and coverage >= 0.80
                and score >= 0.68
            ) or (len(query_tokens) >= 2 and similarity >= 0.90)

            matches.append({
                "record": record,
                "score": score,
                "direct_match": direct_match,
            })

        matches.sort(key=lambda item: item["score"], reverse=True)
        return [item for item in matches[:limit] if item["score"] >= 0.25]


qa_service = QAService()
