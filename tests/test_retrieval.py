"""
Unit Tests for Retrieval Pipeline.
Tests document loading, chunking, embedding generation, and FAISS vector retrieval.
"""
import unittest
import os
import sys
import numpy as np

# Ensure root is in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.document_loader import load_pdf, clean_text
from app.services.text_chunker import split_text_with_overlap, chunk_documents
from app.services.embedding_service import embedding_service
from app.services.faiss_service import FaissService
from app.services.retrieval_service import RetrievalService

class TestRetrievalPipeline(unittest.TestCase):

    def test_clean_text(self):
        """Test whitespace and newline cleaning."""
        dirty = "  Hello   World  \n\n\n\nHow are you?   "
        cleaned = clean_text(dirty)
        self.assertEqual(cleaned, "Hello World\n\nHow are you?")

    def test_text_chunking(self):
        """Test that chunks are produced within desired length and have overlap."""
        long_text = "e-GP user manual step by step. " * 30
        chunks = split_text_with_overlap(long_text, chunk_size=200, chunk_overlap=40)
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertTrue(len(c) <= 250)

    def test_embedding_shape_and_normalization(self):
        """Test that embeddings have correct dimension (1024) and are normalized."""
        sample_text = "Bangladesh e-GP tender submission process."
        vec = embedding_service.embed_text(sample_text)
        self.assertEqual(vec.shape, (1024,))
        # Check L2 norm is approximately 1.0
        norm = np.linalg.norm(vec)
        self.assertAlmostEqual(norm, 1.0, places=3)

    def test_image_and_multimodal_embedding(self):
        """Test embedding an image and joint text+image multimodal embedding."""
        from PIL import Image
        # Create a synthetic test image
        img = Image.new("RGB", (64, 64), color="blue")
        img_vec = embedding_service.embed_image(img)
        self.assertEqual(img_vec.shape, (1024,))
        self.assertAlmostEqual(np.linalg.norm(img_vec), 1.0, places=3)

        # Test joint multimodal embedding
        multi_vec = embedding_service.embed_multimodal(text="e-GP Login Form", image=img)
        self.assertEqual(multi_vec.shape, (1024,))
        self.assertAlmostEqual(np.linalg.norm(multi_vec), 1.0, places=3)

    def test_faiss_index_and_search(self):
        """Test building a temporary FAISS index and retrieving the correct nearest chunk."""
        service = FaissService()
        texts = [
            "Contractor registration requires TIN, Trade License, and VAT Certificate.",
            "Weather forecast predicts heavy rainfall in Sylhet.",
            "Tender opening is executed automatically online by the system."
        ]
        meta = [{"chunk_id": i, "source": "test.pdf", "page": 1, "text": t} for i, t in enumerate(texts)]
        embeddings = embedding_service.embed_documents(texts)
        
        service.build_index(embeddings, meta)
        self.assertEqual(service.index.ntotal, 3)

        # Query for registration
        q_vec = embedding_service.embed_text("How can a contractor register with TIN and Trade license?")
        results = service.search(q_vec, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk"]["chunk_id"], 0)
        self.assertIn("Contractor registration", results[0]["chunk"]["text"])

    def test_retrieval_service_e2e(self):
        """Test end-to-end retrieval with existing generated index from Procuring Entity manual."""
        r = RetrievalService()
        ready = r.load_index_if_needed()
        self.assertTrue(ready, "FAISS index should be loaded for test")
        
        context, sources = r.retrieve("How does a Procuring Entity user create or prepare tender documents?", top_k=2)
        self.assertIn("tender", context.lower())
        self.assertGreater(len(sources), 0)

if __name__ == "__main__":
    unittest.main()

