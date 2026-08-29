import pytest
from app.document.parser import extract_pdf_content, sanitize_filename, normalize_text
from app.exceptions import ApiError

def test_sanitize_filename():
    assert sanitize_filename("CV_Nguyen_Van_A (1)!.pdf") == "CV_Nguyen_Van_A_1_.pdf"

def test_normalize_text():
    raw = "Python   Developer \n\n with 3+ years experience."
    assert normalize_text(raw) == "Python Developer with 3+ years experience."

def test_extract_empty_pdf_raises_error():
    fake_empty_bytes = b"%PDF-1.4 empty content"
    with pytest.raises(ApiError) as exc_info:
        extract_pdf_content(fake_empty_bytes, "empty.pdf")
    assert exc_info.value.status_code in [400, 422]