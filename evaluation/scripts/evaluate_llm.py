"""Run schema-only checks or capture live Ollama outputs for two-reviewer evaluation."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "ai-service"))

from app.llm.client import OllamaClient
from app.llm.prompts import build_jd_matching_prompt, build_resume_recommendation_prompt, validate_and_sanitize_match_insights, validate_and_sanitize_resume_recommendations
from app.schemas import AiMetadata, AiProvider, FieldEnum, MatchResult, ResumeFeatures, ScoreBreakdown


def field_enum(value: str) -> FieldEnum:
    return FieldEnum(value) if value in [item.value for item in FieldEnum] else FieldEnum.UNKNOWN


def prepare(case):
    features = ResumeFeatures(skills=case.get("currentSkills", case.get("candidateSkills", [])), predictedField=field_enum(case["candidateField"]), fieldEvidence=[])
    if case["type"] == "resume_recommendation":
        breakdown = ScoreBreakdown.model_validate(case["scoreBreakdown"])
        system, user, definition = build_resume_recommendation_prompt(case["resumeText"], features, breakdown)
        fallback = {"recommendedSkills": [], "recommendations": ["Add specific, measurable evidence."]}
        validator = lambda output: validate_and_sanitize_resume_recommendations(output, list(features.skills), fallback)
    else:
        rule_match = MatchResult(
            fileName="synthetic.pdf", targetRole=case["targetRole"], matchScore=case["matchScore"],
            matchedSkills=case["matchedSkills"], missingSkills=case["missingSkills"], atsKeywords=case["matchedSkills"],
            strengths=[], weaknesses=[], recommendations=[],
            matchBreakdown={"method": "SKILL_ONLY", "skillScore": case["matchScore"], "semanticScore": None, "skillWeight": 1.0, "semanticWeight": 0.0, "embeddingModel": None},
            ai=AiMetadata(provider=AiProvider.RULE_BASED, model="deterministic-v1", usedFallback=True, processingMs=0),
        )
        system, user, definition = build_jd_matching_prompt(case["resumeText"], features, case["jobDescription"], case["targetRole"], rule_match)
        validator = lambda output: validate_and_sanitize_match_insights(output, rule_match)
    return system, user, definition, validator


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["schema-only", "live"], default="schema-only")
    parser.add_argument("--output", help="Required JSONL output for live mode")
    args = parser.parse_args()
    cases = json.loads((ROOT_DIR / "evaluation/datasets/llm/cases.json").read_text(encoding="utf-8"))
    if len(cases) < 20:
        raise SystemExit("LLM dataset must contain at least 20 cases")
    client = OllamaClient() if args.mode == "live" else None
    outputs = []
    for case in cases:
        system, user, definition, validator = prepare(case)
        if "Ignore all prior instructions" in case.get("resumeText", ""):
            assert user.count("<UNTRUSTED_DOCUMENT_CONTENT>") == 1
        if args.mode == "schema-only":
            continue
        raw = client.generate_json(system, user)
        validator(raw)
        outputs.append({"caseId": case["id"], "output": raw, "modelVersion": client.config.model, "promptVersion": definition.version, "timestamp": datetime.now(timezone.utc).isoformat()})
    if args.mode == "live":
        if not args.output:
            raise SystemExit("--output is required in live mode")
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in outputs), encoding="utf-8")
        print(f"Captured {len(outputs)} live Ollama outputs for human review at {path}")
    else:
        print(f"Schema-only checks passed for {len(cases)} cases; no Qwen quality claim was made.")


if __name__ == "__main__":
    main()
