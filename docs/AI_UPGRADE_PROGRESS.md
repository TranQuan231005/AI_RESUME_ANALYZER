# AI Upgrade Progress Tracking

| Batch | Status | Summary | Tests | Remaining risks |
|---|---|---|---|---|
| **Batch 0 — Audit & Baseline** | COMPLETED | Full repository audit completed. Identified parser newline collapse, name extraction vulnerabilities, scoring section swallow bug, taxonomy misalignment, OpenAPI schema drift, synthetic ground truth limitations, and frontend missing module issue. | AI Service: 78/78 PASS; Backend: PASS (JDK 21); OpenAPI: OUT_OF_DATE; Frontend: 8 FAIL (missing icon module) | No production code modified yet; baseline established. |
| **Batch 1 — Pipeline Correctness** | COMPLETED | Fixed PDF text normalization (preserves newlines and page breaks), robust candidate name extraction, scoring section lookahead regex (prevents section swallowing), taxonomy alignment across all 6 fields, snake_case/camelCase score lookup, removed phone recommendation, synchronized OpenAPI contracts, and added 10 new regression unit tests. | AI Service: 88/88 PASS; OpenAPI: UP-TO-DATE; Backend: PASS; Benchmark: 100% PASS | None on pipeline correctness. Ready for Phase 2 dataset construction. |
| **Batch 2 — ML Dataset Construction** | NOT_STARTED | Build 5-class stratified classification dataset schema, validator, and splits. | - | Dataset provenance and human labeling required. |
| **Batch 3 — Classifier Training** | NOT_STARTED | Train TF-IDF + Classifier (Logistic Regression / SVM / Naive Bayes) with cross-validation and metrics reporting. | - | Model performance dependent on dataset quality. |
| **Batch 4 — CV–JD Matching Upgrade** | NOT_STARTED | Hybrid matching combining skill coverage with semantic similarity and human-annotated ground truth. | - | Need human-labeled pairs. |
| **Batch 5 — Qwen LLM Quality Upgrade** | NOT_STARTED | Versioned prompts, prompt injection defense, structured JSON validation, and rubric-based evaluation. | - | Local Ollama availability and latency. |
| **Batch 6 — Explainability & UI** | NOT_STARTED | Expose model evidence, confidence, match rationale in frontend while maintaining existing design. | - | UI consistency and API contract synchronization. |
| **Batch 7 — Academic Report & Viva QA** | NOT_STARTED | Complete methodology, evaluation, limitations, viva Q&A (25+ questions), and demo script docs. | - | Documentation alignment with actual code/metrics. |
| **Batch 8 — Final Release Audit** | NOT_STARTED | End-to-end reproducibility check, test matrix verification, and release packaging. | - | Final verification before submission. |
