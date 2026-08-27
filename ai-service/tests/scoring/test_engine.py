import pytest
from app.schemas import ParsedDocument, ResumeFeatures, ScoreBreakdown
from app.scoring.engine import calculate_score


def test_deterministic_scoring():
    doc = ParsedDocument(
        fileName="test.pdf",
        text="SUMMARY\nExperienced software engineer.\n\nEXPERIENCE\nBuilt web apps using React.\n\nPROJECTS\nDeveloped fullstack platform.\n\nCERTIFICATIONS\nAWS Certified.",
        pageCount=1,
        sizeBytes=1024
    )
    features = ResumeFeatures(
        candidateName="Le Dinh Vi",
        candidateEmail="test@example.com",
        skills=["Python", "React", "TypeScript", "Python"],
        predictedField="Web Development",
        fieldEvidence=[]
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
            result.quantified_impact
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
        sizeBytes=2048
    )
    features = ResumeFeatures(
        candidateName="Nguyen Van A",
        candidateEmail="a@example.com",
        skills=["Python", "React", "Docker", "Kubernetes", "AWS", "SQL", "Git"],
        predictedField="Web Development",
        fieldEvidence=[]
    )

    result = calculate_score(doc, features)

    assert result.contact <= 5
    assert result.summary <= 10
    assert result.skills <= 15
    assert result.education <= 10
    assert result.experience <= 20
    assert result.projects <= 15
    assert result.achievements_certifications <= 10
    assert result.quantified_impact <= 15
    assert result.total <= 100


def test_quantified_impact_filters_phone_and_years():
    doc = ParsedDocument(
        fileName="phone.pdf",
        text="Phone: +84 912345678. Graduated in 2024. Active during 2020-2024.",
        pageCount=1,
        sizeBytes=500
    )
    features = ResumeFeatures(
        candidateName="Test User",
        candidateEmail="test@example.com",
        skills=[],
        predictedField="Unknown",
        fieldEvidence=[]
    )

    result = calculate_score(doc, features)
    assert result.quantified_impact == 0