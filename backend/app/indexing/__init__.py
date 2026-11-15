"""
Indexing module for e-GP Manual RAG System.
Handles FAISS index construction, SQLite metadata persistence, BM25 indexing, and version management.
"""
from app.indexing.faiss_builder import build_faiss_index, load_faiss_index
from app.indexing.metadata_store import MetadataStore
from app.indexing.bm25_builder import build_bm25_index, load_bm25_index, BM25Index
from app.indexing.index_manager import IndexManager

__all__ = [
    "build_faiss_index",
    "load_faiss_index",
    "MetadataStore",
    "build_bm25_index",
    "load_bm25_index",
    "BM25Index",
    "IndexManager",
]

