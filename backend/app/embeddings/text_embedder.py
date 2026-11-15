"""
Text Embedder for e-GP Manual.
Uses BAAI/bge-m3 (1024-dimensional dense vectors) with L2 normalization.
Supports FlagEmbedding, sentence-transformers, Hugging Face API, and deterministic fallback.
"""
import logging
import os
import zlib
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-m3/pipeline/feature-extraction"


class TextEmbedder:
    """Embeds text into 1024-dimensional normalized dense vectors."""

    def __init__(self, model_name: str = "BAAI/bge-m3", use_fp16: bool = False):
        self.model_name = model_name
        self.use_fp16 = use_fp16
        self.dim = 1024
        self._flag_model = None
        self._st_model = None
        self._hf_token = os.getenv("HF_TOKEN", "").strip()
        self._provider = "init"
        self._init_model()

    def _init_model(self) -> None:
        import importlib
        # 1. Try FlagEmbedding
        try:
            flag_mod = importlib.import_module("FlagEmbedding")
            BGEM3FlagModel = getattr(flag_mod, "BGEM3FlagModel")
            self._flag_model = BGEM3FlagModel(self.model_name, use_fp16=self.use_fp16)
            self._provider = "flag_embedding"
            logger.info("Initialized TextEmbedder via FlagEmbedding: %s", self.model_name)
            return
        except Exception:
            pass

        # 2. Try sentence-transformers
        try:
            st_mod = importlib.import_module("sentence_transformers")
            SentenceTransformer = getattr(st_mod, "SentenceTransformer")
            self._st_model = SentenceTransformer(self.model_name)
            self._provider = "sentence_transformers"
            logger.info("Initialized TextEmbedder via sentence-transformers: %s", self.model_name)
            return
        except Exception:
            pass

        # 3. Check Hugging Face API
        if self._hf_token:
            self._provider = "hf_api"
            logger.info("Configured TextEmbedder via Hugging Face API: %s", self.model_name)
            return

        self._provider = "hash_fallback"
        logger.info("Using deterministic normalized hash fallback for TextEmbedder")

    def encode(self, texts: Union[str, List[str]], batch_size: int = 8) -> np.ndarray:
        """
        Encodes a list of texts into a 2D float32 array (N, 1024).
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.empty((0, self.dim), dtype=np.float32)

        if self._flag_model is not None:
            try:
                res = self._flag_model.encode(
                    texts,
                    batch_size=batch_size,
                    max_length=1024,
                    return_dense=True,
                    return_sparse=False,
                    return_colbert_vecs=False,
                )
                vecs = np.asarray(res["dense_vecs"], dtype=np.float32)
                # L2 normalize
                norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                norms[norms == 0] = 1.0
                return vecs / norms
            except Exception as e:
                logger.warning("FlagEmbedding failed during encode (%s), trying fallbacks", e)

        if self._st_model is not None:
            try:
                vecs = self._st_model.encode(texts, batch_size=batch_size, normalize_embeddings=True)
                return np.asarray(vecs, dtype=np.float32)
            except Exception as e:
                logger.warning("SentenceTransformer failed during encode (%s), trying fallbacks", e)

        if self._hf_token:
            try:
                import requests
                headers = {"Authorization": f"Bearer {self._hf_token}"}
                resp = requests.post(
                    HF_API_URL,
                    headers=headers,
                    json={"inputs": texts, "options": {"wait_for_model": True}},
                    timeout=30,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    vecs = np.asarray(data, dtype=np.float32)
                    if vecs.ndim == 1:
                        vecs = vecs.reshape(1, -1)
                    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
                    norms[norms == 0] = 1.0
                    return vecs / norms
            except Exception as e:
                logger.debug("HF API encode failed (%s), using deterministic fallback", e)

        # Deterministic 1024-dim CRC32 hash fallback
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            words = text.lower().split()
            for w in words:
                h = zlib.crc32(w.encode("utf-8"))
                idx = h % self.dim
                sign = 1.0 if (h & 0x1000) else -1.0
                vecs[i, idx] += sign
            norm = np.linalg.norm(vecs[i])
            if norm > 0:
                vecs[i] /= norm
            else:
                vecs[i, 0] = 1.0

        return vecs


def embed_in_batches(texts: List[str], embedder: TextEmbedder, batch_size: int = 8) -> np.ndarray:
    """Encodes texts in controlled batches to prevent memory spikes."""
    if not texts:
        return np.empty((0, embedder.dim), dtype=np.float32)

    batches = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        vectors = embedder.encode(batch, batch_size=batch_size)
        batches.append(vectors)

    return np.vstack(batches)

