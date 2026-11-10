"""Loads and searches the supplemental e-GP question-and-answer text corpus."""
import logging
import math
import re
from difflib import SequenceMatcher
from collections import Counter, defaultdict
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
    """Builds sparse TF-IDF vectors and inverted indexes for supplemental Q&A documents."""

    def __init__(self, path: Optional[Path] = None, docx_path: Optional[Path] = None):
        self.path = path or settings.QA_DATA_PATH
        self.docx_path = docx_path if path is None else None
        if path is None and self.docx_path is None:
            self.docx_path = settings.QA_DOCX_PATH
        self.records: List[Dict] = []
        self._question_tokens: List[Set[str]] = []
        self._answer_tokens: List[Set[str]] = []
        self._question_vectors: List[Dict[str, float]] = []
        self._answer_vectors: List[Dict[str, float]] = []
        self._question_postings: Dict[str, Set[int]] = defaultdict(set)
        self._answer_postings: Dict[str, Set[int]] = defaultdict(set)
        self._document_frequency: Counter[str] = Counter()
        self._load()

    def _load(self) -> None:
        parsed_sources = []
        for path in (self.path, self.docx_path):
            if path is None:
                continue
            if not path.is_file():
                if path == self.path:
                    logger.warning("Supplemental e-GP Q&A file is missing: %s", path)
                continue
            if path.suffix.lower() == ".docx":
                from docx import Document

                text = "\n".join(paragraph.text for paragraph in Document(path).paragraphs)
            else:
                text = path.read_text(encoding="utf-8-sig")
            parsed_sources.append((path.name, parse_qa_text(text)))

        if not parsed_sources:
            return

        records_by_key: Dict[tuple[int, str], Dict] = {}
        for source_name, source_records in parsed_sources:
            for record in source_records:
                key = (
                    record["question_number"],
                    " ".join(sorted(_search_tokens(record["question"]))),
                )
                existing = records_by_key.get(key)
                if existing is None:
                    records_by_key[key] = {
                        **record,
                        "source": source_name,
                        "source_files": [source_name],
                    }
                elif source_name not in existing["source_files"]:
                    existing["source_files"].append(source_name)

        self.records = sorted(records_by_key.values(), key=lambda record: record["question_number"])
        self._build_index()
        logger.info(
            "Loaded and indexed %s supplemental Q&A records from %s (%s question terms, %s answer terms)",
            len(self.records),
            ", ".join(name for name, _ in parsed_sources),
            len(self._question_postings),
            len(self._answer_postings),
        )

    def _build_index(self) -> None:
        self._question_tokens.clear()
        self._answer_tokens.clear()
        self._question_vectors.clear()
        self._answer_vectors.clear()
        self._question_postings.clear()
        self._answer_postings.clear()
        self._document_frequency.clear()

        for record_id, record in enumerate(self.records):
            question_tokens = _search_tokens(f"{record['title']} {record['question']}")
            answer_tokens = _search_tokens(record["answer"])
            self._question_tokens.append(question_tokens)
            self._answer_tokens.append(answer_tokens)

            for token in question_tokens:
                self._question_postings[token].add(record_id)
            for token in answer_tokens:
                self._answer_postings[token].add(record_id)
            for token in question_tokens | answer_tokens:
                self._document_frequency[token] += 1

        document_count = len(self.records)

        def idf(token: str) -> float:
            frequency = self._document_frequency[token]
            return 1.0 + math.log((document_count + 1) / (frequency + 1))

        def vectorize(tokens: Set[str]) -> Dict[str, float]:
            weights = {token: idf(token) for token in tokens}
            norm = math.sqrt(sum(weight * weight for weight in weights.values()))
            return {token: weight / norm for token, weight in weights.items()} if norm else {}

        for question_tokens, answer_tokens in zip(self._question_tokens, self._answer_tokens):
            self._question_vectors.append(vectorize(question_tokens))
            self._answer_vectors.append(vectorize(answer_tokens))

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        query_tokens = _search_tokens(query)
        if len(query_tokens) < 2 or not self.records or limit < 1:
            return []

        query_weights = {
            token: 1.0 + math.log((len(self.records) + 1) / (self._document_frequency.get(token, 0) + 1))
            for token in query_tokens
        }
        query_norm = math.sqrt(sum(weight * weight for weight in query_weights.values()))
        query_vector = {
            token: weight / query_norm
            for token, weight in query_weights.items()
        } if query_norm else {}
        normalized_query = " ".join(sorted(query_tokens))
        matches = []
        candidate_ids: Set[int] = set()
        for token in query_tokens:
            candidate_ids.update(self._question_postings.get(token, ()))
            candidate_ids.update(self._answer_postings.get(token, ()))

        for record_id in candidate_ids:
            record = self.records[record_id]
            question_tokens = self._question_tokens[record_id]
            answer_tokens = self._answer_tokens[record_id]
            question_matches = query_tokens & question_tokens
            answer_matches = query_tokens & answer_tokens
            if not question_matches and not answer_matches:
                continue

            question_similarity = sum(
                query_vector.get(token, 0.0) * self._question_vectors[record_id].get(token, 0.0)
                for token in query_tokens
            )
            answer_similarity = sum(
                query_vector.get(token, 0.0) * self._answer_vectors[record_id].get(token, 0.0)
                for token in query_tokens
            )
            coverage = len(question_matches) / len(query_tokens)
            answer_coverage = len(answer_matches) / len(query_tokens)
            candidate_text = " ".join(sorted(question_tokens))
            similarity = SequenceMatcher(None, normalized_query, candidate_text).ratio()
            question_score = 0.70 * question_similarity + 0.20 * answer_similarity + 0.10 * similarity
            answer_score = 0.65 * answer_similarity + 0.35 * answer_coverage
            score = min(1.0, max(question_score, answer_score))
            direct_match = coverage >= 0.75 and question_similarity >= 0.68
            matches.append({
                "record": record,
                "score": score,
                "direct_match": direct_match,
            })

        matches.sort(key=lambda item: item["score"], reverse=True)
        return [item for item in matches[:limit] if item["score"] >= 0.25]


qa_service = QAService()
