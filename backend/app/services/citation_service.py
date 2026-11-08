"""
Citation Service (app/services/citation_service.py).
Extracts and validates statutory page references and maps them to manual screenshot assets.
"""
from typing import Optional
from app.core.config import settings

class CitationService:
    @staticmethod
    def format_citation(page: int, section_title: str) -> str:
        """Formats statutory citation line."""
        return f"📖 Source: e-GP System User Manual (Procuring Entity User 1 February 2026), Page {page} — {section_title}"

    @staticmethod
    def resolve_screenshot_path(page: int) -> Optional[str]:
        """Resolves existing extracted page screenshot from data/extracted_images."""
        candidates = [
            settings.EXTRACTED_IMAGES_DIR / f"page_{page}.jpg",
            settings.EXTRACTED_IMAGES_DIR / f"page_{page}.png",
            settings.EXTRACTED_IMAGES_DIR / "page_images" / f"page_{page}.jpg",
            settings.EXTRACTED_IMAGES_DIR / "page_images" / f"page_{page}.png",
            settings.EXTRACTED_IMAGES_DIR / f"page_{page}_img_0.jpg",
            settings.EXTRACTED_IMAGES_DIR / f"page_{page}_img_0.png",
        ]
        for p in candidates:
            if p.exists():
                return f"/api/manual/page/{page}/image"
        return None

citation_service = CitationService()
