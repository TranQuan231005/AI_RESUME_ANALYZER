import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[3] / "evaluation" / "scripts" / "summarize_llm_reviews.py"
spec = importlib.util.spec_from_file_location("summarize_llm_reviews", SCRIPT)
summary = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(summary)


def review(case_id: str, reviewer_id: str, timestamp: str = "2026-01-01T00:00:00Z"):
    return {
        "case_id": case_id, "reviewer_id": reviewer_id,
        "model_version": "qwen3:4b", "prompt_version": "v1", "timestamp": timestamp,
        **{dimension: "5" for dimension in summary.DIMENSIONS},
    }


def test_review_gate_requires_all_twenty_cases_and_matching_output_metadata():
    outputs = [{"caseId": "case-1", "modelVersion": "qwen3:4b", "promptVersion": "v1", "timestamp": "2026-01-01T00:00:00Z"}]
    rows = [review("case-1", "reviewer-1"), review("case-1", "reviewer-2")]

    errors = summary.review_validation_errors(outputs, rows)

    assert any("exactly 20" in error for error in errors)
    assert not any("case-1: " in error for error in errors)
