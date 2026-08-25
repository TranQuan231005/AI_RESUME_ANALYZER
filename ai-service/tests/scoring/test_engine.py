from app.scoring.engine import calculate_score

def test_deterministic_scoring():
    sample_input = {
        "contact_score": 5,
        "summary_score": 8,
        "skills_score": 12,
        "education_score": 8,
        "experience_score": 15,
        "projects_score": 10,
        "achievements_score": 5,
        "impact_score": 8
    }
    res1 = calculate_score(sample_input)
    res2 = calculate_score(sample_input)

    assert res1 == res2
    assert res1["total"] == 71

def test_score_boundary_limits():
    overflow_input = {k: 999 for k in ["contact_score", "summary_score", "skills_score", "education_score", "experience_score", "projects_score", "achievements_score", "impact_score"]}
    res = calculate_score(overflow_input)
    assert res["total"] == 100