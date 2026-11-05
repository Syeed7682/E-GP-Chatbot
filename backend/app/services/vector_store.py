"""
Vector Store Service (app/services/vector_store.py).
Manages FAISS IndexFlatIP (cosine similarity) and chunk metadata persistence.
"""
from typing import List, Dict, Any, Tuple
from app.services.faiss_service import faiss_service, FAISSService

class VectorStore:
    def __init__(self):
        self.service = faiss_service

    def is_ready(self) -> bool:
        return self.service.is_ready()

    def load_index_if_needed(self) -> bool:
        return self.service.load_index_if_needed()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        return self.service.search(query_embedding, top_k=top_k)

    def get_chunk_by_id(self, chunk_id: int) -> Dict[str, Any]:
        return self.service.get_chunk_by_id(chunk_id)

    @property
    def metadata(self) -> List[Dict[str, Any]]:
        return self.service.metadata

vector_store = VectorStore()

