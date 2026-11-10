"""
Test Retrieval (backend/tests/test_retrieval.py).
Tests hybrid FAISS + BM25 retrieval accuracy and verifies TOC exclusion.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.embedding_service import EmbeddingService, embedding_service
from app.services.retrieval_service import retrieval_service

def test_embedding_provider_failure_disables_semantic_search():
    class FailedInferenceClient:
        def feature_extraction(self, *args, **kwargs):
            raise RuntimeError("inference unavailable")

    service = EmbeddingService.__new__(EmbeddingService)
    service.model_name = "test-model"
    service.token = ""
    service.dimension = 1024
    service._hf_client = FailedInferenceClient()
    service._local_model = None
    service._mode = "hf_api"

    vector = service.embed_text("manual query")

    assert vector.shape == (1024,)
    assert service.semantic_search_available is False
    assert service._hf_client is None

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

def test_vague_question_falls_back_to_relevant_keyword_matches(monkeypatch):
    retrieval_service.load_index_if_needed()
    monkeypatch.setattr(embedding_service, "_mode", "offline_multimodal_fallback")

    context, sources = retrieval_service.retrieve(
        "What does the manual say about crucial?",
        top_k=3,
    )

    assert [source["page"] for source in sources] == [6]
    assert "crucial step aimed at enhancing the overall security" in " ".join(context.split())
    assert "Page 477" not in context

def test_generic_step_word_does_not_match_unrelated_manual_steps(monkeypatch):
    retrieval_service.load_index_if_needed()
    monkeypatch.setattr(embedding_service, "_mode", "offline_multimodal_fallback")

    context, sources = retrieval_service.retrieve("What is the crucial step?", top_k=3)

    assert [source["page"] for source in sources] == [6]
    assert "crucial step aimed at enhancing the overall security" in " ".join(context.split())

def test_login_retrieval_excludes_unrelated_debarment_content():
    retrieval_service.load_index_if_needed()
    context, sources = retrieval_service.retrieve("How do I log in to the e-GP portal?", top_k=3)
    pages = [source["page"] for source in sources]

    assert pages
    assert pages[0] in (6, 7, 8)
    assert len(pages) == len(set(pages))
    assert all(page in (6, 7, 8) for page in pages)
    assert "debar" not in context.lower()

def test_login_step_retrieval_includes_full_pages():
    context, sources = retrieval_service.retrieve(
        "Provide concise numbered steps for: How do I log in and change my password?",
        top_k=3,
        include_page_context=True,
    )

    manual_pages = {
        source["page"] for source in sources
        if source.get("source_type") != "qa"
    }
    assert manual_pages.issubset({6, 7, 8})
    assert any(source.get("source_type") == "qa" for source in sources)
    flattened_context = " ".join(context.split())
    assert "1.1 When accessing" in flattened_context
    assert "1.2 For users logging in for the first time" in flattened_context
    assert "Change Password" in flattened_context
    assert 'Submit" button' in flattened_context
    assert "registered email ID" in flattened_context
    assert 'clicking on the " Login" button' in flattened_context

def test_repairs_mid_word_chunk_boundary():
    retrieval_service.load_index_if_needed()
    chunk = next(
        item for item in retrieval_service.faiss_service.metadata
        if item.get("page") == 211 and item.get("chunk_id") == 490
    )

    repaired = retrieval_service._repair_leading_chunk_fragment(chunk)

    assert not repaired.lstrip().startswith("mber from")
    assert "member from evaluation committee" in repaired
    assert "complete the technical evaluation on behalf of the team" in repaired

if __name__ == "__main__":
    test_retrieval_service_ready()
    test_tender_deletion_retrieval()
    test_debarment_retrieval()
    test_login_retrieval_excludes_unrelated_debarment_content()
    test_repairs_mid_word_chunk_boundary()
    print("All retrieval tests PASSED!")
