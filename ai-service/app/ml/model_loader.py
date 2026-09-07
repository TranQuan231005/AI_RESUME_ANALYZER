"""Model loading utilities with safe caching and error handling."""
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Any, Tuple

logger = logging.getLogger(__name__)

LOCAL_ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "models" / "classifier"


def default_artifact_dir() -> Path:
    """Resolve the packaged classifier without depending on the current directory."""
    return Path(os.getenv("CLASSIFIER_ARTIFACT_DIR", str(LOCAL_ARTIFACT_DIR)))

_CACHED_PIPELINE: Any = None
_CACHED_METADATA: dict[str, Any] | None = None
_CACHED_DIR: Path | None = None


def get_artifact_paths(artifact_dir: Path | str | None = None) -> Tuple[Path, Path]:
    base_dir = Path(artifact_dir) if artifact_dir else default_artifact_dir()
    model_path = base_dir / "classifier_pipeline.joblib"
    metadata_path = base_dir / "metadata.json"
    return model_path, metadata_path


def is_model_available(artifact_dir: Path | str | None = None) -> bool:
    model_path, metadata_path = get_artifact_paths(artifact_dir)
    return model_path.is_file() and metadata_path.is_file()


def get_model_metadata(artifact_dir: Path | str | None = None) -> dict[str, Any] | None:
    global _CACHED_METADATA, _CACHED_DIR
    target_dir = Path(artifact_dir) if artifact_dir else default_artifact_dir()
    if _CACHED_METADATA is not None and _CACHED_DIR == target_dir:
        return _CACHED_METADATA

    _, metadata_path = get_artifact_paths(target_dir)
    if not metadata_path.is_file():
        return None

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.warning("Invalid metadata structure in %s", metadata_path)
                return None
            _CACHED_METADATA = data
            _CACHED_DIR = target_dir
            return data
    except Exception as e:
        logger.warning("Failed to load metadata from %s: %s", metadata_path, e)
        return None


def load_classifier_model(artifact_dir: Path | str | None = None, force_reload: bool = False) -> Any:
    global _CACHED_PIPELINE, _CACHED_METADATA, _CACHED_DIR
    target_dir = Path(artifact_dir) if artifact_dir else default_artifact_dir()

    if not force_reload and _CACHED_PIPELINE is not None and _CACHED_DIR == target_dir:
        return _CACHED_PIPELINE

    model_path, _ = get_artifact_paths(target_dir)
    if not model_path.is_file():
        logger.info("Classifier model artifact not found at %s. ML classifier will use fallback.", model_path)
        return None

    try:
        import joblib
        pipeline = joblib.load(model_path)
        _CACHED_PIPELINE = pipeline
        _CACHED_DIR = target_dir
        # Also pre-cache metadata
        get_model_metadata(target_dir)
        logger.info("Loaded ML classifier pipeline successfully from %s", model_path)
        return pipeline
    except Exception as e:
        logger.error("Error loading model pipeline from %s: %s", model_path, e)
        return None


def clear_model_cache() -> None:
    global _CACHED_PIPELINE, _CACHED_METADATA, _CACHED_DIR
    _CACHED_PIPELINE = None
    _CACHED_METADATA = None
    _CACHED_DIR = None
