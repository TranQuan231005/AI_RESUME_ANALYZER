"""Full-stack Compose smoke test for the five public API flows.

The script intentionally uses only standard-library HTTP so it runs in local
development and GitHub Actions after ``docker compose up``.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = "AUDIT_JD_SENTINEL_7F8D4C"


def request_json(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None,
                 token: str | None = None, body: bytes | None = None, content_type: str | None = None,
                 timeout_seconds: int = 20) -> tuple[int, Any]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        content_type = "application/json"
    if content_type:
        headers["Content-Type"] = content_type
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            try:
                return response.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return response.status, raw
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            return error.code, json.loads(raw)
        except json.JSONDecodeError:
            return error.code, raw


def multipart(fields: dict[str, str], files: dict[str, Path]) -> tuple[bytes, str]:
    boundary = f"----resume-smoke-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([f"--{boundary}\r\n".encode(), f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(), value.encode(), b"\r\n"])
    for name, path in files.items():
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'.encode(),
            f"Content-Type: {mime}\r\n\r\n".encode(), path.read_bytes(), b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wait_for(url: str, name: str, seconds: int = 180) -> Any:
    deadline = time.monotonic() + seconds
    last_status = "no response"
    while time.monotonic() < deadline:
        try:
            status, payload = request_json(url)
            last_status = f"HTTP {status}"
            if status == 200:
                return payload
        except (OSError, ValueError) as error:
            last_status = str(error)
        time.sleep(3)
    raise RuntimeError(f"{name} did not become healthy within {seconds}s ({last_status})")


def login(base_url: str, email: str, password: str) -> str:
    status, response = request_json(f"{base_url}/api/auth/login", method="POST", payload={"email": email, "password": password})
    require(status == 200 and isinstance(response, dict) and response.get("accessToken"), f"login failed for {email}: HTTP {status}")
    return response["accessToken"]


def assert_no_raw_storage(db_name: str, db_root_password: str) -> None:
    query = "SELECT result_json FROM analysis_results;"
    command = ["docker", "compose", "exec", "-T", "mysql", "mysql", "-uroot", f"-p{db_root_password}", "-D", db_name, "--batch", "--skip-column-names", "--raw", "-e", query]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    require(result.returncode == 0, f"privacy query failed: {result.stderr.strip()}")
    forbidden = {"resumeText", "jobDescription", "text"}
    def contains_forbidden_key(value: Any) -> bool:
        if isinstance(value, dict):
            return bool(forbidden.intersection(value)) or any(contains_forbidden_key(item) for item in value.values())
        if isinstance(value, list):
            return any(contains_forbidden_key(item) for item in value)
        return False
    for line in result.stdout.splitlines():
        require(not contains_forbidden_key(json.loads(line)), "raw resume/JD text field was persisted in result_json")


def assert_logs_safe() -> None:
    result = subprocess.run(["docker", "compose", "logs", "--no-color"], cwd=ROOT, capture_output=True, text=True, check=False)
    require(result.returncode == 0, f"could not read Compose logs: {result.stderr.strip()}")
    require(SENTINEL not in result.stdout, "smoke-test JD sentinel appeared in Compose logs")
    ai_logs = subprocess.run(["docker", "compose", "logs", "--no-color", "ai-service"], cwd=ROOT, capture_output=True, text=True, check=False)
    require(ai_logs.returncode == 0, f"could not read AI-service logs: {ai_logs.stderr.strip()}")
    forbidden = ("huggingface.co", "Downloading model")
    require(not any(value.casefold() in ai_logs.stdout.casefold() for value in forbidden), "AI runtime attempted an embedding-model download")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai-url", default="http://localhost:8000")
    parser.add_argument("--backend-url", default="http://localhost:8080")
    parser.add_argument("--frontend-url", default="http://localhost:5173")
    parser.add_argument("--resume", default="sample_files/resumes/01_data_science_senior.pdf")
    parser.add_argument("--db-name", default=os.environ.get("DB_NAME", "resume_analyzer"))
    parser.add_argument("--db-root-password", default=os.environ.get("DB_ROOT_PASSWORD", "rootpassword"))
    parser.add_argument("--check-mysql-privacy", action="store_true")
    parser.add_argument("--check-logs", action="store_true")
    args = parser.parse_args()
    resume = ROOT / args.resume
    require(resume.is_file(), f"resume fixture does not exist: {resume}")

    health = wait_for(f"{args.ai_url}/health", "AI service")
    require(health.get("classifierLoaded") is True and health.get("classifierModel"), "classifier health is incomplete")
    require(health.get("embeddingModelLoaded") is True and health.get("embeddingModel"), "embedding health is incomplete")
    wait_for(f"{args.backend_url}/health", "backend")
    frontend_status, _ = request_json(args.frontend_url)
    require(frontend_status < 500, f"frontend was not reachable: HTTP {frontend_status}")
    print("Smoke: service health passed.", flush=True)

    status, _ = request_json(f"{args.backend_url}/api/analyses")
    require(status == 401, f"analysis endpoint must require JWT, got HTTP {status}")
    user_token = login(args.backend_url, "user@example.test", "User@123456")
    admin_token = login(args.backend_url, "admin@example.test", "Admin@123456")
    print("Smoke: USER and ADMIN login passed.", flush=True)

    upload, content_type = multipart({}, {"file": resume})
    status, analysis = request_json(f"{args.backend_url}/api/analyses/resume", method="POST", token=user_token, body=upload, content_type=content_type, timeout_seconds=240)
    require(status == 201 and isinstance(analysis, dict) and analysis.get("id"), f"resume analysis failed: HTTP {status}")
    evidence = analysis.get("result", {}).get("fieldEvidence", [])
    require(bool(evidence) and "topTerms" in evidence[0], "resume response omitted classifier topTerms")
    print("Smoke: resume analysis passed.", flush=True)

    jd = f"{SENTINEL} Senior data scientist role requiring Python, SQL, Pandas, scikit-learn, model deployment, and stakeholder communication."
    upload, content_type = multipart({"jobDescription": jd, "targetRole": "Senior Data Scientist"}, {"file": resume})
    status, match = request_json(f"{args.backend_url}/api/analyses/match", method="POST", token=user_token, body=upload, content_type=content_type, timeout_seconds=240)
    require(status == 201 and isinstance(match, dict) and match.get("id"), f"JD matching failed: HTTP {status}")
    require(match.get("result", {}).get("matchBreakdown", {}).get("method") == "HYBRID_EMBEDDING", "match did not use HYBRID_EMBEDDING")
    print("Smoke: JD matching passed.", flush=True)
    if health.get("ollamaReachable") is False:
        for result in (analysis["result"], match["result"]):
            metadata = result.get("ai", {})
            require(metadata.get("usedFallback") is True and metadata.get("provider") == "RULE_BASED", "offline Ollama did not return deterministic fallback metadata")

    status, history = request_json(f"{args.backend_url}/api/analyses", token=user_token)
    require(status == 200 and history.get("totalItems", 0) >= 2, "analysis history omitted created records")
    status, detail = request_json(f"{args.backend_url}/api/analyses/{analysis['id']}", token=user_token)
    require(status == 200 and detail.get("id") == analysis["id"], "analysis detail was unavailable")

    status, _ = request_json(f"{args.backend_url}/api/admin/metrics", token=user_token)
    require(status == 403, f"USER token reached admin endpoint: HTTP {status}")
    for endpoint in ("users", "analyses", "metrics"):
        status, response = request_json(f"{args.backend_url}/api/admin/{endpoint}", token=admin_token)
        require(status == 200 and isinstance(response, dict), f"ADMIN {endpoint} endpoint failed: HTTP {status}")
    print("Smoke: history/detail, JWT, and admin passed.", flush=True)

    if args.check_mysql_privacy:
        assert_no_raw_storage(args.db_name, args.db_root_password)
    if args.check_logs:
        assert_logs_safe()
    print("Full-stack API smoke passed: login, resume, matching, history/detail, admin, health, privacy, and JWT gates.")


if __name__ == "__main__":
    main()
