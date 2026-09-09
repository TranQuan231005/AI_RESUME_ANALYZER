import asyncio
import logging
import threading
from unittest.mock import MagicMock

from app.llm.client import OllamaClient, OllamaClientError, OllamaConfig, OllamaErrorCode
from app.main import _log_enrichment_failure, analyze_resume, set_ollama_client


def test_default_model_and_explicit_evaluation_override(monkeypatch):
    from app.schemas.common import HealthResponse

    monkeypatch.delenv('OLLAMA_MODEL', raising=False)
    assert OllamaConfig().model == 'qwen3:0.6b'
    assert OllamaConfig.from_env().model == 'qwen3:0.6b'
    assert HealthResponse.model_fields['model'].default == 'qwen3:0.6b'
    monkeypatch.setenv('OLLAMA_MODEL', 'qwen3:4b')
    assert OllamaConfig.from_env().model == 'qwen3:4b'


def test_fallback_log_excludes_exception_content(caplog):
    with caplog.at_level(logging.WARNING):
        _log_enrichment_failure('match', OllamaClientError(OllamaErrorCode.TIMEOUT, 'PRIVATE_CV_SENTINEL'))
    assert 'code=TIMEOUT' in caplog.text
    assert 'PRIVATE_CV_SENTINEL' not in caplog.text


def test_generation_logs_only_numeric_metrics(caplog):
    response = MagicMock()
    response.json.return_value = {
        'response': '{"recommendations": ["PRIVATE_OUTPUT"]}',
        'load_duration': 100, 'eval_count': 10,
        'eval_duration': 'PRIVATE_METRIC', 'error': 'PRIVATE_ERROR',
    }
    with caplog.at_level(logging.INFO):
        OllamaClient._decode_json_object(response)
    assert 'load_duration' in caplog.text
    assert 'PRIVATE' not in caplog.text


def test_warmup_uses_configured_budget_without_logging_remote_body(caplog):
    session = MagicMock()
    session.post.side_effect = RuntimeError('PRIVATE_REMOTE_BODY')
    client = OllamaClient(OllamaConfig(warmup_timeout_seconds=23), session)
    assert client.warmup() is False
    assert session.post.call_args.kwargs['timeout'] == 23
    assert session.post.call_args.kwargs['json']['stream'] is False
    assert 'PRIVATE_REMOTE_BODY' not in caplog.text
    assert 'ollama_warmup failed' in caplog.text


def test_slow_enrichment_does_not_block_event_loop(monkeypatch):
    import io
    from fastapi import UploadFile
    from starlette.datastructures import Headers
    from app.schemas.document import ParsedDocument

    entered = threading.Event()
    released = threading.Event()

    def generate(*args):
        entered.set()
        released.wait(2)
        return {'recommendedSkills': ['SQL'], 'recommendations': ['Add quantified impact.']}

    mock = MagicMock(spec=OllamaClient)
    mock.config = OllamaConfig()
    mock.generate_json.side_effect = generate
    set_ollama_client(mock)
    monkeypatch.setattr('app.main.extract_pdf_content', lambda *args: ParsedDocument(
        fileName='synthetic.pdf', text='SUMMARY\nEngineer\nSKILLS\nPython\nEXPERIENCE\nBuilt APIs', pageCount=1, sizeBytes=50))

    async def scenario():
        upload = UploadFile(filename='synthetic.pdf', file=io.BytesIO(b'%PDF-1.4 synthetic fixture data'), headers=Headers({'content-type': 'application/pdf'}))
        task = asyncio.create_task(analyze_resume(upload))
        try:
            for _ in range(200):
                await asyncio.sleep(0.01)
                if entered.is_set():
                    break
            assert entered.is_set()
            # If generate blocks the loop, the request completes before we can run.
            assert not task.done()
        finally:
            released.set()
            await task

    try:
        asyncio.run(scenario())
    finally:
        set_ollama_client(None)
