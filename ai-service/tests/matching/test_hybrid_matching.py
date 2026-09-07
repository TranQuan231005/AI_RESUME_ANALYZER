"""Unit tests for hybrid lexical-semantic CV-JD matching engine."""
import pytest

from app.matching.engine import compute_lexical_similarity, match_resume_to_job
from app.schemas.matching import MatchResult


def test_compute_lexical_similarity_empty_inputs():
    assert compute_lexical_similarity("", "job description") == 0.0
    assert compute_lexical_similarity("resume text", "") == 0.0
    assert compute_lexical_similarity("   ", "   ") == 0.0


def test_compute_lexical_similarity_identical_texts():
    text = "Senior Python engineer building machine learning models with pandas and numpy."
    sim = compute_lexical_similarity(text, text)
    assert sim >= 95.0


def test_match_resume_to_job_backward_compatibility_without_text():
    result = match_resume_to_job(
        file_name="resume.pdf",
        resume_skills=["Python", "SQL"],
        job_description="Looking for Python, SQL, and Pandas.",
    )
    assert isinstance(result, MatchResult)
    assert result.match_score == 67
    assert result.matched_skills == ["Python", "SQL"]
    assert result.missing_skills == ["Pandas"]
    assert result.ai.model == "deterministic-v1"


def test_match_resume_to_job_hybrid_with_resume_text():
    resume_text = "Senior Data Scientist with 5 years experience in Python, SQL, and exploratory data analysis using Pandas."
    jd_text = "Looking for a Data Scientist with Python, SQL, and Pandas."

    result = match_resume_to_job(
        file_name="resume.pdf",
        resume_skills=["Python", "SQL", "Pandas"],
        job_description=jd_text,
        resume_text=resume_text,
    )

    assert isinstance(result, MatchResult)
    assert result.match_score >= 85
    assert result.matched_skills == ["Python", "SQL", "Pandas"]
    assert len(result.strengths) > 0
    assert result.ai.model == "hybrid-lexical-semantic-v1"


def test_match_resume_to_job_no_skills_in_jd_falls_back_to_semantic():
    resume_text = "Experienced product manager and strategic leader with agile cross-functional delivery."
    jd_text = "We are seeking a collaborative product leader to drive vision, strategy, and roadmap execution."

    result = match_resume_to_job(
        file_name="pm_resume.pdf",
        resume_skills=[],
        job_description=jd_text,
        resume_text=resume_text,
    )

    assert isinstance(result, MatchResult)
    # Should not collapse to 0%
    assert result.match_score > 0
    assert result.matched_skills == []
    assert result.missing_skills == []


def test_keyword_stuffing_penalty():
    # 12 unrelated skills listed without relevant semantic text
    stuffing_skills = ["Python", "React", "Swift", "Kotlin", "Figma", "Java", "SQL", "HTML", "CSS", "TypeScript", "NumPy", "Pandas"]
    resume_text = "Keywords: Python, React, Swift, Kotlin, Figma, Java, SQL, HTML, CSS, TypeScript, NumPy, Pandas."
    jd_text = "Senior Machine Learning Engineer specializing in distributed PyTorch, CUDA, kernel optimization, and GPU clusters."

    result = match_resume_to_job(
        file_name="stuffed.pdf",
        resume_skills=stuffing_skills,
        job_description=jd_text,
        resume_text=resume_text,
    )

    assert isinstance(result, MatchResult)
    # Should be heavily dampened
    assert result.match_score < 40
