import pytest
from fastapi import UploadFile
from io import BytesIO
from app.validation import validate_pdf_file

@pytest.mark.asyncio
async def test_valid_pdf():
    content = b"%PDF-1.4 sample pdf content..."
    upload_file = UploadFile(file=BytesIO(content), filename="resume.pdf")
    
    result = await validate_pdf_file(upload_file)
    assert result is True

@pytest.mark.asyncio
async def test_invalid_magic_bytes():
    content = b"NOT_A_PDF_FILE"
    upload_file = UploadFile(file=BytesIO(content), filename="fake.pdf")
    
    with pytest.raises(Exception) as exc_info:
        await validate_pdf_file(upload_file)
    assert exc_info.value.status_code == 422