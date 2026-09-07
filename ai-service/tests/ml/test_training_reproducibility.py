"""Test training pipeline reproducibility on a small fixture."""
import tempfile
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def test_training_pipeline_reproducibility_on_small_fixture():
    # Synthetic micro dataset
    texts = [
        "Python data analysis pandas numpy scikit-learn machine learning",
        "Data scientist statistics regression deep learning tensorflow",
        "React typescript web developer frontend javascript html css",
        "Node.js express backend web rest api full stack developer",
        "Android developer kotlin java jetpack compose gradle mobile app",
        "Android engineer mvvm room coroutines android studio mobile",
        "iOS engineer swift swiftui xcode uikit combine apple mobile",
        "iOS developer objective-c coredata app store testflight",
        "UI UX designer figma wireframing user research prototyping adobe xd",
        "Product designer visual design design system user experience usability",
    ]
    labels = [
        "Data Science",
        "Data Science",
        "Web Development",
        "Web Development",
        "Android Development",
        "Android Development",
        "iOS Development",
        "iOS Development",
        "UI/UX",
        "UI/UX",
    ]

    pipe1 = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=200, random_state=42)),
    ])

    pipe2 = Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=200, random_state=42)),
    ])

    pipe1.fit(texts, labels)
    pipe2.fit(texts, labels)

    test_input = ["Building iOS apps with Swift and SwiftUI for iPhone"]
    pred1 = pipe1.predict_proba(test_input)
    pred2 = pipe2.predict_proba(test_input)

    assert pipe1.classes_.tolist() == pipe2.classes_.tolist()
    assert (pred1 == pred2).all()
    assert pipe1.predict(test_input)[0] == "iOS Development"
