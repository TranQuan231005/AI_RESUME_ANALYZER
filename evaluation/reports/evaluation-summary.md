# AI Resume Analyzer — Evaluation Benchmark Report

- **Date Generated**: 2026-09-01 08:13:42 UTC
- **Dataset Version**: 1.0.0
- **Total Test Pairs**: 12

## 1. Summary Metrics

| Metric | Rule-Based Mode | Target Standard | Status |
| :--- | :---: | :---: | :---: |
| **Score Accuracy** | **100.0%** | $\ge 95\%$ | ✅ PASS |
| **Matched Skills Accuracy** | **100.0%** | $100\%$ | ✅ PASS |
| **Missing Skills Accuracy** | **100.0%** | $100\%$ | ✅ PASS |
| **P95 Latency** | **0.0 ms** | $< 50$ ms | ✅ PASS |
| **Average Latency** | **0.0 ms** | $< 10$ ms | ✅ PASS |

## 2. Test Cases Breakdown

| Pair ID | Job ID | Expected Score | Actual Score | Score Match | Skills Match | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `pair-data-analyst-perfect` | `jd-data-analyst` | 100% | 100% | PASS | ✅ | 0.0 |
| `pair-data-analyst-partial` | `jd-data-analyst` | 67% | 67% | PASS | ✅ | 0.0 |
| `pair-ml-engineer-aliases` | `jd-ml-engineer` | 40% | 40% | PASS | ✅ | 0.0 |
| `pair-frontend-perfect` | `jd-frontend-engineer` | 100% | 100% | PASS | ✅ | 0.0 |
| `pair-full-stack-partial` | `jd-full-stack-developer` | 60% | 60% | PASS | ✅ | 0.0 |
| `pair-android-partial` | `jd-android-engineer` | 33% | 33% | PASS | ✅ | 0.0 |
| `pair-kotlin-perfect` | `jd-kotlin-developer` | 100% | 100% | PASS | ✅ | 0.0 |
| `pair-ios-partial` | `jd-ios-engineer` | 50% | 50% | PASS | ✅ | 0.0 |
| `pair-ui-ux-partial` | `jd-ui-ux-designer` | 67% | 67% | PASS | ✅ | 0.0 |
| `pair-data-scientist-empty-resume` | `jd-data-scientist` | 0% | 0% | PASS | ✅ | 0.0 |
| `pair-product-designer-partial` | `jd-product-designer` | 67% | 67% | PASS | ✅ | 0.0 |
| `pair-full-stack-mixed-aliases` | `jd-full-stack-developer` | 80% | 80% | PASS | ✅ | 0.0 |
