from app.extraction.features import extract_features


def test_extracts_name_email_and_canonical_skills():
    features = extract_features("Alex Morgan\nalex@example.test\nPython, sklearn, and SQL")
    assert features.candidate_name == "Alex Morgan"
    assert features.candidate_email == "alex@example.test"
    assert features.skills == ["Python", "scikit-learn", "SQL"]


def test_missing_metadata_is_nullable_or_empty():
    features = extract_features("Professional Summary\nExperienced analyst")
    assert features.candidate_name is None
    assert features.candidate_email is None
    assert features.skills == []