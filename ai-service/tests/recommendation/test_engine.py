import re
import pytest
from app.recommendation.engine import generate_recommendations


def is_english_text(text: str) -> bool:
    """Kiểm tra chuỗi ký tự chỉ chứa chữ cái tiếng Anh cơ bản và dấu câu (ASCII/Latin)."""
    return bool(re.match(r"^[\x00-\x7F\s\.,!\?'-]+$", text))


def test_recommendation_limits_and_rules():
    scores = {
        "contact": 2,
        "summary": 5,
        "skills": 10,
        "education": 5,
        "experience": 10,
        "projects": 5,
        "achievementsCertifications": 2,
        "quantifiedImpact": 5,
    }
    existing_skills = ["HTML", "React"]
    predicted_field = "Web Development"

    result = generate_recommendations(scores, existing_skills, predicted_field)

    assert len(result["recommendedSkills"]) <= 8
    assert len(result["recommendations"]) <= 8

    existing_skills_lower = [s.lower() for s in existing_skills]
    for skill in result["recommendedSkills"]:
        assert skill.lower() not in existing_skills_lower

    for skill in result["recommendedSkills"]:
        assert is_english_text(skill), f"Recommended skill '{skill}' contains non-English characters"

    for rec in result["recommendations"]:
        text = rec if isinstance(rec, str) else rec.get("message", rec.get("text", str(rec)))
        assert is_english_text(text), f"Recommendation '{text}' contains non-English characters"


def test_empty_skills_and_unknown_field():
    """Kiểm tra xử lý danh sách kỹ năng rỗng và trường predicted_field = 'Unknown'."""
    scores = {
        "contact": 1,
        "summary": 2,
        "skills": 3,
        "education": 2,
        "experience": 4,
        "projects": 2,
        "achievementsCertifications": 1,
        "quantifiedImpact": 1,
    }
    existing_skills = []
    predicted_field = "Unknown"

    result = generate_recommendations(scores, existing_skills, predicted_field)

    assert isinstance(result["recommendedSkills"], list)
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendedSkills"]) <= 8
    assert len(result["recommendations"]) <= 8


def test_perfect_score_recommendations():
    perfect_scores = {
        "contact": 5,
        "summary": 10,
        "skills": 15,
        "education": 10,
        "experience": 20,
        "projects": 15,
        "achievementsCertifications": 10,
        "quantifiedImpact": 15,
    }
    result = generate_recommendations(perfect_scores, [], "Unknown")
    assert len(result["recommendations"]) == 0


def test_taxonomy_fields_recommendations():
    fields = ["Data Science", "Web Development", "Android Development", "iOS Development", "UI/UX"]
    scores = {"contact": 5, "summary": 10, "skills": 5, "education": 10, "experience": 20, "projects": 15, "achievements_certifications": 10, "quantified_impact": 15}
    for field in fields:
        res = generate_recommendations(scores, [], field)
        assert len(res["recommendedSkills"]) > 0
        assert len(res["recommendations"]) == 1  # Only skills < 15 triggers


def test_snake_case_scores_lookup():
    snake_scores = {
        "contact": 5,
        "summary": 10,
        "skills": 15,
        "education": 10,
        "experience": 20,
        "projects": 15,
        "achievements_certifications": 10,
        "quantified_impact": 15,
    }
    res = generate_recommendations(snake_scores, [], "Data Science")
    assert len(res["recommendations"]) == 0


def test_contact_recommendation_does_not_mention_phone():
    scores = {"contact": 0}
    res = generate_recommendations(scores, [], "Unknown")
    assert any("email" in r.lower() for r in res["recommendations"])
    assert not any("phone" in r.lower() for r in res["recommendations"])