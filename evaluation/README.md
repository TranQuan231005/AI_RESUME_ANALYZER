# Evaluation guide

This directory contains reproducible synthetic benchmarks and human-review evidence. Runtime currently defaults to **Qwen3 0.6B**; saved LLM human reviews describe **Qwen3 4B**, and must not be used as quality scores for 0.6B.

## Layout

| Directory | Contents |
|---|---|
| [datasets/classification](datasets/classification/README.md) | Training, validation and held-out synthetic classifier data |
| [datasets/matching](datasets/matching/README.md) | 70 reviewed CV/JD pairs, split into calibration and held-out evaluation |
| [datasets/llm](datasets/llm/) | 20 synthetic cases, rubric and human-review template |
| [datasets/extraction](datasets/extraction/) | Extraction ground-truth format |
| [datasets/legacy](datasets/legacy/) | Inputs still used by the rule-baseline evaluator and legacy validator |
| [scripts](scripts/) | Dataset generation, validation, evaluation and review import/export |
| [reports](reports/) | Published classifier, matching, rule-baseline and historical 4B LLM results |
| [reviews](reviews/README.md) | Saved outputs, reviewer CSVs and browser forms retained as evidence |

## Validation and reproducibility

Run from the repository root with Python 3.11 and `ai-service/requirements.txt` installed:

```powershell
python evaluation/scripts/validate_classification_dataset.py
python evaluation/scripts/validate_matching_dataset.py
python evaluation/scripts/evaluate_llm.py --mode schema-only
python evaluation/scripts/evaluate_classifier.py --output "$env:TEMP/classification-report.md"
python evaluation/scripts/evaluate_matching.py --output "$env:TEMP/matching-report.md"
python evaluation/scripts/summarize_llm_reviews.py --live-output evaluation/reviews/llm-live-outputs.jsonl --reviews evaluation/reviews/llm-human-reviews.csv --output "$env:TEMP/llm-report.md"
```

Schema-only mode tests validators/sanitizers without calling Ollama. Reproducing matching also requires the pinned local embedding model; follow the [runtime setup guide](../docs/project/OLLAMA_LOCAL_DEMO.md). Use temporary report destinations when checking reproducibility so published evidence is not overwritten.

## Interpretation and evidence rules

- Classifier results on synthetic data do not establish real-world accuracy.
- Matching reviews are complete, but the published MAE and ranking correlation limit claims about practical ranking quality.
- The [LLM report](reports/llm.md) summarizes 40 reviews of the saved 4B outputs. A different model or new generation run needs its own outputs and independent reviews before publishing new quality metrics.
- Preserve reviewer IDs, model/prompt/timestamp metadata and adjudication. Do not fabricate or adjust scores to improve a result.
- Dataset builders and live generation are intentional data-creation operations, not routine cleanup commands. Save new experiments separately.
- Browser review forms, legacy inputs and trained classifier artifacts are relevant project assets, not disposable build output.
