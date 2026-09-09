from __future__ import annotations

from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient

from app.llm.client import OllamaClient, OllamaConfig
from app.main import app, set_ollama_client
from app.schemas.document import ParsedDocument


@pytest.fixture(autouse=True)
def reset_ollama():
    yield
    set_ollama_client(None)


@pytest.fixture
def client():
    return TestClient(app)


def test_analyze_match_with_jd_pdf_success(client, monkeypatch):
    def mock_extract(file_bytes, filename):
        if "cv" in filename.lower():
            return ParsedDocument(
                fileName=filename,
                text="Alex Morgan\nSkills: Python, React, Docker, SQL",
                pageCount=1,
                sizeBytes=len(file_bytes),
            )
        else:
            return ParsedDocument(
                fileName=filename,
                text="Senior Software Engineer\nRequirements: Must have 5 years experience with Python, TypeScript, and React.",
                pageCount=1,
                sizeBytes=len(file_bytes),
            )

    monkeypatch.setattr("app.main.extract_pdf_content", mock_extract)

    cv_bytes = b"%PDF-1.4 mock cv binary stream content"
    jd_bytes = b"%PDF-1.4 mock jd binary stream content"

    response = client.post(
        "/api/analyze-match",
        files={
            "file": ("candidate_cv.pdf", cv_bytes, "application/pdf"),
            "jdFile": ("senior_engineer_jd.pdf", jd_bytes, "application/pdf"),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["fileName"] == "candidate_cv.pdf"
    assert data["jdFileName"] == "senior_engineer_jd.pdf"
    assert data["targetRole"] == "Senior Software Engineer"
    assert data["matchScore"] > 0
    assert "Python" in data["matchedSkills"]
    assert "React" in data["matchedSkills"]
    assert "TypeScript" in data["missingSkills"]


def test_analyze_match_missing_both_jd_inputs(client):
    cv_bytes = b"%PDF-1.4 mock cv binary stream"
    response = client.post(
        "/api/analyze-match",
        files={"file": ("candidate_cv.pdf", cv_bytes, "application/pdf")},
    )
    assert response.status_code == 422


def test_analyze_match_short_jd_pdf(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.extract_pdf_content",
        lambda file_bytes, filename: ParsedDocument(
            fileName=filename,
            text="Short JD",
            pageCount=1,
            sizeBytes=len(file_bytes),
        ),
    )

    cv_bytes = b"%PDF-1.4 mock cv"
    jd_bytes = b"%PDF-1.4 mock jd"

    response = client.post(
        "/api/analyze-match",
        files={
            "file": ("candidate_cv.pdf", cv_bytes, "application/pdf"),
            "jdFile": ("short_jd.pdf", jd_bytes, "application/pdf"),
        },
    )
    assert response.status_code == 422
    assert "at least 50 characters" in response.json()["detail"]
