"""
Chat Schemas (app/schemas/chat.py).
Defines request and response structures for the chat API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Payload for submitting a chat query."""
    question: str = Field(..., description="User query text", min_length=1)
    image: Optional[str] = Field(None, description="Base64 encoded screenshot or image URL")
    image_base64: Optional[str] = Field(None, description="Alias for image base64")
    image_name: Optional[str] = Field(None, description="Optional uploaded image filename")
    top_k: Optional[int] = Field(5, description="Number of manual chunks to retrieve", ge=1, le=20)

class SourceDocument(BaseModel):
    """Source manual passage reference citation."""
    source: str = Field("Official e-GP Procuring Entity Manual", description="Document name")
    page: int = Field(..., description="Page number in official PDF")
    chunk_id: int = Field(..., description="Unique chunk index")
    score: float = Field(..., description="Relevance similarity score")
    snippet: str = Field(..., description="Representative excerpt text")
    screen_reference: Optional[str] = Field(None, description="Portal screen identifier (e.g. Screen - D50)")
    image_path: Optional[str] = Field(None, description="Extracted screenshot image path if available")

class ChatResponse(BaseModel):
    """Chatbot response containing answer and citations."""
    question: str
    answer: str
    sources: List[SourceDocument] = []
    portal_screens: List[str] = []
    model_used: str = "Qwen2.5-72B-Instruct (Grounded)"
    was_offline: bool = False

class HealthResponse(BaseModel):
    """API health and vector index diagnostic status."""
    status: str
    system: str = "e-GP Official Manual Assistant"
    index_loaded: bool
    total_chunks: int
    llm_model: str
    embedding_model: str
    hf_configured: bool = False
    gemini_configured: bool = False

