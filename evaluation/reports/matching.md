# CV–JD Matching Evaluation

Calibration and held-out test pairs are separated by template group. TF-IDF is reported only as a lexical baseline; production calls the packaged sentence-embedding matcher directly.

- Calibrated skill weight: `0.00`
- Held-out pairs: 35
- Production MAE: 35.71
- Production Spearman rho: 0.0438
- Skill-only baseline MAE: 58.49
- TF-IDF lexical baseline MAE: 76.00
- Latency p50/p95: 48.62/71.96 ms

| Scenario | Production MAE |
|---|---:|
| cross_domain | 56.10 |
| keyword_stuffing | 32.10 |
| missing_required_skill | 36.40 |
| no_skills_jd | 47.80 |
| paraphrase_match | 28.10 |
| partial_match | 31.70 |
| standard_match | 17.80 |
