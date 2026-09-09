from app.extraction.taxonomy import SKILL_TAXONOMY, canonicalize_skill, find_skills


def test_aliases_map_to_one_canonical_skill():
    assert canonicalize_skill("SKLearn") == "scikit-learn"
    assert canonicalize_skill("React.js") == "React"


def test_taxonomy_has_unique_canonical_names_and_aliases():
    names = [skill.canonical_name.casefold() for skill in SKILL_TAXONOMY]
    aliases = [alias.casefold() for skill in SKILL_TAXONOMY for alias in skill.aliases]
    assert len(names) == len(set(names))
    assert len(aliases) == len(set(aliases))


def test_skill_matching_is_unique_and_respects_boundaries():
    assert find_skills("Python, python and ReactJS. Not JavaScripted.") == ["Python", "React"]


def test_long_alias_does_not_emit_an_overlapping_short_alias():
    assert find_skills("React.js with TypeScript") == ["React", "TypeScript"]
