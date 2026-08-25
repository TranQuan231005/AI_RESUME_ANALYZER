from __future__ import annotations
from dataclasses import dataclass
import re

from .taxonomy import find_skills


@dataclass(frozen=True)
class ResumeFeatures:
    candidate_name: str | None
    candidate_email: str | None
    skills: list[str]
    predicted_field: str = "Unknown"
    field_evidence: list[dict] | None = None


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
NAME_PATTERN = re.compile(r"^(?:name\s*:\s*)?([A-Za-z]+(?:[ '-][A-Za-z]+){1,5})$")
IGNORED_HEADINGS = {
    "resume",
    "curriculum vitae",
    "cv",
    "contact",
    "profile",
    "summary",
    "professional summary",
}
NON_NAME_TERMS = {
    "analyst",
    "developer",
    "engineer",
    "experienced",
    "manager",
    "specialist",
}


def extract_candidate_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0).lower() if match else None


def extract_candidate_name(text: str) -> str | None:
    for line in text.splitlines():
        candidate = " ".join(line.split()).strip()
        if not candidate or candidate.casefold() in IGNORED_HEADINGS:
            continue
        if any(term in candidate.casefold().split() for term in NON_NAME_TERMS):
            continue
        match = NAME_PATTERN.fullmatch(candidate)
        if match and not any(char.isdigit() for char in candidate):
            return match.group(1)
    return None


def extract_features(text: str) -> ResumeFeatures:
    return ResumeFeatures(
        candidate_name=extract_candidate_name(text),
        candidate_email=extract_candidate_email(text),
        skills=find_skills(text),
    )
