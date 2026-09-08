# Walkthrough: AI Resume Analyzer — current merge-readiness evidence

## Scope and status

The merge gate covers login, resume analysis, CV–JD matching, user history/detail, and the admin dashboard. Batch 4 and Batch 5 remain **PENDING HUMAN REVIEW**. Batch 6 remains in progress until the full Compose API gate passes in CI.

## Required verification

Run the following on the commit being reviewed:

```powershell
python scripts/scan_repository.py --check-history
python scripts/export_openapi.py --check
python -m pytest
cd frontend; npm run lint; npm test -- --runInBand; npm run build
docker compose up --build --detach
python scripts/smoke_stack.py --check-mysql-privacy --check-logs
docker compose down --volumes
```

The Docker smoke script verifies the seed USER and ADMIN logins, JWT authorization, resume analysis, job matching, history/detail, admin endpoints, classifier and embedding health, `topTerms`, and `matchBreakdown.method = "HYBRID_EMBEDDING"`. It also rejects raw resume/JD fields in persisted JSON and the smoke-test JD sentinel in service logs.

## Model and benchmark evidence

The classifier uses a Python 3.11.9 artifact with scikit-learn 1.6.1 and joblib 1.6.0. Its controlled synthetic held-out report is [classification.md](evaluation/reports/classification.md). The heuristic and ML results use the same six-label, 100-sample held-out split.

The Docker image downloads the pinned embedding model at build time. Runtime loads `/opt/models/all-MiniLM-L6-v2` and must not download the model from the Internet. Ollama is optional: the core flows return deterministic fallback data when it is unavailable.

## Human-review gates

The matching report stays **PENDING HUMAN REVIEW** until all 70 pairs have exactly two independent pseudonymous reviewer scores, with adjudication for disagreements above 15 points. LLM quality metrics stay unpublished until all 20 saved live outputs have the two required human reviews. Reviewers must not use Qwen as a reviewer. See [matching dataset instructions](evaluation/datasets/matching/README.md) and [review evidence instructions](evaluation/reviews/README.md).

## Security status

Repository scans check committed files, Markdown links, placeholder-only emails, and Git history. Token revocation is an owner-controlled external action and must be recorded separately before merge if applicable.
