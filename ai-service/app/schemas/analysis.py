from typing import List, Optional
from pydantic import Field
from .common import AiMetadata, FieldEnum, SchemaBase
from .features import FieldEvidence
from .scoring import ScoreBreakdown


class ResumeAnalysisResult(SchemaBase):
    file_name: str = Field(..., serialization_alias="fileName", alias="fileName")
    candidate_name: Optional[str] = Field(
        default=None,   
        serialization_alias="candidateName",
        alias="candidateName",
    )
    candidate_email: Optional[str] = Field(
        default=None,
        serialization_alias="candidateEmail",
        alias="candidateEmail",
    )
    skills: List[str] = Field(default_factory=list)
    predicted_field: FieldEnum = Field(
        ...,
        serialization_alias="predictedField",
        alias="predictedField",
    )
    field_evidence: List[FieldEvidence] = Field(
        default_factory=list,
        serialization_alias="fieldEvidence",
        alias="fieldEvidence",
    )
    resume_score: int = Field(
        ...,
        ge=0,
        le=100,
        serialization_alias="resumeScore",
        alias="resumeScore",
    )
    score_breakdown: ScoreBreakdown = Field(
        ...,
        serialization_alias="scoreBreakdown",
        alias="scoreBreakdown",
    )
    recommended_skills: List[str] = Field(
        default_factory=list,
        max_length=8,
        serialization_alias="recommendedSkills",
        alias="recommendedSkills",
    )
    recommendations: List[str] = Field(default_factory=list, max_length=8)
    ai: AiMetadata
