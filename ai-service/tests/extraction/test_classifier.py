from app.extraction.classifier import classify_features
from app.extraction.features import ResumeFeatures


def test_low_evidence_is_unknown():
    result = classify_features(ResumeFeatures(None, None, ["Python"]))
    assert result.predicted_field == "Unknown"


def test_tie_is_unknown():
    result = classify_features(ResumeFeatures(None, None, ["Python", "Pandas", "React", "HTML"]))
    assert result.predicted_field == "Unknown"


def test_evidence_contains_only_input_skills():
    result = classify_features(ResumeFeatures(None, None, ["Python", "Pandas"]))
    assert result.predicted_field == "Data Science"
    assert result.field_evidence[0]["matchedSkills"] == ["Python", "Pandas"]