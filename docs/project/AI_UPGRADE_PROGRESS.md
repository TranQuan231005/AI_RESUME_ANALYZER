# AI Upgrade Progress Tracking

Runtime update: the default model is now `qwen3:0.6b`. Batch 5 completion below refers only to the saved **Qwen3 4B** evaluation and its 40 human reviews. No human quality metric has been published for 0.6B. See [Ollama runtime evidence](OLLAMA_RELIABILITY_PLAN.md).

| Batch | Status | Implemented remediation | Acceptance still open |
|---|---|---|---|
| Batch 0 — Audit & Baseline | COMPLETED | Baseline captured before remediation. | None. |
| Batch 1 — Pipeline Correctness & Hygiene | COMPLETED | Repository layout normalized; local token file removed/ignored; scripts use `GITHUB_TOKEN`; real-PDF integration tests added. The previously exposed token was revoked by the owner; current repository and Git-history scans are clean. | None. |
| Batch 2 — ML Dataset | COMPLETED | Retained 250 controlled in-domain samples and added 100 synthetic OOD samples split 50/50 for validation/test. | Verified in Python 3.11 environment with clean worktree. |
| Batch 3 — Classifier | IN_PROGRESS | Retrained in Python 3.11.9 (scikit-learn 1.6.1, joblib 1.6.0); model selection uses training-only cross-validation with Logistic Regression; Unknown threshold uses in-domain plus OOD validation; artifact metadata includes runtime/library versions and SHA-256; `topTerms` is exposed end to end. | Complete the safe ML-inference fallback regression and current Python 3.11 suite. Metrics remain synthetic-only. |
| Batch 4 — CV–JD Matching | COMPLETED | Production TF-IDF and arbitrary stuffing penalty replaced by pinned MiniLM embeddings, bounded chunking, metadata weights and `SKILL_ONLY` degradation. All 70 pairs now have two independent pseudonymous reviews; the only disagreement above 15 was adjudicated at 78. | Synthetic benchmark metrics remain evidence for this controlled dataset only. |
| Batch 5 — Qwen Evaluation | COMPLETED | Schema-only and live modes are separated; 20 synthetic Qwen outputs capture model/prompt/timestamp and now have two independent pseudonymous reviews each. Published quality metrics are derived only from those 40 reviews. | Results apply to the synthetic evaluation set only. |
| Batch 6 — Explainability, CI & UI | IN_PROGRESS | Matching breakdown and classifier evidence are synchronized across schemas, contracts, fixtures, and UI. CI includes the frontend and backend gates. | Full Compose API smoke must pass in CI and locally after Docker Desktop is enabled; all current checks must then pass. |
| Batch 7 — Academic Report & Viva QA | NOT_STARTED | Outside current scope. | Not started. |
| Batch 8 — Final Release Audit | NOT_STARTED | Outside current scope. | Not started. |
