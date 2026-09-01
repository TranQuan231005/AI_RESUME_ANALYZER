from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.llm.client import OllamaClient, OllamaClientError, OllamaConfig, OllamaErrorCode
from app.main import app, set_ollama_client


def create_sample_pdf(text: str = "Alex Morgan\nalex@example.com\nPython, React, Docker\nExperience: Built cloud applications.") -> bytes:
    """Create a minimal valid in-memory PDF with extractable text."""
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    # Using pypdf metadata or basic text
    buf = io.BytesIO()
    writer.write(buf)
    # If blank page text extraction is empty in test, we can inject minimal text or use mock parser
    return buf.getvalue()


@pytest.fixture(autouse=True)
def reset_ollama():
    """Reset Ollama client after each test."""
    yield
    set_ollama_client(None)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check_offline(client, monkeypatch):
    mock_session = MagicMock()
    mock_session.get.side_effect = Exception("Connection refused")
    mock_client = OllamaClient(
        config=OllamaConfig(base_url="http://localhost:11434"),
        session=mock_session,
    )
    set_ollama_client(mock_client)

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollamaReachable"] is False


def test_health_check_online(client, monkeypatch):
    mock_session = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_session.get.return_value = mock_response

    mock_client = OllamaClient(
        config=OllamaConfig(base_url="http://localhost:11434"),
        session=mock_session,
    )
    set_ollama_client(mock_client)

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ollamaReachable"] is True


def test_analyze_resume_with_llm_success(client, monkeypatch):
    # Mock PDF extraction
    from app.schemas.document import ParsedDocument
    monkeypatch.setattr(
        "app.main.extract_pdf_content",
        lambda file_bytes, filename: ParsedDocument(
            fileName="test_cv.pdf",
            text="Alex Morgan\nalex@example.com\nSUMMARY\nExperienced Software Engineer.\nSKILLS\nPython, Docker, SQL, React, TypeScript\nEXPERIENCE\nLed fullstack project.\nPROJECTS\nBuilt distributed APIs.\nEDUCATION\nBS Computer Science.",
            pageCount=1,
            sizeBytes=len(file_bytes),
        ),
    )

    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.config = OllamaConfig(model="qwen3:4b")
    mock_ollama.generate_json.return_value = {
        "recommendedSkills": ["Kubernetes", "AWS", "GraphQL"],
        "recommendations": ["Highlight system design experience.", "Add more quantifiable metrics."],
    }
    set_ollama_client(mock_ollama)

    # Valid PDF magic header
    pdf_bytes = b"%PDF-1.4 sample pdf content with valid length"
    response = client.post(
        "/api/analyze-resume",
        files={"file": ("test_cv.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["fileName"] == "test_cv.pdf"
    assert data["candidateName"] == "Alex Morgan"
    assert data["candidateEmail"] == "alex@example.com"
    assert data["ai"]["provider"] == "OLLAMA"
    assert data["ai"]["usedFallback"] is False
    assert "Kubernetes" in data["recommendedSkills"]
    assert len(data["recommendations"]) >= 1
    assert data["resumeScore"] == sum(data["scoreBreakdown"].values()) - data["scoreBreakdown"]["total"]


def test_analyze_resume_fallback_on_ollama_error(client, monkeypatch):
    from app.schemas.document import ParsedDocument
    monkeypatch.setattr(
        "app.main.extract_pdf_content",
        lambda file_bytes, filename: ParsedDocument(
            fileName="test_cv.pdf",
            text="Alex Morgan\nalex@example.com\nSUMMARY\nEngineer\nSKILLS\nPython, React\nEXPERIENCE\nDeveloper",
            pageCount=1,
            sizeBytes=len(file_bytes),
        ),
    )

    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.config = OllamaConfig(model="qwen3:4b")
    mock_ollama.generate_json.side_effect = OllamaClientError(
        OllamaErrorCode.CONNECTION, "Connection refused"
    )
    set_ollama_client(mock_ollama)

    pdf_bytes = b"%PDF-1.4 sample pdf content with valid length"
    response = client.post(
        "/api/analyze-resume",
        files={"file": ("test_cv.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ai"]["provider"] == "RULE_BASED"
    assert data["ai"]["usedFallback"] is True
    assert isinstance(data["recommendedSkills"], list)
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0


def test_analyze_match_with_llm_success(client, monkeypatch):
    from app.schemas.document import ParsedDocument
    monkeypatch.setattr(
        "app.main.extract_pdf_content",
        lambda file_bytes, filename: ParsedDocument(
            fileName="test_cv.pdf",
            text="Alex Morgan\nSkills: Python, SQL, Docker",
            pageCount=1,
            sizeBytes=len(file_bytes),
        ),
    )

    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.config = OllamaConfig(model="qwen3:4b")
    mock_ollama.generate_json.return_value = {
        "atsKeywords": ["Python", "SQL", "Docker", "FastAPI", "PostgreSQL"],
        "strengths": ["Strong Python background", "Containerization skills"],
        "weaknesses": ["Missing Kubernetes experience"],
        "recommendations": ["Tailor CV to mention REST API architecture"],
    }
    set_ollama_client(mock_ollama)

    jd_text = "We are seeking a Senior Backend Engineer proficient in Python, SQL, Docker, FastAPI, and PostgreSQL with strong API development skills."
    pdf_bytes = b"%PDF-1.4 sample pdf content with valid length"

    response = client.post(
        "/api/analyze-match",
        files={"file": ("test_cv.pdf", pdf_bytes, "application/pdf")},
        data={"jobDescription": jd_text, "targetRole": "Backend Engineer"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["targetRole"] == "Backend Engineer"
    assert data["ai"]["provider"] == "OLLAMA"
    assert data["ai"]["usedFallback"] is False
    assert "FastAPI" in data["atsKeywords"]
    assert len(data["strengths"]) >= 1
    assert isinstance(data["matchedSkills"], list)
    assert isinstance(data["missingSkills"], list)


def test_analyze_match_fallback_on_llm_error(client, monkeypatch):
    from app.schemas.document import ParsedDocument
    monkeypatch.setattr(
        "app.main.extract_pdf_content",
        lambda file_bytes, filename: ParsedDocument(
            fileName="test_cv.pdf",
            text="Alex Morgan\nSkills: Python, Docker",
            pageCount=1,
            sizeBytes=len(file_bytes),
        ),
    )

    mock_ollama = MagicMock(spec=OllamaClient)
    mock_ollama.config = OllamaConfig(model="qwen3:4b")
    mock_ollama.generate_json.side_effect = OllamaClientError(
        OllamaErrorCode.TIMEOUT, "Timeout after 60s"
    )
    set_ollama_client(mock_ollama)

    jd_text = "We are seeking a Senior Backend Engineer proficient in Python, SQL, Docker, Kubernetes with at least 3 years experience."
    pdf_bytes = b"%PDF-1.4 sample pdf content with valid length"

    response = client.post(
        "/api/analyze-match",
        files={"file": ("test_cv.pdf", pdf_bytes, "application/pdf")},
        data={"jobDescription": jd_text},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ai"]["provider"] == "RULE_BASED"
    assert data["ai"]["usedFallback"] is True
    assert data["matchScore"] >= 0


def test_analyze_match_short_jd_validation_error(client):
    pdf_bytes = b"%PDF-1.4 sample pdf content"
    response = client.post(
        "/api/analyze-match",
        files={"file": ("test_cv.pdf", pdf_bytes, "application/pdf")},
        data={"jobDescription": "Too short"},
    )
    assert response.status_code == 422
