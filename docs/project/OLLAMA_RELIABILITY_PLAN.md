# Ollama reliability and latency remediation

## Current configuration after cleanup

Qwen3 0.6B is now the runtime default (Python, Compose, environment template and OpenAPI). Qwen4B remains an explicit `OLLAMA_MODEL` override for evaluation. The experimental model override was removed; the existing stack now uses the persistent `docker-compose.local.yml` for ports and image names. Historical measurements below describe the prior verification session and are not re-labeled as fresh measurements.

## Baseline and scope

The running `ai-resume-online` AI container reaches Ollama and finds `qwen3:4b`, but its client lacks the repository's `think=false`. Host microbenchmark: first load 8.59s, subsequent 10-token responses 0.79/0.86s. These are not real CV/JD timings.

Preserve the evaluated 4B model configuration, prompt versions, reviewed outputs and human scores. An optional 0.6B local-demo profile was added after memory pressure was observed; it has no human quality evaluation. Do not infer quality improvement from lower latency.

## Ordered checkpoints

- [x] Diagnose with a synthetic resume/JD against the running image; record only timing and fallback metadata.
- [x] Log classified fallback reasons and numeric Ollama timing without prompts, generated text or exception messages. Make warmup observable with a bounded configurable timeout.
- [x] Run blocking enrichment outside the async event loop; verify concurrent health remains responsive.
- [x] Cache embedding download before application source copy in the Dockerfile; verify the running replacement includes `think=false`.
- [x] Run focused regression tests and Python suite, OpenAPI and repository scans.
- [x] Run real synthetic resume and match requests, online and unavailable Ollama checks. Report exact results, remaining limitations and reproduction commands.

Use isolated containers for verification, then update only the AI service belonging to this repository. Never remove unrelated containers or volumes. Any environment blocker must be reported separately from code verification.

## Results — 2026-09-09

Observed host usable RAM: 5.87 GiB; free RAM during the failing workload: 0.38 GiB. The running image lacked `think=false` although source already contained it. Container-to-Ollama connectivity returned HTTP 200 and listed the expected 4B model.

The old image returned fallback for both real synthetic requests. Adding `think=false` alone still timed out at 60 seconds, and a diagnostic 120-second budget also timed out while build/test activity was present. This rules out a simple connectivity issue and shows that timeout increases alone were insufficient in that environment. Memory pressure is a strong contributing explanation, not an isolated hardware benchmark.

| Configuration and path | Resume seconds | Match seconds | Result |
|---|---:|---:|---|
| Old image, 4B, direct AI | 136.71 | 71.31 | Both fallback |
| New image, 0.6B, first request per flow | 43.81 | 102.05 | Both OLLAMA |
| New image, 0.6B, warm direct AI | 13.23 | 12.07 | Both OLLAMA |
| New image, 0.6B, existing backend | 9.27 | 19.67 | Both OLLAMA |
| New image, unreachable Ollama, cold isolated AI | 14.11 | 56.59 | Both RULE_BASED |

These are individual functional measurements, not p50/p95 or a controlled model-speed comparison. The first 0.6B match spent 72.824 seconds initializing/running embedding. The offline match spent 54.396 seconds in matching, while the failed Ollama call returned in 5 ms. Cold-start costs from local models remain significant on this machine.

Verification completed:

- Focused client/orchestration/diagnostic suite: 25 passed.
- Final Python suite: 132 passed, 5 existing deprecation warnings.
- OpenAPI check: pass in the Python 3.11 image. Host Python lacked `pypdf`, so its failed attempt is not counted as a pass.
- Repository scanner with history: pass.
- Docker build: pass; subsequent source rebuild reused the MiniLM download layer (`CACHED`).
- Source/image SHA-256 comparison: `app/main.py` and `app/llm/client.py` matched.
- Full-stack smoke on project `ai-resume-online`: exit 0, including login, resume, matching, history/detail, admin, JWT, database privacy and log assertions.
- Separate backend probe: explicitly required `provider=OLLAMA`, `usedFallback=false` for both flows; exit 0.
- Unreachable-Ollama probe: explicitly required `provider=RULE_BASED`, `usedFallback=true`; exit 0, both logs reported `CONNECTION`. Matching retained `HYBRID_EMBEDDING`.
- Temporary online/offline AI containers were removed; the main stack and its database were retained.

Runtime image built for this session: `ai-resume-ollama-fix:local`, manifest-list digest `sha256:4417dc1d87ecb182821198daac49f81a62d6b91c86d903568d2c66bba99076b7`. The default 4B model remains installed on disk but was unloaded from RAM for this low-memory demo.

## Handoff and limits

The existing frontend remains at `http://localhost:15173`; backend at `http://localhost:18080`. After cleanup, its AI service inherits the 0.6B default and uses `docker-compose.local.yml` for port mappings. See [startup and probe commands](OLLAMA_LOCAL_DEMO.md).

No human-review scores or saved outputs were rewritten. No quality score is claimed for 0.6B. The temporary port override has now been replaced in the active AI configuration by a repository file; general container-name isolation remains separate work. No frontend/backend source changed; their unit/build suites were not rerun in this task. No Git commit, push or release declaration was made.

## Default-model cleanup follow-up

- Set Python config, environment fallback, health schema, Compose and environment template to 0.6B.
- Regenerated OpenAPI and updated illustrative API fixtures; explicit 4B override tests and historical review metadata remain intact.
- Final Python suite for this change: **133 passed**, 5 deprecation warnings.
- Removed 22 Python/pytest cache directories and the redundant experimental model override file.
- Added persistent local Compose configuration and updated active/archive documentation to distinguish current defaults from historical 4B evaluation.
- Built `ai-resume-analyzer-ai:local` (manifest digest `sha256:6f686007f0f5e46bbfa67169dc25c01ed74f5d462932d3a3c616cdaa30faa16c`) with cached pinned MiniLM.
- Active AI container is healthy and references only repository Compose files (base plus local).
- OpenAPI verification and repository/history scanner passed after the default change.
- Full-stack smoke with the new local configuration passed, including database/log privacy.
- Final backend probe: resume **10.19s**, matching **22.33s**; both explicitly required and returned `OLLAMA`, `qwen3:0.6b`, `usedFallback=false`. Matching retained `HYBRID_EMBEDDING`.
