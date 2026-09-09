from fastapi import APIRouter
from pydantic import BaseModel, Field, ConfigDict
from typing import List

router = APIRouter(tags=["Extraction"])

class FieldEvidence(BaseModel):
    field: str
    matched_skills: List[str] = Field(alias="matchedSkills")
    confidence: float

    model_config = ConfigDict(populate_by_name=True)

class ExtractResponse(BaseModel):
    candidate_name: str = Field(alias="candidateName")
    candidate_email: str = Field(alias="candidateEmail")
    skills: List[str]
    predicted_field: str = Field(alias="predictedField")
    field_evidence: List[FieldEvidence] = Field(alias="fieldEvidence")

    model_config = ConfigDict(populate_by_name=True)

class ExtractRequest(BaseModel):
    file_name: str = Field(alias="fileName")
    text: str
    page_count: int = Field(alias="pageCount")
    size_bytes: int = Field(alias="sizeBytes")

    model_config = ConfigDict(populate_by_name=True)

@router.post("/extract-features", response_model=ExtractResponse)
async def extract_features(payload: ExtractRequest):
    return {
        "candidateName": "Alex Morgan",
        "candidateEmail": "alex@example.test",
        "skills": ["Python", "scikit-learn", "SQL"],
        "predictedField": "Data Science",
        "fieldEvidence": [
            {
                "field": "Data Science",
                "matchedSkills": ["Python", "scikit-learn", "SQL"],
                "confidence": 1.0
            },
            {
                "field": "Web Development",
                "matchedSkills": ["SQL"],
                "confidence": 0.33
            }
        ]
    }