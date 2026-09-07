# CV-JD Matching Evaluation Benchmark

## 1. Overview
This controlled synthetic benchmark contains 70 CV–JD pairs, 10 for each scenario. It is split into 35 calibration and 35 held-out test pairs by template group. It is not human ground truth until the review gate below is complete.

## 2. Dataset Structure
Each sample in `pairs.jsonl` follows `dataset.schema.json`:
- `id`: Unique identifier (e.g., `pair-ds-01-perfect`).
- `resumeText`: Anonymized candidate summary & experience text.
- `jdText`: Real-world job description requirements.
- `targetRole`: Target job title.
- `domain`: Domain classification (Data Science, Web Development, Android, iOS, UI/UX, Cross-Domain).
- `provisionalScore`: Synthetic authoring target, never used as human ground truth.
- `requiredSkills`: List of essential canonical skills specified by the JD.
- `preferredSkills`: Nice-to-have skills.
- `scenarioType`: Evaluation category.
- `explanation`: Human justification for the score.
- `reviewerScores`: Exactly two independent reviewer IDs and scores are required.
- `adjudicatedScore`: Required when reviewer scores differ by more than 15 points.
- `reviewed`: May be `true` only after the two-reviewer/adjudication gate passes.
- `split` and `templateGroup`: Prevent calibration/test leakage.

## 3. Evaluated Scenarios
1. **`standard_match`**: Strong alignment between candidate skills/experience and job requirements.
2. **`partial_match`**: Candidate has foundational skills but lacks core advanced frameworks.
3. **`paraphrase_match`**: Candidate describes domain competencies using synonyms/conceptual phrasing rather than exact canonical keywords.
4. **`missing_required_skill`**: Candidate has peripheral tools but lacks the non-negotiable core language/stack.
5. **`keyword_stuffing`**: Resume contains dense lists of buzzwords across unrelated fields without demonstrated project depth.
6. **`cross_domain`**: High seniority in an unrelated field (e.g. Android engineer applying for UI/UX Designer).
7. **`no_skills_jd`**: Broad or vague job description lacking explicit technical requirements.

## 4. Evaluation Metrics
- **Mean Absolute Error (MAE):** Average absolute difference between predicted score and human score:
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|$$
- **Spearman Rank Correlation ($\rho$):** Measures monotonicity between predicted rank and human preference rank.
- **Skill Extraction F1:** Precision, recall, and F1 of extracted canonical skills against ground truth.
- **Latency:** Average execution time per match pair (ms).

Until all 70 records pass review, `evaluation/reports/matching.md` must say `PENDING HUMAN REVIEW` and no MAE/Spearman or paraphrase-robustness claim may be published.

```bash
python evaluation/scripts/validate_matching_dataset.py
python evaluation/scripts/evaluate_matching.py --output evaluation/reports/matching.md
```
