"""
Core RAG Service for e-GP Manual Chatbot.
Orchestrates multi-channel retrieval, metadata resolution, grounded context assembly,
and integrates with LLM synthesis.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from app.config import INDEX_DIR, FINAL_CONTEXT_K
from app.indexing.index_manager import IndexManager
from app.indexing.faiss_builder import load_faiss_index
from app.indexing.metadata_store import MetadataStore
from app.indexing.bm25_builder import load_bm25_index
from app.embeddings.text_embedder import TextEmbedder
from app.embeddings.visual_embedder import VisualEmbedder
from app.embeddings.reranker import DocumentReranker
from app.retrieval.hybrid_retriever import MultiChannelRetriever
from app.retrieval.context_builder import build_grounded_context

logger = logging.getLogger(__name__)


class EGP_RAG_Service:
    """Production RAG orchestrator for Bangladesh e-GP Procuring Entity manual."""

    def __init__(
        self,
        retriever: MultiChannelRetriever,
        text_embedder: TextEmbedder,
        visual_embedder: VisualEmbedder,
        metadata_store: MetadataStore,
        version: str = "v001",
    ):
        self.retriever = retriever
        self.text_embedder = text_embedder
        self.visual_embedder = visual_embedder
        self.metadata_store = metadata_store
        self.version = version

    def retrieve(
        self,
        query: str,
        screenshot_vector: Optional[np.ndarray] = None,
        top_k: int = FINAL_CONTEXT_K,
    ) -> Tuple[str, List[Dict[str, Any]], List[str]]:
        """
        Retrieves grounded evidence context, citations, and portal screen references.
        
        Returns:
            Tuple: (context_string, sources_list, portal_screens_list)
        """
        candidates = self.retriever.retrieve(
            query=query,
            screenshot_vector=screenshot_vector,
            top_k=top_k,
        )

        return build_grounded_context(candidates)


def load_rag_service(index_dir: Optional[Path] = None) -> Optional[EGP_RAG_Service]:
    """
    Initializes and loads the active production RAG service bundle.
    Reads active_version.json, loads indices, connects SQLite, and returns configured service.
    Falls back gracefully if indices are not yet built.
    """
    idx_dir = Path(index_dir or INDEX_DIR)
    mgr = IndexManager(idx_dir)
    active_ver = mgr.get_active_version()
    v_dir = mgr.get_version_dir(active_ver)

    logger.info("Initializing RAG Service for version: %s (path: %s)", active_ver, v_dir)

    pdf_index_path = v_dir / "pdf_text.faiss"
    qa_index_path = v_dir / "qa.faiss"
    vis_index_path = v_dir / "visual.faiss"
    bm25_path = v_dir / "bm25.pkl"
    db_path = Path("data/structured/metadata/pdf_manual.db")

    # Fallback to legacy index paths if versioned index is not yet built
    structured_faiss = Path("data/structured/indexes/pdf_manual.faiss")
    structured_metadata = Path("data/structured/metadata/pdf_manual.json")

    pdf_index = None
    if pdf_index_path.exists():
        try:
            pdf_index = load_faiss_index(pdf_index_path)
        except Exception as e:
            logger.warning("Could not load pdf_text.faiss: %s", e)
    elif structured_faiss.exists():
        try:
            pdf_index = load_faiss_index(structured_faiss)
            logger.info("Loaded structured FAISS index from %s", structured_faiss)
        except Exception as e:
            logger.warning("Could not load legacy faiss index: %s", e)

    qa_index = None
    if qa_index_path.exists():
        try:
            qa_index = load_faiss_index(qa_index_path)
        except Exception as e:
            logger.debug("qa.faiss not found or error: %s", e)

    visual_index = None
    if vis_index_path.exists():
        try:
            visual_index = load_faiss_index(vis_index_path)
        except Exception as e:
            logger.debug("visual.faiss not found or error: %s", e)

    bm25_index = None
    if bm25_path.exists():
        try:
            bm25_index = load_bm25_index(bm25_path)
        except Exception as e:
            logger.debug("bm25.pkl not loaded: %s", e)

    # Initialize Metadata Store
    if not db_path.exists() and structured_metadata.exists():
        # Initialize the structured SQLite metadata cache on the fly.
        try:
            import json
            legacy_data = json.loads(structured_metadata.read_text(encoding="utf-8"))
            metadata_store = MetadataStore(db_path)
            metadata_store.insert_many(legacy_data)
            logger.info("Seeded metadata.db from %s (%d chunks)", structured_metadata, len(legacy_data))
        except Exception as e:
            logger.warning("Could not seed metadata.db from structured metadata: %s", e)
            metadata_store = MetadataStore(db_path)
    else:
        metadata_store = MetadataStore(db_path)

    # Load Embedders & Reranker
    text_embedder = TextEmbedder()
    visual_embedder = VisualEmbedder()
    reranker = DocumentReranker()

    retriever = MultiChannelRetriever(
        pdf_index=pdf_index,
        qa_index=qa_index,
        visual_index=visual_index,
        bm25_index=bm25_index,
        text_embedder=text_embedder,
        visual_embedder=visual_embedder,
        reranker=reranker,
        metadata_store=metadata_store,
    )

    return EGP_RAG_Service(
        retriever=retriever,
        text_embedder=text_embedder,
        visual_embedder=visual_embedder,
        metadata_store=metadata_store,
        version=active_ver,
    )

