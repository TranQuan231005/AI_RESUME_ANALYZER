# CV–JD Matching Model Notes

Production combines deterministic taxonomy skill coverage with normalized sentence embeddings from `sentence-transformers/all-MiniLM-L6-v2` at revision `f5610b47471b118dafc55f4c387822dbfc8413ae`.

```text
FinalScore = skillWeight × SkillCoverage + semanticWeight × SemanticScore
```

The engine reads weights from `ai-service/models/matching/metadata.json`; it does not hard-code alpha. If the JD contains no recognized skills, weights become 0/1. If the embedding model cannot load, the method becomes `SKILL_ONLY` with weights 1/0. The former arbitrary keyword-stuffing multiplier was removed.

TF-IDF cosine remains only a lexical baseline inside `evaluation/scripts/evaluate_matching.py`; it is never labeled a semantic embedding and is not called by production.

## Calibration status

**PENDING HUMAN REVIEW.** The 70 synthetic pairs are correctly split 35/35, but each needs two independent reviewer scores. After review:

```bash
python evaluation/scripts/evaluate_matching.py --output evaluation/reports/matching.md
```

The evaluator searches alpha from 0.00 through 1.00 in 0.05 increments on calibration only, then calls the production matching function directly on the held-out test split.
