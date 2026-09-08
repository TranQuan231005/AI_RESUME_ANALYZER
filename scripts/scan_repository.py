#!/usr/bin/env python3
"""Fail on common committed secrets, evaluation PII, or broken relative Markdown links."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SECRET_PATTERNS = [
    re.compile(rb"ghp_[A-Za-z0-9]{20,}"),
    re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,})\b", re.IGNORECASE)
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def tracked_files() -> list[Path]:
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    return [ROOT / name for name in names if (ROOT / name).is_file()]


def markdown_link_error(path: Path, raw_target: str) -> str | None:
    """Return a concise hygiene error for a Markdown link, if any."""
    target = raw_target.split("#", 1)[0]
    if not target or target.startswith("mailto:"):
        return None
    if target.casefold().startswith("file:"):
        return "local file URL"
    if "://" in target:
        return None
    if not (path.parent / target).resolve().exists():
        return f"missing relative target: {target}"
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-history", action="store_true")
    args = parser.parse_args()
    errors = []
    for path in tracked_files():
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            errors.append(f"secret pattern: {path.relative_to(ROOT)}")
        if "evaluation" in path.parts and path.suffix.lower() in {".json", ".jsonl", ".csv", ".md"}:
            text = data.decode("utf-8", errors="ignore")
            for match in EMAIL.finditer(text):
                if match.group(1).casefold() not in {"example.test", "example.com", "example.org"}:
                    errors.append(f"non-placeholder email: {path.relative_to(ROOT)}")
                    break
        if path.suffix.lower() == ".md":
            text = data.decode("utf-8", errors="ignore")
            for raw_target in LINK.findall(text):
                link_error = markdown_link_error(path, raw_target)
                if link_error:
                    errors.append(
                        f"invalid link in {path.relative_to(ROOT)}: {raw_target} ({link_error})"
                    )
    if args.check_history:
        affected = subprocess.check_output(
            ["git", "log", "--all", "--format=%h", "--", "scripts/config.yml"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        if affected:
            errors.append(f"scripts/config.yml remains in {len(affected)} historical commit(s)")
    if errors:
        raise SystemExit("Repository scan failed:\n- " + "\n- ".join(sorted(set(errors))))
    print("Repository secret/PII/link scan passed.")


if __name__ == "__main__":
    main()
