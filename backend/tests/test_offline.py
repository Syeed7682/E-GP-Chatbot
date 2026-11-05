"""
Test Offline Functionality (backend/tests/test_offline.py).
Tests offline fallback generator and sync versioning.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.llm_service import llm_service
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_offline_synthesizer_debarment():
    ans = llm_service._offline_answer_generator("what is debarment?", "Chapter 7 Debarment")
    assert "Debarment" in ans
    assert "PPR" in ans or "Page 342" in ans or "HOPE" in ans
    print("[PASS] Debarment offline synthesizer test")

def test_offline_synthesizer_delete_tender():
    ans = llm_service._offline_answer_generator("How to delete a tender?", "Chapter 4 Tender")
    assert "cancel" in ans.lower() or "cancellation" in ans.lower()
    assert "Page 178" in ans or "Page 191" in ans
    print("[PASS] Delete tender offline synthesizer test")

def test_sync_version_endpoint():
    res = client.get("/api/sync/version")
    assert res.status_code == 200
    data = res.json()
    assert "version" in data
    assert "hash" in data
    print("[PASS] Sync version endpoint test")

if __name__ == "__main__":
    test_offline_synthesizer_debarment()
    test_offline_synthesizer_delete_tender()
    test_sync_version_endpoint()
    print("All offline tests PASSED!")
