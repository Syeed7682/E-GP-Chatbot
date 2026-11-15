"""
Embeddings module for e-GP Manual RAG System.
Provides text embedder (BGE-M3), visual embedder (SigLIP), and cross-encoder reranker.
"""
from app.embeddings.text_embedder import TextEmbedder, embed_in_batches
from app.embeddings.visual_embedder import VisualEmbedder
from app.embeddings.reranker import DocumentReranker

__all__ = [
    "TextEmbedder",
    "embed_in_batches",
    "VisualEmbedder",
    "DocumentReranker",
]

