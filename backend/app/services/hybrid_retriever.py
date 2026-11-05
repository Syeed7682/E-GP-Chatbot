"""
Hybrid Retriever Service (app/services/hybrid_retriever.py).
Combines FAISS vector search with BM25 keyword search, fused and reranked.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.services.reranker import reranker

class HybridRetriever:
    def __init__(self):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.reranker = reranker

    def retrieve(self, query: str, top_k: int = 5, image: Optional[str] = None) -> List[Tuple[Dict[str, Any], float]]:
        """Performs hybrid retrieval using BGE-M3 text embeddings and BM25 candidate fusion."""
        # Ensure vector store is loaded
        if not self.vector_store.is_ready():
            self.vector_store.load_index_if_needed()

        candidates: List[Tuple[Dict[str, Any], float]] = []

        # 1. Dense Vector Search with BGE-M3
        try:
            query_vector = self.embedding_service.embed_query(query)
            # Retrieve 2x top_k candidates for reranking
            dense_results = self.vector_store.search(query_vector, top_k=max(top_k * 3, 15))
            candidates.extend(dense_results)
        except Exception as e:
            print(f"[hybrid_retriever] Vector search notice: {e}")

        # 2. BM25 / Exact keyword matching on loaded metadata
        q_words = [w.lower() for w in query.split() if len(w) > 2]
        if self.vector_store.metadata:
            for item in self.vector_store.metadata:
                text = item.get("content", "").lower()
                title = item.get("section_title", "").lower()
                bm25_score = 0.0
                for w in q_words:
                    if w in title:
                        bm25_score += 0.5
                    if w in text:
                        bm25_score += 0.2
                if bm25_score > 0.4:
                    candidates.append((item, min(0.9, bm25_score)))

        # Deduplicate candidates by chunk_id keeping max score
        dedup_map: Dict[int, Tuple[Dict[str, Any], float]] = {}
        for chunk, score in candidates:
            cid = chunk.get("chunk_id", hash(chunk.get("content", "")))
            if cid not in dedup_map or score > dedup_map[cid][1]:
                dedup_map[cid] = (chunk, score)

        unique_candidates = list(dedup_map.values())
        if not unique_candidates:
            return []

        # 3. Rerank candidates and filter TOC
        reranked = self.reranker.rerank(query, unique_candidates, top_k=top_k)
        return reranked

hybrid_retriever = HybridRetriever()

