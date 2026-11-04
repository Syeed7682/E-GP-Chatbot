"""
API Integration Tests for e-GP Manual Chatbot.
Tests the FastAPI endpoints using starlette / fastapi TestClient.
"""
import unittest
import os
import sys
from fastapi.testclient import TestClient

# Add root directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

class TestChatAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """Test GET / returns basic metadata."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("app"), "e-GP Manual Chatbot")
        self.assertIn("docs_url", data)

    def test_health_endpoint(self):
        """Test GET /api/chat/health returns operational status."""
        response = self.client.get("/api/chat/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("index_loaded", data)
        self.assertIn("total_chunks", data)
        self.assertTrue(data["index_loaded"])
        self.assertGreater(data["total_chunks"], 0)

    def test_chat_query_success(self):
        """Test POST /api/chat with valid inquiry."""
        payload = {
            "question": "How does a Procuring Entity user login and create a tender in e-GP?",
            "top_k": 2
        }
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("question", data)
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertTrue(len(data["answer"]) > 10)
        self.assertGreater(len(data["sources"]), 0)
        # Check source attributes
        first_source = data["sources"][0]
        self.assertIn("source", first_source)
        self.assertIn("page", first_source)
        self.assertIn("score", first_source)

    def test_chat_query_empty_validation(self):
        """Test POST /api/chat with invalid short/empty question fails validation."""
        payload = {"question": "a", "top_k": 2}
        response = self.client.post("/api/chat", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_get_chunks_endpoint(self):
        """Test GET /api/chat/chunks returns chunk previews."""
        response = self.client.get("/api/chat/chunks?limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_indexed", data)
        self.assertIn("chunks", data)
        self.assertTrue(len(data["chunks"]) <= 5)

if __name__ == "__main__":
    unittest.main()

