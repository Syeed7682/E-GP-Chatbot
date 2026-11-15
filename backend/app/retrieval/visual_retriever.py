"""
Visual Retriever for e-GP Manual Screenshot and Page-Image Index.
Searches SigLIP visual FAISS index with either text embeddings or uploaded image embeddings.
"""
import logging
from typing import Any, Dict, List
import faiss
import numpy as np

logger = logging.getLogger(__name__)


def retrieve_visual(query_vector: np.ndarray, visual_index: Any, top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Performs visual similarity search using a query vector in the shared SigLIP space.
    
    Args:
        query_vector: (1, 768) float32 vector (from text or image encoding)
        visual_index: FAISS visual index
        top_k: Top candidate count
        
    Returns:
        List of dicts: [{"id": int(vector_id), "score": float(similarity)}]
    """
    if visual_index is None or visual_index.ntotal == 0 or query_vector is None:
        return []

    try:
        vec = np.asarray(query_vector, dtype=np.float32)
        if vec.ndim == 1:
            vec = vec.reshape(1, -1)
        faiss.normalize_L2(vec)

        scores, ids = visual_index.search(vec, min(top_k, visual_index.ntotal))
        results = [
            {"id": int(idx), "score": float(score)}
            for score, idx in zip(scores[0], ids[0])
            if idx != -1
        ]
        return results
    except Exception as e:
        logger.warning("Error during visual retrieval: %s", e)
        return []

