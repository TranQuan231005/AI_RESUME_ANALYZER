# Resume Field Classifier Evaluation Report

## 1. Overview & Dataset Provenance
- **Dataset Version:** `1.0.0`
- **Evaluation Date:** `2026-09-07T05:56:17.226706+00:00`
- **Test Set Size:** 50 samples (strictly independent, 0% template leakage)
- **Classes Evaluated (5):** Android Development, Data Science, UI/UX, Web Development, iOS Development
- **Model Type:** `Logistic Regression`
- **Random Seed:** `42`
- **Unknown Threshold:** `0.35`

## 2. Model vs Baseline Comparison (Held-out Test Split)

| Metric | Heuristic Baseline (Keyword Overlap) | ML Classifier (TF-IDF + Logistic Regression) | Delta |
|---|---|---|---|
| **Accuracy** | 78.00% | **100.00%** | +22.00% |
| **Macro F1** | 0.8611 | **1.0000** | +0.1389 |
| **Weighted F1** | 0.8611 | **1.0000** | +0.1389 |
| **Avg Latency** | 0.23 ms | 0.60 ms | - |

## 3. Per-Class Performance on Test Set

| Field Label | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Android Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Data Science** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **UI/UX** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Web Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **iOS Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Macro Average** | - | - | **1.0000** | 50 |
| **Weighted Average** | - | - | **1.0000** | 50 |

## 4. Confusion Matrix

| True \ Pred | Android Development | Data Science | UI/UX | Web Development | iOS Development |
|---|---|---|---|---|---|
| **Android Development** | 10 | 0 | 0 | 0 | 0 |
| **Data Science** | 0 | 10 | 0 | 0 | 0 |
| **UI/UX** | 0 | 0 | 10 | 0 | 0 |
| **Web Development** | 0 | 0 | 0 | 10 | 0 |
| **iOS Development** | 0 | 0 | 0 | 0 | 10 |

## 5. Inference Latency Benchmark
- **Mean Latency:** 0.60 ms per resume
- **p50 Latency:** 0.56 ms
- **p95 Latency:** 1.03 ms
- **p99 Latency:** 1.21 ms

## 6. Model Hyperparameters & Configuration
```json
{
  "lowercase": true,
  "stopWords": "english",
  "ngramRange": [
    1,
    2
  ],
  "sublinearTf": true,
  "minDf": 2,
  "vocabSize": 1677
}
```
