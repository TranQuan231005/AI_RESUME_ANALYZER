from typing import Annotated, Optional
from fastapi import FastAPI, UploadFile, File, Form
from app.schemas.matching import MatchResult
from app.validation import validate_pdf_file
from app.extraction.router import router as extraction_router

app = FastAPI(title="AI Service Contract API")

app.include_router(extraction_router, prefix="/api")

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
    await validate_pdf_file(file)
    
    raise NotImplementedError("Pipeline implementation will be integrated in D7-D8")