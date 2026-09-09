"""Schema-only evaluation must exercise sanitizers without calling Ollama."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "evaluation" / "scripts" / "evaluate_llm.py"
SPEC = importlib.util.spec_from_file_location("evaluate_llm", SCRIPT_PATH)
assert SPEC and SPEC.loader
evaluate_llm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluate_llm)


def test_schema_only_runs_valid_and_invalid_sanitizer_inputs_for_every_case():
    cases = json.loads(
        (ROOT / "evaluation" / "datasets" / "llm" / "cases.json").read_text(encoding="utf-8")
    )

    result = evaluate_llm.run_schema_only(cases)

    assert result == {"cases": 20, "validatorCalls": 40}
