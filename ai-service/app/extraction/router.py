from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(tags=["Extraction"])

class FieldEvidence(BaseModel):
    field: str
    matched_skills: List[str]
    confidence: float

class ExtractResponse(BaseModel):
    predicted_field: str
    field_evidence: List[FieldEvidence]

class ExtractRequest(BaseModel):
    file_name: str
    text: str
    page_count: int
    size_bytes: int

@router.post("/extract-features", response_model=ExtractResponse)
async def extract_features(payload: ExtractRequest):
    return {
        "predicted_field": "Data Science",
        "field_evidence": [
            {
                "field": "Data Science",
                "matched_skills": ["Python", "scikit-learn", "SQL"],
                "confidence": 1.0
            },
            {
                "field": "Web Development",
                "matched_skills": ["SQL"],
                "confidence": 0.33
            }
        ]
    }