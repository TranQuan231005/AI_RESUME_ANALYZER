# Reproducible human-review evidence

The saved LLM outputs/reviews in this directory describe **Qwen3 4B**. Runtime now defaults to Qwen3 0.6B; these reviews and the published LLM metrics must not be attributed to 0.6B. Retain the original model metadata and scores when changing runtime configuration.

This directory holds review evidence committed with pseudonymous IDs only: `reviewer-1` and `reviewer-2`. Do not store reviewer names, email addresses, or raw personal CV data here.

Create blinded matching forms for the two reviewers with:

```powershell
python evaluation/scripts/export_matching_review_forms.py
```

If Excel is unavailable, create and open `matching-review.html` in any browser instead:

```powershell
python evaluation/scripts/generate_matching_review_form.py
```

Select one reviewer ID, score the 70 pairs one at a time, then use **Tải CSV**. Browser local storage keeps unfinished work on that computer. Each reviewer must use a separate browser profile or clear local storage before the other begins.

The resulting `matching-reviewer-1.csv` and `matching-reviewer-2.csv` deliberately omit the provisional score, split, scenario, expected skills, and author explanation. Send each reviewer only their own CSV. They fill `score_0_to_100` and optional notes, then return the files to the owner. Do not let either reviewer see the other's completed CSV before both have finished.

For matching, enter two independent scores in `evaluation/datasets/matching/pairs.jsonl`. Every pair requires exactly two distinct reviewer IDs and integer scores from 0 to 100. The designated owner adds `adjudicatedScore` whenever the two scores differ by more than 15.

For the live Qwen evaluation, first save exactly 20 synthetic outputs as JSONL here. Each record must include `caseId`, `modelVersion`, `promptVersion`, and `timestamp`. Copy [`../datasets/llm/human_review_template.csv`](../datasets/llm/human_review_template.csv) into this directory, then record two reviews per case with matching metadata. Run:

```powershell
python evaluation/scripts/summarize_llm_reviews.py --live-output evaluation/reviews/llm-live-outputs.jsonl --reviews evaluation/reviews/llm-human-reviews.csv --output evaluation/reports/llm.md
```

When the live output exists, reviewers without spreadsheet software can run `python evaluation/scripts/generate_llm_review_form.py` and open `llm-review.html` in a browser. Each reviewer selects their own ID, scores all 20 outputs on the six rubric dimensions, and downloads one CSV. The owner combines them without changing scores:

```powershell
python evaluation/scripts/combine_llm_reviews.py --reviewer-1 evaluation/reviews/llm-reviewer-1.csv --reviewer-2 evaluation/reviews/llm-reviewer-2.csv --output evaluation/reviews/llm-human-reviews.csv
```

The evaluator writes `PENDING HUMAN REVIEW` until all 20 cases and both reviews are valid. Qwen must never act as a reviewer.
