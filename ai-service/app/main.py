from typing import Optional
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.schemas import (
    HealthResponse,
    MatchResult,
    ResumeAnalysisResult,
)

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
    "/api/analyze-resume",
    response_model=ResumeAnalysisResult,
    summary="Analyze resume PDF",
    tags=["Analysis"],
)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume PDF file (max 5 MB)"),
) -> ResumeAnalysisResult:
    """Extract features, classify field, score resume, and provide recommendations."""
    # Stubs for D2 - actual pipeline implementation is in later tasks
    raise NotImplementedError("Pipeline implementation will be integrated in D7-D8")


@app.post(
    "/api/analyze-match",
    response_model=MatchResult,
    summary="Match resume with job description",
    tags=["Matching"],
)
async def analyze_match(
    file: UploadFile = File(..., description="Resume PDF file (max 5 MB)"),
    job_description: str = Form(..., alias="jobDescription", min_length=50, description="Job description text"),
    target_role: Optional[str] = Form(None, alias="targetRole", description="Target role name (optional)"),
) -> MatchResult:
    """Match resume features against job description skills and ATS criteria."""
    # Stubs for D2 - actual pipeline implementation is in later tasks
    raise NotImplementedError("Pipeline implementation will be integrated in D7-D8")
