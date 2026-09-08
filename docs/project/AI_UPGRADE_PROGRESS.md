# AI Upgrade Progress Tracking

| Batch | Status | Implemented remediation | Acceptance still open |
|---|---|---|---|
| Batch 0 — Audit & Baseline | COMPLETED | Baseline captured before remediation. | None. |
| Batch 1 — Pipeline Correctness & Hygiene | IN_PROGRESS | Repository layout normalized; local token file removed/ignored; scripts use `GITHUB_TOKEN`; real-PDF integration tests added. | Revoke remote token and purge affected Git history under separate approval; complete final scans. |
| Batch 2 — ML Dataset | COMPLETED | Retained 250 controlled in-domain samples and added 100 synthetic OOD samples split 50/50 for validation/test. | Verified in Python 3.11 environment with clean worktree. |
| Batch 3 — Classifier | IN_PROGRESS | Retrained in Python 3.11.9 (scikit-learn 1.6.1, joblib 1.6.0); model selection uses training-only cross-validation with Logistic Regression; Unknown threshold uses in-domain plus OOD validation; artifact metadata includes runtime/library versions and SHA-256; `topTerms` is exposed end to end. | Complete the safe ML-inference fallback regression and current Python 3.11 suite. Metrics remain synthetic-only. |
| Batch 4 — CV–JD Matching | IN_PROGRESS | Production TF-IDF and arbitrary stuffing penalty replaced by pinned MiniLM embeddings, bounded chunking, metadata weights and `SKILL_ONLY` degradation. Dataset expanded to 70 cases with separated calibration/test groups. | All 70 cases need two independent human reviewers; alpha and held-out metrics remain `PENDING HUMAN REVIEW`. |
| Batch 5 — Qwen Evaluation | IN_PROGRESS | Schema-only and live modes separated; 20 synthetic cases cover five fields, matching, overlap and injection; live output captures model/prompt/timestamp; review CSV no longer contains fabricated scores. | Live Ollama evaluation ready; awaiting two independent human reviews per case before publishing quality scores. |
| Batch 6 — Explainability, CI & UI | IN_PROGRESS | Matching breakdown and classifier evidence are synchronized across schemas, contracts, fixtures, and UI. CI includes the frontend and backend gates. | Full Compose API smoke must pass in CI and locally after Docker Desktop is enabled; all current checks must then pass. |
| Batch 7 — Academic Report & Viva QA | NOT_STARTED | Outside current scope. | Not started. |
| Batch 8 — Final Release Audit | NOT_STARTED | Outside current scope. | Not started. |
