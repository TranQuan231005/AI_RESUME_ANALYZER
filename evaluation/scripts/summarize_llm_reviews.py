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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviews", required=True)
    parser.add_argument("--live-output", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()
    live_ids = {
        json.loads(line)["caseId"]
        for line in Path(args.live_output).read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    rows = list(csv.DictReader(Path(args.reviews).open(encoding="utf-8")))
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["case_id"]].append(row)
    valid = bool(live_ids) and all(
        len(grouped[case_id]) == 2
        and len({row["reviewer_id"] for row in grouped[case_id]}) == 2
        and all(row["model_version"] and row["prompt_version"] and row["timestamp"] for row in grouped[case_id])
        and all(row[dimension].isdigit() and 1 <= int(row[dimension]) <= 5 for row in grouped[case_id] for dimension in DIMENSIONS)
        for case_id in live_ids
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not valid:
        output.write_text("# LLM Evaluation\n\n**PENDING HUMAN REVIEW**\n", encoding="utf-8")
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
