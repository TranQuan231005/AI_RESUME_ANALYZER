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
URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+|\b(?:github\.com|linkedin\.com)\S*", re.IGNORECASE)
NAME_PATTERN = re.compile(
    r"^(?:name\s*:\s*)?((?:(?:Dr|Mr|Ms|Mrs)\.?\s+)?[A-Za-z]+(?:[ '-][A-Za-z]+){1,5})$",
    re.IGNORECASE,
)
IGNORED_HEADINGS = {
    "resume",
    "curriculum vitae",
    "cv",
    "contact",
    "contact info",
    "contact information",
    "profile",
    "summary",
    "professional summary",
    "about me",
    "experience",
    "education",
    "skills",
    "technical skills",
    "projects",
}
NON_NAME_TERMS = {
    "analyst",
    "developer",
    "engineer",
    "experienced",
    "manager",
    "specialist",
    "designer",
    "architect",
    "consultant",
    "intern",
    "senior",
    "junior",
    "lead",
}


def extract_candidate_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0).lower() if match else None


def extract_candidate_name(text: str) -> str | None:
    for line in text.splitlines()[:15]:
        # Bỏ qua nếu dòng chứa URL hoặc email
        if EMAIL_PATTERN.search(line) or URL_PATTERN.search(line):
            continue
        candidate = " ".join(line.split()).strip()
        if not candidate:
            continue
        if candidate.casefold() in IGNORED_HEADINGS or candidate.rstrip(":").casefold() in IGNORED_HEADINGS:
            continue
        # Bỏ qua nếu toàn bộ dòng là chức danh hoặc chứa từ khóa chức danh đơn lẻ
        words = [w.strip(" ,.-") for w in candidate.casefold().split()]
        if any(term in words for term in NON_NAME_TERMS):
            continue
        match = NAME_PATTERN.fullmatch(candidate)
        if match and not any(char.isdigit() for char in candidate):
            extracted = match.group(1).strip()
            # Đảm bảo có ít nhất 2 từ hợp lệ
            if len(extracted.split()) >= 2:
                return extracted
    return None


def extract_features(text: str) -> ResumeFeatures:
    return ResumeFeatures(
        candidate_name=extract_candidate_name(text),
        candidate_email=extract_candidate_email(text),
        skills=find_skills(text),
    )
