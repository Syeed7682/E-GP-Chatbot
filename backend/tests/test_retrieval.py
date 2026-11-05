"""
Test Retrieval (backend/tests/test_retrieval.py).
Tests hybrid FAISS + BM25 retrieval accuracy and verifies TOC exclusion.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.retrieval_service import retrieval_service

def test_retrieval_service_ready():
    ready = retrieval_service.load_index_if_needed()
    assert ready is True
    print("[PASS] Retrieval service ready")

def test_tender_deletion_retrieval():
    retrieval_service.load_index_if_needed()
    context, sources = retrieval_service.retrieve("How to delete a tender?", top_k=3)
    assert len(sources) > 0
    # Must not return Table of Contents (Pages 1-5)
    for s in sources:
        assert s["page"] > 5, f"Unexpected TOC page returned: {s['page']}"
    print(f"[PASS] Tender deletion retrieved pages: {[s['page'] for s in sources]}")

def test_debarment_retrieval():
    retrieval_service.load_index_if_needed()
    context, sources = retrieval_service.retrieve("what is debarment?", top_k=3)
    assert len(sources) > 0
    pages = [s["page"] for s in sources]
    print(f"[PASS] Debarment retrieved pages: {pages}")
    assert any(p in (342, 343, 344, 345, 346, 347, 348) for p in pages)

if __name__ == "__main__":
    test_retrieval_service_ready()
    test_tender_deletion_retrieval()
    test_debarment_retrieval()
    print("All retrieval tests PASSED!")
