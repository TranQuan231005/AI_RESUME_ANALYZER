from __future__ import annotations
from dataclasses import dataclass
import re


FIELD_NAMES = (
    "Data Science",
    "Web Development",
    "Android Development",
    "iOS Development",
    "UI/UX",
    "Unknown",
)


@dataclass(frozen=True)
class SkillDefinition:
    canonical_name: str
    aliases: tuple[str, ...]
    fields: tuple[str, ...]


SKILL_TAXONOMY = (
    SkillDefinition("Python", ("python",), ("Data Science",)),
    SkillDefinition("SQL", ("sql",), ("Data Science", "Web Development")),
    SkillDefinition("Pandas", ("pandas",), ("Data Science",)),
    SkillDefinition("NumPy", ("numpy",), ("Data Science",)),
    SkillDefinition("scikit-learn", ("scikit-learn", "sklearn"), ("Data Science",)),
    SkillDefinition("TensorFlow", ("tensorflow",), ("Data Science",)),
    SkillDefinition("React", ("react", "react.js", "reactjs"), ("Web Development",)),
    SkillDefinition("TypeScript", ("typescript", "ts"), ("Web Development",)),
    SkillDefinition("JavaScript", ("javascript", "js"), ("Web Development",)),
    SkillDefinition("HTML", ("html",), ("Web Development",)),
    SkillDefinition("CSS", ("css",), ("Web Development", "UI/UX")),
    SkillDefinition("Java", ("java",), ("Android Development",)),
    SkillDefinition("Kotlin", ("kotlin",), ("Android Development",)),
    SkillDefinition("Swift", ("swift",), ("iOS Development",)),
    SkillDefinition("SwiftUI", ("swiftui",), ("iOS Development",)),
    SkillDefinition("Figma", ("figma",), ("UI/UX",)),
    SkillDefinition("Adobe XD", ("adobe xd", "xd"), ("UI/UX",)),
)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().casefold())


_ALIAS_TO_SKILL = {
    _normalise(alias): skill.canonical_name
    for skill in SKILL_TAXONOMY
    for alias in skill.aliases
}


def canonicalize_skill(value: str) -> str | None:
    return _ALIAS_TO_SKILL.get(_normalise(value))


def find_skills(text: str) -> list[str]:
    lowered = text.casefold()
    matches: list[tuple[int, int, str]] = []
    for skill in SKILL_TAXONOMY:
        for alias in skill.aliases:
            pattern = rf"(?<![a-z0-9+#]){re.escape(alias.casefold())}(?![a-z0-9+#])"
            for match in re.finditer(pattern, lowered):
                matches.append((match.start(), match.end(), skill.canonical_name))

    result: list[str] = []
    accepted_spans: list[tuple[int, int]] = []
    for start, end, canonical_name in sorted(
        matches, key=lambda item: (item[0], -(item[1] - item[0]), item[2])
    ):
        overlaps = any(
            start < accepted_end and end > accepted_start
            for accepted_start, accepted_end in accepted_spans
        )
        if overlaps:
            continue
        accepted_spans.append((start, end))
        if canonical_name not in result:
            result.append(canonical_name)
    return result
