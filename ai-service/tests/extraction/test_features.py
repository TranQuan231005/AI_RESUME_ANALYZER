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


def test_candidate_name_two_words():
    features = extract_features("John Doe\njohn@example.com\nPython Developer")
    assert features.candidate_name == "John Doe"


def test_candidate_name_with_hyphen_and_apostrophe():
    features1 = extract_features("Jean-Luc Picard\npicard@starfleet.org")
    assert features1.candidate_name == "Jean-Luc Picard"

    features2 = extract_features("Sarah O'Connor\nsarah@sky.net")
    assert features2.candidate_name == "Sarah O'Connor"


def test_candidate_name_with_preceding_heading():
    text = "Curriculum Vitae\nRESUME\nAlex Morgan\nalex@example.com\nSummary"
    features = extract_features(text)
    assert features.candidate_name == "Alex Morgan"


def test_candidate_name_with_following_job_title():
    text = "Jane Smith\nSenior Software Engineer\njane@example.com"
    features = extract_features(text)
    assert features.candidate_name == "Jane Smith"


def test_candidate_name_missing():
    text = "Resume\nSoftware Engineer\nengineer@example.com\nPython, React"
    features = extract_features(text)
    assert features.candidate_name is None