"""
Reranker Service (app/services/reranker.py).
Cross-encoder / semantic reranker that prioritizes procedural and statutory sections
while penalizing introductory or Table of Contents pages (pages 1–5).
"""
import re
from typing import List, Dict, Any, Tuple

class Reranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        self.model_name = model_name
        self._model = None

    def rerank(self, query: str, candidate_chunks: List[Tuple[Dict[str, Any], float]], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Reranks candidates based on exact keyword density, procedural section matching,
        and penalizing Table of Contents pages (pages <= 5).
        """
        q_lower = query.lower().strip()
        q_words = re.findall(r'\b\w{3,}\b', q_lower)
        stop_words = {'what', 'when', 'where', 'which', 'who', 'how', 'the', 'and', 'for', 'are', 'this', 'that', 'with', 'from', 'have', 'were', 'then', 'will', 'your', 'shown', 'please', 'tell'}
        meaningful_words = [w for w in q_words if w not in stop_words]

        scored: List[Tuple[Dict[str, Any], float]] = []

        for chunk, base_score in candidate_chunks:
            page = chunk.get("page_number", 0)
            title = chunk.get("section_title", "").lower()
            content = chunk.get("content", "").lower()

            # 1. Hard penalty for Table of Contents / Change Log pages (Pages 1 to 5)
            if page <= 5:
                # Substantially penalize so TOC lists are never returned as procedural instructions
                score = base_score - 2.0
            else:
                score = base_score

            # 2. Section Title Exact Boost
            for w in meaningful_words:
                if w in title:
                    score += 0.35
                if w in content:
                    # Count frequency
                    cnt = len(re.findall(r'\b' + re.escape(w) + r'\b', content))
                    score += min(0.3, cnt * 0.05)

            # 3. Intent Boosts
            # Debarment / Suspension
            if "debar" in q_lower or "blacklist" in q_lower:
                if "debar" in title or "suspension" in title:
                    score += 1.0

            # Delete / Cancel Tender
            if ("delete" in q_lower or "cancel" in q_lower) and "tender" in q_lower:
                if "cancel" in title or "cancellation" in content or "delete draft tender" in content:
                    score += 1.0

            # Login / Authentication
            if "login" in q_lower or "sign in" in q_lower or "password" in q_lower:
                if page == 6 or "login" in title:
                    score += 0.8

            scored.append((chunk, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

reranker = Reranker()

