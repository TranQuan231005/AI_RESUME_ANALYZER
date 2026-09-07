#!/usr/bin/env python3
"""
AI Resume Analyzer - Classification Dataset Validator
Validates schema, class distributions, leakage, PII, and provenance across splits.

Usage:
    python evaluation/scripts/validate_classification_dataset.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

VALID_LABELS = {
    "Data Science",
    "Web Development",
    "Android Development",
    "iOS Development",
    "UI/UX",
}

VALID_SOURCE_TYPES = {"licensed-public", "manually-authored", "synthetic"}

# Potential PII patterns
REAL_PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)
UNANONYMIZED_EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@(?!example\.(?:com|test|org)|test\.|demo\.)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    samples = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                samples.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON on line {line_num} of {file_path}: {exc}")
    return samples


def validate_sample(sample: Dict[str, Any], file_name: str, index: int, *, allow_unknown: bool = False) -> List[str]:
    errors = []
    prefix = f"[{file_name} #{index}]"

    # Required keys
    required_keys = {"id", "text", "label", "sourceType", "sourceReference", "templateGroup", "reviewed"}
    missing_keys = required_keys - set(sample.keys())
    if missing_keys:
        errors.append(f"{prefix} Missing required keys: {missing_keys}")

    # ID validation
    sample_id = sample.get("id")
    if not isinstance(sample_id, str) or not sample_id.strip():
        errors.append(f"{prefix} 'id' must be a non-empty string")

    # Text validation
    text = sample.get("text")
    if not isinstance(text, str) or len(text.strip()) < 50:
        errors.append(f"{prefix} 'text' must be at least 50 characters long")
    else:
        # PII checks
        if UNANONYMIZED_EMAIL_PATTERN.search(text):
            errors.append(f"{prefix} Potential non-anonymized email detected in text")

    # Label validation
    label = sample.get("label")
    accepted_labels = VALID_LABELS | ({"Unknown"} if allow_unknown else set())
    if label not in accepted_labels:
        errors.append(f"{prefix} Invalid label '{label}'. Must be one of {accepted_labels}")

    # Source type validation
    source_type = sample.get("sourceType")
    if source_type not in VALID_SOURCE_TYPES:
        errors.append(f"{prefix} Invalid sourceType '{source_type}'. Must be one of {VALID_SOURCE_TYPES}")

    # Reviewed validation
    reviewed = sample.get("reviewed")
    if not isinstance(reviewed, bool):
        errors.append(f"{prefix} 'reviewed' must be a boolean")

    return errors


def validate_dataset(dir_path: Path) -> Dict[str, Any]:
    splits = ["train", "validation", "test", "ood-validation", "ood-test"]
    split_samples: Dict[str, List[Dict[str, Any]]] = {}
    all_errors: List[str] = []

    for split in splits:
        split_file = dir_path / f"{split}.jsonl"
        if not split_file.exists():
            all_errors.append(f"Missing split file: {split_file}")
            continue
        try:
            samples = load_jsonl(split_file)
            split_samples[split] = samples
        except Exception as exc:
            all_errors.append(f"Error loading {split_file}: {exc}")

    if all_errors:
        return {"valid": False, "errors": all_errors}

    # Individual sample checks
    all_ids: Dict[str, str] = {}  # id -> split
    text_hashes: Dict[str, str] = {}  # text_hash -> split
    template_groups_by_split: Dict[str, Set[str]] = defaultdict(set)
    stats_by_split: Dict[str, Dict[str, Any]] = {}

    for split, samples in split_samples.items():
        class_counts = Counter()
        source_counts = Counter()

        for idx, sample in enumerate(samples, 1):
            sample_errors = validate_sample(
                sample, f"{split}.jsonl", idx, allow_unknown=split.startswith("ood-")
            )
            all_errors.extend(sample_errors)

            sample_id = sample.get("id")
            if sample_id:
                if sample_id in all_ids:
                    all_errors.append(
                        f"Duplicate sample ID '{sample_id}' found in {split} (first seen in {all_ids[sample_id]})"
                    )
                else:
                    all_ids[sample_id] = split

            # Duplicate text hash check
            text = sample.get("text", "")
            norm_text = re.sub(r"\s+", " ", text.strip().casefold())
            text_hash = hash(norm_text)
            if text_hash in text_hashes:
                all_errors.append(
                    f"Duplicate text content detected for ID '{sample_id}' in {split} (duplicate of sample in {text_hashes[text_hash]})"
                )
            else:
                text_hashes[text_hash] = split

            # Group template check
            group = sample.get("templateGroup")
            if group:
                template_groups_by_split[split].add(group)

            label = sample.get("label")
            if label:
                class_counts[label] += 1
            source_type = sample.get("sourceType")
            if source_type:
                source_counts[source_type] += 1

        stats_by_split[split] = {
            "total_samples": len(samples),
            "class_distribution": dict(class_counts),
            "source_distribution": dict(source_counts),
        }

    # Cross-split Template Group Leakage check
    split_names = list(template_groups_by_split)
    for left_index, left in enumerate(split_names):
        for right in split_names[left_index + 1:]:
            leakage = template_groups_by_split[left] & template_groups_by_split[right]
            if leakage:
                all_errors.append(f"Template group leakage between {left} and {right}: {leakage}")

    # Total counts
    total_samples = sum(len(s) for s in split_samples.values())
    total_by_class = Counter()
    for s in split_samples.values():
        for sample in s:
            total_by_class[sample.get("label")] += 1

    manifest = {
        "version": "2.0.0",
        "randomSeed": 42,
        "classes": sorted(list(VALID_LABELS)),
        "totalSamples": total_samples,
        "classSummary": dict(total_by_class),
        "splitSummary": stats_by_split,
        "validationStatus": "PASSED" if not all_errors else "FAILED",
    }

    return {
        "valid": len(all_errors) == 0,
        "errors": all_errors,
        "manifest": manifest,
    }


def main():
    base_dir = Path(__file__).resolve().parents[1] / "datasets" / "classification"
    result = validate_dataset(base_dir)

    if not result["valid"]:
        print("[FAIL] Dataset validation FAILED with errors:", file=sys.stderr)
        for err in result["errors"]:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    manifest = result["manifest"]
    manifest_path = base_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("[SUCCESS] Classification Dataset Validation Passed!")
    print(f"Total Samples: {manifest['totalSamples']}")
    for cls_name, count in manifest["classSummary"].items():
        print(f"   - {cls_name}: {count} samples")
    print(f"Manifest updated at: {manifest_path}")


if __name__ == "__main__":
    main()
