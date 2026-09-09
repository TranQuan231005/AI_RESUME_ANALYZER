"""Integration checks against repository-owned synthetic PDF fixtures."""
from pathlib import Path

from app.document.parser import extract_pdf_content
from app.extraction.features import extract_features
from app.ml.classifier import classify_resume_features_ml
from app.recommendation.engine import generate_recommendations
from app.schemas import FieldEnum, ResumeFeatures
from app.scoring.engine import calculate_score

ROOT = Path(__file__).resolve().parents[3]


def test_real_multiline_pdf_runs_complete_resume_pipeline():
    pdf_path = ROOT / "sample_files" / "resumes" / "01_data_science_senior.pdf"
    parsed = extract_pdf_content(pdf_path.read_bytes(), pdf_path.name)
    assert "\n" in parsed.text
    assert "EXPERIENCE" in parsed.text.upper()
    assert "SKILLS" in parsed.text.upper()

    raw = extract_features(parsed.text)
    classified = classify_resume_features_ml(parsed.text, raw)
    evidence = classified.field_evidence or []
    schema_features = ResumeFeatures(
        candidateName=classified.candidate_name,
        candidateEmail=classified.candidate_email,
        skills=classified.skills,
        predictedField=classified.predicted_field if classified.predicted_field in [item.value for item in FieldEnum] else FieldEnum.UNKNOWN,
        fieldEvidence=evidence,
    )
    score = calculate_score(parsed, schema_features)
    recommendations = generate_recommendations(
        score.model_dump(), schema_features.skills, str(schema_features.predicted_field)
    )

    assert schema_features.candidate_name == "Dr. Sarah Chen"
    assert score.total == sum(value for key, value in score.model_dump().items() if key != "total")
    assert all("topTerms" in item for item in evidence)
    assert recommendations["recommendations"]


def test_real_pdf_without_contact_does_not_cross_section_boundaries():
    pdf_path = ROOT / "sample_files" / "resumes" / "07_missing_contact_info_edge_case.pdf"
    parsed = extract_pdf_content(pdf_path.read_bytes(), pdf_path.name)
    features = extract_features(parsed.text)
    assert features.candidate_email is None
    assert "PROFESSIONAL SUMMARY" not in (features.candidate_name or "").upper()
