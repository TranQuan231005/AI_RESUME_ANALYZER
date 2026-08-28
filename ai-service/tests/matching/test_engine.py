from app.matching.engine import (
    calculate_match_score,
    extract_jd_skills,
    match_resume_to_job,
    match_skills,
    normalize_skills,
)
from app.schemas import MatchResult


def test_matching_uses_frozen_score_formula_and_jd_order():
    result = match_skills(
        ["SQL", "Python"],
        ["Python", "Pandas", "SQL"],
    )

    assert result.match_score == 67
    assert result.matched_skills == ("Python", "SQL")
    assert result.missing_skills == ("Pandas",)


def test_empty_resume_skills_produces_zero_and_all_skills_missing():
    result = match_skills([], ["Python", "SQL"])

    assert result.match_score == 0
    assert result.matched_skills == ()
    assert result.missing_skills == ("Python", "SQL")


def test_jd_with_no_recognized_skills_returns_contract_compatible_result():
    result = match_resume_to_job(
        file_name="resume.pdf",
        resume_skills=["Python"],
        job_description="General Specialist\nCollaborate with a cross-functional team.",
    )

    assert isinstance(result, MatchResult)
    assert result.match_score == 0
    assert result.matched_skills == []
    assert result.missing_skills == []
    assert result.target_role == "General Specialist"
    assert result.recommendations == [
        "Provide a more specific job description with recognizable technical skills."
    ]


def test_duplicate_aliases_and_mixed_casing_are_canonical_and_unique():
    assert normalize_skills(["SKLearn", "scikit-learn", "PYTHON", "python"]) == [
        "scikit-learn",
        "Python",
    ]

    result = match_skills(
        ["react.js", "TYPESCRIPT", "reactjs"],
        ["React", "react.js", "ts", "TypeScript", "CSS"],
    )
    assert result.match_score == 67
    assert result.matched_skills == ("React", "TypeScript")
    assert result.missing_skills == ("CSS",)
    assert set(result.matched_skills).isdisjoint(result.missing_skills)


def test_jd_extraction_respects_boundaries_and_first_occurrence_order():
    assert extract_jd_skills("Use React.js with TypeScript, SQL, and ReactJS.") == [
        "React",
        "TypeScript",
        "SQL",
    ]
    assert extract_jd_skills("A javascripted phrase contains no named tool.") == []


def test_output_is_stable_and_serializes_with_match_result_aliases():
    inputs = {
        "file_name": "resume.pdf",
        "resume_skills": ["PYTHON", "sql", "SQL"],
        "job_description": "Data Analyst\nPython, Pandas, and SQL are required.",
        "target_role": "Data Analyst",
    }
    first = match_resume_to_job(**inputs).model_dump(by_alias=True)
    second = match_resume_to_job(**inputs).model_dump(by_alias=True)

    assert first == second
    assert first["matchScore"] == 67
    assert first["matchedSkills"] == ["Python", "SQL"]
    assert first["missingSkills"] == ["Pandas"]
    assert first["ai"]["provider"] == "RULE_BASED"


def test_score_uses_frozen_round_formula_and_invalid_denominator_is_zero():
    assert calculate_match_score(1, 8) == round(100 * 1 / 8)
    assert calculate_match_score(9, 8) == 100
    assert calculate_match_score(1, 0) == 0
