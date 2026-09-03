from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.extraction.taxonomy import canonicalize_skill, find_skills
from app.schemas import AiMetadata, AiProvider, MatchResult


@dataclass(frozen=True)
class SkillMatch:
    """Deterministic skill evidence produced before ATS enrichment."""

    match_score: int
    matched_skills: tuple[str, ...]
    missing_skills: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "matchScore": self.match_score,
            "matchedSkills": list(self.matched_skills),
            "missingSkills": list(self.missing_skills),
        }


def normalize_skills(skills: Iterable[str]) -> list[str]:
    """Return unique canonical skills while preserving the input order."""
    normalized: list[str] = []
    seen: set[str] = set()
    for value in skills:
        if not isinstance(value, str):
            continue
        canonical = canonicalize_skill(value)
        if canonical is None or canonical.casefold() in seen:
            continue
        seen.add(canonical.casefold())
        normalized.append(canonical)
    return normalized


def extract_jd_skills(job_description: str) -> list[str]:
    """Extract canonical, unique skills from JD text in their first-seen order."""
    if not isinstance(job_description, str) or not job_description.strip():
        return []
    return find_skills(job_description)


def calculate_match_score(matched_count: int, jd_skill_count: int) -> int:
    """Apply the frozen ``round(100 * matched / JD skills)`` formula."""
    if matched_count < 0 or jd_skill_count <= 0:
        return 0
    bounded_matched = min(matched_count, jd_skill_count)
    return round(100 * bounded_matched / jd_skill_count)


def match_skills(
    resume_skills: Iterable[str],
    jd_skills: Iterable[str],
) -> SkillMatch:
    """Partition canonical JD skills into disjoint matched and missing skills."""
    normalized_resume = {skill.casefold() for skill in normalize_skills(resume_skills)}
    normalized_jd = normalize_skills(jd_skills)

    matched = tuple(
        skill for skill in normalized_jd if skill.casefold() in normalized_resume
    )
    missing = tuple(
        skill for skill in normalized_jd if skill.casefold() not in normalized_resume
    )
    return SkillMatch(
        match_score=calculate_match_score(len(matched), len(normalized_jd)),
        matched_skills=matched,
        missing_skills=missing,
    )


def _target_role(job_description: str, requested_role: str | None) -> str:
    if requested_role and requested_role.strip():
        return requested_role.strip()[:120]
    for line in job_description.splitlines():
        title = line.strip()
        if title:
            return title[:120]
    return "Unspecified Role"


def match_resume_to_job(
    *,
    file_name: str,
    jd_file_name: str | None = None,
    resume_skills: Iterable[str],
    job_description: str,
    target_role: str | None = None,
    processing_ms: int = 0,
) -> MatchResult:
    """Build a contract-compatible rule-based MatchResult from skill evidence."""
    evidence = match_skills(resume_skills, extract_jd_skills(job_description))
    recommendations = []
    if not evidence.matched_skills and not evidence.missing_skills:
        recommendations.append(
            "Provide a more specific job description with recognizable technical skills."
        )

    return MatchResult(
        fileName=file_name,
        jdFileName=jd_file_name,
        targetRole=_target_role(job_description, target_role),
        matchScore=evidence.match_score,
        matchedSkills=list(evidence.matched_skills),
        missingSkills=list(evidence.missing_skills),
        atsKeywords=[],
        strengths=[],
        weaknesses=[],
        recommendations=recommendations,
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED,
            model="deterministic-v1",
            usedFallback=True,
            processingMs=max(0, processing_ms),
        ),
    )
