from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_extract_features_endpoint_returns_contract_shape():
    response = client.post(
        "/api/extract-features",
        json={
            "fileName": "alex_resume.pdf",
            "text": "Alex Morgan\nalex@example.test\nPython, sklearn, SQL",
            "pageCount": 1,
            "sizeBytes": 1000,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "candidateName": "Alex Morgan",
        "candidateEmail": "alex@example.test",
        "skills": ["Python", "scikit-learn", "SQL"],
        "predictedField": "Data Science",
        "fieldEvidence": [
            {
                "field": "Data Science",
                "matchedSkills": ["Python", "scikit-learn", "SQL"],
                "confidence": 1.0,
            },
            {
                "field": "Web Development",
                "matchedSkills": ["SQL"],
                "confidence": 0.33,
            },
        ],
    }
