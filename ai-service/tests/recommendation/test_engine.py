from app.recommendation.engine import generate_recommendations

def test_recommendation_limits_and_rules():
    scores = {
        "contact": 2,
        "summary": 5,
        "skills": 10,
        "education": 5,
        "experience": 10,
        "projects": 5,
        "achievementsCertifications": 2,
        "quantifiedImpact": 5
    }
    existing_skills = ["Docker", "React"]
    predicted_field = "Software Engineering"

    result = generate_recommendations(scores, existing_skills, predicted_field)

    # Kiểm tra số lượng giới hạn tối đa <= 8
    assert len(result["recommendedSkills"]) <= 8
    assert len(result["recommendations"]) <= 8

    # Kiểm tra kỹ năng gợi ý không chứa kỹ năng đã có
    for skill in result["recommendedSkills"]:
        assert skill.lower() not in [s.lower() for s in existing_skills]

def test_perfect_score_recommendations():
    perfect_scores = {
        "contact": 5, "summary": 10, "skills": 15, "education": 10,
        "experience": 20, "projects": 15, "achievementsCertifications": 10, "quantifiedImpact": 15
    }
    result = generate_recommendations(perfect_scores, [], "Unknown")
    assert len(result["recommendations"]) == 0