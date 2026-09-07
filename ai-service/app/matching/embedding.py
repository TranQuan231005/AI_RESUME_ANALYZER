"""Offline sentence-embedding loading and bounded document similarity."""
from __future__ import annotations

from functools import lru_cache
import logging
import os
from pathlib import Path
import re
from typing import Any

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "all-MiniLM-L6-v2"


def embedding_model_path() -> Path:
    return Path(os.getenv("EMBEDDING_MODEL_PATH", str(LOCAL_MODEL_PATH)))


@lru_cache(maxsize=1)
def load_embedding_model() -> Any | None:
    """Load the local model once. Runtime network downloads are forbidden."""
    model_path = embedding_model_path()
    if not model_path.is_dir():
        logger.warning("Embedding model directory is unavailable at %s", model_path)
        return None
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(str(model_path), device="cpu", local_files_only=True)
        logger.info("Loaded embedding model from %s", model_path)
        return model
    except Exception as exc:
        logger.error("Unable to load embedding model at %s: %s", model_path, exc)
        return None


def chunk_text(text: str, *, max_words: int, max_chunks: int) -> list[str]:
    """Pack paragraph/sentence content into bounded chunks without empty entries."""
    if not isinstance(text, str) or not text.strip():
        return []
    blocks = [part.strip() for part in re.split(r"\n\s*\n+", text) if part.strip()]
    if len(blocks) == 1:
        blocks = [part.strip() for part in re.split(r"(?<=[.!?])\s+", blocks[0]) if part.strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for block in blocks:
        words = block.split()
        while words:
            capacity = max_words - current_words
            current.extend(words[:capacity])
            current_words += min(len(words), capacity)
            words = words[capacity:]
            if current_words >= max_words:
                chunks.append(" ".join(current))
                current, current_words = [], 0
                if len(chunks) >= max_chunks:
                    return chunks
    if current and len(chunks) < max_chunks:
        chunks.append(" ".join(current))
    return chunks


def compute_embedding_similarity(
    resume_text: str,
    job_description: str,
    *,
    model: Any | None = None,
) -> float | None:
    """Return length-weighted JD-to-resume maximum cosine similarity on a 0–100 scale."""
    encoder = model if model is not None else load_embedding_model()
    if encoder is None:
        return None
    resume_chunks = chunk_text(resume_text, max_words=180, max_chunks=12)
    jd_chunks = chunk_text(job_description, max_words=180, max_chunks=8)
    if not resume_chunks or not jd_chunks:
        return None
    try:
        vectors = encoder.encode(
            resume_chunks + jd_chunks,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        resume_vectors = vectors[: len(resume_chunks)]
        jd_vectors = vectors[len(resume_chunks) :]
        similarities = jd_vectors @ resume_vectors.T
        maxima = similarities.max(axis=1)
        weights = [max(1, len(chunk.split())) for chunk in jd_chunks]
        weighted = sum(float(score) * weight for score, weight in zip(maxima, weights)) / sum(weights)
        return round(max(0.0, min(100.0, weighted * 100.0)), 2)
    except Exception as exc:
        logger.error("Embedding inference failed: %s", exc)
        return None
