"""
FAISS Service.
Manages the creation, persistence, loading, and querying of the FAISS vector index.
Uses IndexFlatIP (Inner Product) which computes exact Cosine Similarity on L2-normalized vectors.
"""
import os
import json
import faiss
import numpy as np
from typing import List, Dict, Tuple, Optional

DEFAULT_INDEX_PATH = "data/faiss_index/index.faiss"
DEFAULT_METADATA_PATH = "data/faiss_index/metadata.json"

class FaissService:
    def __init__(self, index_path: str = DEFAULT_INDEX_PATH, metadata_path: str = DEFAULT_METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict] = []

    def build_index(self, embeddings: np.ndarray, metadata: List[Dict]) -> faiss.IndexFlatIP:
        """
        Builds a new FAISS index from an embedding matrix.
        
        Args:
            embeddings: Float32 numpy array of shape (N, dimension).
            metadata: List of metadata dictionaries corresponding to each vector.
            
        Returns:
            The populated FAISS IndexFlatIP.
        """
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings must be 2D array, got shape {embeddings.shape}")
        
        num_vectors, dimension = embeddings.shape
        if num_vectors != len(metadata):
            raise ValueError(f"Vector count ({num_vectors}) does not match metadata length ({len(metadata)})")

        print(f"[faiss_service] Creating FAISS IndexFlatIP with dimension {dimension} for {num_vectors} vectors...")
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings.astype(np.float32))

        self.index = index
        self.metadata = metadata
        print(f"[faiss_service] Index built successfully. Total entries: {index.ntotal}")
        return index

    def save(self, index_path: Optional[str] = None, metadata_path: Optional[str] = None) -> None:
        """Saves current index and metadata to disk."""
        if self.index is None or not self.metadata:
            raise ValueError("No index or metadata in memory to save.")

        idx_path = index_path or self.index_path
        meta_path = metadata_path or self.metadata_path

        os.makedirs(os.path.dirname(idx_path), exist_ok=True)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)

        # 1. Save FAISS binary index
        faiss.write_index(self.index, idx_path)

        # 2. Save metadata JSON
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)

        print(f"[faiss_service] Saved FAISS index to '{idx_path}' and metadata to '{meta_path}'.")

    def load(self, index_path: Optional[str] = None, metadata_path: Optional[str] = None) -> bool:
        """
        Loads index and metadata from disk into memory.
        
        Returns:
            True if loaded successfully, False otherwise.
        """
        idx_path = index_path or self.index_path
        meta_path = metadata_path or self.metadata_path

        if not os.path.exists(idx_path) or not os.path.exists(meta_path):
            print(f"[faiss_service] Index or metadata not found at '{idx_path}'.")
            return False

        try:
            self.index = faiss.read_index(idx_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print(f"[faiss_service] Successfully loaded FAISS index ({self.index.ntotal} vectors) from '{idx_path}'.")
            return True
        except Exception as e:
            print(f"[faiss_service] Error loading FAISS index: {e}")
            return False

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Dict]:
        """
        Searches the index for the most similar chunks.
        
        Args:
            query_vector: 1D numpy array of shape (dimension,) or 2D of shape (1, dimension).
            top_k: Number of nearest matches to retrieve.
            
        Returns:
            List of result dicts: [{"score": float, "chunk": dict}, ...]
        """
        if self.index is None or not self.metadata:
            raise RuntimeError("FAISS index is not loaded. Build or load an index first.")

        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)

        query_vector = query_vector.astype(np.float32)
        top_k = min(top_k, self.index.ntotal)

        # Perform FAISS search
        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for rank in range(top_k):
            idx = indices[0][rank]
            score = float(scores[0][rank])
            if idx < len(self.metadata):
                chunk_data = self.metadata[idx]
                results.append({
                    "score": round(score, 4),
                    "chunk": chunk_data
                })

        return results

# Singleton instance
faiss_service = FaissService()

if __name__ == "__main__":
    # Test FAISS operations
    sample_dim = 1024
    sample_vecs = np.random.randn(5, sample_dim).astype(np.float32)
    # L2 normalize
    sample_vecs = sample_vecs / np.linalg.norm(sample_vecs, axis=1, keepdims=True)
    sample_meta = [{"chunk_id": i, "source": f"manual_{i}.pdf", "page": 1, "text": f"Sample chunk {i}"} for i in range(5)]

    fs = FaissService()
    fs.build_index(sample_vecs, sample_meta)
    test_q = sample_vecs[0]
    hits = fs.search(test_q, top_k=2)
    print("Search Top Hits:")
    for h in hits:
        print(f"  Score: {h['score']} -> {h['chunk']['source']}")

