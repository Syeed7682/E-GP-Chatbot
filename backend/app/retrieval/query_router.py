"""
Query Router for e-GP Manual RAG System.
Analyzes user inputs to determine modality, intent, and appropriate retrieval channels.
"""
import re
from typing import Any, Dict, Optional


class QueryRouter:
    """Routes queries to optimal retrieval channels and model pipelines."""

    def __init__(self):
        self.fee_pattern = re.compile(r"\b(fee|cost|price|tender\s*document\s*fee|nct|ict|bdt|charge)\b", re.IGNORECASE)
        self.code_pattern = re.compile(r"\b(rule|section|clause|app|slt|tec|tsc|ter|tor|pcc|tds|noa|jvca|pg|mb|ddo|ibas)\b", re.IGNORECASE)
        self.procedure_pattern = re.compile(r"\b(how\s+to|step|procedure|process|workflow|create|submit|approve|register|verify|delete)\b", re.IGNORECASE)
        self.bangla_pattern = re.compile(r"[\u0980-\u09FF]")

    def route(self, query: str, has_image: bool = False) -> Dict[str, Any]:
        """
        Analyzes query and returns routing directives.
        """
        text = query.strip()
        is_visual = has_image or bool(re.search(r"\b(screenshot|screen|image|look\s+at|show\s+screen)\b", text, re.IGNORECASE))
        has_fee = bool(self.fee_pattern.search(text))
        has_exact_code = bool(self.code_pattern.search(text))
        is_procedure = bool(self.procedure_pattern.search(text))
        has_bangla = bool(self.bangla_pattern.search(text))

        channels = ["pdf_text", "qa", "bm25"]
        if is_visual:
            channels.append("visual")

        return {
            "query": text,
            "has_image": has_image,
            "is_visual": is_visual,
            "has_fee": has_fee,
            "has_exact_code": has_exact_code,
            "is_procedure": is_procedure,
            "has_bangla": has_bangla,
            "channels": channels,
            "use_vision_model": is_visual,
        }

