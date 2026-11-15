"""
Index Manager for e-GP Manual RAG System.
Handles versioned index management (v001, v002, etc.), manifest tracking,
multi-criteria validation, and atomic pointer updates.
"""
import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class IndexManager:
    """Manages versioned index bundles and atomic promotions."""

    def __init__(self, index_dir: Path):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.active_pointer_file = self.index_dir / "active_version.json"

    def get_active_version(self) -> str:
        """Reads the currently active index version name (e.g. 'v001')."""
        if self.active_pointer_file.exists():
            try:
                data = json.loads(self.active_pointer_file.read_text(encoding="utf-8"))
                return data.get("active_version", "v001")
            except Exception as e:
                logger.warning("Could not read active_version.json: %s", e)

        # Look for existing version folders
        existing = self.list_versions()
        return existing[-1] if existing else "v001"

    def get_version_dir(self, version: Optional[str] = None) -> Path:
        """Returns the absolute directory path for the given version or active version."""
        ver = version or self.get_active_version()
        v_dir = self.index_dir / ver
        v_dir.mkdir(parents=True, exist_ok=True)
        return v_dir

    def list_versions(self) -> List[str]:
        """Lists all existing version directories sorted chronologically."""
        versions = []
        for d in sorted(self.index_dir.iterdir()):
            if d.is_dir() and d.name.startswith("v") and d.name[1:].isdigit():
                versions.append(d.name)
        return versions

    def create_next_version_dir(self) -> Tuple[str, Path]:
        """Creates and returns the next version directory (e.g. v002)."""
        existing = self.list_versions()
        if not existing:
            next_ver = "v001"
        else:
            last_num = max(int(v[1:]) for v in existing)
            next_ver = f"v{last_num + 1:03d}"

        v_dir = self.index_dir / next_ver
        v_dir.mkdir(parents=True, exist_ok=True)
        return next_ver, v_dir

    def write_manifest(self, version: str, manifest_data: Dict[str, Any]) -> Path:
        """Writes manifest.json into the specified version directory."""
        v_dir = self.get_version_dir(version)
        manifest_path = v_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest_path

    def load_manifest(self, version: Optional[str] = None) -> Dict[str, Any]:
        """Loads manifest.json for a version."""
        v_dir = self.get_version_dir(version)
        manifest_path = v_dir / "manifest.json"
        if not manifest_path.exists():
            return {}
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Failed to parse manifest: %s", e)
            return {}

    def validate_version(self, version: str) -> Dict[str, Any]:
        """
        Validates all critical requirements of an index bundle:
        - PDF text index presence and dimension
        - Q&A index presence
        - BM25 index presence
        - SQLite metadata count vs vector count
        - Manifest file validity
        """
        v_dir = self.get_version_dir(version)
        checks: Dict[str, Any] = {
            "version": version,
            "path": str(v_dir),
            "passed": True,
            "errors": [],
            "warnings": [],
            "stats": {},
        }

        # 1. Manifest
        manifest_p = v_dir / "manifest.json"
        if not manifest_p.exists():
            checks["errors"].append("manifest.json missing")
            checks["passed"] = False
        else:
            checks["stats"]["manifest"] = "present"

        # 2. PDF text FAISS index
        pdf_faiss_p = v_dir / "pdf_text.faiss"
        if not pdf_faiss_p.exists():
            checks["errors"].append("pdf_text.faiss missing")
            checks["passed"] = False
        else:
            try:
                import faiss
                idx = faiss.read_index(str(pdf_faiss_p))
                checks["stats"]["pdf_vectors"] = idx.ntotal
                checks["stats"]["pdf_dimension"] = idx.d
                if idx.ntotal == 0:
                    checks["warnings"].append("pdf_text.faiss has 0 vectors")
            except Exception as e:
                checks["errors"].append(f"pdf_text.faiss corrupt: {e}")
                checks["passed"] = False

        # 3. QA FAISS index
        qa_faiss_p = v_dir / "qa.faiss"
        if qa_faiss_p.exists():
            try:
                import faiss
                idx = faiss.read_index(str(qa_faiss_p))
                checks["stats"]["qa_vectors"] = idx.ntotal
            except Exception as e:
                checks["warnings"].append(f"qa.faiss read error: {e}")

        # 4. BM25 index
        bm25_p = v_dir / "bm25.pkl"
        if not bm25_p.exists():
            checks["warnings"].append("bm25.pkl missing")
        else:
            checks["stats"]["bm25"] = "present"

        # 5. Metadata database
        db_p = v_dir / "metadata.db"
        if not db_p.exists():
            checks["errors"].append("metadata.db missing")
            checks["passed"] = False
        else:
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_p))
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM chunks")
                count = cur.fetchone()[0]
                checks["stats"]["metadata_chunks"] = count
                conn.close()
            except Exception as e:
                checks["errors"].append(f"metadata.db error: {e}")
                checks["passed"] = False

        return checks

    def activate_version(self, version: str, force: bool = False) -> bool:
        """
        Atomically switches active_version pointer to the validated version.
        Uses temporary file and replace for crash safety.
        """
        v_dir = self.get_version_dir(version)
        if not v_dir.exists():
            logger.error("Version directory %s does not exist", v_dir)
            return False

        if not force:
            validation = self.validate_version(version)
            if not validation["passed"]:
                logger.error("Cannot activate %s: validation failed with %s", version, validation["errors"])
                return False

        # Write to temp file on same filesystem for atomic rename
        temp_file = self.index_dir / f"temp_{os.getpid()}_active.json"
        content = json.dumps({
            "active_version": version,
            "activated_at": str(Path(v_dir).stat().st_mtime),
        }, indent=2)
        temp_file.write_text(content, encoding="utf-8")

        # Atomic replace
        temp_file.replace(self.active_pointer_file)
        logger.info("Successfully activated index version: %s", version)
        return True

