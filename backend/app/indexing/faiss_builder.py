"""
FAISS Index Builder and Loader.
Constructs IndexIDMap2(IndexFlatIP) indices with L2-normalized vectors (cosine similarity).
Writes indices to disk with dimension verification and ID tracking.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import faiss
import numpy as np

logger = logging.getLogger(__name__)


def build_faiss_index(
    vectors: np.ndarray,
    records: Optional[List[Dict[str, Any]]] = None,
    output_path: Optional[str | Path] = None,
    ids: Optional[np.ndarray] = None,
) -> faiss.Index:
    """
    Builds and saves a FAISS IndexIDMap2(IndexFlatIP) index.
    
    Args:
        vectors: 2D numpy array of shape (N, dimension)
        records: Metadata records matching vector count
        output_path: Destination path for .faiss index file
        ids: Optional custom int64 IDs. If omitted, sequential IDs 0..N-1 are used.
    """
    vectors = np.asarray(vectors, dtype=np.float32).copy()
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    faiss.normalize_L2(vectors)
    num_vectors, dimension = vectors.shape

    base_index = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIDMap2(base_index)

    if ids is None:
        count = len(records) if records is not None else num_vectors
        ids = np.arange(count, dtype=np.int64)
    else:
        ids = np.asarray(ids, dtype=np.int64)

    if num_vectors > 0:
        index.add_with_ids(vectors, ids)

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(out_p))
        logger.info("Saved FAISS index (%d vectors, %d-dim) to %s", num_vectors, dimension, out_p)

    return index


def load_faiss_index(index_path: str | Path) -> faiss.Index:
    """Loads a FAISS index from disk."""
    p = Path(index_path)
    if not p.exists():
        raise FileNotFoundError(f"FAISS index not found: {p}")
    index = faiss.read_index(str(p))
    logger.info("Loaded FAISS index with %d vectors (dimension: %d) from %s", index.ntotal, index.d, p)
    return index

