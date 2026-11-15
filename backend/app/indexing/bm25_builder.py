"""
BM25 Lexical Index Builder and Retriever.
Uses rank-bm25 (BM25Okapi) for exact terminology matching (e-GP codes, NCT, tender security, etc.).
Serializes and loads lexical indexes alongside FAISS dense indices.
"""
import logging
import pickle
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "what", "when", "where", "who", "will", "with", "the", "e", "gp",
}


def tokenize_for_bm25(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric keywords, filtering stopwords."""
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = [t for t in re.split(r"[\s-]+", clean) if len(t) > 1 and t not in STOP_WORDS]
    return tokens


class BM25Index:
    """Wrapper around rank-bm25 BM25Okapi with document metadata tracking."""

    def __init__(self, bm25_model=None, doc_ids: Optional[List[str]] = None):
        self.bm25 = bm25_model
        self.doc_ids = doc_ids or []

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Searches BM25 index and returns list of {id: doc_id, score: float}."""
        if self.bm25 is None or not self.doc_ids:
            return []

        tokens = tokenize_for_bm25(query)
        if not tokens:
            return []

        try:
            scores = self.bm25.get_scores(tokens)
            ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            results = []
            for idx in ranked_indices:
                if scores[idx] > 0.0:
                    results.append({
                        "id": self.doc_ids[idx],
                        "score": float(scores[idx]),
                    })
            return results
        except Exception as e:
            logger.warning("BM25 search error: %s", e)
            return []


def build_bm25_index(documents: List[Dict[str, Any]], output_path: Optional[str | Path] = None) -> BM25Index:
    """
    Builds a BM25 index over a list of chunk dictionaries.
    Each document must have 'chunk_id' (or 'id') and 'text'.
    """
    import importlib
    try:
        bm25_mod = importlib.import_module("rank_bm25")
        BM25Okapi = getattr(bm25_mod, "BM25Okapi")
    except Exception:
        BM25Okapi = None

    corpus_tokens = []
    doc_ids = []

    for doc in documents:
        doc_id = doc.get("chunk_id") or doc.get("id") or str(len(doc_ids))
        text = doc.get("text") or doc.get("content") or ""
        tokens = tokenize_for_bm25(text)
        corpus_tokens.append(tokens)
        doc_ids.append(doc_id)

    bm25_model = BM25Okapi(corpus_tokens) if BM25Okapi is not None else None
    index = BM25Index(bm25_model=bm25_model, doc_ids=doc_ids)

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "wb") as f:
            pickle.dump({"bm25": bm25_model, "doc_ids": doc_ids}, f)
        logger.info("Saved BM25 index (%d documents) to %s", len(doc_ids), out_p)

    return index


def load_bm25_index(index_path: str | Path) -> BM25Index:
    """Loads a serialized BM25 index from disk."""
    p = Path(index_path)
    if not p.exists():
        raise FileNotFoundError(f"BM25 index not found: {p}")

    with open(p, "rb") as f:
        data = pickle.load(f)

    logger.info("Loaded BM25 index with %d documents from %s", len(data.get("doc_ids", [])), p)
    return BM25Index(bm25_model=data.get("bm25"), doc_ids=data.get("doc_ids", []))

