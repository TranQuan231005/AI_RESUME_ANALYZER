# Walkthrough: AI Resume Analyzer — current merge-readiness evidence

## Scope and status

The merge gate covers login, resume analysis, CV–JD matching, user history/detail, and the admin dashboard. Matching review is complete for all 70 pairs. The saved Qwen3 4B evaluation has 20 outputs and 40 human reviews; it does not evaluate the current Qwen3 0.6B default. Batch 3's classifier regression and Python suite have passed locally. Batch 6 remains in progress pending official CI evidence and final release checks.

The most recent recorded local verification includes 133 Python tests, OpenAPI, repository/history scans and the full-stack API smoke with JWT and database/log privacy checks. These are prior execution results, not a claim that every check was rerun during documentation cleanup. See [runtime evidence](docs/project/OLLAMA_RELIABILITY_PLAN.md).

## Required verification

Run the following from the repository root in a Python 3.11 environment with the AI dependencies installed:

```powershell
python scripts/scan_repository.py --check-history
python scripts/export_openapi.py --check
python -m pytest
Push-Location frontend
npm.cmd run lint
npm.cmd test -- --runInBand
npm.cmd run build
Pop-Location
```

For the existing local stack (project `ai-resume-online`), use its repository port configuration consistently:

```powershell
$env:COMPOSE_PROJECT_NAME = 'ai-resume-online'
$env:COMPOSE_FILE = 'docker-compose.yml;docker-compose.local.yml'
docker compose up --build --detach
python scripts/smoke_stack.py --ai-url http://localhost:18000 --backend-url http://localhost:18080 --frontend-url http://localhost:15173 --check-mysql-privacy --check-logs
python scripts/probe_ollama_pipeline.py --backend-url http://localhost:18080 --expect OLLAMA
```

The semicolon-separated Compose file list above is for Windows PowerShell. Preserve the existing stack's database; volume deletion belongs only to disposable test projects. See [local setup](docs/project/OLLAMA_LOCAL_DEMO.md) for fresh-stack and model-selection instructions.

The Docker smoke script verifies the seed USER and ADMIN logins, JWT authorization, resume analysis, job matching, history/detail, admin endpoints, classifier and embedding health, `topTerms`, and `matchBreakdown.method = "HYBRID_EMBEDDING"`. It also rejects raw resume/JD fields in persisted JSON and the smoke-test JD sentinel in service logs.

## Model and benchmark evidence

The classifier uses a Python 3.11.9 artifact with scikit-learn 1.6.1 and joblib 1.6.0. Its controlled synthetic held-out report is [classification.md](evaluation/reports/classification.md). The heuristic and ML results use the same six-label, 100-sample held-out split.

The Docker image downloads the pinned embedding model at build time. Runtime loads `/opt/models/all-MiniLM-L6-v2` and must not download the model from the Internet. Ollama is optional: the core flows return deterministic fallback data when it is unavailable.

## Human-review gates

The matching dataset has two independent pseudonymous scores per pair; the disagreement above 15 points was adjudicated at 78. The [matching report](evaluation/reports/matching.md) is published, with synthetic-only results and weak ranking correlation. The [LLM report](evaluation/reports/llm.md) describes the reviewed Qwen3 4B outputs only. No human quality score is published for 0.6B.

For future evaluations, retain the validation gates: two independent reviewers per item, matching adjudication when required, and output/review metadata alignment. Never manufacture scores or use an LLM as a human reviewer. See [matching dataset instructions](evaluation/datasets/matching/README.md) and [review evidence instructions](evaluation/reviews/README.md).

## Security status

Repository scans check committed files, Markdown links, placeholder-only emails, and Git history. Token revocation is an owner-controlled external action and must be recorded separately before merge if applicable.
