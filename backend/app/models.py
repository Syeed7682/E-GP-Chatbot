"""
Models Definition File (app/models.py).
Centralizes:
1. AI Model Configurations & Registry (BGE-M3, Qwen2.5-VL-3B-Instruct, optional Liquid AI).
2. Domain Data & API Schemas supporting both Text and Image (DocumentChunk, SourceDocument, ChatRequest, ChatResponse, HealthResponse).
"""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# ==============================================================================
# 1. AI MODEL REGISTRY & CONFIGURATIONS
# ==============================================================================

class ModelProvider(str, Enum):
    """Supported inference providers."""
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    OPENAI_COMPATIBLE = "openai_compatible"


class EmbeddingModelConfig(BaseModel):
    """Metadata and parameters for a multimodal embedding model."""
    name: str = Field(..., description="Friendly display name")
    model_id: str = Field(..., description="Hugging Face hub repo ID or local path")
    dimension: int = Field(..., description="Vector dimensionality output")
    modality: str = Field("multimodal", description="Supported modalities (text, image, multimodal)")
    description: str = Field("", description="Capabilities and primary use cases")


class LLMModelConfig(BaseModel):
    """Metadata and inference defaults for a Large Language Model."""
    name: str = Field(..., description="Friendly display name")
    model_id: str = Field(..., description="Hugging Face hub repo ID or provider endpoint name")
    provider: ModelProvider = Field(default=ModelProvider.HUGGINGFACE)
    default_temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    default_max_tokens: int = Field(default=800, ge=64, le=4096)
    description: str = Field("", description="Capabilities and primary use cases")


# Pre-configured Multimodal Embedding Models Registry
SUPPORTED_EMBEDDING_MODELS: Dict[str, EmbeddingModelConfig] = {
    "BAAI/bge-visualized-m3": EmbeddingModelConfig(
        name="BGE-Visualized-M3 (Multimodal Text + Image)",
        model_id="BAAI/bge-visualized-m3",
        dimension=1024,
        modality="multimodal",
        description="Flagship multimodal visual embedding model by BAAI. Projects text, document screenshots, and diagrams into a shared 1024-dim semantic space."
    ),
    "BAAI/bge-m3": EmbeddingModelConfig(
        name="BGE-M3 (Text)",
        model_id="BAAI/bge-m3",
        dimension=1024,
        modality="text",
        description="State-of-the-art multilingual 1024-dim text embedding model."
    ),
    "google/siglip-base-patch16-224": EmbeddingModelConfig(
        name="SigLIP Base (Google Multimodal)",
        model_id="google/siglip-base-patch16-224",
        dimension=768,
        modality="multimodal",
        description="Google's sigmoid contrastive vision-language model mapping text and images into a joint 768-dim space."
    ),
    "openai/clip-vit-base-patch32": EmbeddingModelConfig(
        name="CLIP ViT-B/32",
        model_id="openai/clip-vit-base-patch32",
        dimension=512,
        modality="multimodal",
        description="Classic OpenAI multimodal embedding model."
    )
}

# Pre-configured Large Language Models Registry
SUPPORTED_LLM_MODELS: Dict[str, LLMModelConfig] = {
    "Qwen/Qwen2.5-VL-3B-Instruct": LLMModelConfig(
        name="Qwen2.5-VL-3B-Instruct (Default Multimodal)",
        model_id="Qwen/Qwen2.5-VL-3B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        default_temperature=0.2,
        default_max_tokens=800,
        description="Default vision-language model for grounded e-GP manual answers and portal screenshots."
    ),
    "LiquidAI/LFM2.5-VL-1.6B": LLMModelConfig(
        name="Liquid AI LFM2.5-VL-1.6B (Optional)",
        model_id="LiquidAI/LFM2.5-VL-1.6B",
        provider=ModelProvider.HUGGINGFACE,
        default_temperature=0.2,
        default_max_tokens=800,
        description="Optional vision-language engine, used only when explicitly selected."
    ),
    "Qwen/Qwen2.5-VL-72B-Instruct": LLMModelConfig(
        name="Qwen2.5-VL-72B-Instruct (Default Multimodal)",
        model_id="Qwen/Qwen2.5-VL-72B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        default_temperature=0.2,
        default_max_tokens=800,
        description="Alibaba Cloud's state-of-the-art 72B parameter vision-language model. Excels at multimodal reasoning over text, diagrams, and UI screenshots."
    ),
    "Qwen/Qwen2.5-72B-Instruct": LLMModelConfig(
        name="Qwen2.5-72B-Instruct",
        model_id="Qwen/Qwen2.5-72B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        default_temperature=0.2,
        default_max_tokens=800,
        description="Top-tier 72B parameter text reasoning model."
    ),
    "meta-llama/Llama-3.3-70B-Instruct": LLMModelConfig(
        name="Llama 3.3 70B Instruct",
        model_id="meta-llama/Llama-3.3-70B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        default_temperature=0.2,
        default_max_tokens=800,
        description="Meta's latest 70B open-weights model."
    )
}


def get_embedding_config(model_id: str = "BAAI/bge-visualized-m3") -> EmbeddingModelConfig:
    """Returns the configuration for the requested embedding model or a sensible default."""
    return SUPPORTED_EMBEDDING_MODELS.get(
        model_id,
        EmbeddingModelConfig(
            name=model_id,
            model_id=model_id,
            dimension=1024,
            modality="multimodal",
            description="Custom multimodal embedding model"
        )
    )


def get_llm_config(model_id: str = "Qwen/Qwen2.5-VL-3B-Instruct") -> LLMModelConfig:
    """Returns the configuration for the requested LLM or a sensible default."""
    return SUPPORTED_LLM_MODELS.get(
        model_id,
        LLMModelConfig(
            name=model_id,
            model_id=model_id,
            provider=ModelProvider.HUGGINGFACE,
            default_temperature=0.2,
            default_max_tokens=800,
            description="Custom LLM model"
        )
    )


# ==============================================================================
# 2. DOMAIN DATA & API SCHEMAS (TEXT & IMAGE CAPABLE)
# ==============================================================================

class DocumentChunk(BaseModel):
    """Represents a discrete text/image chunk extracted from a manual."""
    chunk_id: int = Field(..., description="Unique sequential chunk index")
    source: str = Field(..., description="Source manual filename")
    page: int = Field(..., description="1-indexed page number")
    text: str = Field(..., description="Text content of the chunk")
    image_path: Optional[str] = Field(None, description="Path to screenshot or diagram on this page")
    content_type: str = Field("text", description="Type: text, image, or multimodal")


class SourceDocument(BaseModel):
    """Represents a chunk retrieved from the FAISS vector index."""
    source: str = Field(..., description="File name of the manual (e.g., egp_user_manual.pdf)")
    page: int = Field(..., description="Page number where the content appears")
    chunk_id: int = Field(..., description="Unique chunk index in the index")
    score: float = Field(..., description="Cosine similarity score (higher = more relevant)")
    snippet: str = Field(..., description="Excerpt of the retrieved text")
    image_path: Optional[str] = Field(None, description="Associated screenshot image path if available")


class ChatRequest(BaseModel):
    """User query payload sent to the chat endpoint (text + optional image)."""
    question: str = Field(..., min_length=2, description="User query about the e-GP manual")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of manual chunks to retrieve")
    image: Optional[str] = Field(None, description="Optional image path, URL, or base64 string for multimodal queries")


class ChatResponse(BaseModel):
    """Chatbot response payload containing generated answer and references."""
    question: str = Field(..., description="Echo of original question")
    answer: str = Field(..., description="LLM generated answer based on retrieved context")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source references used to generate the answer")


class HealthResponse(BaseModel):
    """System health and status info."""
    status: str
    index_loaded: bool
    total_chunks: int
    llm_model: str
    embedding_model: str
    multimodal_enabled: bool = True
