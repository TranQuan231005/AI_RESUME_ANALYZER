# Ollama local demo and diagnostics

## Configuration profiles

The default runtime model is `qwen3:0.6b` in Python, Compose, the environment template and the health schema. Historical human evaluation used `qwen3:4b`. On the observed Windows machine (5.87 GiB usable RAM), running 4B together with Docker left about 0.38 GiB free. A short standalone greeting benchmark does not represent the full-stack workload.

No model override file is needed for 0.6B. The 4B human-review scores **do not apply** to this model. Saved review evidence remains unchanged.

For a fresh stack with default ports available, run from the repository root in PowerShell:

```powershell
ollama pull qwen3:0.6b
docker compose up --build --detach
```

Do not start a second default stack over the existing one. The repository still has fixed container names; this change does not resolve general multi-project isolation.

For the optional alternate-port stack (`ai-resume-online`, frontend 15173, backend 18080, AI 18000), port mappings now live in `docker-compose.local.yml` in the repository. To rebuild and update only AI:

```powershell
docker compose -p ai-resume-online -f docker-compose.yml -f docker-compose.local.yml build ai-service
docker compose -p ai-resume-online -f docker-compose.yml -f docker-compose.local.yml up --detach --no-build --no-deps ai-service
```

To start the complete local stack, use the same two files and project name with `up --build --detach`. Do not use `down --volumes` on this stack if its saved analyses should be retained.

To explicitly select the historical model, set `$env:OLLAMA_MODEL = 'qwen3:4b'` before running Compose or an evaluator. Remove that environment variable to return to the 0.6B default. When evaluating 4B, save new outputs separately; never overwrite reviewed outputs or reuse their scores for a different model run.

Docker reaches host Ollama through `http://host.docker.internal:11434`. Direct host execution uses `http://localhost:11434`. Copying the latter into Docker environment variables points at the wrong machine.

## Diagnosis

Use `ollama ps` to confirm which model is loaded and its processor. Do not run a large model concurrently with a low-memory benchmark. Unload unused models only after confirming no request needs them.

The AI service logs:

- `ollama_warmup`: HTTP status and elapsed milliseconds, or a failure notice.
- `ai_stage`: parsing, extraction, classification, matching and enrichment duration.
- `ollama_generation`: numeric duration/count fields returned by Ollama (durations are nanoseconds).
- `ollama_fallback`: operation and classified error code, without exception text or document content.

`/health` reports reachability separately from classifier/embedding readiness. `ollamaReachable=true` is not proof of successful generation. Verify the actual response has `ai.provider=OLLAMA` and `ai.usedFallback=false`.

With Python installed (no additional packages needed), use the repository's synthetic fixture:

```powershell
python scripts/probe_ollama_pipeline.py --ai-url http://localhost:18000 --expect OLLAMA
python scripts/probe_ollama_pipeline.py --backend-url http://localhost:18080 --expect OLLAMA
```

Adjust the port to the running stack. The command prints metadata only and fails if either resume or matching falls back. It does not score LLM quality or replace the full-stack authentication/privacy gate.

The first health/model load can take substantially longer on a low-memory machine. Wait for classifier and embedding health, then rehearse once before presenting; warm timings must not be described as cold-start timings.

## Scope of improvements

Generation disables thinking explicitly. Synchronous parsing, classification, matching and Ollama work are dispatched to a thread pool so the async event loop can serve other requests. This improves responsiveness; it does not make CPU inference intrinsically faster. Model download now precedes source copy in the Dockerfile, so later source edits reuse the pinned embedding layer.

References: [FastAPI concurrency](https://fastapi.tiangolo.com/async/), [Ollama thinking control](https://docs.ollama.com/capabilities/thinking), [Ollama performance metrics](https://docs.ollama.com/api/usage).

## Recorded performance and limitations

Measurements from 2026-09-09 on a Windows host with 5.87 GiB usable RAM:

| Request path | Resume | Match | Result |
|---|---:|---:|---|
| Warm 0.6B through backend, final verification | 10.19 s | 22.33 s | OLLAMA, no fallback |
| First request per flow, earlier 0.6B verification | 43.81 s | 102.05 s | OLLAMA, no fallback |
| Unreachable Ollama, cold isolated AI | 14.11 s | 56.59 s | RULE_BASED; matching retained HYBRID_EMBEDDING |

These are individual historical observations, not p50/p95, performance guarantees or a controlled model comparison. Embedding initialization contributed heavily to cold requests. Raising the Ollama timeout alone did not resolve the observed 4B failures under memory pressure.

The default-model verification recorded 133 Python tests passing, OpenAPI and repository/history checks passing, and a full-stack smoke passing authentication, analysis, matching, history, admin and privacy assertions. These records do not replace running current CI checks. Human quality scores remain specific to the saved 4B outputs; see the [evaluation guide](../../evaluation/README.md).
