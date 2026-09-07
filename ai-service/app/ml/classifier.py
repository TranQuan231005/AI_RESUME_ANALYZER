"""ML Field Classifier with explainable evidence and deterministic fallback."""
from __future__ import annotations
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any

from app.extraction.classifier import classify_features as fallback_classify_features
from app.extraction.features import ResumeFeatures, extract_features
from app.extraction.taxonomy import FIELD_NAMES
from .model_loader import get_model_metadata, load_classifier_model

logger = logging.getLogger(__name__)


@dataclass
class MLPredictionResult:
    predicted_field: str
    confidence: float
    per_class_probabilities: dict[str, float]
    top_terms: list[str]
    field_evidence: list[dict[str, Any]]
    used_model: bool = True


def extract_top_terms(pipeline: Any, text: str, target_class_idx: int, top_n: int = 5) -> list[str]:
    """Extract top TF-IDF n-grams contributing positively to the predicted class."""
    try:
        vectorizer = pipeline.named_steps.get("tfidf") or pipeline.named_steps.get("vectorizer")
        classifier = pipeline.named_steps.get("clf") or pipeline.named_steps.get("classifier")

        if not vectorizer or not classifier:
            return []

        feature_names = vectorizer.get_feature_names_out()
        tfidf_vec = vectorizer.transform([text]).tocsr()

        if tfidf_vec.nnz == 0:
            return []

        # Feature indices present in text
        indices = tfidf_vec.indices
        values = tfidf_vec.data

        # If classifier has coef_
        if hasattr(classifier, "coef_"):
            coefs = classifier.coef_
            # For multiclass, shape is (n_classes, n_features)
            if target_class_idx < len(coefs):
                class_coefs = coefs[target_class_idx]
                weights = [values[i] * class_coefs[idx] for i, idx in enumerate(indices)]
                sorted_idx = sorted(range(len(weights)), key=lambda k: weights[k], reverse=True)
                top_terms = [feature_names[indices[k]] for k in sorted_idx if weights[k] > 0][:top_n]
                return top_terms
        
        # Fallback to highest TF-IDF values
        sorted_idx = sorted(range(len(values)), key=lambda k: values[k], reverse=True)
        return [feature_names[indices[k]] for k in sorted_idx][:top_n]
    except Exception as e:
        logger.debug("Could not extract top terms: %s", e)
        return []


class MLClassificationEngine:
    def __init__(self, artifact_dir: Path | str | None = None):
        self.artifact_dir = artifact_dir

    def predict(self, text: str, raw_features: ResumeFeatures | None = None) -> MLPredictionResult:
        pipeline = load_classifier_model(self.artifact_dir)
        metadata = get_model_metadata(self.artifact_dir) or {}

        if pipeline is None or not hasattr(pipeline, "predict_proba"):
            # Fallback to taxonomy keyword heuristic
            if raw_features is None:
                raw_features = extract_features(text)
            fallback_res = fallback_classify_features(raw_features)
            
            evidence = [
                {**item, "topTerms": list(item.get("topTerms", []))}
                for item in (fallback_res.field_evidence or [])
            ]
            conf = 0.0
            for ev in evidence:
                if ev.get("field") == fallback_res.predicted_field:
                    conf = float(ev.get("confidence", 0.0))
                    break

            probs = {ev.get("field", ""): float(ev.get("confidence", 0.0)) for ev in evidence if ev.get("field")}
            return MLPredictionResult(
                predicted_field=fallback_res.predicted_field,
                confidence=conf,
                per_class_probabilities=probs,
                top_terms=[],
                field_evidence=evidence,
                used_model=False,
            )

        classes = list(pipeline.classes_)
        probabilities = pipeline.predict_proba([text])[0]
        prob_dict = {classes[i]: round(float(probabilities[i]), 4) for i in range(len(classes))}

        # Determine top prediction
        best_idx = int(probabilities.argmax())
        best_class = classes[best_idx]
        best_confidence = float(probabilities[best_idx])

        # Apply unknown threshold
        unknown_threshold = float(metadata.get("unknownThreshold", 0.35))
        if best_confidence < unknown_threshold:
            predicted_field = "Unknown"
        elif str(best_class) in FIELD_NAMES:
            predicted_field = str(best_class)
        else:
            predicted_field = "Unknown"

        top_terms = extract_top_terms(pipeline, text, best_idx, top_n=5)

        # Build field evidence structure compatible with existing API contract
        if raw_features is None:
            raw_features = extract_features(text)

        # Extract skills matched per field
        from app.extraction.taxonomy import SKILL_TAXONOMY
        evidence_skills: dict[str, list[str]] = {c: [] for c in classes}
        for skill_name in raw_features.skills:
            definition = next(
                (item for item in SKILL_TAXONOMY if item.canonical_name == skill_name),
                None,
            )
            if definition is None:
                continue
            for field_name in definition.fields:
                if field_name in evidence_skills:
                    evidence_skills[field_name].append(skill_name)

        # Build evidence list sorted by probability
        evidence_list = []
        for cls in sorted(classes, key=lambda c: prob_dict[c], reverse=True):
            if prob_dict[cls] >= 0.05:  # show classes with >= 5% confidence
                evidence_list.append({
                    "field": cls,
                    "matchedSkills": evidence_skills.get(cls, []),
                    "confidence": round(prob_dict[cls], 2),
                    "topTerms": extract_top_terms(pipeline, text, classes.index(cls), top_n=3),
                })

        return MLPredictionResult(
            predicted_field=predicted_field,
            confidence=round(best_confidence, 4),
            per_class_probabilities=prob_dict,
            top_terms=top_terms,
            field_evidence=evidence_list,
            used_model=True,
        )


def predict_field_from_text(text: str, raw_features: ResumeFeatures | None = None, artifact_dir: Path | str | None = None) -> MLPredictionResult:
    engine = MLClassificationEngine(artifact_dir=artifact_dir)
    return engine.predict(text, raw_features=raw_features)


def classify_resume_features_ml(
    text: str,
    raw_features: ResumeFeatures,
    artifact_dir: Path | str | None = None,
) -> ResumeFeatures:
    """Unified wrapper returning standard ResumeFeatures with ML predictions and evidence."""
    prediction = predict_field_from_text(text, raw_features=raw_features, artifact_dir=artifact_dir)
    return ResumeFeatures(
        candidate_name=raw_features.candidate_name,
        candidate_email=raw_features.candidate_email,
        skills=list(raw_features.skills),
        predicted_field=prediction.predicted_field,
        field_evidence=prediction.field_evidence,
    )
