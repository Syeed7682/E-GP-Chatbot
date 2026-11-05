"""
Manual Schemas (app/schemas/manual.py).
Defines schemas for manual page inspection, search, and client synchronization.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ManualChunkModel(BaseModel):
    chunk_id: int
    page_number: int
    section_title: str
    content: str
    key_terms: List[str] = []
    screen_references: List[str] = []
    category: str = "general"
    source: str = "Official e-GP Procuring Entity Manual"

class ManualPage(BaseModel):
    page_number: int
    total_pages: int = 543
    title: Optional[str] = None
    chunks: List[ManualChunkModel] = []
    image_url: Optional[str] = None

class SyncMutation(BaseModel):
    id: str
    type: str
    payload: Dict[str, Any]
    revision: Optional[int] = 0
    hash: Optional[str] = None

class SyncPushRequest(BaseModel):
    client_id: Optional[str] = "web-client"
    conflict_strategy: str = "server_wins"
    mutations: List[SyncMutation] = []

class SyncPushResponse(BaseModel):
    status: str
    processed_count: int
    processed_ids: List[str]
    conflicts: List[Dict[str, Any]] = []
    server_time: int

