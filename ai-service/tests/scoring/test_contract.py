import json
import os
import pytest

RUBRIC_BOUNDS = {
    "contact": (0, 5),
    "summary": (0, 10),
    "skills": (0, 15),
    "education": (0, 10),
    "experience": (0, 20),
    "projects": (0, 15),
    "achievementsCertifications": (0, 10),
    "quantifiedImpact": (0, 15)
}

def load_fixtures():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.abspath(os.path.join(base_dir, "../../../contracts/fixtures/scoring-cases.json"))
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_score_breakdown(breakdown: dict) -> bool:
    """Kiểm tra tính hợp lệ của ScoreBreakdown."""
    total_calculated = 0
    for field, (min_val, max_val) in RUBRIC_BOUNDS.items():
        val = breakdown.get(field)
        if val is None or not isinstance(val, int):
            return False
        if not (min_val <= val <= max_val):
            return False
        total_calculated += val
    if breakdown.get("total") != total_calculated:
        return False
    if not (0 <= total_calculated <= 100):
        return False        
    return True

def test_valid_scoring_cases():
    fixtures = load_fixtures()
    for case in fixtures["valid_cases"]:
        assert validate_score_breakdown(case["breakdown"]) is True, f"Failed on valid case: {case['name']}"

def test_invalid_scoring_cases():
    fixtures = load_fixtures()
    for case in fixtures["invalid_cases"]:
        assert validate_score_breakdown(case["breakdown"]) is False, f"Failed on invalid case: {case['name']}"