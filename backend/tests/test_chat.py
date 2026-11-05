"""
Test Chat API (backend/tests/test_chat.py).
Tests chat endpoint responses and grounding.
"""
import sys
from pathlib import Path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_health():
    res = client.get("/api/chat/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("healthy", "index_not_loaded")
    print("[PASS] Chat health check")

def test_chat_debarment():
    res = client.post("/api/chat", json={"question": "what is debarment?", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert "debar" in data["answer"].lower() or "suspension" in data["answer"].lower()
    assert len(data["sources"]) > 0
    print("[PASS] Chat debarment test passed")

def test_chat_delete_tender():
    res = client.post("/api/chat", json={"question": "How to delete a tender?", "top_k": 3})
    assert res.status_code == 200
    data = res.json()
    assert "cancel" in data["answer"].lower() or "delete" in data["answer"].lower()
    print("[PASS] Chat delete tender test passed")

if __name__ == "__main__":
    test_chat_health()
    test_chat_debarment()
    test_chat_delete_tender()
    print("All chat API tests PASSED!")
