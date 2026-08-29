from typing import Annotated, Optional
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.schemas import (
    HealthResponse,
    MatchResult,
    ParsedDocument,
    ResumeAnalysisResult,
    ResumeFeatures,
)
from app.extraction.features import extract_features
from app.extraction.classifier import classify_features
from app.validation import validate_pdf_file

app = FastAPI(
    title="AI Resume Analyzer - AI Service",
    description="Internal AI service for CV parsing, extraction, scoring, matching, and Ollama orchestration.",
    version="1.0.0",
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Return health status and model availability."""
    return HealthResponse(
        status="healthy",
        model="qwen3:4b",
        ollamaReachable=False,
    )


@app.post(
    "/api/extract-features",
    response_model=ResumeFeatures,
    summary="Extract resume features from parsed document",
    tags=["Extraction"],
)
async def extract_resume_features(document: ParsedDocument) -> ResumeFeatures:
    """Extract candidate metadata, canonical skills, and predicted field."""
    extracted = extract_features(document.text)
    classified = classify_features(extracted)
    return ResumeFeatures(
        candidateName=classified.candidate_name,
        candidateEmail=classified.candidate_email,
        skills=classified.skills,
        predictedField=classified.predicted_field,
        fieldEvidence=classified.field_evidence or [],
    )


@app.post(
    "/api/analyze-resume",
    response_model=ResumeAnalysisResult,
    summary="Analyze resume PDF",
    tags=["Analysis"],
)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume PDF file (max 5 MB)"),
) -> ResumeAnalysisResult:
    """Extract features, classify field, score resume, and provide recommendations."""
    # Kiểm tra tính hợp lệ của file PDF (dung lượng và magic bytes)
    await validate_pdf_file(file)
    
    # Stubs for D2 - actual pipeline implementation is in later tasks
    raise NotImplementedError("Pipeline implementation will be integrated in D7-D8")


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
    job_description: Annotated[
        str,
        Form(
            alias="jobDescription",
            min_length=50,
            description="Job description text",
        ),
    ],
    target_role: Annotated[
        Optional[str],
        Form(
            alias="targetRole",
            description="Target role name (optional)",
        ),
    ] = None,
) -> MatchResult:
    """Match resume features against job description skills and ATS criteria."""
    # Kiểm tra tính hợp lệ của file PDF trước khi match
    await validate_pdf_file(file)
    
    # Stubs for D2 - actual pipeline implementation is in later tasks
    raise NotImplementedError("Pipeline implementation will be integrated in D7-D8")