"""Combine two independently exported LLM review CSV files."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reviewer-1", required=True, type=Path)
    parser.add_argument("--reviewer-2", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    headers_1, rows_1 = read_rows(args.reviewer_1)
    headers_2, rows_2 = read_rows(args.reviewer_2)
    if headers_1 != headers_2:
        raise SystemExit("Review CSV headers differ")
    if {row.get("reviewer_id") for row in rows_1} != {"reviewer-1"}:
        raise SystemExit("First CSV must contain only reviewer-1")
    if {row.get("reviewer_id") for row in rows_2} != {"reviewer-2"}:
        raise SystemExit("Second CSV must contain only reviewer-2")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers_1)
        writer.writeheader()
        writer.writerows(rows_1 + rows_2)
    print(f"Wrote {len(rows_1) + len(rows_2)} reviews to {args.output}")


if __name__ == "__main__":
    main()
