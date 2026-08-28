#!/usr/bin/env python3
"""Validate the frozen JD matching evaluation dataset."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AI_SERVICE = ROOT / "ai-service"
if str(AI_SERVICE) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE))

from app.extraction.taxonomy import FIELD_NAMES, canonicalize_skill  # noqa: E402
from app.matching.engine import (  # noqa: E402
    extract_jd_skills,
    match_resume_to_job,
    normalize_skills,
)
from app.schemas import MatchResult  # noqa: E402


JD_PATH = ROOT / "evaluation" / "job-descriptions.json"
PAIR_PATH = ROOT / "evaluation" / "matching-ground-truth.json"
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){7,}(?!\w)")


class DatasetValidationError(ValueError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetValidationError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(data, dict):
        raise DatasetValidationError(f"{path.name} must contain a JSON object")
    return data


def _require_string(item: dict[str, Any], key: str, context: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DatasetValidationError(f"{context}.{key} must be a non-empty string")
    return value


def _require_string_list(item: dict[str, Any], key: str, context: str) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list) or any(not isinstance(entry, str) for entry in value):
        raise DatasetValidationError(f"{context}.{key} must be a string array")
    return value


def _validate_canonical_skills(skills: list[str], context: str) -> None:
    if len(skills) != len(set(skills)):
        raise DatasetValidationError(f"{context} contains duplicate skills")
    for skill in skills:
        if normalize_skills([skill]) != [skill]:
            raise DatasetValidationError(
                f"{context} contains non-canonical taxonomy skill: {skill!r}"
            )


def _validate_recognized_skills(skills: list[str], context: str) -> None:
    for skill in skills:
        if canonicalize_skill(skill) is None:
            raise DatasetValidationError(
                f"{context} contains a skill or alias outside the frozen taxonomy: {skill!r}"
            )


def _validate_no_pii(text: str, context: str) -> None:
    if EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text):
        raise DatasetValidationError(f"{context} contains email or phone-like PII")
    if not text.isascii():
        raise DatasetValidationError(f"{context} must use English ASCII text")


def validate_dataset() -> tuple[int, int]:
    jd_document = _read_json(JD_PATH)
    pair_document = _read_json(PAIR_PATH)
    job_descriptions = jd_document.get("jobDescriptions")
    pairs = pair_document.get("pairs")

    if not isinstance(job_descriptions, list) or len(job_descriptions) != 10:
        raise DatasetValidationError("Dataset must contain exactly 10 job descriptions")
    if not isinstance(pairs, list) or not 10 <= len(pairs) <= 15:
        raise DatasetValidationError("Dataset must contain between 10 and 15 matching pairs")

    jobs_by_id: dict[str, dict[str, Any]] = {}
    for index, job in enumerate(job_descriptions):
        context = f"jobDescriptions[{index}]"
        if not isinstance(job, dict):
            raise DatasetValidationError(f"{context} must be an object")
        job_id = _require_string(job, "id", context)
        if job_id in jobs_by_id:
            raise DatasetValidationError(f"Duplicate job description id: {job_id}")
        title = _require_string(job, "title", context)
        field = _require_string(job, "field", context)
        description = _require_string(job, "jobDescription", context)
        skills = _require_string_list(job, "skills", context)
        if field not in FIELD_NAMES or field == "Unknown":
            raise DatasetValidationError(f"{context}.field is not a supported project field")
        if len(description) < 50:
            raise DatasetValidationError(f"{context}.jobDescription must be at least 50 characters")
        _validate_no_pii(f"{title}\n{description}", context)
        _validate_canonical_skills(skills, f"{context}.skills")
        extracted = extract_jd_skills(description)
        if extracted != skills:
            raise DatasetValidationError(
                f"{context}.skills {skills!r} do not match extracted skills {extracted!r}"
            )
        jobs_by_id[job_id] = job

    pair_ids: set[str] = set()
    referenced_job_ids: set[str] = set()
    for index, pair in enumerate(pairs):
        context = f"pairs[{index}]"
        if not isinstance(pair, dict):
            raise DatasetValidationError(f"{context} must be an object")
        pair_id = _require_string(pair, "id", context)
        if pair_id in pair_ids:
            raise DatasetValidationError(f"Duplicate pair id: {pair_id}")
        pair_ids.add(pair_id)

        job_id = _require_string(pair, "jobDescriptionId", context)
        if job_id not in jobs_by_id:
            raise DatasetValidationError(f"{context} references unknown JD: {job_id}")
        referenced_job_ids.add(job_id)
        resume_skills = _require_string_list(pair, "resumeSkills", context)
        _validate_recognized_skills(resume_skills, f"{context}.resumeSkills")
        expected_matched = _require_string_list(pair, "expectedMatchedSkills", context)
        expected_missing = _require_string_list(pair, "expectedMissingSkills", context)
        reason = _require_string(pair, "reason", context)
        _validate_no_pii(reason, f"{context}.reason")
        _validate_canonical_skills(expected_matched, f"{context}.expectedMatchedSkills")
        _validate_canonical_skills(expected_missing, f"{context}.expectedMissingSkills")
        if set(expected_matched).intersection(expected_missing):
            raise DatasetValidationError(f"{context} matched and missing skills overlap")

        expected_score = pair.get("expectedScore")
        if not isinstance(expected_score, int) or not 0 <= expected_score <= 100:
            raise DatasetValidationError(f"{context}.expectedScore must be an integer from 0 to 100")

        job = jobs_by_id[job_id]
        result = match_resume_to_job(
            file_name="synthetic-resume.pdf",
            resume_skills=resume_skills,
            job_description=job["jobDescription"],
            target_role=job["title"],
        )
        MatchResult.model_validate(result.model_dump(by_alias=True))
        if result.matched_skills != expected_matched:
            raise DatasetValidationError(
                f"{context} expected matched {expected_matched!r}, got {result.matched_skills!r}"
            )
        if result.missing_skills != expected_missing:
            raise DatasetValidationError(
                f"{context} expected missing {expected_missing!r}, got {result.missing_skills!r}"
            )
        if result.match_score != expected_score:
            raise DatasetValidationError(
                f"{context} expected score {expected_score}, got {result.match_score}"
            )

    missing_coverage = set(jobs_by_id).difference(referenced_job_ids)
    if missing_coverage:
        raise DatasetValidationError(
            f"Every JD must be covered by a pair; missing: {sorted(missing_coverage)}"
        )
    return len(job_descriptions), len(pairs)


def main() -> int:
    try:
        job_count, pair_count = validate_dataset()
    except DatasetValidationError as exc:
        print(f"Dataset validation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Dataset validation passed: {job_count} job descriptions, {pair_count} pairs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
