import pytest
from app.document.parser import extract_pdf_content, sanitize_filename, normalize_text
from app.exceptions import ApiError

def test_sanitize_filename():
    assert sanitize_filename("CV_Nguyen_Van_A (1)!.pdf") == "CV_Nguyen_Van_A_1_.pdf"

def test_normalize_text():
    raw = "JOHN   DOE\n\nEXPERIENCE\nBuilt APIs"
    expected = "JOHN DOE\n\nEXPERIENCE\nBuilt APIs"
    assert normalize_text(raw) == expected

def test_normalize_text_preserves_single_and_double_newlines():
    raw = "Line 1   with spaces\nLine 2\n\nLine 3 after break"
    expected = "Line 1 with spaces\nLine 2\n\nLine 3 after break"
    assert normalize_text(raw) == expected

def test_extract_empty_pdf_raises_error():
    fake_empty_bytes = b"%PDF-1.4 empty content"
    with pytest.raises(ApiError) as exc_info:
        extract_pdf_content(fake_empty_bytes, "empty.pdf")
    assert exc_info.value.status_code in [400, 422]