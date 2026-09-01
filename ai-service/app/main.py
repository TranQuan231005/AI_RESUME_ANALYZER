from __future__ import annotations

import time
from typing import Annotated, Optional

from fastapi import FastAPI, File, Form, UploadFile

from app.document.parser import extract_pdf_content
from app.extraction.classifier import classify_features
from app.extraction.features import extract_features
from app.extraction.router import router as extraction_router
from app.llm.client import OllamaClient
from app.matching.engine import match_resume_to_job
from app.recommendation.engine import generate_recommendations
from app.schemas import (
    AiMetadata,
    AiProvider,
    FieldEnum,
    HealthResponse,
    MatchResult,
    ResumeAnalysisResult,
    ResumeFeatures as SchemaResumeFeatures,
    ScoreBreakdown,
)
from app.schemas.features import FieldEvidence as SchemaFieldEvidence
from app.scoring.engine import calculate_score
from app.validation import validate_pdf_file

app = FastAPI(
    title="AI Service Contract API",
    description="AI Service for Resume Parsing, Feature Extraction, Rubric Scoring, JD Matching, and Ollama Hybrid Enrichment.",
    version="1.0.0",
)

app.include_router(extraction_router, prefix="/api")

_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def set_ollama_client(client: Optional[OllamaClient]) -> None:
    global _ollama_client
    _ollama_client = client


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    client = get_ollama_client()
    ollama_reachable = False
    try:
        res = client._session.get(f"{client.config.base_url}/api/tags", timeout=2.0)
        ollama_reachable = res.status_code == 200
    except Exception:
        ollama_reachable = False

    return HealthResponse(
        status="healthy",
        model=client.config.model,
        ollama_reachable=ollama_reachable,
    )


def _enrich_resume_with_llm(
    client: OllamaClient,
    resume_text: str,
    features: SchemaResumeFeatures,
    score_breakdown: ScoreBreakdown,
    rule_recs: dict,
) -> tuple[list[str], list[str], bool, str]:
    """Attempt to enrich recommendations using Ollama; fall back gracefully on failure."""
    system_prompt = (
        "You are an expert technical recruiter and resume reviewer. "
        "Analyze the provided resume details and return actionable recommendations. "
        "You MUST respond ONLY with a valid JSON object in this exact schema:\n"
        "{\n"
        '  "recommendedSkills": ["skill1", "skill2"],\n'
        '  "recommendations": ["advice 1", "advice 2"]\n'
        "}\n"
        "Constraints:\n"
        "- recommendedSkills: array of up to 8 strings.\n"
        "- recommendations: array of up to 8 concise improvement bullet points.\n"
        "- Do not include markdown fences or any text outside the JSON object."
    )
    user_prompt = (
        f"Candidate Field: {features.predicted_field}\n"
        f"Current Skills: {', '.join(features.skills) if features.skills else 'None'}\n"
        f"Total Score: {score_breakdown.total}/100\n"
        f"Score Breakdown: Contact={score_breakdown.contact}/5, Summary={score_breakdown.summary}/10, "
        f"Skills={score_breakdown.skills}/15, Education={score_breakdown.education}/10, "
        f"Experience={score_breakdown.experience}/20, Projects={score_breakdown.projects}/15, "
        f"Certifications={score_breakdown.achievements_certifications}/10, "
        f"Impact={score_breakdown.quantified_impact}/15\n\n"
        f"Resume Text Excerpt:\n{resume_text[:2000]}"
    )
    try:
        data = client.generate_json(system_prompt, user_prompt)
        llm_skills = data.get("recommendedSkills")
        llm_recs = data.get("recommendations")
        if isinstance(llm_skills, list) and isinstance(llm_recs, list):
            cleaned_skills = [str(s).strip() for s in llm_skills if s and str(s).strip()][:8]
            cleaned_recs = [str(r).strip() for r in llm_recs if r and str(r).strip()][:8]
            final_skills = cleaned_skills if cleaned_skills else rule_recs.get("recommendedSkills", [])[:8]
            final_recs = cleaned_recs if cleaned_recs else rule_recs.get("recommendations", [])[:8]
            return final_skills[:8], final_recs[:8], False, client.config.model
    except Exception:
        pass

    return (
        rule_recs.get("recommendedSkills", [])[:8],
        rule_recs.get("recommendations", [])[:8],
        True,
        "deterministic-v1",
    )


def _enrich_match_with_llm(
    client: OllamaClient,
    resume_text: str,
    features: SchemaResumeFeatures,
    job_description: str,
    target_role: str,
    rule_match: MatchResult,
) -> tuple[list[str], list[str], list[str], list[str], bool, str]:
    """Attempt to enrich match insights with Ollama; fall back gracefully on failure."""
    system_prompt = (
        "You are an expert ATS (Applicant Tracking System) parser and senior technical recruiter. "
        "Analyze the candidate's resume against the target job description. "
        "You MUST respond ONLY with a valid JSON object in this exact schema:\n"
        "{\n"
        '  "atsKeywords": ["keyword1", "keyword2"],\n'
        '  "strengths": ["strength 1", "strength 2"],\n'
        '  "weaknesses": ["gap 1", "gap 2"],\n'
        '  "recommendations": ["recommendation 1", "recommendation 2"]\n'
        "}\n"
        "Constraints:\n"
        "- atsKeywords: array of up to 15 strings (high-priority keywords from JD).\n"
        "- strengths: array of up to 6 strings highlighting candidate qualifications.\n"
        "- weaknesses: array of up to 6 strings highlighting missing qualifications/skills.\n"
        "- recommendations: array of up to 8 actionable suggestions for tailoring the CV.\n"
        "- Do not include markdown fences or any text outside the JSON object."
    )
    user_prompt = (
        f"Target Role: {target_role}\n"
        f"Candidate Extracted Skills: {', '.join(features.skills) if features.skills else 'None'}\n"
        f"Matched Skills: {', '.join(rule_match.matched_skills)}\n"
        f"Missing Skills: {', '.join(rule_match.missing_skills)}\n"
        f"Rule Match Score: {rule_match.match_score}%\n\n"
        f"Job Description:\n{job_description[:2500]}\n\n"
        f"Resume Text Excerpt:\n{resume_text[:2000]}"
    )
    try:
        data = client.generate_json(system_prompt, user_prompt)
        ats_keywords = data.get("atsKeywords")
        strengths = data.get("strengths")
        weaknesses = data.get("weaknesses")
        recommendations = data.get("recommendations")
        if (
            isinstance(ats_keywords, list)
            and isinstance(strengths, list)
            and isinstance(weaknesses, list)
            and isinstance(recommendations, list)
        ):
            cleaned_ats = [str(k).strip() for k in ats_keywords if k and str(k).strip()][:15]
            cleaned_str = [str(s).strip() for s in strengths if s and str(s).strip()][:6]
            cleaned_weak = [str(w).strip() for w in weaknesses if w and str(w).strip()][:6]
            cleaned_recs = [str(r).strip() for r in recommendations if r and str(r).strip()][:8]
            return (
                cleaned_ats,
                cleaned_str,
                cleaned_weak,
                cleaned_recs if cleaned_recs else rule_match.recommendations[:8],
                False,
                client.config.model,
            )
    except Exception:
        pass

    return (
        [],
        [],
        [],
        rule_match.recommendations[:8],
        True,
        "deterministic-v1",
    )


@app.post(
    "/api/analyze-resume",
    response_model=ResumeAnalysisResult,
    summary="Analyze resume PDF",
    tags=["Resume Analysis"],
)
async def analyze_resume(
    file: Annotated[
        UploadFile,
        File(description="Resume PDF file (max 5 MB)"),
    ],
) -> ResumeAnalysisResult:
    """Analyze resume PDF: validate, extract features, compute rubric scores and enrich with LLM."""
    start_time = time.monotonic()
    await validate_pdf_file(file)

    file_bytes = await file.read()
    parsed_doc = extract_pdf_content(file_bytes, file.filename or "resume.pdf")

    # 1. Feature extraction & field classification
    raw_features = extract_features(parsed_doc.text)
    classified_features = classify_features(raw_features)

    field_evidence = [
        SchemaFieldEvidence(
            field=FieldEnum(ev["field"]) if ev["field"] in [f.value for f in FieldEnum] else FieldEnum.UNKNOWN,
            matchedSkills=ev.get("matchedSkills", []),
            confidence=float(ev.get("confidence", 0.0)),
        )
        for ev in (classified_features.field_evidence or [])
    ]

    predicted_enum = (
        FieldEnum(classified_features.predicted_field)
        if classified_features.predicted_field in [f.value for f in FieldEnum]
        else FieldEnum.UNKNOWN
    )

    schema_features = SchemaResumeFeatures(
        candidateName=classified_features.candidate_name,
        candidateEmail=classified_features.candidate_email,
        skills=list(classified_features.skills),
        predictedField=predicted_enum,
        fieldEvidence=field_evidence,
    )

    # 2. Rule scoring & recommendations
    score_breakdown = calculate_score(parsed_doc, schema_features)
    rule_recs = generate_recommendations(
        score_breakdown.model_dump(by_alias=False),
        schema_features.skills,
        schema_features.predicted_field.value if isinstance(schema_features.predicted_field, FieldEnum) else str(schema_features.predicted_field),
    )

    # 3. Hybrid LLM enrichment & fallback
    client = get_ollama_client()
    rec_skills, rec_texts, used_fallback, model_name = _enrich_resume_with_llm(
        client=client,
        resume_text=parsed_doc.text,
        features=schema_features,
        score_breakdown=score_breakdown,
        rule_recs=rule_recs,
    )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return ResumeAnalysisResult(
        fileName=parsed_doc.fileName,
        candidateName=schema_features.candidate_name,
        candidateEmail=schema_features.candidate_email,
        skills=schema_features.skills,
        predictedField=schema_features.predicted_field,
        fieldEvidence=schema_features.field_evidence,
        resumeScore=score_breakdown.total,
        scoreBreakdown=score_breakdown,
        recommendedSkills=rec_skills,
        recommendations=rec_texts,
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED if used_fallback else AiProvider.OLLAMA,
            model=model_name,
            usedFallback=used_fallback,
            processingMs=max(0, elapsed_ms),
        ),
    )


@app.post(
    "/api/analyze-match",
    response_model=MatchResult,
    summary="Match resume with job description",
    tags=["Matching"],
)
async def analyze_match(
    file: Annotated[
        UploadFile,
        File(description="Resume PDF file (max 5 MB)"),
    ],
    jobDescription: Annotated[
        str,
        Form(
            min_length=50,
            description="Job description text",
        ),
    ],
    targetRole: Annotated[
        Optional[str],
        Form(
            description="Target role name (optional)",
        ),
    ] = None,
) -> MatchResult:
    """Match resume features against job description skills and ATS criteria."""
    start_time = time.monotonic()
    await validate_pdf_file(file)

    file_bytes = await file.read()
    parsed_doc = extract_pdf_content(file_bytes, file.filename or "resume.pdf")

    # 1. Feature extraction
    raw_features = extract_features(parsed_doc.text)
    classified_features = classify_features(raw_features)

    predicted_enum = (
        FieldEnum(classified_features.predicted_field)
        if classified_features.predicted_field in [f.value for f in FieldEnum]
        else FieldEnum.UNKNOWN
    )

    schema_features = SchemaResumeFeatures(
        candidateName=classified_features.candidate_name,
        candidateEmail=classified_features.candidate_email,
        skills=list(classified_features.skills),
        predictedField=predicted_enum,
        fieldEvidence=[],
    )

    # 2. Deterministic rule matching
    rule_match = match_resume_to_job(
        file_name=parsed_doc.fileName,
        resume_skills=schema_features.skills,
        job_description=jobDescription,
        target_role=targetRole,
    )

    # 3. Hybrid LLM enrichment & fallback
    client = get_ollama_client()
    ats_keywords, strengths, weaknesses, recommendations, used_fallback, model_name = _enrich_match_with_llm(
        client=client,
        resume_text=parsed_doc.text,
        features=schema_features,
        job_description=jobDescription,
        target_role=rule_match.target_role,
        rule_match=rule_match,
    )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return MatchResult(
        fileName=parsed_doc.fileName,
        targetRole=rule_match.target_role,
        matchScore=rule_match.match_score,
        matchedSkills=rule_match.matched_skills,
        missingSkills=rule_match.missing_skills,
        atsKeywords=ats_keywords,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED if used_fallback else AiProvider.OLLAMA,
            model=model_name,
            usedFallback=used_fallback,
            processingMs=max(0, elapsed_ms),
        ),
    )