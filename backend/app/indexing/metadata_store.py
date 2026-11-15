"""
SQLite Metadata Store for e-GP Manual RAG System.
Maps FAISS vector IDs to rich document chunks, answers, and image provenance.
Stores PDF chunks, supplemental Q&A pairs, and visual regions with relational indexes.
"""
import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS chunks (
    vector_id INTEGER PRIMARY KEY,
    chunk_id TEXT UNIQUE NOT NULL,
    parent_id TEXT,
    source_type TEXT NOT NULL,
    source_file TEXT,
    page_start INTEGER,
    page_end INTEGER,
    section TEXT,
    content_type TEXT,
    content TEXT,
    image_path TEXT,
    category TEXT,
    answer TEXT,
    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_chunks_page ON chunks(page_start);
CREATE INDEX IF NOT EXISTS idx_chunks_type ON chunks(source_type);
CREATE INDEX IF NOT EXISTS idx_chunks_parent ON chunks(parent_id);
CREATE INDEX IF NOT EXISTS idx_chunks_cid ON chunks(chunk_id);
"""


class MetadataStore:
    """Manages SQLite storage of document and Q&A chunk metadata."""

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        with self.conn:
            self.conn.executescript(CREATE_TABLES_SQL)

    def insert_chunk(self, record: Dict[str, Any], vector_id: Optional[int] = None) -> int:
        """Inserts a single chunk record, returning the vector_id."""
        with self.conn:
            cursor = self.conn.cursor()
            vid = vector_id if vector_id is not None else record.get("vector_id")
            chunk_id = record.get("chunk_id")
            if not chunk_id:
                raise ValueError("Record must contain a non-empty 'chunk_id'")

            cursor.execute(
                """
                INSERT OR REPLACE INTO chunks (
                    vector_id, chunk_id, parent_id, source_type, source_file,
                    page_start, page_end, section, content_type, content,
                    image_path, category, answer, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vid,
                    chunk_id,
                    record.get("parent_id"),
                    record.get("source_type", "pdf"),
                    record.get("source_file") or record.get("source", "egp_manual.pdf"),
                    record.get("page_start") or record.get("page", 1),
                    record.get("page_end") or record.get("page", 1),
                    record.get("section", "General Overview"),
                    record.get("content_type", "text"),
                    record.get("text") or record.get("content", ""),
                    record.get("image_path"),
                    record.get("category") or record.get("module"),
                    record.get("answer"),
                    json.dumps(record, ensure_ascii=False),
                ),
            )
            return cursor.lastrowid or (vid if vid is not None else 0)

    def insert_many(self, records: List[Dict[str, Any]], start_vector_id: int = 0) -> None:
        """Inserts multiple chunk records in a single transaction."""
        with self.conn:
            cursor = self.conn.cursor()
            for idx, rec in enumerate(records):
                vid = rec.get("vector_id", start_vector_id + idx)
                chunk_id = rec.get("chunk_id") or f"CHUNK_{vid:06d}"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO chunks (
                        vector_id, chunk_id, parent_id, source_type, source_file,
                        page_start, page_end, section, content_type, content,
                        image_path, category, answer, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        vid,
                        chunk_id,
                        rec.get("parent_id"),
                        rec.get("source_type", "pdf"),
                        rec.get("source_file") or rec.get("source", "egp_manual.pdf"),
                        rec.get("page_start") or rec.get("page", 1),
                        rec.get("page_end") or rec.get("page", 1),
                        rec.get("section", "General Overview"),
                        rec.get("content_type", "text"),
                        rec.get("text") or rec.get("content", ""),
                        rec.get("image_path"),
                        rec.get("category") or rec.get("module"),
                        rec.get("answer"),
                        json.dumps(rec, ensure_ascii=False),
                    ),
                )

    def get_by_vector_id(self, vector_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a chunk record by its numeric FAISS vector ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE vector_id = ?", (vector_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    def get_many(self, vector_ids: List[int]) -> List[Dict[str, Any]]:
        """Retrieves records for a list of vector IDs, preserving input order."""
        if not vector_ids:
            return []
        cursor = self.conn.cursor()
        placeholders = ",".join("?" * len(vector_ids))
        cursor.execute(f"SELECT * FROM chunks WHERE vector_id IN ({placeholders})", vector_ids)
        rows = {r["vector_id"]: self._row_to_dict(r) for r in cursor.fetchall()}
        return [rows[vid] for vid in vector_ids if vid in rows]

    def get_by_chunk_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a chunk by its unique chunk_id string."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_dict(row)

    def search_by_page(self, page_num: int) -> List[Dict[str, Any]]:
        """Finds all chunks that span the given page number."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM chunks WHERE page_start <= ? AND page_end >= ? ORDER BY vector_id ASC",
            (page_num, page_num),
        )
        return [self._row_to_dict(r) for r in cursor.fetchall()]

    def count(self, source_type: Optional[str] = None) -> int:
        """Counts records, optionally filtered by source_type."""
        cursor = self.conn.cursor()
        if source_type:
            cursor.execute("SELECT COUNT(*) FROM chunks WHERE source_type = ?", (source_type,))
        else:
            cursor.execute("SELECT COUNT(*) FROM chunks")
        return cursor.fetchone()[0]

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        # Parse original metadata json if available
        if data.get("metadata_json"):
            try:
                orig = json.loads(data["metadata_json"])
                orig.update({
                    "vector_id": data["vector_id"],
                    "chunk_id": data["chunk_id"],
                    "parent_id": data["parent_id"],
                    "source_type": data["source_type"],
                    "page_start": data["page_start"],
                    "page_end": data["page_end"],
                    "section": data["section"],
                    "content_type": data["content_type"],
                    "text": data["content"],
                    "category": data["category"],
                    "answer": data["answer"],
                })
                return orig
            except Exception:
                pass
        return data

    def close(self) -> None:
        self.conn.close()

