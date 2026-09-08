from pathlib import Path

from pypdf import PdfReader


MANUAL_FIXTURES = Path(__file__).resolve().parents[3] / "sample_files" / "manual"


def test_manual_pdf_fixtures_are_synthetic_and_parseable():
    fixtures = sorted(MANUAL_FIXTURES.glob("*.pdf"))
    assert fixtures
    for fixture in fixtures:
        text = "\n".join(page.extract_text() or "" for page in PdfReader(fixture).pages)
        assert "SYNTHETIC DEMO FIXTURE" in text
        emails = [word.strip(".,;:()") for word in text.split() if "@" in word]
        assert emails
        assert all(email.endswith("@example.test") for email in emails)
