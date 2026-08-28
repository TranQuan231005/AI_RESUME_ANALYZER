import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.schemas import (
    AiMetadata,
    AiProvider,
    ApiError,
    FieldEnum,
    HealthResponse,
    LoginRequest,
    LoginResponse,
    MatchAnalysisRequest,
    MatchResult,
    ParsedDocument,
    ResumeAnalysisResult,
    ResumeFeatures,
    ScoreBreakdown,
    UserDto,
    UserRole,
)

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "contracts" / "fixtures"


def load_fixture(filename: str) -> dict:
    filepath = FIXTURES_DIR / filename
    assert filepath.exists(), f"Fixture file not found: {filepath}"
    return json.loads(filepath.read_text(encoding="utf-8"))


# --- Valid Fixture Contract Tests ---


def test_auth_login_request_fixture():
    data = load_fixture("auth-login-request.json")
    obj = LoginRequest.model_validate(data)
    assert obj.email == "user@example.test"
    assert obj.password == "User@123456"


def test_auth_login_response_fixture():
    data = load_fixture("auth-login-response.json")
    obj = LoginResponse.model_validate(data)
    assert obj.token_type == "Bearer"
    assert obj.expires_in == 7200
    assert obj.user.role == UserRole.USER
    assert obj.user.email == "user@example.test"


def test_auth_me_response_fixture():
    data = load_fixture("auth-me-response.json")
    obj = UserDto.model_validate(data)
    assert obj.id == 1
    assert obj.role == UserRole.USER
    assert obj.full_name == "Demo User"


def test_parsed_document_fixture():
    data = load_fixture("parsed-document.json")
    obj = ParsedDocument.model_validate(data)
    assert obj.file_name == "alex_resume.pdf"
    assert obj.page_count == 2
    assert obj.size_bytes == 184220
    assert len(obj.text) > 0


def test_resume_features_fixture():
    data = load_fixture("resume-features.json")
    obj = ResumeFeatures.model_validate(data)
    assert obj.candidate_name == "Alex Morgan"
    assert obj.candidate_email == "alex@example.test"
    assert obj.predicted_field == FieldEnum.DATA_SCIENCE
    assert len(obj.skills) == 3
    assert len(obj.field_evidence) == 2


def test_resume_features_missing_fields_fixture():
    data = load_fixture("resume-features-missing-fields.json")
    obj = ResumeFeatures.model_validate(data)
    assert obj.candidate_name is None
    assert obj.candidate_email is None
    assert obj.skills == []
    assert obj.predicted_field == FieldEnum.UNKNOWN
    assert obj.field_evidence == []


def test_resume_analysis_result_fixtures():
    for fixture_name in ["resume-analysis-result.json", "resume-analysis-result-fallback.json"]:
        data = load_fixture(fixture_name)
        obj = ResumeAnalysisResult.model_validate(data)
        assert obj.file_name == "alex_resume.pdf"
        assert obj.resume_score == 71
        assert obj.score_breakdown.total == 71
        assert obj.predicted_field == FieldEnum.DATA_SCIENCE
        assert obj.ai.provider in [AiProvider.OLLAMA, AiProvider.RULE_BASED]
        # Verify serialized output uses camelCase
        dumped = obj.model_dump(by_alias=True)
        assert "fileName" in dumped
        assert "resumeScore" in dumped
        assert "scoreBreakdown" in dumped
        assert "recommendedSkills" in dumped
        assert "usedFallback" in dumped["ai"]


def test_match_result_fixtures():
    for fixture_name in ["match-result.json", "match-result-fallback.json"]:
        data = load_fixture(fixture_name)
        obj = MatchResult.model_validate(data)
        assert obj.file_name == "alex_resume.pdf"
        assert obj.target_role == "Data Analyst"
        assert obj.match_score == 67
        assert "Python" in obj.matched_skills
        assert "Power BI" in obj.missing_skills
        # Verify serialized output uses camelCase
        dumped = obj.model_dump(by_alias=True)
        assert "fileName" in dumped
        assert "targetRole" in dumped
        assert "matchScore" in dumped
        assert "matchedSkills" in dumped
        assert "missingSkills" in dumped
        assert "atsKeywords" in dumped


def test_api_error_fixtures():
    error_fixtures = [
        ("api-error-400-malformed.json", 400, "MALFORMED_REQUEST"),
        ("api-error-401-bad-credentials.json", 401, "BAD_CREDENTIALS"),
        ("api-error-401-unauthorized.json", 401, "UNAUTHORIZED"),
        ("api-error-403-forbidden.json", 403, "FORBIDDEN"),
        ("api-error-404-not-found.json", 404, "NOT_FOUND"),
        ("api-error-413-file-too-large.json", 413, "FILE_TOO_LARGE"),
        ("api-error-422-invalid-pdf.json", 422, "INVALID_PDF"),
        ("api-error-422-pdf-not-readable.json", 422, "PDF_NOT_READABLE"),
        ("api-error-422-text-not-extractable.json", 422, "TEXT_NOT_EXTRACTABLE"),
        ("api-error-422-jd-required.json", 422, "JD_REQUIRED"),
        ("api-error-500-internal-error.json", 500, "INTERNAL_ERROR"),
        ("api-error-502-ai-service-error.json", 502, "AI_SERVICE_ERROR"),
    ]
    for fixture_name, expected_status, expected_code in error_fixtures:
        data = load_fixture(fixture_name)
        err = ApiError.model_validate(data)
        assert err.status == expected_status
        assert err.code == expected_code
        dumped = err.model_dump(by_alias=True)
        assert "requestId" in dumped
        assert "fieldErrors" in dumped


# --- Rejection / Invariant Contract Tests ---


def test_score_breakdown_rejects_mismatched_total():
    with pytest.raises(ValidationError):
        ScoreBreakdown(
            contact=5,
            summary=8,
            skills=12,
            education=8,
            experience=15,
            projects=10,
            achievements_certifications=5,
            quantified_impact=8,
            total=100,  # Real sum is 71, mismatch should fail
        )


def test_score_breakdown_rejects_out_of_bounds_components():
    with pytest.raises(ValidationError):
        ScoreBreakdown(
            contact=10,  # Max is 5
            summary=8,
            skills=12,
            education=8,
            experience=15,
            projects=10,
            achievements_certifications=5,
            quantified_impact=8,
            total=76,
        )


def test_parsed_document_rejects_zero_page_or_oversize():
    with pytest.raises(ValidationError):
        ParsedDocument(file_name="test.pdf", text="hello", page_count=0, size_bytes=1000)

    with pytest.raises(ValidationError):
        ParsedDocument(
            file_name="test.pdf", text="hello", page_count=1, size_bytes=6_000_000
        )


def test_match_request_rejects_short_job_description():
    with pytest.raises(ValidationError):
        MatchAnalysisRequest(job_description="Too short")


def test_match_request_accepts_and_serializes_frozen_public_field_names():
    request = MatchAnalysisRequest.model_validate(
        {
            "jobDescription": "Data Analyst role requiring Python, SQL, and stakeholder reporting skills.",
            "targetRole": "Data Analyst",
        }
    )

    assert request.job_description.startswith("Data Analyst")
    assert request.target_role == "Data Analyst"
    assert request.model_dump(by_alias=True) == {
        "jobDescription": request.job_description,
        "targetRole": "Data Analyst",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"jobDescription": "Too short"},
        {"jobDescription": None},
    ],
)
def test_match_request_rejects_invalid_public_payloads(payload):
    with pytest.raises(ValidationError):
        MatchAnalysisRequest.model_validate(payload)
