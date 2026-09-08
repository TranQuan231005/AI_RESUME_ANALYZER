import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "smoke_stack.py"
spec = importlib.util.spec_from_file_location("smoke_stack", SCRIPT)
smoke = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(smoke)


def test_multipart_includes_form_fields_and_pdf_bytes(tmp_path):
    resume = tmp_path / "resume.pdf"
    resume.write_bytes(b"%PDF-demo")

    payload, content_type = smoke.multipart({"jobDescription": "safe JD"}, {"file": resume})

    assert "multipart/form-data; boundary=" in content_type
    assert b'name="jobDescription"' in payload
    assert b'filename="resume.pdf"' in payload
    assert b"%PDF-demo" in payload
