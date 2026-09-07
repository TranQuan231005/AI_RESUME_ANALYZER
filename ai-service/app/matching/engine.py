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


def compute_lexical_similarity(resume_text: str, job_description: str) -> float:
    """Compute sublinear TF-IDF cosine similarity between resume and job description."""
    if not isinstance(resume_text, str) or not isinstance(job_description, str):
        return 0.0
    if not resume_text.strip() or not job_description.strip():
        return 0.0
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vec = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        matrix = vec.fit_transform([resume_text, job_description])
        sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        return round(max(0.0, min(100.0, sim * 100.0)), 2)
    except Exception:
        return 0.0


def match_resume_to_job(
    *,
    file_name: str,
    jd_file_name: str | None = None,
    resume_skills: Iterable[str],
    job_description: str,
    resume_text: str | None = None,
    target_role: str | None = None,
    processing_ms: int = 0,
    alpha: float = 0.80,
) -> MatchResult:
    """Build a contract-compatible hybrid MatchResult from skill evidence and semantic alignment."""
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

    # If resume_text is supplied, compute calibrated hybrid score
    if resume_text and resume_text.strip():
        lexical_score = compute_lexical_similarity(resume_text, job_description)
        if len(jd_skills) == 0:
            final_score = round(lexical_score)
        else:
            # Check for keyword stuffing: high raw skill count but low semantic cohesion
            normalized_skills = list(normalize_skills(resume_skills))
            is_stuffing = len(normalized_skills) >= 10 and lexical_score < 25.0
            if is_stuffing:
                raw_hybrid = (alpha * evidence.match_score) + ((1.0 - alpha) * lexical_score)
                final_score = round(raw_hybrid * 0.4)
                weaknesses.append("High volume of disjoint skills detected without relevant project context.")
            else:
                raw_hybrid = (alpha * evidence.match_score) + ((1.0 - alpha) * lexical_score)
                final_score = round(min(100.0, max(0.0, raw_hybrid)))
        model_name = "hybrid-lexical-semantic-v1"
    else:
        final_score = evidence.match_score
        model_name = "deterministic-v1"

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
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED,
            model=model_name,
            usedFallback=True,
            processingMs=max(0, processing_ms),
        ),
    )
