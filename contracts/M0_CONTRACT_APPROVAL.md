# Biên bản phê duyệt và khóa hợp đồng M0 (M0 Contract Freeze Sign-off)

> **Mốc thời gian:** Cuối D3 (Milestone M0)  
> **Trạng thái:** **FROZEN & APPROVED**  
> **Điều phối viên (Owner):** TV5  
> **Hội đồng phê duyệt:** TV1, TV2, TV3, TV4, TV5  

---

## 1. Danh sách các hợp đồng (Contracts) được khóa chính thức

| Contract | Pydantic Schema | OpenAPI Path | Fixture mẫu | Owner | Reviewers / Sign-off | Trạng thái |
|---|---|---|---|---|---|---|
| **Auth Contract** | `LoginRequest`, `LoginResponse`, `UserDto` | `/api/auth/login`, `/api/me` | `auth-login-request.json`, `auth-login-response.json`, `auth-me-response.json` | TV1 | TV2, TV5 | **APPROVED** |
| **ParsedDocument & PDF Errors** | `ParsedDocument`, `ApiError` | `/api/analyses/resume` | `parsed-document.json`, `parsed-document-empty.json`, `api-error-422-*.json` | TV1 | TV2, TV5 | **APPROVED** |
| **ResumeFeatures & Taxonomy** | `ResumeFeatures`, `FieldEvidence`, `FieldEnum` | N/A (Internal) | `resume-features.json`, `resume-features-missing-fields.json`, `taxonomy-format.json` | TV2 | TV3, TV5 | **APPROVED** |
| **ScoreBreakdown & Analysis Result** | `ScoreBreakdown`, `ResumeAnalysisResult`, `AiMetadata` | `/api/analyses/resume`, `/api/analyze-resume` | `resume-analysis-result.json`, `resume-analysis-result-fallback.json` | TV3 | TV4, TV5 | **APPROVED** |
| **MatchResult & JD Criteria** | `MatchResult`, `MatchAnalysisRequest` | `/api/analyses/match`, `/api/analyze-match` | `match-result.json`, `match-result-fallback.json` | TV4 | TV5, TV1 | **APPROVED** |
| **Global Error Payload** | `ApiError` (12 error codes) | Toàn bộ endpoints | `api-error-*.json` (400, 401, 403, 404, 413, 422, 500, 502) | TV5 | TV1, TV2, TV3, TV4 | **APPROVED** |

---

## 2. Cam kết thực thi từ M0 trở đi

1. **Không thay đổi đơn phương:** Sau mốc M0, không thành viên nào được tự ý sửa đổi tên trường, kiểu dữ liệu, ràng buộc required/nullable trong các file contracts/schemas/fixtures.
2. **Quy trình Contract Change Request (CCR):** Mọi thay đổi phát sinh bắt buộc phải:
   - Mở Contract Change Request giải trình lý do kỹ thuật.
   - Được sự đồng thuận của cả 5 thành viên (TV1..TV5).
   - Cập nhật đồng bộ Pydantic schemas, OpenAPI specs (`scripts/export_openapi.py`), và toàn bộ JSON fixtures liên quan.
3. **Phát triển độc lập (Decoupled Implementation):** Từ D4, các thành viên triển khai logic nghiệp vụ và frontend components dựa trên contract và mock fixtures đã khóa mà không bị block lẫn nhau.

---

## 3. Chữ ký xác nhận đồng thuận

- [x] **TV1 (Auth & App Shell & Document):** Đã đồng thuận `ParsedDocument`, `Auth`, và các mã lỗi PDF.
- [x] **TV2 (Taxonomy & Features & History):** Đã đồng thuận `ResumeFeatures`, taxonomy format, và database V1 mapping.
- [x] **TV3 (Scoring & Recommendation & Result UI):** Đã đồng thuận `ScoreBreakdown` (invariants tổng = 100) và `ResumeAnalysisResult`.
- [x] **TV4 (Matching & ATS & Evaluation):** Đã đồng thuận `MatchResult`, `MatchAnalysisRequest`, và JD matching format.
- [x] **TV5 (Contracts, OpenAPI & Orchestration):** Đã hoàn tất đóng gói, test tự động 100% pass và freeze hệ thống hợp đồng M0.
