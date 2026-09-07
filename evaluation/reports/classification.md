# Resume Field Classifier Evaluation Report

## 1. Overview & Dataset Provenance
- **Dataset Version:** `2.0.0-controlled-synthetic`
- **Evaluation Date:** `2026-09-07T09:55:42.240377+00:00`
- **Test Set Size:** 100 samples (50 in-domain + 50 held-out OOD)
- **Classes Evaluated (6):** Android Development, Data Science, UI/UX, Web Development, iOS Development, Unknown
- **Model Type:** `Logistic Regression`
- **Random Seed:** `42`
- **Unknown Threshold:** `0.3`
- **Limitation:** All records are controlled synthetic templates. These metrics do not estimate performance on real-world resumes.

## 2. Model vs Baseline Comparison (Held-out Test Split)

| Metric | Heuristic Baseline (Keyword Overlap) | ML Classifier (TF-IDF + Logistic Regression) | Delta |
|---|---|---|---|
| **Accuracy** | 78.00% | **100.00%** | +22.00% |
| **Macro F1** | 0.8611 | **1.0000** | +0.1389 |
| **Weighted F1** | 0.8611 | **1.0000** | +0.1389 |
| **Avg Latency** | 0.64 ms | 1.92 ms | - |

## 3. Unknown/OOD Performance
- **In-domain accuracy:** 1.0000
- **Six-label Macro F1:** 1.0000
- **OOD recall:** 1.0000
- **OOD false-acceptance rate:** 0.0000
- **Known-class rejection rate:** 0.0000

## 4. Per-Class Performance on Test Set

| Field Label | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **Android Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Data Science** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **UI/UX** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Web Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **iOS Development** | 1.0000 | 1.0000 | 1.0000 | 10 |
| **Unknown** | 1.0000 | 1.0000 | 1.0000 | 50 |
| **Macro Average** | - | - | **1.0000** | 100 |
| **Weighted Average** | - | - | **1.0000** | 100 |

## 5. Confusion Matrix (Six Labels)

| True \ Pred | Android Development | Data Science | UI/UX | Web Development | iOS Development | Unknown |
|---|---|---|---|---|---|---|
| **Android Development** | 10 | 0 | 0 | 0 | 0 | 0 |
| **Data Science** | 0 | 10 | 0 | 0 | 0 | 0 |
| **UI/UX** | 0 | 0 | 10 | 0 | 0 | 0 |
| **Web Development** | 0 | 0 | 0 | 10 | 0 | 0 |
| **iOS Development** | 0 | 0 | 0 | 0 | 10 | 0 |
| **Unknown** | 0 | 0 | 0 | 0 | 0 | 50 |

## 6. Inference Latency Benchmark
- **Mean Latency:** 1.92 ms per resume
- **p50 Latency:** 1.53 ms
- **p95 Latency:** 4.86 ms
- **p99 Latency:** 6.35 ms

## 7. Model Hyperparameters & Configuration
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
  "vocabSize": 1467
}
```
