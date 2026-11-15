"""
Document Reranker for e-GP Manual.
Uses BAAI/bge-reranker-v2-m3 cross-encoder to refine candidate evidence.
Includes CPU-efficient heuristic cross-scoring fallback.
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class DocumentReranker:
    """Reranks retrieved candidate documents using cross-attention scoring."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", use_fp16: bool = False):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.model = None
        self._init_model()

    def _init_model(self) -> None:
        try:
            from FlagEmbedding import FlagReranker
            self.model = FlagReranker(self.model_name, use_fp16=self.use_fp16)
            logger.info("Initialized DocumentReranker: %s", self.model_name)
        except Exception as e:
            logger.debug("FlagReranker not loaded (%s); using score-preserving ranker", e)
            self.model = None

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 7) -> List[Dict[str, Any]]:
        """
        Reranks a list of candidate documents against the query.
        Returns the top_k most relevant documents with 'rerank_score'.
        """
        if not documents:
            return []

        if self.model is not None:
            try:
                pairs = [[query, doc.get("text", "")[:1024]] for doc in documents]
                scores = self.model.compute_score(pairs, normalize=True)
                if not isinstance(scores, list):
                    scores = [scores]
                ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
                return [{**doc, "rerank_score": float(score)} for doc, score in ranked[:top_k]]
            except Exception as e:
                logger.warning("Reranker execution failed (%s); using heuristic ranking", e)

        # Fallback: combine existing candidate score / RRF score with query term overlap
        q_terms = set(query.lower().split())
        scored_docs = []
        for doc in documents:
            text = doc.get("text", "").lower()
            overlap = sum(1 for term in q_terms if term in text)
            base_score = float(doc.get("rrf_score", doc.get("score", 0.5)))
            combined_score = base_score + (overlap * 0.05)
            scored_docs.append({**doc, "rerank_score": float(combined_score)})

        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_docs[:top_k]

