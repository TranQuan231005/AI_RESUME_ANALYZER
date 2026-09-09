"""Regression tests for human-review gates used by matching evaluation."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "evaluation" / "scripts" / "evaluate_matching.py"
SPEC = importlib.util.spec_from_file_location("evaluate_matching", SCRIPT_PATH)
assert SPEC and SPEC.loader
evaluate_matching = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate_matching)


def reviewed_pair(**overrides):
    pair = {
        "id": "pair-test-01",
        "reviewed": True,
        "reviewerScores": [
            {"reviewerId": "reviewer-1", "score": 60},
            {"reviewerId": "reviewer-2", "score": 65},
        ],
        "adjudicatedScore": None,
        "split": "calibration",
    }
    pair.update(overrides)
    return pair


def test_review_gate_rejects_reviewed_record_with_one_reviewer():
    errors = evaluate_matching.review_validation_errors(
        [reviewed_pair(reviewerScores=[{"reviewerId": "reviewer-1", "score": 60}])]
    )

    assert errors == ["pair-test-01: exactly two reviewer scores are required"]


def test_review_gate_requires_adjudication_for_large_disagreement():
    errors = evaluate_matching.review_validation_errors(
        [reviewed_pair(reviewerScores=[
            {"reviewerId": "reviewer-1", "score": 20},
            {"reviewerId": "reviewer-2", "score": 80},
        ])]
    )

    assert errors == ["pair-test-01: disagreement above 15 requires an adjudicated score"]


def test_review_gate_accepts_two_distinct_integer_scores_with_adjudication():
    errors = evaluate_matching.review_validation_errors(
        [reviewed_pair(
            reviewerScores=[
                {"reviewerId": "reviewer-1", "score": 20},
                {"reviewerId": "reviewer-2", "score": 80},
            ],
            adjudicatedScore=50,
        )]
    )

    assert errors == []
