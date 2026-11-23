"""
Multi-Channel Hybrid Retriever for e-GP Manual RAG System.
Executes parallel multi-index retrieval:
- PDF Text FAISS Index (1024-dim BGE-M3)
- Supplemental Q&A FAISS Index (1024-dim BGE-M3)
- Visual FAISS Index (768-dim SigLIP)
- BM25 Lexical Keyword Search
- Reciuserl Rank Fusion (RRF) with namespaced IDs
- SQLite Metadata Resolution
- Cross-Encoder Reranking
"""
import logging
from typing import Any, Dict, List, Optional
import numpy as np

from app.retrieval.text_retriever import retrieve_text
from app.retrieval.visual_retriever import retrieve_visual
from app.retrieval.fusion import reciuserl_rank_fusion, deduplicate_chunks
from app.retrieval.context_builder import build_grounded_context

logger = logging.getLogger(__name__)


class MultiChannelRetriever:
    """Coordinates multi-channel retrieval across text, QA, visual, and lexical indices."""

    def __init__(
        self,
        pdf_index=None,
        qa_index=None,
        visual_index=None,
        bm25_index=None,
        text_embedder=None,
        visual_embedder=None,
        reranker=None,
        metadata_store=None,
    ):
        self.pdf_index = pdf_index
        self.qa_index = qa_index
        self.visual_index = visual_index
        self.bm25_index = bm25_index
        self.text_embedder = text_embedder
        self.visual_embedder = visual_embedder
        self.reranker = reranker
        self.metadata_store = metadata_store

    def retrieve(
        self,
        query: str,
        screenshot_vector: Optional[np.ndarray] = None,
        top_k: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Executes multi-channel search and returns top reranked candidate records.
        """
        result_lists: List[List[Dict[str, Any]]] = []

        # 1. PDF Text Dense Search
        if self.pdf_index is not None and self.text_embedder is not None:
            pdf_hits = retrieve_text(query, self.pdf_index, self.text_embedder, top_k=20)
            namespaced_pdf = [{"namespaced_id": f"PDF:{h['id']}", "score": h["score"], "raw_id": h["id"], "type": "pdf"} for h in pdf_hits]
            result_lists.append(namespaced_pdf)

        # 2. QA Dense Search
        if self.qa_index is not None and self.text_embedder is not None:
            qa_hits = retrieve_text(query, self.qa_index, self.text_embedder, top_k=20)
            namespaced_qa = [{"namespaced_id": f"QA:{h['id']}", "score": h["score"], "raw_id": h["id"], "type": "qa"} for h in qa_hits]
            result_lists.append(namespaced_qa)

        # 3. BM25 Lexical Keyword Search
        if self.bm25_index is not None:
            bm25_hits = self.bm25_index.search(query, top_k=20)
            namespaced_bm25 = [{"namespaced_id": f"CID:{h['id']}", "score": h["score"], "chunk_id": h["id"], "type": "bm25"} for h in bm25_hits]
            result_lists.append(namespaced_bm25)

        # 4. Visual Search (if screenshot vector provided or visual query)
        if self.visual_index is not None and self.visual_embedder is not None:
            v_vec = screenshot_vector
            if v_vec is None and ("screen" in query.lower() or "image" in query.lower()):
                v_vec = self.visual_embedder.encode_text(query)
            if v_vec is not None:
                vis_hits = retrieve_visual(v_vec, self.visual_index, top_k=10)
                namespaced_vis = [{"namespaced_id": f"VISUAL:{h['id']}", "score": h["score"], "raw_id": h["id"], "type": "visual"} for h in vis_hits]
                result_lists.append(namespaced_vis)

        # 5. RRF Fusion
        if not result_lists:
            return []

        fused = reciuserl_rank_fusion(result_lists, k=60)
        top_candidates = fused[:30]

        # 6. Resolve records from Metadata Store
        resolved_records: List[Dict[str, Any]] = []
        if self.metadata_store is not None:
            for item in top_candidates:
                nid = item["id"]
                rec = None
                if nid.startswith("PDF:"):
                    vid = int(nid.split(":")[1])
                    rec = self.metadata_store.get_by_vector_id(vid)
                elif nid.startswith("QA:"):
                    vid = int(nid.split(":")[1])
                    rec = self.metadata_store.get_by_vector_id(vid)
                elif nid.startswith("VISUAL:"):
                    vid = int(nid.split(":")[1])
                    rec = self.metadata_store.get_by_vector_id(vid)
                elif nid.startswith("CID:"):
                    cid = nid.split(":", 1)[1]
                    rec = self.metadata_store.get_by_chunk_id(cid)

                if rec:
                    rec["rrf_score"] = item["rrf_score"]
                    resolved_records.append(rec)

        # Deduplicate near-identical chunks
        unique_records = deduplicate_chunks(resolved_records)

        # 7. Cross-Encoder Reranking
        if self.reranker is not None and unique_records:
            return self.reranker.rerank(query, unique_records, top_k=top_k)

        return unique_records[:top_k]

