"""Compute LLM quality metrics from two-reviewer CSV; never invent manual scores."""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

DIMENSIONS = [
    "relevance_1_to_5", "actionability_1_to_5", "faithfulness_1_to_5",
    "skill_anti_overlap_1_to_5", "injection_defense_1_to_5", "schema_compliance_1_to_5",
]


def review_validation_errors(live_outputs: list[dict], rows: list[dict[str, str]]) -> list[str]:
    """Validate human review evidence before publishing any live-model metric."""
    errors: list[str] = []
    live_by_id: dict[str, dict] = {}
    for output in live_outputs:
        case_id = output.get("caseId")
        if not isinstance(case_id, str) or not case_id or case_id in live_by_id:
            errors.append("live outputs must have unique non-empty caseId values")
            continue
        if not all(isinstance(output.get(field), str) and output[field] for field in ("modelVersion", "promptVersion", "timestamp")):
            errors.append(f"{case_id}: live output is missing model/prompt/timestamp metadata")
        live_by_id[case_id] = output
    if len(live_by_id) != 20:
        errors.append(f"live output must contain exactly 20 cases; found {len(live_by_id)}")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        case_id = row.get("case_id", "")
        if case_id not in live_by_id:
            errors.append(f"{case_id or 'blank'}: review refers to an unknown live-output case")
            continue
        grouped[case_id].append(row)
    for case_id, output in live_by_id.items():
        case_rows = grouped[case_id]
        if len(case_rows) != 2:
            errors.append(f"{case_id}: exactly two reviews are required")
            continue
        reviewers = [row.get("reviewer_id", "").strip() for row in case_rows]
        if any(not reviewer for reviewer in reviewers) or len(set(reviewers)) != 2:
            errors.append(f"{case_id}: two distinct reviewer IDs are required")
        for row in case_rows:
            if (row.get("model_version") != output.get("modelVersion")
                    or row.get("prompt_version") != output.get("promptVersion")
                    or row.get("timestamp") != output.get("timestamp")):
                errors.append(f"{case_id}: review metadata must match the saved live output")
            if any(not row.get(dimension, "").isdigit() or not 1 <= int(row[dimension]) <= 5 for dimension in DIMENSIONS):
                errors.append(f"{case_id}: every dimension must be an integer from 1 to 5")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", required=True)
    parser.add_argument("--live-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()
    live_outputs = [
        json.loads(line)
        for line in Path(args.live_output).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    live_ids = {output.get("caseId") for output in live_outputs}
    rows = list(csv.DictReader(Path(args.reviews).open(encoding="utf-8")))
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["case_id"]].append(row)
    validation_errors = review_validation_errors(live_outputs, rows)
    valid = not validation_errors
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not valid:
        detail = validation_errors[0] if validation_errors else "two independent reviews are required"
        output.write_text(f"# LLM Evaluation\n\n**PENDING HUMAN REVIEW**\n\n{detail}\n", encoding="utf-8")
        if not args.allow_pending:
            raise SystemExit(2)
        return
    averages = {
        dimension: sum(int(row[dimension]) for case_id in live_ids for row in grouped[case_id]) / (2 * len(live_ids))
        for dimension in DIMENSIONS
    }
    table = "\n".join(f"| {name} | {value:.2f}/5 |" for name, value in averages.items())
    output.write_text(
        f"# LLM Live Quality Evaluation\n\n{len(live_ids)} saved Qwen outputs, each reviewed by two independent reviewers.\n\n| Dimension | Mean |\n|---|---:|\n{table}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
