"""
Schemas module (app/schemas/chat_schema.py).
Re-exports data schemas from app.models for backward compatibility.
"""
from app.models import (
    DocumentChunk,
    SourceDocument,
    ChatRequest,
    ChatResponse,
    HealthResponse
)

__all__ = [
    "DocumentChunk",
    "SourceDocument",
    "ChatRequest",
    "ChatResponse",
    "HealthResponse",
]
