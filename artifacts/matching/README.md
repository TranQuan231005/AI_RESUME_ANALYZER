# Hybrid CV-JD Matching Model & Benchmark

## Overview
This component implements a calibrated hybrid matching engine combining:
1. **Deterministic Skill Coverage:** Exact canonical skill matching from taxonomy ($0 - 100\%$).
2. **Lexical-Semantic Cosine Alignment:** Sublinear TF-IDF character & word n-gram cosine similarity ($0 - 100\%$).
3. **Keyword Stuffing Defense & Zero-Skill Fallback:** Contextual penalty for disjoint keyword spam and smooth semantic fallback when JDs lack explicit technical terms.

## Formula & Calibration
$$\text{FinalMatchScore} = \alpha \times \text{SkillCoverage} + (1 - \alpha) \times \text{SemanticSimilarity}$$
- **Calibrated $\alpha$:** `0.65` (Skill Coverage: 65%, Semantic Context: 35%).
- **Parameters Selected Via:** Grid-search cross-evaluation on the independent human benchmark (`evaluation/matching/pairs.jsonl`).

## Evaluation Execution
To run the matching benchmark evaluation:
```bash
py -3.9 ai-service/training/evaluate_matching.py
```
Evaluation metrics report will be generated at `artifacts/matching/evaluation_report.md`.
