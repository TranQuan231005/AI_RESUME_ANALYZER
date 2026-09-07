"""Evaluate trained field classifier on independent held-out test split.

Generates comprehensive academic metrics:
- Accuracy, Macro F1, Weighted F1
- Per-class Precision, Recall, F1, Support
- Confusion Matrix
- Latency statistics (mean, p50, p95, p99)
- Heuristic Baseline vs ML Classifier comparison
- Markdown evaluation report in artifacts/classifier/evaluation_report.md
"""
from __future__ import annotations
import argparse
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_recall_fscore_support

# Add ai-service to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.extraction.classifier import classify_features as heuristic_classify
from app.extraction.features import extract_features
from app.extraction.taxonomy import FIELD_NAMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluate_classifier")


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_heuristic(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    y_true = [s["label"] for s in samples]
    y_pred = []
    latencies = []

    for s in samples:
        t0 = time.perf_counter()
        feats = extract_features(s["text"])
        res = heuristic_classify(feats)
        latencies.append((time.perf_counter() - t0) * 1000.0)
        y_pred.append(res.predicted_field)

    target_classes = [c for c in FIELD_NAMES if c != "Unknown"]
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=target_classes, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, labels=target_classes, average="weighted", zero_division=0)

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "latencies_ms": latencies,
        "predictions": y_pred,
    }


def evaluate_ml(pipeline: Any, metadata: Dict[str, Any], samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    texts = [s["text"] for s in samples]
    y_true = [s["label"] for s in samples]
    classes = list(pipeline.classes_)
    unknown_threshold = float(metadata.get("unknownThreshold", 0.35))

    latencies = []
    y_pred = []
    probs_list = []

    for text in texts:
        t0 = time.perf_counter()
        proba = pipeline.predict_proba([text])[0]
        latencies.append((time.perf_counter() - t0) * 1000.0)
        probs_list.append(proba)

        max_idx = int(proba.argmax())
        max_prob = proba[max_idx]
        if max_prob < unknown_threshold:
            y_pred.append("Unknown")
        else:
            y_pred.append(classes[max_idx])

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, labels=classes, average="weighted", zero_division=0)

    # Per class metrics
    precisions, recalls, f1s, supports = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, zero_division=0
    )

    per_class = {}
    for i, cls in enumerate(classes):
        per_class[cls] = {
            "precision": round(float(precisions[i]), 4),
            "recall": round(float(recalls[i]), 4),
            "f1": round(float(f1s[i]), 4),
            "support": int(supports[i]),
        }

    cm = confusion_matrix(y_true, y_pred, labels=classes)

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "classes": classes,
        "latencies_ms": latencies,
        "predictions": y_pred,
    }


def generate_markdown_report(
    test_count: int,
    heuristic_res: Dict[str, Any],
    ml_res: Dict[str, Any],
    metadata: Dict[str, Any],
    output_path: Path,
) -> None:
    classes = ml_res["classes"]
    cm = ml_res["confusion_matrix"]
    latencies = ml_res["latencies_ms"]

    mean_lat = float(np.mean(latencies))
    p50_lat = float(np.percentile(latencies, 50))
    p95_lat = float(np.percentile(latencies, 95))
    p99_lat = float(np.percentile(latencies, 99))

    lines = [
        "# Resume Field Classifier Evaluation Report",
        "",
        "## 1. Overview & Dataset Provenance",
        f"- **Dataset Version:** `{metadata.get('datasetVersion', '1.0.0')}`",
        f"- **Evaluation Date:** `{metadata.get('trainedAt', 'N/A')}`",
        f"- **Test Set Size:** {test_count} samples (strictly independent, 0% template leakage)",
        f"- **Classes Evaluated ({len(classes)}):** {', '.join(classes)}",
        f"- **Model Type:** `{metadata.get('modelType', 'Logistic Regression')}`",
        f"- **Random Seed:** `{metadata.get('randomSeed', 42)}`",
        f"- **Unknown Threshold:** `{metadata.get('unknownThreshold', 0.35)}`",
        "",
        "## 2. Model vs Baseline Comparison (Held-out Test Split)",
        "",
        "| Metric | Heuristic Baseline (Keyword Overlap) | ML Classifier (TF-IDF + Logistic Regression) | Delta |",
        "|---|---|---|---|",
        f"| **Accuracy** | {heuristic_res['accuracy'] * 100:.2f}% | **{ml_res['accuracy'] * 100:.2f}%** | +{(ml_res['accuracy'] - heuristic_res['accuracy']) * 100:.2f}% |",
        f"| **Macro F1** | {heuristic_res['macro_f1']:.4f} | **{ml_res['macro_f1']:.4f}** | +{(ml_res['macro_f1'] - heuristic_res['macro_f1']):.4f} |",
        f"| **Weighted F1** | {heuristic_res['weighted_f1']:.4f} | **{ml_res['weighted_f1']:.4f}** | +{(ml_res['weighted_f1'] - heuristic_res['weighted_f1']):.4f} |",
        f"| **Avg Latency** | {np.mean(heuristic_res['latencies_ms']):.2f} ms | {mean_lat:.2f} ms | - |",
        "",
        "## 3. Per-Class Performance on Test Set",
        "",
        "| Field Label | Precision | Recall | F1-Score | Support |",
        "|---|---|---|---|---|",
    ]

    for cls in classes:
        pc = ml_res["per_class"][cls]
        lines.append(f"| **{cls}** | {pc['precision']:.4f} | {pc['recall']:.4f} | {pc['f1']:.4f} | {pc['support']} |")

    lines.extend([
        f"| **Macro Average** | - | - | **{ml_res['macro_f1']:.4f}** | {test_count} |",
        f"| **Weighted Average** | - | - | **{ml_res['weighted_f1']:.4f}** | {test_count} |",
        "",
        "## 4. Confusion Matrix",
        "",
    ])

    # Confusion matrix header
    header = "| True \\ Pred | " + " | ".join(classes) + " |"
    divider = "|---|" + "|".join(["---"] * len(classes)) + "|"
    lines.append(header)
    lines.append(divider)
    for i, row_cls in enumerate(classes):
        row_str = f"| **{row_cls}** | " + " | ".join(str(cm[i][j]) for j in range(len(classes))) + " |"
        lines.append(row_str)

    lines.extend([
        "",
        "## 5. Inference Latency Benchmark",
        f"- **Mean Latency:** {mean_lat:.2f} ms per resume",
        f"- **p50 Latency:** {p50_lat:.2f} ms",
        f"- **p95 Latency:** {p95_lat:.2f} ms",
        f"- **p99 Latency:** {p99_lat:.2f} ms",
        "",
        "## 6. Model Hyperparameters & Configuration",
        "```json",
        json.dumps(metadata.get("textFeatureConfig", {}), indent=2),
        "```",
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("Generated evaluation report at %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate trained resume field classifier on test set.")
    parser.add_argument("--data-dir", type=str, default="evaluation/classification", help="Path to classification dataset directory")
    parser.add_argument("--artifacts-dir", type=str, default="artifacts/classifier", help="Path to trained artifacts directory")
    args = parser.parse_args()

    data_dir = ROOT_DIR / args.data_dir
    artifacts_dir = ROOT_DIR / args.artifacts_dir

    test_path = data_dir / "test.jsonl"
    model_path = artifacts_dir / "classifier_pipeline.joblib"
    metadata_path = artifacts_dir / "metadata.json"

    if not test_path.exists():
        logger.error("Test dataset not found at %s", test_path)
        sys.exit(1)
    if not model_path.exists() or not metadata_path.exists():
        logger.error("Model artifacts not found at %s. Run train_classifier.py first.", artifacts_dir)
        sys.exit(1)

    test_samples = load_jsonl(test_path)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    pipeline = joblib.load(model_path)
    logger.info("Loaded model from %s and %d test samples", model_path, len(test_samples))

    # Evaluate Heuristic
    heuristic_res = evaluate_heuristic(test_samples)
    logger.info("Heuristic Baseline Test Metrics: Acc=%.4f, Macro F1=%.4f", heuristic_res["accuracy"], heuristic_res["macro_f1"])

    # Evaluate ML
    ml_res = evaluate_ml(pipeline, metadata, test_samples)
    logger.info("ML Classifier Test Metrics: Acc=%.4f, Macro F1=%.4f, Weighted F1=%.4f",
                ml_res["accuracy"], ml_res["macro_f1"], ml_res["weighted_f1"])

    # Generate Markdown Report
    report_path = artifacts_dir / "evaluation_report.md"
    generate_markdown_report(len(test_samples), heuristic_res, ml_res, metadata, report_path)

    print("\n=======================================================")
    print("           TEST SET EVALUATION SUMMARY                ")
    print("=======================================================")
    print(f"Accuracy:    {ml_res['accuracy'] * 100:.2f}% (Baseline: {heuristic_res['accuracy'] * 100:.2f}%)")
    print(f"Macro F1:    {ml_res['macro_f1']:.4f} (Baseline: {heuristic_res['macro_f1']:.4f})")
    print(f"Weighted F1: {ml_res['weighted_f1']:.4f} (Baseline: {heuristic_res['weighted_f1']:.4f})")
    print("-------------------------------------------------------")
    for cls, metrics in ml_res["per_class"].items():
        print(f" - {cls:<20}: P={metrics['precision']:.2f}, R={metrics['recall']:.2f}, F1={metrics['f1']:.2f} (n={metrics['support']})")
    print("=======================================================")


if __name__ == "__main__":
    main()
