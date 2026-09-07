"""Validator for CV-JD matching evaluation dataset."""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List

DATASET_DIR = Path(__file__).resolve().parents[1] / "datasets" / "matching"
SCHEMA_PATH = DATASET_DIR / "dataset.schema.json"
PAIRS_PATH = DATASET_DIR / "pairs.jsonl"
MANIFEST_PATH = DATASET_DIR / "manifest.json"

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], path_str: str = "") -> List[str]:
    errors = []
    required = schema.get("required", [])
    for req in required:
        if req not in data:
            errors.append(f"{path_str}: Missing required field '{req}'")

    props = schema.get("properties", {})
    for key, value in data.items():
        if key not in props and not schema.get("additionalProperties", True):
            errors.append(f"{path_str}: Disallowed additional property '{key}'")
            continue
        spec = props.get(key, {})
        expected_type = spec.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"{path_str}.{key}: Expected string, got {type(value).__name__}")
        elif expected_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            errors.append(f"{path_str}.{key}: Expected integer, got {type(value).__name__}")
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"{path_str}.{key}: Expected boolean, got {type(value).__name__}")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"{path_str}.{key}: Expected array, got {type(value).__name__}")

        if "minimum" in spec and isinstance(value, (int, float)) and value < spec["minimum"]:
            errors.append(f"{path_str}.{key}: Value {value} is below minimum {spec['minimum']}")
        if "maximum" in spec and isinstance(value, (int, float)) and value > spec["maximum"]:
            errors.append(f"{path_str}.{key}: Value {value} is above maximum {spec['maximum']}")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{path_str}.{key}: Value '{value}' not in allowed enum {spec['enum']}")
        if "minLength" in spec and isinstance(value, str) and len(value) < spec["minLength"]:
            errors.append(f"{path_str}.{key}: Length {len(value)} is below minLength {spec['minLength']}")
        if "pattern" in spec and isinstance(value, str) and not re.match(spec["pattern"], value):
            errors.append(f"{path_str}.{key}: Value does not match pattern {spec['pattern']}")

    return errors


def main() -> None:
    if not SCHEMA_PATH.exists():
        print(f"Error: Schema not found at {SCHEMA_PATH}")
        sys.exit(1)
    if not PAIRS_PATH.exists():
        print(f"Error: Pairs file not found at {PAIRS_PATH}")
        sys.exit(1)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    pairs = []
    with open(PAIRS_PATH, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    pairs.append((idx, json.loads(line)))
                except json.JSONDecodeError as e:
                    print(f"JSON decode error at line {idx}: {e}")
                    sys.exit(1)

    print(f"Validating {len(pairs)} CV-JD matching benchmark pairs...")
    all_errors = []
    seen_ids = set()
    seen_pairs = set()
    scenario_counts = Counter()
    domain_counts = Counter()
    split_counts = Counter()
    template_splits = {}

    for line_no, item in pairs:
        pair_id = item.get("id", f"line_{line_no}")
        errs = validate_schema(item, schema, f"Line {line_no} [{pair_id}]")
        all_errors.extend(errs)

        if pair_id in seen_ids:
            all_errors.append(f"Duplicate pair ID: {pair_id}")
        seen_ids.add(pair_id)

        pair_key = (item.get("resumeText", "").strip(), item.get("jdText", "").strip())
        if pair_key in seen_pairs:
            all_errors.append(f"Duplicate (resumeText, jdText) pair at line {line_no}")
        seen_pairs.add(pair_key)

        scenario_counts[item.get("scenarioType", "unknown")] += 1
        domain_counts[item.get("domain", "unknown")] += 1
        split = item.get("split", "unknown")
        split_counts[split] += 1
        template_group = item.get("templateGroup")
        if template_group in template_splits and template_splits[template_group] != split:
            all_errors.append(f"Template group {template_group!r} leaks across splits")
        template_splits[template_group] = split

        reviewer_scores = item.get("reviewerScores", [])
        if item.get("reviewed"):
            if len(reviewer_scores) != 2:
                all_errors.append(f"{pair_id}: reviewed=true requires exactly two reviewer scores")
            else:
                reviewer_ids = {score.get("reviewerId") for score in reviewer_scores}
                values = [score.get("score") for score in reviewer_scores]
                if len(reviewer_ids) != 2 or not all(isinstance(value, int) and 0 <= value <= 100 for value in values):
                    all_errors.append(f"{pair_id}: reviewers must be distinct and scores must be 0..100")
                elif abs(values[0] - values[1]) > 15 and item.get("adjudicatedScore") is None:
                    all_errors.append(f"{pair_id}: reviewer difference above 15 requires adjudication")

    if all_errors:
        print(f"Validation FAILED with {len(all_errors)} errors:")
        for err in all_errors[:20]:
            print(f" - {err}")
        sys.exit(1)

    # Write manifest
    manifest = {
        "datasetVersion": "2.0.0",
        "totalPairs": len(pairs),
        "domainDistribution": dict(domain_counts),
        "scenarioDistribution": dict(scenario_counts),
        "splitDistribution": dict(split_counts),
        "reviewStatus": "READY" if pairs and all(pair[1].get("reviewed") for pair in pairs) else "PENDING_HUMAN_REVIEW",
        "scoreRange": {
            "kind": "provisionalSyntheticTargetNotHumanGroundTruth",
            "min": min(p[1]["provisionalScore"] for p in pairs),
            "max": max(p[1]["provisionalScore"] for p in pairs),
            "mean": round(sum(p[1]["provisionalScore"] for p in pairs) / len(pairs), 2),
        },
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("All pairs valid! Manifest generated at:", MANIFEST_PATH)
    print("\nScenario Breakdown:")
    for sc, count in scenario_counts.items():
        print(f"  - {sc:<25}: {count}")
    print("\nDomain Breakdown:")
    for dm, count in domain_counts.items():
        print(f"  - {dm:<25}: {count}")


if __name__ == "__main__":
    main()
