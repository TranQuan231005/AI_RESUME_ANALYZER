import json
from pathlib import Path
import pytest
from app.schemas import ParsedDocument, ResumeFeatures, ScoreBreakdown
from app.scoring.engine import calculate_score

FIXTURE_PATH = Path(__file__).parents[3] / "contracts" / "fixtures" / "scoring-cases.json"


def load_scoring_cases():
    """Hàm bổ trợ nạp các test cases từ fixture JSON."""
    if FIXTURE_PATH.exists():
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("valid_cases", []), data.get("invalid_cases", [])
    return [], []


def test_deterministic_scoring():
    doc = ParsedDocument(
        fileName="test.pdf",
        text="SUMMARY\nExperienced software engineer.\n\nEXPERIENCE\nBuilt web apps using React.\n\nPROJECTS\nDeveloped fullstack platform.\n\nCERTIFICATIONS\nAWS Certified.",
        pageCount=1,
        sizeBytes=1024,
    )
    features = ResumeFeatures(
        candidateName="Le Dinh Vi",
        candidateEmail="test@example.com",
        skills=["Python", "React", "TypeScript", "Python"],
        predictedField="Web Development",
        fieldEvidence=[],
    )

    first_result = calculate_score(doc, features)

    for _ in range(10):
        result = calculate_score(doc, features)
        assert result == first_result
        assert result.total == sum([
            result.contact,
            result.summary,
            result.skills,
            result.education,
            result.experience,
            result.projects,
            result.achievements_certifications,
            result.quantified_impact,
        ])


def test_score_boundary_limits():
    doc = ParsedDocument(
        fileName="full.pdf",
        text="""
        SUMMARY
        Senior Full Stack Engineer with 10+ years of experience building scalable systems.
        EDUCATION
        Bachelor of Science in Computer Science, University of Technology.
        EXPERIENCE
        - Led a team of 10 engineers, reduced latency by 45%.
        - Increased active users from 10k to 100k users.
        PROJECTS
        Built microservice architecture handling $10M transactions.
        ACHIEVEMENTS
        AWS Certified Solutions Architect, Best Employee Award 2025.
        """,
        pageCount=2,
        sizeBytes=2048,
    )
    features = ResumeFeatures(
        candidateName="Nguyen Van A",
        candidateEmail="a@example.com",
        skills=["Python", "React", "Docker", "Kubernetes", "AWS", "SQL", "Git"],
        predictedField="Web Development",
        fieldEvidence=[],
    )

    result = calculate_score(doc, features)

    assert 0 <= result.contact <= 5
    assert 0 <= result.summary <= 10
    assert 0 <= result.skills <= 15
    assert 0 <= result.education <= 10
    assert 0 <= result.experience <= 20
    assert 0 <= result.projects <= 15
    assert 0 <= result.achievements_certifications <= 10
    assert 0 <= result.quantified_impact <= 15
    assert 0 <= result.total <= 100


def test_quantified_impact_filters_phone_and_years():
    doc = ParsedDocument(
        fileName="phone.pdf",
        text="Phone: +84 912345678. Graduated in 2024. Active during 2020-2024.",
        pageCount=1,
        sizeBytes=500,
    )
    features = ResumeFeatures(
        candidateName="Test User",
        candidateEmail="test@example.com",
        skills=[],
        predictedField="Unknown",
        fieldEvidence=[],
    )

    result = calculate_score(doc, features)
    assert result.quantified_impact == 0


def test_zero_score_boundary():
    """Kiểm tra trường hợp CV không chứa thông tin hợp lệ để tính điểm."""
    doc = ParsedDocument(
        fileName="empty.pdf",
        text=" ", 
        pageCount=1,
        sizeBytes=100,
    )
    features = ResumeFeatures(
        candidateName="",
        candidateEmail="",
        skills=[],
        predictedField="Unknown",
        fieldEvidence=[],
    )

    result = calculate_score(doc, features)
    assert result.total == 0
    assert result.contact == 0
    assert result.summary == 0
    assert result.skills == 0
    assert result.education == 0
    assert result.experience == 0
    assert result.projects == 0
    assert result.achievements_certifications == 0
    assert result.quantified_impact == 0


def test_scoring_cases_fixture_coverage():
    """Kiểm tra tính hợp lệ của toàn bộ 15+ cases trong fixture file JSON."""
    valid_cases, invalid_cases = load_scoring_cases()
    
    assert len(valid_cases) + len(invalid_cases) >= 15, "Phải có ít nhất 15 scoring cases trong fixture JSON"

    for case in valid_cases:
        bd = case["breakdown"]
        components_sum = (
            bd["contact"]
            + bd["summary"]
            + bd["skills"]
            + bd["education"]
            + bd["experience"]
            + bd["projects"]
            + bd["achievementsCertifications"]
            + bd["quantifiedImpact"]
        )
        assert bd["total"] == components_sum, f"Mismatch sum in case: {case['name']}"


def test_contract_field_aliases():
    """Đảm bảo Pydantic model xuất ra đúng tên trường camelCase cho Frontend."""
    breakdown = ScoreBreakdown(
        contact=5,
        summary=8,
        skills=12,
        education=8,
        experience=15,
        projects=10,
        achievements_certifications=5,
        quantified_impact=8,
        total=71,
    )
    
    dumped = breakdown.model_dump(by_alias=True)
    
    assert "achievementsCertifications" in dumped
    assert "quantifiedImpact" in dumped
    assert "achievements_certifications" not in dumped
    assert "quantified_impact" not in dumped