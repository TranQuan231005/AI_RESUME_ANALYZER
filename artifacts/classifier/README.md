# Resume Field Classifier Model Artifacts

## Overview
This directory contains the trained Machine Learning pipeline and metadata for classifying resumes into 5 core technical fields:
- `Data Science`
- `Web Development`
- `Android Development`
- `iOS Development`
- `UI/UX`

## Model Architecture
- **Vectorization:** `TfidfVectorizer` (English stopwords, n-gram range `(1, 2)`, sublinear TF scaling, `min_df=2`, `lowercase=True`).
- **Classifier:** `LogisticRegression` (multinomial L-BFGS, balanced class weights, `max_iter=1000`, `random_state=42`).
- **Explainability:** Feature attribution maps top positive TF-IDF n-grams to predicted fields alongside taxonomy skill matches.
- **Out-of-Distribution Rejection:** Empirical Unknown confidence threshold calibrated on validation split (default: `0.35`).

## Files
- `classifier_pipeline.joblib`: Serialized scikit-learn pipeline (TF-IDF vectorizer + LogisticRegression classifier).
- `metadata.json`: Model version, training parameters, vocabulary size, cross-validation metrics, and threshold calibration.
- `evaluation_report.md`: Independent test split evaluation results and confusion matrix.

## Reproduction Command
To retrain and evaluate the model from scratch:
```bash
# 1. Train candidate models and serialize winning pipeline
py -3.9 ai-service/training/train_classifier.py

# 2. Evaluate against independent held-out test split
py -3.9 ai-service/training/evaluate_classifier.py
```

## Runtime Fallback
If `classifier_pipeline.joblib` is missing or corrupted at runtime, `app.ml.MLClassificationEngine` falls back to the deterministic taxonomy keyword heuristic (`app.extraction.classifier.classify_features`), ensuring zero downtime or service failure.
