"""Generate parseable, synthetic text-PDF fixtures for manual demos.

These files deliberately contain only placeholder contact data and are never
inputs to training or evaluation datasets.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "sample_files" / "manual"


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def text_pdf(lines: list[str]) -> bytes:
    stream_lines = ["BT", "/F1 11 Tf", "72 740 Td", "15 TL"]
    for index, line in enumerate(lines):
        if index:
            stream_lines.append("T*")
        stream_lines.append(f"({escape_pdf_text(line)}) Tj")
    stream_lines.append("ET")
    stream = "\n".join(stream_lines).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    output = bytearray(b"%PDF-1.4\n% synthetic fixture\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f\n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n\n".encode())
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(output)


def main() -> None:
    for path in sorted(FIXTURES.glob("*.pdf")):
        role = "resume" if "CV" in path.name else "job-description"
        lines = [
            "SYNTHETIC DEMO FIXTURE - NOT FOR TRAINING OR EVALUATION",
            f"Fixture file: {path.name}",
            f"Synthetic {role} sample for local upload demonstrations.",
            "Contact: demo.candidate@example.test",
            "Skills: Python, SQL, Docker, machine learning, communication.",
            "All names, contact details, and claims in this fixture are placeholders.",
        ]
        path.write_bytes(text_pdf(lines))
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
