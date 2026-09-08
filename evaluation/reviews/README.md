# Reproducible human-review evidence

This directory holds review evidence committed with pseudonymous IDs only: `reviewer-1` and `reviewer-2`. Do not store reviewer names, email addresses, or raw personal CV data here.

For matching, enter two independent scores in `evaluation/datasets/matching/pairs.jsonl`. Every pair requires exactly two distinct reviewer IDs and integer scores from 0 to 100. The designated owner adds `adjudicatedScore` whenever the two scores differ by more than 15.

For the live Qwen evaluation, first save exactly 20 synthetic outputs as JSONL here. Each record must include `caseId`, `modelVersion`, `promptVersion`, and `timestamp`. Copy [`../datasets/llm/human_review_template.csv`](../datasets/llm/human_review_template.csv) into this directory, then record two reviews per case with matching metadata. Run:

```powershell
python evaluation/scripts/summarize_llm_reviews.py --live-output evaluation/reviews/llm-live-outputs.jsonl --reviews evaluation/reviews/llm-human-reviews.csv --output evaluation/reports/llm.md
```

The evaluator writes `PENDING HUMAN REVIEW` until all 20 cases and both reviews are valid. Qwen must never act as a reviewer.
