# CV-JD Matching Evaluation Benchmark

## 1. Overview
This benchmark evaluates CV–JD matching algorithms against an independent human-annotated ground truth. It tests whether matching models can accurately reflect candidate–job relevance across realistic recruiting scenarios beyond naive keyword overlap.

## 2. Dataset Structure
Each sample in `pairs.jsonl` follows `dataset.schema.json`:
- `id`: Unique identifier (e.g., `pair-ds-01-perfect`).
- `resumeText`: Anonymized candidate summary & experience text.
- `jdText`: Real-world job description requirements.
- `targetRole`: Target job title.
- `domain`: Domain classification (Data Science, Web Development, Android, iOS, UI/UX, Cross-Domain).
- `humanMatchScore`: Independent human relevance score ($0 - 100$).
- `requiredSkills`: List of essential canonical skills specified by the JD.
- `preferredSkills`: Nice-to-have skills.
- `scenarioType`: Evaluation category.
- `explanation`: Human justification for the score.
- `reviewed`: Manual verification flag (`true`).

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
