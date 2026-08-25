from __future__ import annotations
from collections import defaultdict

from .features import ResumeFeatures
from .taxonomy import FIELD_NAMES, SKILL_TAXONOMY


def classify_features(features: ResumeFeatures) -> ResumeFeatures:
    counts: dict[str, int] = defaultdict(int)
    evidence_skills: dict[str, list[str]] = defaultdict(list)

    for skill_name in features.skills:
        definition = next(
            (item for item in SKILL_TAXONOMY if item.canonical_name == skill_name),
            None,
        )
        if definition is None:
            continue
        for field in definition.fields:
            counts[field] += 1
            evidence_skills[field].append(skill_name)

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    predicted_field = "Unknown"
    if ranked and ranked[0][1] >= 2 and (len(ranked) == 1 or ranked[0][1] > ranked[1][1]):
        predicted_field = ranked[0][0]

    evidence = [
        {
            "field": field,
            "matchedSkills": evidence_skills[field],
            "confidence": round(count / max(len(features.skills), 1), 2),
        }
        for field, count in ranked
        if count > 0
    ]
    return ResumeFeatures(
        candidate_name=features.candidate_name,
        candidate_email=features.candidate_email,
        skills=list(features.skills),
        predicted_field=predicted_field if predicted_field in FIELD_NAMES else "Unknown",
        field_evidence=evidence,
    )