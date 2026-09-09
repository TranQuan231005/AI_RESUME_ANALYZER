"""Calibrate and evaluate the production CV-JD matcher on reviewed benchmark pairs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import time
from typing import Any

import numpy as np
from scipy.stats import spearmanr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.extraction.taxonomy import find_skills
from app.matching.embedding import load_embedding_model
from app.matching.engine import match_resume_to_job, match_skills, extract_jd_skills


def load_pairs(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def review_validation_errors(pairs: list[dict[str, Any]]) -> list[str]:
    """Return review-gate failures without calculating any human-quality metric."""
    errors: list[str] = []
    for pair in pairs:
        pair_id = str(pair.get("id", "unknown-pair"))
        if pair.get("reviewed") is not True:
            errors.append(f"{pair_id}: two-reviewer approval is required")
            continue

        scores = pair.get("reviewerScores")
        if not isinstance(scores, list) or len(scores) != 2:
            errors.append(f"{pair_id}: exactly two reviewer scores are required")
            continue

        reviewer_ids = [item.get("reviewerId") for item in scores if isinstance(item, dict)]
        values = [item.get("score") for item in scores if isinstance(item, dict)]
        if (
            len(reviewer_ids) != 2
            or any(not isinstance(reviewer_id, str) or not reviewer_id.strip() for reviewer_id in reviewer_ids)
            or len(set(reviewer_ids)) != 2
        ):
            errors.append(f"{pair_id}: two distinct reviewer IDs are required")
            continue
        if any(type(value) is not int or not 0 <= value <= 100 for value in values):
            errors.append(f"{pair_id}: reviewer scores must be integers from 0 to 100")
            continue

        adjudicated = pair.get("adjudicatedScore")
        if adjudicated is not None and (type(adjudicated) is not int or not 0 <= adjudicated <= 100):
            errors.append(f"{pair_id}: adjudicated score must be an integer from 0 to 100")
            continue
        if abs(values[0] - values[1]) > 15 and adjudicated is None:
            errors.append(f"{pair_id}: disagreement above 15 requires an adjudicated score")
    return errors


def human_score(pair: dict[str, Any]) -> float:
    adjudicated = pair.get("adjudicatedScore")
    if adjudicated is not None:
        return float(adjudicated)
    scores = pair.get("reviewerScores", [])
    return sum(float(item["score"]) for item in scores) / len(scores)


def tfidf_baseline(resume_text: str, jd_text: str) -> float:
    matrix = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2)).fit_transform(
        [resume_text, jd_text]
    )
    return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0] * 100.0)


def config_for_alpha(alpha: float, directory: Path) -> Path:
    path = directory / f"matching-{alpha:.2f}.json"
    path.write_text(json.dumps({
        "skillWeight": alpha,
        "semanticWeight": 1.0 - alpha,
        "embeddingModel": "sentence-transformers/all-MiniLM-L6-v2",
    }), encoding="utf-8")
    return path


def production_predictions(pairs: list[dict[str, Any]], alpha: float, model: Any, temp_dir: Path):
    config_path = config_for_alpha(alpha, temp_dir)
    predictions, latencies = [], []
    for pair in pairs:
        started = time.perf_counter()
        result = match_resume_to_job(
            file_name=f"{pair['id']}.pdf",
            resume_skills=find_skills(pair["resumeText"]),
            resume_text=pair["resumeText"],
            job_description=pair["jdText"],
            target_role=pair["targetRole"],
            config_path=config_path,
            embedding_model=model,
        )
        latencies.append((time.perf_counter() - started) * 1000.0)
        if result.match_breakdown.method != "HYBRID_EMBEDDING":
            raise RuntimeError("Production matcher did not load the required embedding model")
        predictions.append(result.match_score)
    return np.asarray(predictions), latencies


def mae(predictions: np.ndarray, truth: np.ndarray) -> float:
    return float(np.mean(np.abs(predictions - truth)))


def select_alpha(calibration: list[dict[str, Any]], model: Any, temp_dir: Path) -> float:
    truth = np.asarray([human_score(pair) for pair in calibration])
    candidates = []
    for alpha in np.arange(0.0, 1.001, 0.05):
        predictions, _ = production_predictions(calibration, round(float(alpha), 2), model, temp_dir)
        candidates.append((mae(predictions, truth), round(float(alpha), 2)))
    return min(candidates)[1]


def evaluate(test_pairs: list[dict[str, Any]], alpha: float, model: Any, temp_dir: Path) -> dict[str, Any]:
    truth = np.asarray([human_score(pair) for pair in test_pairs])
    production, latencies = production_predictions(test_pairs, alpha, model, temp_dir)
    skill = np.asarray([
        match_skills(find_skills(pair["resumeText"]), extract_jd_skills(pair["jdText"])).match_score
        for pair in test_pairs
    ])
    tfidf = np.asarray([tfidf_baseline(pair["resumeText"], pair["jdText"]) for pair in test_pairs])
    scenarios = {}
    for scenario in sorted({pair["scenarioType"] for pair in test_pairs}):
        indexes = [index for index, pair in enumerate(test_pairs) if pair["scenarioType"] == scenario]
        scenarios[scenario] = round(mae(production[indexes], truth[indexes]), 2)
    return {
        "alpha": alpha,
        "testCount": len(test_pairs),
        "productionMae": round(mae(production, truth), 2),
        "productionSpearman": round(float(spearmanr(production, truth).statistic), 4),
        "skillBaselineMae": round(mae(skill, truth), 2),
        "tfidfBaselineMae": round(mae(tfidf, truth), 2),
        "latencyP50Ms": round(float(np.percentile(latencies, 50)), 2),
        "latencyP95Ms": round(float(np.percentile(latencies, 95)), 2),
        "scenarioMae": scenarios,
    }


def write_report(path: Path, result: dict[str, Any] | None, pending_reason: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if result is None:
        text = "# CV–JD Matching Evaluation\n\n**PENDING HUMAN REVIEW**\n\n" + (pending_reason or "Two independent reviewer scores are required for every pair.") + "\n"
    else:
        scenario_rows = "\n".join(f"| {name} | {value:.2f} |" for name, value in result["scenarioMae"].items())
        text = f"""# CV–JD Matching Evaluation

Calibration and held-out test pairs are separated by template group. TF-IDF is reported only as a lexical baseline; production calls the packaged sentence-embedding matcher directly.

- Calibrated skill weight: `{result['alpha']:.2f}`
- Held-out pairs: {result['testCount']}
- Production MAE: {result['productionMae']:.2f}
- Production Spearman rho: {result['productionSpearman']:.4f}
- Skill-only baseline MAE: {result['skillBaselineMae']:.2f}
- TF-IDF lexical baseline MAE: {result['tfidfBaselineMae']:.2f}
- Latency p50/p95: {result['latencyP50Ms']:.2f}/{result['latencyP95Ms']:.2f} ms

| Scenario | Production MAE |
|---|---:|
{scenario_rows}
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", default="evaluation/datasets/matching/pairs.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--allow-pending", action="store_true")
    args = parser.parse_args()
    pairs = load_pairs(ROOT_DIR / args.data_path)
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT_DIR / output
    review_errors = review_validation_errors(pairs)
    if review_errors:
        approved_count = sum(not review_validation_errors([pair]) for pair in pairs)
        reason = (
            f"Only {approved_count}/{len(pairs)} pairs have valid two-reviewer approval; "
            f"no quality metrics were calculated. First issue: {review_errors[0]}"
        )
        write_report(output, None, reason)
        if not args.allow_pending:
            raise SystemExit(2)
        return
    model = load_embedding_model()
    if model is None:
        write_report(output, None, "The pinned embedding model is not installed locally; no production metrics were calculated.")
        if not args.allow_pending:
            raise SystemExit(2)
        return
    calibration = [pair for pair in pairs if pair["split"] == "calibration"]
    test_pairs = [pair for pair in pairs if pair["split"] == "test"]
    with tempfile.TemporaryDirectory(prefix="matching-evaluation-") as temp:
        temp_dir = Path(temp)
        alpha = select_alpha(calibration, model, temp_dir)
        result = evaluate(test_pairs, alpha, model, temp_dir)
    write_report(output, result)


if __name__ == "__main__":
    main()
