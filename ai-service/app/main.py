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