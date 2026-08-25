# Walkthrough — TV5: D2 Contract Foundation + Repo Skeleton

Đã hoàn thành toàn bộ các yêu cầu của **TV5** cho mốc **D2 — Contract foundation + repo skeleton** và thay thế / chuẩn hóa toàn bộ contracts cũ theo [KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md](file:///d:/AI_RESUME_ANALYZER/KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md) và [CHECKLIST_DU_AN.md](file:///d:/AI_RESUME_ANALYZER/CHECKLIST_DU_AN.md).

---

## 1. Các thành phần đã triển khai

### Pydantic Schemas (`ai-service/app/schemas/`)
- [__init__.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/__init__.py): Central export cho toàn bộ schema models.
- [common.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/common.py): `AiMetadata`, `AiProvider` (`OLLAMA`, `RULE_BASED`), `FieldEnum` (6 fields đã khóa), `ApiError`, `HealthResponse`.
- [auth.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/auth.py): `LoginRequest`, `LoginResponse`, `UserDto`, `UserRole` (`USER`, `ADMIN`).
- [document.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/document.py): `ParsedDocument` (fileName, text, pageCount, sizeBytes <= 5MB).
- [features.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/features.py): `FieldEvidence`, `ResumeFeatures` (candidateName, candidateEmail, skills, predictedField, fieldEvidence).
- [scoring.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/scoring.py): `ScoreBreakdown` (8 components ràng buộc điểm theo rubric và `total == sum(components)`).
- [analysis.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/analysis.py): `ResumeAnalysisResult` (kết quả phân tích CV hoàn chỉnh).
- [matching.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/schemas/matching.py): `MatchResult` và `MatchAnalysisRequest` (kết quả và request so khớp JD).

### AI Service FastAPI & Health-check (`ai-service/app/main.py`)
- [main.py](file:///d:/AI_RESUME_ANALYZER/ai-service/app/main.py): Khởi tạo FastAPI app với các endpoint:
  - `GET /health` -> `HealthResponse`
  - `POST /api/analyze-resume` -> `ResumeAnalysisResult`
  - `POST /api/analyze-match` -> `MatchResult`

### OpenAPI Specification & Export Automation
- [export_openapi.py](file:///d:/AI_RESUME_ANALYZER/scripts/export_openapi.py): CLI tool xuất và kiểm tra tính đồng bộ của OpenAPI spec (`--check`).
- [ai-service.json](file:///d:/AI_RESUME_ANALYZER/contracts/openapi/ai-service.json): OpenAPI 3.1 schema tự động sinh từ FastAPI app.
- [public-api.json](file:///d:/AI_RESUME_ANALYZER/contracts/openapi/public-api.json): OpenAPI 3.0 schema hoàn chỉnh cho Spring Boot public API (Auth, Resume, Match, History, Admin, Error).

### Bộ Fixtures Chuẩn Hóa (`contracts/fixtures/`)
- **Auth**: [auth-login-request.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/auth-login-request.json), [auth-login-response.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/auth-login-response.json), [auth-me-response.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/auth-me-response.json)
- **Document**: [parsed-document.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/parsed-document.json), [parsed-document-empty.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/parsed-document-empty.json)
- **Resume Features**: [resume-features.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/resume-features.json), [resume-features-missing-fields.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/resume-features-missing-fields.json)
- **Resume Result**: [resume-analysis-result.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/resume-analysis-result.json), [resume-analysis-result-fallback.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/resume-analysis-result-fallback.json)
- **Match Result**: [match-result.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/match-result.json), [match-result-fallback.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/match-result-fallback.json)
- **ApiError (Đầy đủ 12 mã lỗi)**:
  - [api-error-400-malformed.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-400-malformed.json)
  - [api-error-401-bad-credentials.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-401-bad-credentials.json)
  - [api-error-401-unauthorized.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-401-unauthorized.json)
  - [api-error-403-forbidden.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-403-forbidden.json)
  - [api-error-404-not-found.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-404-not-found.json)
  - [api-error-413-file-too-large.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-413-file-too-large.json)
  - [api-error-422-invalid-pdf.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-422-invalid-pdf.json)
  - [api-error-422-pdf-not-readable.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-422-pdf-not-readable.json)
  - [api-error-422-text-not-extractable.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-422-text-not-extractable.json)
  - [api-error-422-jd-required.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-422-jd-required.json)
  - [api-error-500-internal-error.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-500-internal-error.json)
  - [api-error-502-ai-service-error.json](file:///d:/AI_RESUME_ANALYZER/contracts/fixtures/api-error-502-ai-service-error.json)

### Infrastructure & CI Skeleton
- [docker-compose.yml](file:///d:/AI_RESUME_ANALYZER/docker-compose.yml): Định nghĩa 4 containers (`mysql`, `backend`, `ai-service`, `frontend`) và network routing với host Ollama.
- [.env.example](file:///d:/AI_RESUME_ANALYZER/.env.example): Template cấu hình biến môi trường chuẩn.
- [.github/workflows/ci.yml](file:///d:/AI_RESUME_ANALYZER/.github/workflows/ci.yml): CI workflow cho contract verification, AI service tests, backend & frontend checks.

---

## 2. Kết quả kiểm thử (Verification)

```bash
$ py scripts/export_openapi.py --check
OK: contracts/openapi/ai-service.json is up-to-date.

$ py -m pytest
============================= test session starts =============================
platform win32 -- Python 3.9.13, pytest-8.4.2, pluggy-1.6.0
rootdir: D:\AI_RESUME_ANALYZER
configfile: pytest.ini
testpaths: ai-service/tests
plugins: anyio-4.12.1
collected 23 items

ai-service\tests\contracts\test_contract_schemas.py .............        [ 56%]
ai-service\tests\extraction\test_classifier.py ...                       [ 69%]
ai-service\tests\extraction\test_contract_fixtures.py ..                 [ 78%]
ai-service\tests\extraction\test_features.py ..                          [ 86%]
ai-service\tests\extraction\test_taxonomy.py ...                         [100%]

============================= 23 passed in 0.17s ==============================
```

Toàn bộ 23 tests (bao gồm 13 contract tests mới và 10 extraction tests) đã vượt qua 100%.
Mục D2 của TV5 trong [CHECKLIST_DU_AN.md](file:///d:/AI_RESUME_ANALYZER/CHECKLIST_DU_AN.md) đã được cập nhật hoàn tất.
