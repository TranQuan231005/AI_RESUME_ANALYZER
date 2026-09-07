"""Unit tests for production sentence-embedding CV-JD matching."""
import numpy as np

from app.matching.embedding import chunk_text, compute_embedding_similarity
from app.matching.engine import match_resume_to_job
from app.schemas.matching import MatchResult


class FakeEmbeddingModel:
    def encode(self, chunks, **_kwargs):
        vectors = []
        for chunk in chunks:
            lowered = chunk.lower()
            vectors.append([
                float("python" in lowered or "data" in lowered),
                float("product" in lowered or "strategy" in lowered),
                0.2,
            ])
        values = np.asarray(vectors, dtype=float)
        norms = np.linalg.norm(values, axis=1, keepdims=True)
        return values / np.maximum(norms, 1e-12)


def test_chunk_text_is_bounded():
    chunks = chunk_text("word " * 2000, max_words=180, max_chunks=8)
    assert len(chunks) == 8
    assert all(len(chunk.split()) <= 180 for chunk in chunks)


def test_embedding_similarity_empty_inputs():
    assert compute_embedding_similarity("", "job description", model=FakeEmbeddingModel()) is None
    assert compute_embedding_similarity("resume text", "", model=FakeEmbeddingModel()) is None


def test_embedding_similarity_identical_topic():
    score = compute_embedding_similarity(
        "Python data engineering", "Python data developer", model=FakeEmbeddingModel()
    )
    assert score is not None and score >= 95.0


def test_match_without_embedding_uses_skill_only(monkeypatch):
    monkeypatch.setattr("app.matching.engine.compute_embedding_similarity", lambda *args, **kwargs: None)
    result = match_resume_to_job(
        file_name="resume.pdf",
        resume_skills=["Python", "SQL"],
        job_description="Looking for Python, SQL, and Pandas.",
    )
    assert isinstance(result, MatchResult)
    assert result.match_score == 67
    assert result.match_breakdown.method == "SKILL_ONLY"
    assert result.match_breakdown.semantic_score is None


def test_hybrid_match_exposes_embedding_breakdown():
    result = match_resume_to_job(
        file_name="resume.pdf",
        resume_skills=["Python", "SQL", "Pandas"],
        job_description="Looking for a Data Scientist with Python, SQL, and Pandas.",
        resume_text="Senior Data Scientist using Python, SQL, and Pandas.",
        embedding_model=FakeEmbeddingModel(),
    )
    assert result.match_score >= 95
    assert result.match_breakdown.method == "HYBRID_EMBEDDING"
    assert result.match_breakdown.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    assert result.match_breakdown.skill_weight + result.match_breakdown.semantic_weight == 1.0


def test_no_recognized_jd_skills_uses_semantic_only():
    result = match_resume_to_job(
        file_name="pm_resume.pdf",
        resume_skills=[],
        job_description="We seek a collaborative product leader to drive strategy and roadmap execution.",
        resume_text="Experienced product manager leading product strategy.",
        embedding_model=FakeEmbeddingModel(),
    )
    assert result.match_score > 0
    assert result.match_breakdown.skill_weight == 0.0
    assert result.match_breakdown.semantic_weight == 1.0
