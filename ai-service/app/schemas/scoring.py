from pydantic import Field, model_validator
from .common import SchemaBase


class ScoreBreakdown(SchemaBase):
    contact: int = Field(..., ge=0, le=5)
    summary: int = Field(..., ge=0, le=10)
    skills: int = Field(..., ge=0, le=15)
    education: int = Field(..., ge=0, le=10)
    experience: int = Field(..., ge=0, le=20)
    projects: int = Field(..., ge=0, le=15)
    achievements_certifications: int = Field(
        ...,
        ge=0,
        le=10,
        serialization_alias="achievementsCertifications",
        alias="achievementsCertifications",
    )
    quantified_impact: int = Field(
        ...,
        ge=0,
        le=15,
        serialization_alias="quantifiedImpact",
        alias="quantifiedImpact",
    )
    total: int = Field(..., ge=0, le=100)

    @model_validator(mode="after")
    def check_total_matches_sum(self) -> "ScoreBreakdown":
        computed_sum = (
            self.contact
            + self.summary
            + self.skills
            + self.education
            + self.experience
            + self.projects
            + self.achievements_certifications
            + self.quantified_impact
        )
        if self.total != computed_sum:
            raise ValueError(
                f"Score breakdown total ({self.total}) does not match component sum ({computed_sum})"
            )
        return self
