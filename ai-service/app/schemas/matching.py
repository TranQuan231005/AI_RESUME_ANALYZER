from typing import List, Optional
from pydantic import Field
from .common import AiMetadata, SchemaBase


class MatchAnalysisRequest(SchemaBase):
    job_description: str = Field(
        ...,
        min_length=50,
        serialization_alias="jobDescription",
        alias="jobDescription",
    )
    target_role: Optional[str] = Field(
        default=None,
        serialization_alias="targetRole",
        alias="targetRole",
    )


class MatchResult(SchemaBase):
    file_name: str = Field(..., serialization_alias="fileName", alias="fileName")
    jd_file_name: Optional[str] = Field(
        default=None,
        serialization_alias="jdFileName",
        alias="jdFileName",
    )
    target_role: str = Field(..., serialization_alias="targetRole", alias="targetRole")
    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        serialization_alias="matchScore",
        alias="matchScore",
    )
    matched_skills: List[str] = Field(
        default_factory=list,
        serialization_alias="matchedSkills",
        alias="matchedSkills",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        serialization_alias="missingSkills",
        alias="missingSkills",
    )
    ats_keywords: List[str] = Field(
        default_factory=list,
        max_length=15,
        serialization_alias="atsKeywords",
        alias="atsKeywords",
    )
    strengths: List[str] = Field(default_factory=list, max_length=6)
    weaknesses: List[str] = Field(default_factory=list, max_length=6)
    recommendations: List[str] = Field(default_factory=list, max_length=8)
    ai: AiMetadata
