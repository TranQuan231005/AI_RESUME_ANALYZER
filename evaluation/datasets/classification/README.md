# Resume Domain Classification Dataset

## 1. Overview & Problem Formulation

This controlled synthetic dataset trains and evaluates a five-class resume classifier and calibrates an additional `Unknown` outcome:
1. **Data Science** (Machine Learning, MLOps, Data Analytics, Deep Learning, NLP, Computer Vision)
2. **Web Development** (Frontend, Backend, Fullstack, React, TypeScript, Node.js, Spring Boot, Django)
3. **Android Development** (Kotlin, Java, Jetpack Compose, Android SDK, Room, NDK)
4. **iOS Development** (Swift, SwiftUI, UIKit, Combine, CoreData, Xcode)
5. **UI/UX** (Product Design, UX Research, Figma, Adobe XD, Design Systems, Wireframing)

---

## 2. Dataset Provenance & Synthesis Methodology

In strict adherence to academic ethics and privacy safeguards:
- **Zero Real PII:** All candidate names, phone numbers, and company details use fictitious placeholders (`@example.test` email domains).
- **Domain Authenticity:** Resumes were manually authored and curated across 10 distinct template groups per class to capture varying seniority levels (Junior, Mid, Senior, Lead, Architect) and specialization sub-tracks.
- **Source Type Tagging:** All samples are tagged with `sourceType: "synthetic"`, explicitly noting their synthetic provenance to prevent exaggerated real-world performance claims.

---

## 3. Stratified Partitioning & Leakage Prevention

To ensure rigorous ML evaluation without data contamination:
- **Random Seed:** Fixed deterministic seed `42`.
- **Group-Aware Splitting:** Each domain is divided into 10 discrete `templateGroup` clusters (`g01` to `g10`).
  - Groups 1–7 $\rightarrow$ **Train Split** (35 samples/class, 175 total = 70%)
  - Group 8 $\rightarrow$ **Validation Split** (5 samples/class, 25 total = 10%)
  - Groups 9–10 $\rightarrow$ **Test Split** (10 samples/class, 50 total = 20%)
- **Zero Group Leakage:** No template structure or phrasing variant appearing in the test set exists in the training set.
- **OOD only for gating/evaluation:** 50 OOD validation and 50 OOD held-out test samples cover Business, Finance, Marketing, Human Resources, Product Management and non-resume text. They are never added to five-class training.

### Distribution Matrix

| Class | Train (70%) | Validation (10%) | Test (20%) | Total |
|---|---|---|---|---|
| **Data Science** | 35 | 5 | 10 | 50 |
| **Web Development** | 35 | 5 | 10 | 50 |
| **Android Development** | 35 | 5 | 10 | 50 |
| **iOS Development** | 35 | 5 | 10 | 50 |
| **UI/UX** | 35 | 5 | 10 | 50 |
| **Total** | **175** | **25** | **50** | **250** |

The 100 OOD records are separate, producing 350 total controlled benchmark records. A perfect synthetic score must not be described as real-resume performance.

---

## 4. Schema Specification (`dataset.schema.json`)

Each record in `train.jsonl`, `validation.jsonl`, and `test.jsonl` conforms to the following JSON schema:

```json
{
  "id": "cv-data-science-001",
  "text": "Alex Morgan\nalex.morgan@example.test\n\nSenior ML Engineer with 5+ years experience...",
  "label": "Data Science",
  "sourceType": "synthetic",
  "sourceReference": "Curated academic domain template ds-g01-v01",
  "templateGroup": "ds-g01",
  "reviewed": true
}
```

---

## 5. Validation & Reproducibility

To validate dataset integrity, run:

```bash
python evaluation/scripts/validate_classification_dataset.py
```

The validator checks:
1. JSON Schema conformance.
2. Label validity against the 5 canonical classes.
3. Content deduplication (normalized SHA/text hashing).
4. Absence of non-anonymized PII.
5. Cross-split disjointness (Sample IDs & Template Groups).
6. Class distribution balance.
