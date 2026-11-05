"""
AI Models Configuration (ai_models/model_config.py).
Central configuration definitions for embedding, vision, and language models.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmbeddingConfig:
    name: str = "BAAI/bge-m3"
    dimension: int = 1024
    max_length: int = 8192
    normalize: bool = True

@dataclass
class VisionConfig:
    ocr_engine: str = "PaddleOCR"
    fallback_engine: str = "Tesseract"
    supported_formats: tuple = ("png", "jpg", "jpeg", "webp")

@dataclass
class LLMConfig:
    primary_model: str = "Qwen/Qwen2.5-72B-Instruct"
    vision_model: str = "Qwen/Qwen2.5-VL-72B-Instruct"
    fallback_gemini: str = "gemini-2.0-flash"
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 0.9

default_embedding_config = EmbeddingConfig()
default_vision_config = VisionConfig()
default_llm_config = LLMConfig()

