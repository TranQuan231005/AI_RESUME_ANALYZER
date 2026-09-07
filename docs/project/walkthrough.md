# Walkthrough — TV5: AI Orchestration, Hybrid Fallback & Evaluation Runner

Completed all requirements for **Member 5 (TV5)** covering **AI Pipeline Orchestration (Task T5.3)**, **Evaluation Benchmark Runner (Task T5.6)**, and **Contract & CI Hardening (Task T5.5)**.

---

## 1. Implemented Components

### A. AI Service Core Orchestration ([`ai-service/app/main.py`](file:///d:/AI_RESUME_ANALYZER/ai-service/app/main.py))
- **`GET /health`**: Healthcheck endpoint returning `status="healthy"`, `model="qwen3:4b"`, and `ollamaReachable: bool`.
- **`POST /api/analyze-resume`**:
  1. Validates PDF size ($\le$ 5MB) and type.
  2. Extracts and sanitizes text into `ParsedDocument`.
  3. Extracts features (`candidateName`, `candidateEmail`, `skills`, `predictedField`, `fieldEvidence`).
  4. Computes 8-part deterministic score breakdown (`ScoreBreakdown`) totaling 0–100.
  5. Computes rule-based recommendations (`generate_recommendations`).
  6. Attempts Ollama enrichment via `_enrich_resume_with_llm` with JSON mode.
  7. Gracefully falls back to deterministic rule results on timeout/connection error, setting `usedFallback = True` and `provider = "RULE_BASED"`.
  8. Returns validated `ResumeAnalysisResult`.
- **`POST /api/analyze-match`**:
  1. Validates PDF file and JD input text (min 50 characters).
  2. Extracts candidate skills and runs deterministic skill matching (`match_resume_to_job`).
  3. Attempts Ollama ATS enrichment via `_enrich_match_with_llm` to extract `atsKeywords`, `strengths`, `weaknesses`, and `recommendations`.
  4. Gracefully falls back to deterministic rule matching results on LLM failure.
  5. Returns validated `MatchResult`.

### B. Schema Base Enhancement ([`ai-service/app/schemas/common.py`](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/common.py))
- Enhanced `SchemaBase.__getattr__` to support camelCase serialization aliases directly in Python attribute access (e.g., `parsed_doc.fileName`, `features.candidateName`).

### C. Test Suite for AI Orchestration ([`ai-service/tests/test_orchestration.py`](file:///d:/AI_RESUME_ANALYZER/ai-service/tests/test_orchestration.py))
- `test_health_check_offline` & `test_health_check_online`
- `test_analyze_resume_with_llm_success`
- `test_analyze_resume_fallback_on_ollama_error`
- `test_analyze_match_with_llm_success`
- `test_analyze_match_fallback_on_llm_error`
- `test_analyze_match_short_jd_validation_error`

### D. Automated Evaluation Runner ([`evaluation/run_evaluation.py`](file:///d:/AI_RESUME_ANALYZER/evaluation/run_evaluation.py))
- Benchmarks skill matching accuracy and latency across frozen ground truth datasets (`job-descriptions.json` and `matching-ground-truth.json`).
- Automatically generates formatted markdown reports in [`evaluation/reports/evaluation-summary.md`](file:///d:/AI_RESUME_ANALYZER/evaluation/reports/evaluation-summary.md).

---

## 2. Verification Results

### 1. Full Pytest Test Suite (`75/75 passed`):
```bash
$ py -m pytest ai-service/tests
============================= 75 passed in 8.52s ==============================
```

### 2. OpenAPI Spec Synchronization (`--check`):
```bash
$ py scripts/export_openapi.py --check
OK: contracts/openapi/ai-service.json is up-to-date.
```

### 3. Evaluation Dataset Validation:
```bash
$ py evaluation/validate_dataset.py
Dataset validation passed: 10 job descriptions, 12 pairs.
```

### 4. Benchmark Runner Execution:
```bash
$ py evaluation/run_evaluation.py --mode rule-only
============================================================
AI RESUME ANALYZER — EVALUATION BENCHMARK SUITE
Mode: RULE-ONLY
============================================================

--- Benchmark Results (Rule-Based Engine) ---
• Total Evaluated Pairs: 12
• Score Match Accuracy:  100.0%
• Matched Skills Acc:    100.0%
• Missing Skills Acc:    100.0%
• Latency P50:           0.0 ms
• Latency P95:           0.0 ms

Successfully generated evaluation report at: D:\AI_RESUME_ANALYZER\evaluation\reports\evaluation-summary.md
============================================================
```
