"""
Test Citations Service (backend/tests/test_citations.py).
Tests citation formatting and screen references.
"""
from app.services.citation_service import citation_service

def test_format_citation():
    cit = citation_service.format_citation(56, "Tender Preparation")
    assert "Page 56" in cit
    assert "e-GP System User Manual" in cit

def test_resolve_screenshot():
    # If page 6 screenshot exists, it should return an endpoint URL
    path = citation_service.resolve_screenshot_path(6)
    if path:
        assert "/api/manual/page/6/image" in path

