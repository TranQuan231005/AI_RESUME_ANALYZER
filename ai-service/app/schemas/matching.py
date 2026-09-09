from typing import List, Literal, Optional
from pydantic import Field, model_validator
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


class MatchBreakdown(SchemaBase):
    method: Literal["HYBRID_EMBEDDING", "SKILL_ONLY"]
    skill_score: int = Field(..., ge=0, le=100, alias="skillScore", serialization_alias="skillScore")
    semantic_score: Optional[int] = Field(default=None, ge=0, le=100, alias="semanticScore", serialization_alias="semanticScore")
    skill_weight: float = Field(..., ge=0.0, le=1.0, alias="skillWeight", serialization_alias="skillWeight")
    semantic_weight: float = Field(..., ge=0.0, le=1.0, alias="semanticWeight", serialization_alias="semanticWeight")
    embedding_model: Optional[str] = Field(default=None, alias="embeddingModel", serialization_alias="embeddingModel")

    @model_validator(mode="after")
    def validate_method_and_weights(self) -> "MatchBreakdown":
        if abs((self.skill_weight + self.semantic_weight) - 1.0) > 1e-6:
            raise ValueError("skillWeight and semanticWeight must sum to 1")
        if self.method == "SKILL_ONLY" and (
            self.semantic_score is not None or self.embedding_model is not None
        ):
            raise ValueError("SKILL_ONLY must not expose semantic model data")
        if self.method == "HYBRID_EMBEDDING" and (
            self.semantic_score is None or not self.embedding_model
        ):
            raise ValueError("HYBRID_EMBEDDING requires semantic score and model")
        return self
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
    match_breakdown: MatchBreakdown = Field(
        ...,
        alias="matchBreakdown",
        serialization_alias="matchBreakdown",
    )
    ai: AiMetadata
