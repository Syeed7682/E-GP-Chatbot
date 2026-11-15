"""
AI & Multimodal Models Registry for e-GP Manual Chatbot.
Provides centralized configurations and data models for:
- Multimodal Embedding Models (BGE-M3 / BGE-Visualized-M3)
- Large Language Models (Gemini 2.0 Flash, Qwen2.5-VL-72B, Local Synthesizer)
"""

from .models import (
    ModelProvider,
    EmbeddingModelConfig,
    LLMModelConfig,
    SUPPORTED_EMBEDDING_MODELS,
    SUPPORTED_LLM_MODELS,
    get_embedding_config,
    get_llm_config,
    DocumentChunk,
    SourceDocument,
    ChatRequest,
    ChatResponse,
    HealthResponse,
)

__all__ = [
    "ModelProvider",
    "EmbeddingModelConfig",
    "LLMModelConfig",
    "SUPPORTED_EMBEDDING_MODELS",
    "SUPPORTED_LLM_MODELS",
    "get_embedding_config",
    "get_llm_config",
    "DocumentChunk",
    "SourceDocument",
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
]

