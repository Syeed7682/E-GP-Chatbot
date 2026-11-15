"""
Visual Embedder for e-GP Manual Screenshots and Diagrams.
Uses SigLIP (google/siglip-base-patch16-224, 768-dimensional joint embedding space).
Enables text-to-page-image and screenshot-to-manual retrieval.
"""
import logging
from pathlib import Path
from typing import Union
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class VisualEmbedder:
    """Computes 768-dimensional normalized joint embeddings for images and text."""

    def __init__(self, model_name: str = "google/siglip-base-patch16-224"):
        self.model_name = model_name
        self.dim = 768
        self.device = "cpu"
        self.processor = None
        self.model = None
        self.available = False
        self._init_model()

    def _init_model(self) -> None:
        try:
            import torch
            from transformers import AutoModel, AutoProcessor

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
            self.available = True
            logger.info("Initialized VisualEmbedder on %s: %s", self.device, self.model_name)
        except Exception as e:
            logger.debug("VisualEmbedder local model not loaded (%s); using deterministic projection fallback", e)
            self.available = False

    def encode_image(self, image_input: Union[str, Path, Image.Image]) -> np.ndarray:
        """Encodes an image to a normalized (1, 768) float32 vector."""
        if isinstance(image_input, (str, Path)):
            p = Path(image_input)
            if not p.exists():
                return np.zeros((1, self.dim), dtype=np.float32)
            image = Image.open(p).convert("RGB")
        elif isinstance(image_input, Image.Image):
            image = image_input.convert("RGB")
        else:
            return np.zeros((1, self.dim), dtype=np.float32)

        if self.available and self.model is not None and self.processor is not None:
            try:
                import torch
                import torch.nn.functional as F

                with torch.inference_mode():
                    inputs = self.processor(images=image, return_tensors="pt").to(self.device)
                    features = self.model.get_image_features(**inputs)
                    features = F.normalize(features.float(), p=2, dim=-1)
                    return features.cpu().numpy().astype(np.float32)
            except Exception as e:
                logger.warning("Error encoding image via SigLIP: %s", e)

        # Fallback: color/histogram deterministic feature projection
        hist = np.array(image.resize((16, 16)).convert("RGB")).flatten().astype(np.float32)
        vec = np.zeros(self.dim, dtype=np.float32)
        vec[:min(len(hist), self.dim)] = hist[:min(len(hist), self.dim)]
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.reshape(1, -1)

    def encode_text(self, text: str) -> np.ndarray:
        """Encodes text into the joint SigLIP 768-dim space for visual search."""
        if not text or not text.strip():
            return np.zeros((1, self.dim), dtype=np.float32)

        if self.available and self.model is not None and self.processor is not None:
            try:
                import torch
                import torch.nn.functional as F

                with torch.inference_mode():
                    inputs = self.processor(text=[text], padding="max_length", return_tensors="pt").to(self.device)
                    features = self.model.get_text_features(**inputs)
                    features = F.normalize(features.float(), p=2, dim=-1)
                    return features.cpu().numpy().astype(np.float32)
            except Exception as e:
                logger.warning("Error encoding text via SigLIP: %s", e)

        import zlib
        vec = np.zeros(self.dim, dtype=np.float32)
        for w in text.lower().split():
            h = zlib.crc32(w.encode("utf-8"))
            idx = h % self.dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec.reshape(1, -1)

