"""
Text Retriever for e-GP Manual FAISS dense index.
Encodes query with BGE-M3 text embedder and searches inner product index.
"""
import logging
from typing import Any, Dict, List
import faiss
import numpy as np

logger = logging.getLogger(__name__)


def retrieve_text(query: str, index: Any, embedder: Any, top_k: int = 20) -> List[Dict[str, Any]]:
    """
    Performs dense semantic search on a FAISS index.
    
    Args:
        query: User text query
        index: FAISS index
        embedder: Text embedder with .encode()
        top_k: Number of candidates to retrieve
        
    Returns:
        List of dicts: [{"id": int(vector_id), "score": float(cosine_sim)}]
    """
    if not query or not query.strip() or index is None or index.ntotal == 0:
        return []

    try:
        vector = embedder.encode([query])
        vector = np.asarray(vector, dtype=np.float32)
        if vector.ndim == 1:
            vector = vector.reshape(1, -1)
        faiss.normalize_L2(vector)

        scores, ids = index.search(vector, min(top_k, index.ntotal))
        results = [
            {"id": int(idx), "score": float(score)}
            for score, idx in zip(scores[0], ids[0])
            if idx != -1
        ]
        return results
    except Exception as e:
        logger.warning("Error during text dense retrieval: %s", e)
        return []

