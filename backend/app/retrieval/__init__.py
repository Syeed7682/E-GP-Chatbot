"""
Retrieval module for e-GP Manual RAG System.
Provides query routing, text retrieval, visual retrieval, RRF fusion, and hybrid orchestration.
"""
from app.retrieval.query_router import QueryRouter
from app.retrieval.text_retriever import retrieve_text
from app.retrieval.visual_retriever import retrieve_visual
from app.retrieval.fusion import reciprocal_rank_fusion
from app.retrieval.context_builder import build_grounded_context
from app.retrieval.hybrid_retriever import MultiChannelRetriever

__all__ = [
    "QueryRouter",
    "retrieve_text",
    "retrieve_visual",
    "reciprocal_rank_fusion",
    "build_grounded_context",
    "MultiChannelRetriever",
]

