"""Import two independent matching-review CSV files into the benchmark."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
PAIRS_PATH = ROOT / "evaluation" / "datasets" / "matching" / "pairs.jsonl"


def read_scores(path: Path) -> dict[str, int]:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    scores: dict[str, int] = {}
    for row in rows:
        pair_id = row.get("pair_id", "")
        value = row.get("score_0_to_100", "")
        if not pair_id or not value.isdigit() or not 0 <= int(value) <= 100 or pair_id in scores:
            raise ValueError(f"Invalid or duplicate review row in {path.name}: {pair_id!r}")
        scores[pair_id] = int(value)
    return scores


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-1", required=True, type=Path)
    parser.add_argument("--reviewer-2", required=True, type=Path)
    parser.add_argument("--adjudication", action="append", default=[], metavar="PAIR_ID:SCORE")
    args = parser.parse_args()
    first, second = read_scores(args.reviewer_1), read_scores(args.reviewer_2)
    pairs = [json.loads(line) for line in PAIRS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    pair_ids = {pair["id"] for pair in pairs}
    if set(first) != pair_ids or set(second) != pair_ids:
        raise SystemExit("Review CSV pair IDs must exactly match the 70 benchmark pair IDs.")
    adjudications: dict[str, int] = {}
    for item in args.adjudication:
        pair_id, separator, raw_score = item.partition(":")
        if not separator or pair_id not in pair_ids or not raw_score.isdigit() or not 0 <= int(raw_score) <= 100:
            raise SystemExit(f"Invalid adjudication: {item!r}")
        adjudications[pair_id] = int(raw_score)
    for pair in pairs:
        score_1, score_2 = first[pair["id"]], second[pair["id"]]
        if abs(score_1 - score_2) > 15 and pair["id"] not in adjudications:
            raise SystemExit(f"Missing adjudication for {pair['id']}")
        pair["reviewed"] = True
        pair["reviewerScores"] = [{"reviewerId": "reviewer-1", "score": score_1}, {"reviewerId": "reviewer-2", "score": score_2}]
        pair["adjudicatedScore"] = adjudications.get(pair["id"])
    PAIRS_PATH.write_text("".join(json.dumps(pair, ensure_ascii=False) + "\n" for pair in pairs), encoding="utf-8")
    evidence_dir = ROOT / "evaluation" / "reviews"
    evidence_dir.mkdir(exist_ok=True)
    shutil.copy2(args.reviewer_1, evidence_dir / "matching-reviewer-1.csv")
    shutil.copy2(args.reviewer_2, evidence_dir / "matching-reviewer-2.csv")
    print(f"Imported {len(pairs)} pairs with {len(adjudications)} adjudication(s).")


if __name__ == "__main__":
    main()
