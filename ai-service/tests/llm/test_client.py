from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterator, List, Tuple

import pytest

from app.llm import (
    OllamaClient,
    OllamaClientError,
    OllamaConfig,
    OllamaErrorCode,
)


ResponseSpec = Tuple[int, Any, float]


@contextmanager
def mock_ollama_server(
    response_specs: List[ResponseSpec],
) -> Iterator[Tuple[str, List[Dict[str, Any]]]]:
    recorded_requests: List[Dict[str, Any]] = []
    queued_responses = list(response_specs)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            content_length = int(self.headers.get("Content-Length", "0"))
            request_body = self.rfile.read(content_length)
            recorded_requests.append(
                {"path": self.path, "body": json.loads(request_body.decode("utf-8"))}
            )

            status, body, delay_seconds = queued_responses.pop(0)
            if delay_seconds:
                time.sleep(delay_seconds)
            encoded_body = (
                body
                if isinstance(body, bytes)
                else json.dumps(body).encode("utf-8")
            )

            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded_body)))
                self.end_headers()
                self.wfile.write(encoded_body)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", recorded_requests
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=1)


def make_client(base_url: str, timeout_seconds: float = 1.0) -> OllamaClient:
    return OllamaClient(
        OllamaConfig(base_url=base_url, timeout_seconds=timeout_seconds)
    )


def test_config_reads_environment_and_normalizes_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.test:11434/")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "12.5")

    config = OllamaConfig.from_env()

    assert config.base_url == "http://ollama.test:11434"
    assert config.model == "custom-model"
    assert config.timeout_seconds == 12.5
    assert config.temperature == 0.1


def test_valid_json_returns_object_and_sends_json_mode_payload() -> None:
    expected = {"recommendations": ["Add measurable impact"]}
    response = {"model": "qwen3:4b", "response": json.dumps(expected), "done": True}

    with mock_ollama_server([(200, response, 0)]) as (base_url, requests):
        result = make_client(base_url).generate_json("system rules", "resume data")

    assert result == expected
    assert len(requests) == 1
    assert requests[0]["path"] == "/api/generate"
    assert requests[0]["body"] == {
        "model": "qwen3:4b",
        "system": "system rules",
        "prompt": "resume data",
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }


def test_malformed_json_is_retried_once_then_succeeds() -> None:
    malformed = {"response": "not-json"}
    valid = {"response": json.dumps({"status": "ok"})}

    with mock_ollama_server([(200, malformed, 0), (200, valid, 0)]) as (
        base_url,
        requests,
    ):
        result = make_client(base_url).generate_json("system", "user")

    assert result == {"status": "ok"}
    assert len(requests) == 2


@pytest.mark.parametrize(
    "body",
    [
        b"not-an-envelope",
        {"response": "not-json"},
        {"response": json.dumps(["not", "an", "object"])},
    ],
)
def test_malformed_json_twice_is_classified(
    body: Any,
) -> None:
    with mock_ollama_server([(200, body, 0), (200, body, 0)]) as (
        base_url,
        requests,
    ):
        with pytest.raises(OllamaClientError) as error:
            make_client(base_url).generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.MALFORMED_JSON
    assert len(requests) == 2


@pytest.mark.parametrize("body", [{}, {"response": ""}, {"response": None}])
def test_missing_or_empty_response_is_rejected_without_retry(body: Any) -> None:
    with mock_ollama_server([(200, body, 0)]) as (base_url, requests):
        with pytest.raises(OllamaClientError) as error:
            make_client(base_url).generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.INVALID_RESPONSE
    assert len(requests) == 1


def test_timeout_is_classified_without_retry() -> None:
    valid = {"response": json.dumps({"status": "too late"})}
    with mock_ollama_server([(200, valid, 0.2)]) as (base_url, requests):
        with pytest.raises(OllamaClientError) as error:
            make_client(base_url, timeout_seconds=0.05).generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.TIMEOUT
    assert len(requests) == 1


def test_retry_uses_only_time_remaining_from_total_timeout() -> None:
    malformed = {"response": "not-json"}
    valid = {"response": json.dumps({"status": "too late"})}
    with mock_ollama_server([(200, malformed, 0.03), (200, valid, 0.05)]) as (
        base_url,
        requests,
    ):
        with pytest.raises(OllamaClientError) as error:
            make_client(base_url, timeout_seconds=0.06).generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.TIMEOUT
    assert len(requests) == 2


def test_connection_error_is_classified_without_retry() -> None:
    temporary_socket = socket.socket()
    temporary_socket.bind(("127.0.0.1", 0))
    _, unused_port = temporary_socket.getsockname()
    temporary_socket.close()

    with pytest.raises(OllamaClientError) as error:
        make_client(f"http://127.0.0.1:{unused_port}").generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.CONNECTION


def test_http_error_is_classified_without_retry() -> None:
    with mock_ollama_server([(503, {"error": "unavailable"}, 0)]) as (
        base_url,
        requests,
    ):
        with pytest.raises(OllamaClientError) as error:
            make_client(base_url).generate_json("system", "user")

    assert error.value.code == OllamaErrorCode.HTTP_ERROR
    assert len(requests) == 1


def test_prompts_and_output_are_not_logged(caplog: pytest.LogCaptureFixture) -> None:
    sensitive_system = "PRIVATE_SYSTEM_INSTRUCTION"
    sensitive_user = "PRIVATE_RESUME_TEXT"
    sensitive_output = "PRIVATE_MODEL_OUTPUT"
    response = {"response": json.dumps({"text": sensitive_output})}

    with mock_ollama_server([(200, response, 0)]) as (base_url, _):
        make_client(base_url).generate_json(sensitive_system, sensitive_user)

    log_output = caplog.text
    assert sensitive_system not in log_output
    assert sensitive_user not in log_output
    assert sensitive_output not in log_output
