"""Fallback order used by the e-GP retrieval pipeline.

This module is intentionally standalone. It documents the runtime order and
provides small helpers for CSV fallback decisions without changing retrieval
or application state.
"""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence


EMBEDDING_PROVIDER_ORDER: tuple[str, ...] = (
    "FlagEmbedding",
    "sentence-transformers",
    "Hugging Face inference API",
    "deterministic CRC32 hash fallback",
)

CSV_MIN_SCORE = 0.60
_STEPS_QUERY = re.compile(r"\b(?:steps?|step by step|procedure)\b", re.IGNORECASE)


def should_search_csv(
    question: str,
    qa_matches: Sequence[Mapping[str, Any]],
) -> bool:
    """Return whether the contractor-evaluation CSV should be searched."""

    is_steps_query = bool(_STEPS_QUERY.search(question))
    has_direct_qa_match = any(match.get("direct_match") for match in qa_matches)
    return not is_steps_query and not has_direct_qa_match


def select_csv_fallback(
    csv_matches: Sequence[Mapping[str, Any]],
    qa_matches: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Select CSV matches according to the current fallback rules.

    Direct CSV matches take priority. Otherwise, CSV results are accepted only
    when there are no baseline Q&A results and the score is at least 0.60.
    """

    direct_matches = [match for match in csv_matches if match.get("direct_match")]
    if direct_matches:
        return direct_matches

    if qa_matches:
        return []

    return [
        match
        for match in csv_matches
        if float(match.get("score", 0.0)) >= CSV_MIN_SCORE
    ]


def fallback_order() -> tuple[str, ...]:
    """Return the high-level retrieval fallback order."""

    return (
        "standard Q&A dataset",
        "contractor evaluation CSV",
        "FAISS semantic search when embeddings are available",
        "keyword retrieval when semantic search is unavailable",
        "hybrid ranking and top-k selection",
        "no relevant context response",
    )


if __name__ == "__main__":
    print("Retrieval fallback order:")
    for index, step in enumerate(fallback_order(), start=1):
        print(f"{index}. {step}")
    print("\nEmbedding providers:")
    for index, provider in enumerate(EMBEDDING_PROVIDER_ORDER, start=1):
        print(f"{index}. {provider}")
