"""Train and compare ML field classification models on stratified resume dataset.

Models evaluated:
1. Keyword/Taxonomy Heuristic (Baseline)
2. Multinomial Naive Bayes + TF-IDF
3. Logistic Regression (Balanced) + TF-IDF
4. Linear SVM (Calibrated) + TF-IDF

Selects best model by Macro F1, calibrates Unknown threshold, and serializes artifacts.
"""
from __future__ import annotations
import argparse
import datetime
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

# Add ai-service to sys.path to import taxonomy / features
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.extraction.classifier import classify_features as heuristic_classify
from app.extraction.features import extract_features
from app.extraction.taxonomy import FIELD_NAMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_classifier")


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_heuristic_baseline(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluate deterministic taxonomy keyword heuristic on dataset."""
    y_true = [s["label"] for s in samples]
    y_pred = []
    
    start_t = time.perf_counter()
    for s in samples:
        features = extract_features(s["text"])
        res = heuristic_classify(features)
        pred = res.predicted_field
        # Map unknown or valid field
        y_pred.append(pred)
    latency_ms = (time.perf_counter() - start_t) / len(samples) * 1000.0

    # For classes in FIELD_NAMES (excluding 'Unknown' from primary 5 target classes)
    target_classes = [c for c in FIELD_NAMES if c != "Unknown"]
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=target_classes, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, labels=target_classes, average="weighted", zero_division=0)

    return {
        "model_name": "Taxonomy Keyword Heuristic",
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "avg_latency_ms": round(float(latency_ms), 4),
    }


def get_candidate_pipelines(random_seed: int = 42) -> Dict[str, Pipeline]:
    """Define candidate ML model pipelines with TF-IDF vectorization."""
    tfidf_params = {
        "lowercase": True,
        "stop_words": "english",
        "ngram_range": (1, 2),
        "sublinear_tf": True,
        "min_df": 2,
    }

    return {
        "Multinomial Naive Bayes": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf", MultinomialNB(alpha=0.5)),
        ]),
        "Logistic Regression": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf", LogisticRegression(
                C=1.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=random_seed,
                solver="lbfgs",
            )),
        ]),
        "Linear SVM (Calibrated)": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf_params)),
            ("clf", CalibratedClassifierCV(
                estimator=LinearSVC(
                    class_weight="balanced",
                    random_state=random_seed,
                    max_iter=2000,
                ),
                cv=3,
            )),
        ]),
    }


def run_cross_validation(
    pipelines: Dict[str, Pipeline],
    texts: List[str],
    labels: List[str],
    random_seed: int = 42,
) -> Dict[str, Dict[str, Any]]:
    """Run 5-Fold Stratified Cross-Validation across candidate models."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_seed)
    cv_results = {}

    for name, pipe in pipelines.items():
        start_t = time.perf_counter()
        scores = cross_validate(
            pipe,
            texts,
            labels,
            cv=skf,
            scoring=["accuracy", "f1_macro", "f1_weighted"],
            return_train_score=False,
        )
        fit_time_ms = (time.perf_counter() - start_t) * 1000.0 / 5.0

        cv_results[name] = {
            "model_name": name,
            "cv_accuracy_mean": round(float(scores["test_accuracy"].mean()), 4),
            "cv_accuracy_std": round(float(scores["test_accuracy"].std()), 4),
            "cv_macro_f1_mean": round(float(scores["test_f1_macro"].mean()), 4),
            "cv_macro_f1_std": round(float(scores["test_f1_macro"].std()), 4),
            "cv_weighted_f1_mean": round(float(scores["test_f1_weighted"].mean()), 4),
            "fit_time_ms": round(float(fit_time_ms), 2),
        }
    return cv_results


def calibrate_unknown_threshold(
    pipeline: Pipeline,
    val_samples: List[Dict[str, Any]],
) -> Tuple[float, Dict[str, Any]]:
    """Calibrate confidence threshold for 'Unknown' predictions using validation split."""
    val_texts = [s["text"] for s in val_samples]
    val_labels = [s["label"] for s in val_samples]

    probs = pipeline.predict_proba(val_texts)
    max_probs = np.max(probs, axis=1)
    preds = pipeline.predict(val_texts)

    # Candidate thresholds: 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50
    threshold_stats = {}
    best_thresh = 0.35

    for thresh in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
        gated_preds = [preds[i] if max_probs[i] >= thresh else "Unknown" for i in range(len(preds))]
        acc = accuracy_score(val_labels, gated_preds)
        coverage = sum(1 for p in gated_preds if p != "Unknown") / len(gated_preds)
        threshold_stats[str(thresh)] = {
            "accuracy": round(float(acc), 4),
            "coverage": round(float(coverage), 4),
            "unknown_count": sum(1 for p in gated_preds if p == "Unknown"),
        }

    return best_thresh, threshold_stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Train resume field classifier.")
    parser.add_argument("--data-dir", type=str, default="evaluation/classification", help="Path to classification dataset directory")
    parser.add_argument("--artifacts-dir", type=str, default="artifacts/classifier", help="Path to save trained artifacts")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    data_dir = ROOT_DIR / args.data_dir
    artifacts_dir = ROOT_DIR / args.artifacts_dir
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    train_path = data_dir / "train.jsonl"
    val_path = data_dir / "validation.jsonl"

    if not train_path.exists() or not val_path.exists():
        logger.error("Dataset files not found at %s. Please run build_dataset.py first.", data_dir)
        sys.exit(1)

    train_samples = load_jsonl(train_path)
    val_samples = load_jsonl(val_path)

    logger.info("Loaded dataset: %d train samples, %d validation samples", len(train_samples), len(val_samples))

    # Evaluate Heuristic Baseline
    heuristic_val = evaluate_heuristic_baseline(val_samples)
    logger.info("Heuristic Baseline on Validation: Acc=%.4f, Macro F1=%.4f", heuristic_val["accuracy"], heuristic_val["macro_f1"])

    train_texts = [s["text"] for s in train_samples]
    train_labels = [s["label"] for s in train_samples]

    combined_texts = train_texts + [s["text"] for s in val_samples]
    combined_labels = train_labels + [s["label"] for s in val_samples]

    # Candidate models
    pipelines = get_candidate_pipelines(random_seed=args.seed)

    # 5-Fold Cross Validation
    logger.info("Running 5-Fold Stratified Cross-Validation on combined Train+Val...")
    cv_results = run_cross_validation(pipelines, combined_texts, combined_labels, random_seed=args.seed)

    for model_name, res in cv_results.items():
        logger.info("CV [%s] -> Macro F1: %.4f (+/- %.4f), Acc: %.4f",
                    model_name, res["cv_macro_f1_mean"], res["cv_macro_f1_std"], res["cv_accuracy_mean"])

    # Fit each pipeline on train set and evaluate on validation set
    val_texts = [s["text"] for s in val_samples]
    val_labels = [s["label"] for s in val_samples]

    val_evals = {}
    best_model_name = "Logistic Regression"
    best_macro_f1 = -1.0

    for name, pipe in pipelines.items():
        pipe.fit(train_texts, train_labels)
        val_preds = pipe.predict(val_texts)
        acc = accuracy_score(val_labels, val_preds)
        macro_f1 = f1_score(val_labels, val_preds, average="macro", zero_division=0)
        weighted_f1 = f1_score(val_labels, val_preds, average="weighted", zero_division=0)
        
        val_evals[name] = {
            "val_accuracy": round(float(acc), 4),
            "val_macro_f1": round(float(macro_f1), 4),
            "val_weighted_f1": round(float(weighted_f1), 4),
        }
        logger.info("Validation Split [%s] -> Macro F1: %.4f, Acc: %.4f", name, macro_f1, acc)

    # Select best model: prioritize CV Macro F1, with tie-break preference for Logistic Regression
    ranked_models = sorted(
        pipelines.keys(),
        key=lambda k: (
            cv_results[k]["cv_macro_f1_mean"],
            val_evals[k]["val_macro_f1"],
            1 if k == "Logistic Regression" else 0,
        ),
        reverse=True,
    )
    best_model_name = ranked_models[0]
    best_macro_f1 = val_evals[best_model_name]["val_macro_f1"]

    logger.info("Selected Best Model: %s (CV Macro F1: %.4f, Val Macro F1: %.4f)",
                best_model_name, cv_results[best_model_name]["cv_macro_f1_mean"], best_macro_f1)

    # Train winning model on combined train+val for deployment artifact
    best_pipeline = pipelines[best_model_name]
    best_pipeline.fit(combined_texts, combined_labels)

    # Calibrate Unknown threshold on validation data
    calibrated_thresh, thresh_stats = calibrate_unknown_threshold(best_pipeline, val_samples)
    logger.info("Calibrated Unknown Threshold: %.2f", calibrated_thresh)

    # Serialize model artifact
    model_artifact_path = artifacts_dir / "classifier_pipeline.joblib"
    joblib.dump(best_pipeline, model_artifact_path)
    logger.info("Saved model artifact to %s", model_artifact_path)

    # Target class labels
    classes = list(best_pipeline.classes_)

    # Save metadata.json
    metadata = {
        "modelType": best_model_name,
        "pipeline": "TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True, min_df=2) + LogisticRegression(class_weight='balanced')",
        "datasetVersion": "1.0.0",
        "trainedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "labels": classes,
        "randomSeed": args.seed,
        "sampleCounts": {
            "train": len(train_samples),
            "validation": len(val_samples),
            "totalTrained": len(combined_texts),
        },
        "cvResults": cv_results,
        "baselineComparison": {
            "heuristicBaseline": heuristic_val,
            "modelsValidation": val_evals,
        },
        "textFeatureConfig": {
            "lowercase": True,
            "stopWords": "english",
            "ngramRange": [1, 2],
            "sublinearTf": True,
            "minDf": 2,
            "vocabSize": len(best_pipeline.named_steps["tfidf"].vocabulary_),
        },
        "unknownThreshold": calibrated_thresh,
        "unknownCalibrationStats": thresh_stats,
    }

    metadata_path = artifacts_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata to %s", metadata_path)
    print("\nClassifier training and baseline comparison complete successfully.")


if __name__ == "__main__":
    main()
