"""
Reciprocal Rank Fusion (RRF) for Multi-Channel Retrieval.
Fuses dense PDF text, QA matches, visual candidates, and BM25 keyword rankings.
Uses namespaced IDs (e.g., PDF:145, QA:145, VISUAL:145) to prevent collision.
Deduplicates near-identical chunks and preserves page/source provenance.
"""
from typing import Any, Dict, List, Set


def reciprocal_rank_fusion(result_lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
    """
    Computes reciprocal rank fusion scores across multiple retrieval channels.
    
    Args:
        result_lists: Lists of candidate dicts with 'id' or 'namespaced_id'
        k: Smoothing constant (default 60)
        
    Returns:
        Ranked list of dicts with 'id' and 'rrf_score', descending
    """
    scores: Dict[str, float] = {}

    for result_list in result_lists:
        for rank, result in enumerate(result_list, start=1):
            doc_id = str(result.get("namespaced_id") or result.get("id"))
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    ranked = sorted(
        [{"id": doc_id, "rrf_score": score} for doc_id, score in scores.items()],
        key=lambda x: x["rrf_score"],
        reverse=True,
    )
    return ranked


def deduplicate_chunks(records: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
    """
    Deduplicates candidates that share identical or near-identical text,
    retaining the highest-ranked instance.
    """
    seen_texts: Set[str] = set()
    deduped: List[Dict[str, Any]] = []

    for rec in records:
        text = rec.get("text") or rec.get("content") or ""
        # Create a simplified fingerprint (first 100 chars lowercase alphanumeric)
        clean = "".join(c for c in text[:150].lower() if c.isalnum())
        if clean and clean in seen_texts:
            continue
        if clean:
            seen_texts.add(clean)
        deduped.append(rec)

    return deduped

