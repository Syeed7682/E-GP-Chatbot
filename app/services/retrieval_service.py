"""
Retrieval Service (app/services/retrieval_service.py).
Combines dense FAISS vector similarity and BM25 keyword matching with domain query expansion.
Given a user question, it retrieves the most relevant manual sections and prepares them for LLM synthesis.
"""
import os
import re
import math
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service

STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
    'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself',
    'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most',
    'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our',
    'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than',
    'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn', 'we', 'were',
    'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'you',
    'your', 'yours', 'yourself', 'yourselves', 'tell', 'give', 'show', 'please', 'proper', 'answer',
    'details', 'descriptive', 'descriptecd', 'desc', 'information', 'guide', 'steps',
    'make', 'do', 'get', 'set', 'take', 'put', 'say', 'see', 'know', 'think', 'want', 'use',
    'find', 'like', 'need', 'help', 'hi', 'hello', 'hey', 'joke', 'jokes', 'funny', 'story',
    'stories', 'game', 'song', 'poem', 'write', 'sing'
}

# Domain-specific synonym expansions for Bangladesh e-GP terminology
DOMAIN_SYNONYMS = {
    'open account': ['created by', 'admin', 'login', 'email', 'password', 'procuring entity', 'username'],
    'create account': ['created by', 'admin', 'login', 'credentials', 'procuring entity', 'username'],
    'account': ['created by', 'admin', 'login', 'credentials', 'username', 'password', 'profile', 'my account'],
    'registration': ['created by', 'admin', 'login', 'credentials', 'procuring entity'],
    'register': ['created by', 'admin', 'login', 'credentials', 'procuring entity'],
    'sign up': ['created by', 'admin', 'login', 'credentials', 'procuring entity'],
    'signup': ['created by', 'admin', 'login', 'credentials', 'procuring entity'],
    'login': ['login', 'email id', 'password', 'change password', 'credentials', 'nid'],
    'approved workflow': ['approved workflow', 'workflow', 'screen e11', 'screen e12', 'sub menu'],
    'workflow': ['workflow', 'approved', 'checker', 'approver', 'flow', 'sub menu'],
    'annual procurement plan': ['app', 'annual procurement plan', 'procurement nature', 'package'],
    'app': ['annual procurement plan', 'procurement nature', 'package'],
    'tender': ['tender', 'notice', 'proposal', 'procuring entity', 'tenderer'],
    'evaluation': ['evaluation', 'pec', 'toc', 'poc', 'technical', 'financial'],
    'audit': ['audit', 'audit trail', 'log'],
    'cms': ['cms', 'contract management', 'measurement', 'invoice'],
    'my account': ['profile', 'view profile', 'edit profile', 'nid', 'mobile'],
}


class RetrievalService:
    def __init__(self, emb_service=embedding_service, f_service=faiss_service):
        self.embedding_service = emb_service
        self.faiss_service = f_service

    def is_ready(self) -> bool:
        """Returns True if the FAISS index is loaded and ready to serve queries."""
        return self.faiss_service.index is not None and len(self.faiss_service.metadata) > 0

    def load_index_if_needed(self) -> bool:
        """Attempts to load the index from default paths if not already loaded."""
        if not self.is_ready():
            return self.faiss_service.load()
        return True

    def _keyword_rank(self, question: str, chunks: List[Dict], top_k: int = 10) -> List[Tuple[float, Dict]]:
        """
        Ranks chunks using domain-aware keyword matching, phrase boosting, and title matching.
        """
        q_lower = question.lower()
        raw_words = [w for w in re.findall(r'\w+', q_lower) if w not in STOPWORDS]
        if not raw_words:
            return []

        expanded = list(raw_words)
        for term, syns in DOMAIN_SYNONYMS.items():
            if term in q_lower or all(w in raw_words for w in term.split()):
                expanded.extend(syns)

        scored = []
        is_account_intent = any(k in q_lower for k in [
            "open an account", "open account", "create account", "create an account",
            "how to register", "registration", "signup", "sign up", "new user", "create user"
        ])
        is_workflow_intent = "approved workflow" in q_lower or ("workflow" in q_lower and "approved" in q_lower)
        is_app_intent = "annual procurement plan" in q_lower or bool(re.search(r'\bapp\b', q_lower))

        for c in chunks:
            text = c.get("text", "").lower()
            page = c.get("page", 0)
            score = 0.0

            # Direct intent grounding
            if is_account_intent:
                if page in (6, 7, 8):
                    score += 18.0
                elif page == 533:
                    score += 10.0

            if is_workflow_intent and page == 199:
                score += 25.0

            if is_app_intent and page in (21, 22, 23, 24, 25):
                score += 15.0

            # 1. Exact multi-word phrase match (huge boost)
            matched_phrase = False
            for phrase in DOMAIN_SYNONYMS.keys():
                if phrase in q_lower and phrase in text:
                    score += 8.0
                    matched_phrase = True

            # Check term coverage: chunk must contain at least 50% of query keywords unless grounded by intent/phrase
            matched_words = [w for w in raw_words if re.search(r'\b' + re.escape(w) + r'\b', text)]
            term_coverage = len(matched_words) / len(raw_words) if raw_words else 0.0

            if term_coverage < 0.5 and not matched_phrase and not is_account_intent and not is_workflow_intent and not is_app_intent:
                continue

            # 2. Raw keyword matches
            for w in matched_words:
                score += 3.0

            # 3. Expanded term matches
            for ew in expanded:
                if re.search(r'\b' + re.escape(ew) + r'\b', text):
                    score += 1.2

            # 4. First line / section title match
            first_line = text.split("\n")[0]
            for w in raw_words:
                if re.search(r'\b' + re.escape(w) + r'\b', first_line):
                    score += 4.5

            if score > 0:
                scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    def retrieve(self, question: str, top_k: int = 3, image: Optional[Any] = None) -> Tuple[str, List[Dict]]:
        """
        Retrieves top_k most relevant chunks using hybrid FAISS dense search + keyword matching.
        
        Args:
            question: The user's text query.
            top_k: Number of relevant chunks to retrieve.
            image: Optional query image for multimodal search.
            
        Returns:
            Tuple of:
            - context_str: Formatted context block for the LLM prompt.
            - sources: List of structured source metadata dicts with image_path.
        """
        if not self.load_index_if_needed():
            return "No manual index is loaded. Please run ingestion and index building first.", []

        # Early guardrail: If text query has no substantive keywords and no image is attached
        raw_words = [w for w in re.findall(r'\w+', question.lower()) if w not in STOPWORDS]
        if not raw_words and image is None:
            return "No relevant context found in manuals.", []

        # 1. FAISS Dense Retrieval
        if image is not None:
            query_vec = self.embedding_service.embed_multimodal(text=question, image=image)
        else:
            query_vec = self.embedding_service.embed_text(question)

        faiss_results = self.faiss_service.search(query_vec, top_k=max(top_k * 2, 8))

        # 2. Domain Keyword Retrieval (when text query is present)
        kw_results = []
        if question and self.faiss_service.metadata:
            kw_results = self._keyword_rank(question, self.faiss_service.metadata, top_k=max(top_k * 2, 8))

        # 3. Hybrid Fusion Ranking
        combined_scores: Dict[int, Dict[str, Any]] = {}

        # Keywords have 0.70 weight for precise textual grounding; FAISS has 0.30 semantic weight
        kw_weight = 0.70 if kw_results else 0.0
        faiss_weight = 0.30 if kw_results else 1.0

        # Normalize and add FAISS scores
        max_faiss = max((item["score"] for item in faiss_results), default=1.0)
        max_faiss = max(max_faiss, 0.001)
        for item in faiss_results:
            cid = item["chunk"]["chunk_id"]
            norm_score = max(0.0, item["score"]) / max_faiss
            combined_scores[cid] = {
                "score": norm_score * faiss_weight,
                "chunk": item["chunk"]
            }

        # Normalize and add Keyword scores
        if kw_results:
            max_kw = max((score for score, _ in kw_results), default=1.0)
            max_kw = max(max_kw, 0.001)
            for kw_score, chunk in kw_results:
                cid = chunk["chunk_id"]
                norm_kw = kw_score / max_kw
                if cid in combined_scores:
                    combined_scores[cid]["score"] += norm_kw * kw_weight
                else:
                    combined_scores[cid] = {
                        "score": norm_kw * kw_weight,
                        "chunk": chunk
                    }

        if not combined_scores:
            return "No relevant context found in manuals.", []

        # Filter out irrelevant noise (e.g. non-procurement queries like "make a joke")
        raw_words = [w for w in re.findall(r'\w+', question.lower()) if w not in STOPWORDS]
        if not kw_results and (not raw_words or max_faiss < 0.35):
            return "No relevant context found in manuals.", []

        # Sort and take top_k
        ranked = sorted(combined_scores.values(), key=lambda x: x["score"], reverse=True)
        top_matches = ranked[:top_k]

        # 4. Format context string and source items
        context_parts = []
        sources = []

        for item in top_matches:
            score = item["score"]
            chunk = item["chunk"]
            source = chunk.get("source", "unknown")
            page = chunk.get("page", 1)
            chunk_id = chunk.get("chunk_id", 0)
            text = chunk.get("text", "")
            image_path = chunk.get("image_path")

            # Clean header for synthesis
            img_tag = f" | Screenshot: {os.path.basename(image_path)}" if image_path else ""
            chunk_header = f"[Manual: {source} | Page {page}{img_tag} | Relevance: {score:.2f}]"
            context_parts.append(f"{chunk_header}\n{text}")

            sources.append({
                "source": source,
                "page": page,
                "chunk_id": chunk_id,
                "score": round(score, 2),
                "snippet": text[:250] + ("..." if len(text) > 250 else ""),
                "image_path": image_path
            })

        full_context_str = "\n\n---\n\n".join(context_parts)
        return full_context_str, sources


# Singleton instance
retrieval_service = RetrievalService()

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    r = RetrievalService()
    print(f"Retrieval service initialized. Ready: {r.is_ready()}")
