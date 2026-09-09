from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
from typing import Iterable

from app.extraction.taxonomy import canonicalize_skill, find_skills
from app.matching.embedding import EMBEDDING_MODEL_ID, compute_embedding_similarity
from app.schemas import AiMetadata, AiProvider, MatchBreakdown, MatchResult

logger = logging.getLogger(__name__)
LOCAL_MATCHING_CONFIG = Path(__file__).resolve().parents[2] / "models" / "matching" / "metadata.json"


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


def load_matching_config(config_path: Path | str | None = None) -> dict[str, object]:
    path = Path(config_path or os.getenv("MATCHING_CONFIG_PATH", str(LOCAL_MATCHING_CONFIG)))
    try:
        with path.open(encoding="utf-8") as stream:
            config = json.load(stream)
        skill_weight = float(config["skillWeight"])
        semantic_weight = float(config["semanticWeight"])
        if not 0.0 <= skill_weight <= 1.0 or abs(skill_weight + semantic_weight - 1.0) > 1e-6:
            raise ValueError("matching weights must be in [0, 1] and sum to 1")
        return config
    except Exception as exc:
        logger.error("Matching metadata is invalid at %s: %s", path, exc)
        raise RuntimeError("Matching metadata is unavailable or invalid") from exc


def match_resume_to_job(
    *,
    file_name: str,
    jd_file_name: str | None = None,
    resume_skills: Iterable[str],
    job_description: str,
    resume_text: str | None = None,
    target_role: str | None = None,
    processing_ms: int = 0,
    config_path: Path | str | None = None,
    embedding_model: object | None = None,
) -> MatchResult:
    """Run the production skill/embedding matcher using versioned metadata."""
    jd_skills = extract_jd_skills(job_description)
    evidence = match_skills(resume_skills, jd_skills)
    
    recommendations: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []

    if evidence.matched_skills:
        strengths.append(f"Matched {len(evidence.matched_skills)} required skill(s): {', '.join(evidence.matched_skills[:4])}")
    if evidence.missing_skills:
        weaknesses.append(f"Missing {len(evidence.missing_skills)} required skill(s): {', '.join(evidence.missing_skills[:4])}")
        recommendations.append(f"Add experience or certifications in {', '.join(evidence.missing_skills[:3])} to strengthen fit.")

    if not evidence.matched_skills and not evidence.missing_skills:
        recommendations.append(
            "Provide a more specific job description with recognizable technical skills."
        )

    config = load_matching_config(config_path)
    semantic_score = compute_embedding_similarity(
        resume_text or "", job_description, model=embedding_model
    )
    if semantic_score is None:
        final_score = evidence.match_score
        breakdown = MatchBreakdown(
            method="SKILL_ONLY",
            skillScore=evidence.match_score,
            semanticScore=None,
            skillWeight=1.0,
            semanticWeight=0.0,
            embeddingModel=None,
        )
    else:
        skill_weight = 0.0 if not jd_skills else float(config["skillWeight"])
        semantic_weight = 1.0 if not jd_skills else float(config["semanticWeight"])
        final_score = round(max(0.0, min(100.0, skill_weight * evidence.match_score + semantic_weight * semantic_score)))
        breakdown = MatchBreakdown(
            method="HYBRID_EMBEDDING",
            skillScore=evidence.match_score,
            semanticScore=round(semantic_score),
            skillWeight=skill_weight,
            semanticWeight=semantic_weight,
            embeddingModel=str(config.get("embeddingModel", EMBEDDING_MODEL_ID)),
        )

    return MatchResult(
        fileName=file_name,
        jdFileName=jd_file_name,
        targetRole=_target_role(job_description, target_role),
        matchScore=final_score,
        matchedSkills=list(evidence.matched_skills),
        missingSkills=list(evidence.missing_skills),
        atsKeywords=list(evidence.matched_skills)[:10],
        strengths=strengths[:6],
        weaknesses=weaknesses[:6],
        recommendations=recommendations[:8],
        matchBreakdown=breakdown,
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED,
            model="deterministic-v1",
            usedFallback=True,
            processingMs=max(0, processing_ms),
        ),
    )
