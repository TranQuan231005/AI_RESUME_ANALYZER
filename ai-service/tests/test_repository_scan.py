"""Regression checks for repository Markdown-link hygiene."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "scan_repository.py"
SPEC = importlib.util.spec_from_file_location("scan_repository", SCRIPT_PATH)
assert SPEC and SPEC.loader
scan_repository = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scan_repository)


def test_local_file_url_is_rejected():
    assert scan_repository.markdown_link_error(
        ROOT / "README.md", "file:///d:/AI_RESUME_ANALYZER/docs/project/OLLAMA_LOCAL_DEMO.md"
    ) == "local file URL"


def test_https_and_relative_markdown_links_are_allowed_when_resolvable():
    assert scan_repository.markdown_link_error(ROOT / "README.md", "https://example.test/docs") is None
    assert scan_repository.markdown_link_error(ROOT / "README.md", "docs/project/OLLAMA_LOCAL_DEMO.md") is None
