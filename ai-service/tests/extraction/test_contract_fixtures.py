import json
from pathlib import Path

from app.extraction import classify_features, extract_features


ROOT = Path(__file__).resolve().parents[3]


def _to_contract(features):
    return {
        "candidateName": features.candidate_name,
        "candidateEmail": features.candidate_email,
        "skills": features.skills,
        "predictedField": features.predicted_field,
        "fieldEvidence": features.field_evidence or [],
    }


def test_resume_features_fixture_matches_extraction_pipeline():
    fixture = json.loads((ROOT / "contracts/fixtures/resume-features.json").read_text())
    features = classify_features(
        extract_features("Alex Morgan\nalex@example.test\nPython, sklearn, and SQL")
    )
    assert _to_contract(features) == fixture


def test_missing_fields_fixture_matches_extraction_pipeline():
    fixture = json.loads(
        (ROOT / "contracts/fixtures/resume-features-missing-fields.json").read_text()
    )
    features = classify_features(extract_features("Professional Summary\nExperienced analyst"))
    assert _to_contract(features) == fixture
