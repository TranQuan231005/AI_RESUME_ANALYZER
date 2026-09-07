"""Unit tests for ML model loading, caching, and fallback behavior."""
import json
from pathlib import Path
import pytest

from app.ml.model_loader import (
    clear_model_cache,
    get_artifact_paths,
    get_model_metadata,
    is_model_available,
    load_classifier_model,
)


@pytest.fixture(autouse=True)
def reset_cache():
    clear_model_cache()
    yield
    clear_model_cache()


def test_is_model_available_returns_true_for_existing_artifacts():
    assert is_model_available() is True


def test_load_classifier_model_returns_pipeline():
    pipeline = load_classifier_model()
    assert pipeline is not None
    assert hasattr(pipeline, "predict")
    assert hasattr(pipeline, "predict_proba")


def test_model_caching_returns_identical_instance():
    p1 = load_classifier_model()
    p2 = load_classifier_model()
    assert p1 is p2


def test_get_model_metadata_structure():
    metadata = get_model_metadata()
    assert metadata is not None
    assert "modelType" in metadata
    assert "labels" in metadata
    assert "unknownThreshold" in metadata
    assert isinstance(metadata["labels"], list)
    assert len(metadata["labels"]) == 5
    assert set(metadata["labels"]) == {
        "Data Science",
        "Web Development",
        "Android Development",
        "iOS Development",
        "UI/UX",
    }


def test_missing_artifact_directory_returns_none(tmp_path: Path):
    empty_dir = tmp_path / "empty_artifacts"
    empty_dir.mkdir()
    assert is_model_available(empty_dir) is False
    assert load_classifier_model(empty_dir) is None
    assert get_model_metadata(empty_dir) is None


def test_invalid_metadata_file_returns_none(tmp_path: Path):
    corrupt_dir = tmp_path / "corrupt_artifacts"
    corrupt_dir.mkdir()
    meta_file = corrupt_dir / "metadata.json"
    meta_file.write_text("invalid json content", encoding="utf-8")

    assert get_model_metadata(corrupt_dir) is None
