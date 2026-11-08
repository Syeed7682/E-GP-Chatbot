import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_manual_image_endpoint_serves_jpeg_page():
    response = client.get("/api/manual/page/6/image")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")
    assert response.content.startswith(b"\xff\xd8\xff")


def test_manual_image_endpoint_detects_png_despite_jpg_filename():
    response = client.get("/api/manual/page/342/image")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.parametrize("page_num", [22, 89, 195, 539, 543])
def test_manual_image_endpoint_renders_pages_without_extracted_screenshots(page_num):
    response = client.get(f"/api/manual/page/{page_num}/image")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_manual_page_marks_pdf_renderable_pages_as_having_an_image():
    response = client.get("/api/manual/page/22")

    assert response.status_code == 200
    assert response.json()["has_image"] is True
    assert response.json()["image_url"] == "/api/manual/page/22/image"


def test_manual_download_endpoint_returns_the_full_pdf(monkeypatch, tmp_path):
    from app.api import manual

    pdf_path = tmp_path / "official-manual.pdf"
    pdf_path.write_bytes(b"%PDF-1.7 test manual")
    monkeypatch.setattr(manual, "_manual_pdf_path", lambda: pdf_path)

    response = client.get("/api/manual/download")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers["content-disposition"]
    assert response.content == b"%PDF-1.7 test manual"


def test_manual_image_endpoint_rejects_out_of_range_page():
    response = client.get("/api/manual/page/544/image")

    assert response.status_code == 404
