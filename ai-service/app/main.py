


from __future__ import annotations

import time
import logging
from typing import Annotated, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.document.parser import extract_pdf_content
from app.extraction.classifier import classify_features
from app.extraction.features import extract_features
from app.extraction.router import router as extraction_router
from app.ml.classifier import classify_resume_features_ml
from app.ml.model_loader import get_model_metadata, load_classifier_model
from app.matching.embedding import EMBEDDING_MODEL_ID, load_embedding_model
from app.llm.client import OllamaClient, OllamaClientError
from app.llm.prompts import (
    build_jd_matching_prompt,
    build_resume_recommendation_prompt,
    validate_and_sanitize_match_insights,
    validate_and_sanitize_resume_recommendations,
)
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

import threading

app.include_router(extraction_router, prefix="/api")

_ollama_client: Optional[OllamaClient] = None
logger = logging.getLogger('uvicorn.error')


def _log_enrichment_failure(operation: str, error: Exception) -> None:
    # Exception messages can contain document text or remote response bodies.
    code = error.code.value if isinstance(error, OllamaClientError) else 'INTERNAL_ERROR'
    logger.warning('ollama_fallback operation=%s code=%s', operation, code)


def _timed_call(stage, function, *args, **kwargs):
    started = time.monotonic()
    try:
        return function(*args, **kwargs)
    finally:
        logger.info('ai_stage stage=%s elapsed_ms=%d', stage, int((time.monotonic() - started) * 1000))


def get_ollama_client() -> OllamaClient:
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


def set_ollama_client(client: Optional[OllamaClient]) -> None:
    global _ollama_client
    _ollama_client = client


@app.on_event("startup")
def startup_warmup() -> None:
    """Preload Ollama model in background on app startup to prevent cold-starts."""
    def _do_warmup() -> None:
        try:
            client = get_ollama_client()
            client.warmup()
        except Exception as error:
            _log_enrichment_failure('warmup', error)

    threading.Thread(target=_do_warmup, daemon=True).start()


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["Health"],
)
def health_check() -> HealthResponse:
    client = get_ollama_client()
    ollama_reachable = False
    try:
        res = client._session.get(f"{client.config.base_url}/api/tags", timeout=2.0)
        ollama_reachable = res.status_code == 200
    except Exception:
        ollama_reachable = False

    classifier_loaded = load_classifier_model() is not None
    embedding_loaded = load_embedding_model() is not None

    return HealthResponse(
        status="healthy",
        model=client.config.model,
        ollama_reachable=ollama_reachable,
        classifierLoaded=classifier_loaded,
        classifierModel=(get_model_metadata() or {}).get("modelType") if classifier_loaded else None,
        embeddingModelLoaded=embedding_loaded,
        embeddingModel=EMBEDDING_MODEL_ID if embedding_loaded else None,
    )


def _enrich_resume_with_llm(
    client: OllamaClient,
    resume_text: str,
    features: SchemaResumeFeatures,
    score_breakdown: ScoreBreakdown,
    rule_recs: dict,
) -> tuple[list[str], list[str], bool, str]:
    """Attempt to enrich recommendations using Ollama v2 prompt; fall back gracefully on failure."""
    system_prompt, user_prompt, prompt_def = build_resume_recommendation_prompt(
        resume_text=resume_text,
        features=features,
        score_breakdown=score_breakdown,
    )
    try:
        data = client.generate_json(system_prompt, user_prompt)
        final_skills, final_recs = validate_and_sanitize_resume_recommendations(
            raw_response=data,
            existing_skills=list(features.skills),
            rule_fallback=rule_recs,
        )
        return final_skills, final_recs, False, client.config.model
    except Exception as error:
        _log_enrichment_failure('resume', error)

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
    """Attempt to enrich match insights with Ollama v2 prompt; fall back gracefully on failure."""
    system_prompt, user_prompt, prompt_def = build_jd_matching_prompt(
        resume_text=resume_text,
        features=features,
        job_description=job_description,
        target_role=target_role,
        rule_match=rule_match,
    )
    try:
        data = client.generate_json(system_prompt, user_prompt)
        ats, strengths, weaknesses, recs = validate_and_sanitize_match_insights(
            raw_response=data,
            rule_match=rule_match,
        )
        return ats, strengths, weaknesses, recs, False, client.config.model
    except Exception as error:
        _log_enrichment_failure('match', error)

    return (
        list(rule_match.ats_keywords)[:15],
        list(rule_match.strengths)[:6],
        list(rule_match.weaknesses)[:6],
        list(rule_match.recommendations)[:8],
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
    parsed_doc = await run_in_threadpool(_timed_call, 'resume_parse', extract_pdf_content, file_bytes, file.filename or "resume.pdf")

    # 1. Feature extraction & field classification
    raw_features = await run_in_threadpool(_timed_call, 'feature_extraction', extract_features, parsed_doc.text)
    classified_features = await run_in_threadpool(_timed_call, 'classification', classify_resume_features_ml, parsed_doc.text, raw_features)

    field_evidence = [
        SchemaFieldEvidence(
            field=FieldEnum(ev["field"]) if ev["field"] in [f.value for f in FieldEnum] else FieldEnum.UNKNOWN,
            matchedSkills=ev.get("matchedSkills", []),
            confidence=float(ev.get("confidence", 0.0)),
            topTerms=ev.get("topTerms", []),
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
    rec_skills, rec_texts, used_fallback, model_name = await run_in_threadpool(
        _timed_call, 'resume_enrichment', _enrich_resume_with_llm,
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
    jdFile: Annotated[
        Optional[UploadFile],
        File(description="Job description PDF file (max 5 MB, optional if jobDescription is provided)"),
    ] = None,
    jobDescription: Annotated[
        Optional[str],
        Form(
            description="Job description text (optional if jdFile is provided)",
        ),
    ] = None,
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

    jd_text = ""
    jd_file_name: Optional[str] = None

    if jdFile is not None and jdFile.filename:
        await validate_pdf_file(jdFile)
        jd_bytes = await jdFile.read()
        parsed_jd = await run_in_threadpool(_timed_call, 'jd_parse', extract_pdf_content, jd_bytes, jdFile.filename)
        jd_text = parsed_jd.text.strip() if parsed_jd.text else ""
        jd_file_name = jdFile.filename
    elif jobDescription and jobDescription.strip():
        jd_text = jobDescription.strip()
    else:
        raise HTTPException(
            status_code=422,
            detail="Job description text or valid JD PDF file is required",
        )

    if len(jd_text) < 50:
        raise HTTPException(
            status_code=422,
            detail="Job description must contain at least 50 characters",
        )

    file_bytes = await file.read()
    parsed_doc = await run_in_threadpool(_timed_call, 'resume_parse', extract_pdf_content, file_bytes, file.filename or "resume.pdf")

    # 1. Feature extraction
    raw_features = await run_in_threadpool(_timed_call, 'feature_extraction', extract_features, parsed_doc.text)
    classified_features = await run_in_threadpool(_timed_call, 'classification', classify_resume_features_ml, parsed_doc.text, raw_features)

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

    # 2. Deterministic & Hybrid matching
    rule_match = await run_in_threadpool(
        _timed_call, 'matching', match_resume_to_job,
        file_name=parsed_doc.fileName,
        jd_file_name=jd_file_name,
        resume_skills=schema_features.skills,
        job_description=jd_text,
        resume_text=parsed_doc.text,
        target_role=targetRole,
    )

    # 3. Hybrid LLM enrichment & fallback
    client = get_ollama_client()
    ats_keywords, strengths, weaknesses, recommendations, used_fallback, model_name = await run_in_threadpool(
        _timed_call, 'match_enrichment', _enrich_match_with_llm,
        client=client,
        resume_text=parsed_doc.text,
        features=schema_features,
        job_description=jd_text,
        target_role=rule_match.target_role,
        rule_match=rule_match,
    )

    elapsed_ms = int((time.monotonic() - start_time) * 1000)

    return MatchResult(
        fileName=parsed_doc.fileName,
        jdFileName=jd_file_name,
        targetRole=rule_match.target_role,
        matchScore=rule_match.match_score,
        matchedSkills=rule_match.matched_skills,
        missingSkills=rule_match.missing_skills,
        atsKeywords=ats_keywords,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        matchBreakdown=rule_match.match_breakdown,
        ai=AiMetadata(
            provider=AiProvider.RULE_BASED if used_fallback else AiProvider.OLLAMA,
            model=model_name,
            usedFallback=used_fallback,
            processingMs=max(0, elapsed_ms),
        ),
    )
