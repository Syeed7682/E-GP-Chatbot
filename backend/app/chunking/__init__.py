"""
Chunking module for e-GP Manual RAG System.
Provides token chunking, structure-aware PDF chunking, table chunking, and Q&A chunking.
"""
from app.chunking.token_chunker import chunk_text
from app.chunking.structure_chunker import create_pdf_chunks
from app.chunking.table_chunker import chunk_table
from app.chunking.qa_chunker import prepare_qa_records

__all__ = [
    "chunk_text",
    "create_pdf_chunks",
    "chunk_table",
    "prepare_qa_records",
]

