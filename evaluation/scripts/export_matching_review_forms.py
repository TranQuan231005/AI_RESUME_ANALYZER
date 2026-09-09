"""Export blinded, independent CSV forms for matching human reviewers."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAIRS = ROOT / "evaluation" / "datasets" / "matching" / "pairs.jsonl"
REVIEW_DIR = ROOT / "evaluation" / "reviews"
REVIEWERS = ("reviewer-1", "reviewer-2")


def main() -> None:
    pairs = [json.loads(line) for line in PAIRS.read_text(encoding="utf-8").splitlines() if line.strip()]
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for reviewer_id in REVIEWERS:
        path = REVIEW_DIR / f"matching-{reviewer_id}.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=("pair_id", "target_role", "resume_text", "job_description", "score_0_to_100", "reviewer_notes"),
            )
            writer.writeheader()
            for pair in pairs:
                writer.writerow({
                    "pair_id": pair["id"],
                    "target_role": pair["targetRole"],
                    "resume_text": pair["resumeText"],
                    "job_description": pair["jdText"],
                    "score_0_to_100": "",
                    "reviewer_notes": "",
                })
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
