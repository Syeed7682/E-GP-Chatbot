"""
Citation Service (app/services/citation_service.py).
Extracts and validates statutory page references and maps them to manual screenshot assets.
Supports chunk-level screenshot mapping, related sentence captions, and on-demand page rendering.
"""
import re
from pathlib import Path
from typing import Any, Optional
from app.core.config import settings


class CitationService:
    @staticmethod
    def format_citation(page: int, section_title: str) -> str:
        """Formats statutory citation line."""
        return f"📖 Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Page {page} — {section_title}"

    @staticmethod
    def resolve_chunk_image_path(chunk_id: Any, page: Optional[int] = None) -> Optional[str]:
        """
        Resolves the exact extracted diagram or portal screenshot mapped to this chunk.
        Returns the API URL if an image file exists for the chunk, otherwise page fallback.
        """
        if chunk_id is not None:
            cid = re.sub(r"^[a-zA-Z]+:", "", str(chunk_id)).strip()
            chunks_dir = settings.EXTRACTED_IMAGES_DIR / "chunks"
            if chunks_dir.exists():
                matches = list(chunks_dir.glob(f"chunk_{cid}_page_*.*"))
                if matches:
                    return f"/api/manual/chunk/{cid}/image"

        if page is not None and page > 0:
            return CitationService.resolve_screenshot_path(page)

        return None

    @staticmethod
    def resolve_screenshot_path(page: int) -> Optional[str]:
        """
        Resolves manual page screenshot URL.
        Checks for chunk images on that page, or delegates to manual viewer renderer.
        """
        chunks_dir = settings.EXTRACTED_IMAGES_DIR / "chunks"
        if chunks_dir.exists():
            matches = list(chunks_dir.glob(f"chunk_*_page_{page}_*.*"))
            if matches:
                return f"/api/manual/page/{page}/image"

        # Check if raw PDF is available for on-the-fly rendering
        for filename in (
            "egp_manual.pdf",
            "egp_official_manual.pdf",
            "e-GP System User Manual - Procuring Entity User 1 February 2026.pdf",
        ):
            if (settings.DATA_RAW_DIR / filename).is_file():
                return f"/api/manual/page/{page}/image"

        return None


citation_service = CitationService()
