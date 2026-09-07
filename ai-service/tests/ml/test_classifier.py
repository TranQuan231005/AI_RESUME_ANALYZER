"""Unit tests for ML classifier inference, explainability, threshold gating, and fallback."""
from pathlib import Path
import pytest

from app.extraction.features import ResumeFeatures, extract_features
from app.ml.classifier import (
    MLClassificationEngine,
    classify_resume_features_ml,
    predict_field_from_text,
)


def test_predict_field_data_science_sample():
    text = """
    Alex Morgan
    Email: alex@example.com
    Experience with Python, Pandas, NumPy, scikit-learn, and building machine learning models.
    Trained neural networks using TensorFlow and analyzed datasets with SQL and PyTorch.
    """
    res = predict_field_from_text(text)
    assert res.predicted_field == "Data Science"
    assert res.confidence > 0.50
    assert "Data Science" in res.per_class_probabilities
    assert res.used_model is True
    assert len(res.field_evidence) > 0


def test_predict_field_ios_development_sample():
    text = """
    iOS Software Engineer
    Developed mobile apps using Swift, SwiftUI, Xcode, Combine, and UIKit.
    Integrated CoreData and published applications to Apple App Store.
    """
    res = predict_field_from_text(text)
    assert res.predicted_field == "iOS Development"
    assert res.confidence > 0.50
    assert res.used_model is True


def test_predict_field_ui_ux_sample():
    text = """
    UI/UX Product Designer
    Created wireframes, user personas, interactive prototypes in Figma and Adobe XD.
    Conducted user research, usability testing, design systems, typography and visual hierarchy.
    """
    res = predict_field_from_text(text)
    assert res.predicted_field == "UI/UX"
    assert res.confidence > 0.50


def test_predict_field_android_sample():
    text = """
    Android Developer
    Built native mobile applications with Kotlin, Java, Jetpack Compose, Android SDK, and Gradle.
    Implemented MVVM architecture and Room database.
    """
    res = predict_field_from_text(text)
    assert res.predicted_field == "Android Development"
    assert res.confidence > 0.50


def test_predict_field_web_development_sample():
    text = """
    Full Stack Web Developer
    Built responsive web applications with TypeScript, React, Next.js, Node.js, Express, HTML, and CSS.
    Developed REST APIs and managed PostgreSQL databases.
    """
    res = predict_field_from_text(text)
    assert res.predicted_field == "Web Development"
    assert res.confidence > 0.50


def test_unknown_threshold_gating_on_unrelated_text():
    gibberish_text = "The quick brown fox jumps over the lazy dog in the sunny forest with flowers."
    res = predict_field_from_text(gibberish_text)
    assert res.predicted_field == "Unknown"
    # Max confidence should be below or gated to Unknown
    assert res.used_model is True


def test_missing_model_graceful_fallback(tmp_path: Path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    engine = MLClassificationEngine(artifact_dir=empty_dir)
    text = "Experienced with React, JavaScript, HTML, CSS for web development."
    res = engine.predict(text)

    # Should use fallback heuristic without throwing
    assert res.used_model is False
    assert res.predicted_field in ["Web Development", "Unknown"]
    assert isinstance(res.field_evidence, list)


def test_classify_resume_features_ml_wrapper():
    text = "Jane Doe\nEmail: jane@test.com\nSkills: Swift, SwiftUI, iOS\nExperience building iOS apps."
    raw_features = extract_features(text)
    classified = classify_resume_features_ml(text, raw_features)

    assert isinstance(classified, ResumeFeatures)
    assert classified.predicted_field == "iOS Development"
    assert classified.candidate_name == "Jane Doe"
    assert classified.candidate_email == "jane@test.com"
