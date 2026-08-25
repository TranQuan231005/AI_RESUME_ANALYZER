from typing import List, Optional
from pydantic import Field
from .common import FieldEnum, SchemaBase


class FieldEvidence(SchemaBase):
    field: FieldEnum
    matched_skills: List[str] = Field(
        default_factory=list,
        serialization_alias="matchedSkills",
        alias="matchedSkills",
    )
    confidence: float = Field(..., ge=0.0, le=1.0)


class ResumeFeatures(SchemaBase):
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
        default=FieldEnum.UNKNOWN,
        serialization_alias="predictedField",
        alias="predictedField",
    )
    field_evidence: List[FieldEvidence] = Field(
        default_factory=list,
        serialization_alias="fieldEvidence",
        alias="fieldEvidence",
    )
