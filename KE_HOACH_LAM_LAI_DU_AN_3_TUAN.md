# Kế hoạch xây dựng lại AI Resume Analyzer trong 3 tuần

> Single source of truth cho nhóm 5 thành viên. Tài liệu này đủ để tạo repo mới, tạo GitHub Issue, phát triển, kiểm thử, chạy demo local và chuẩn bị vấn đáp.

## 0. Quyết định đã khóa

| Thuộc tính | Quyết định |
| --- | --- |
| Thời lượng | 3 tuần, 15 ngày làm việc |
| Nhân sự | 5 thành viên, mỗi người 18 story points |
| Mục tiêu | Demo môn Trí tuệ nhân tạo trên máy local |
| Ngôn ngữ tài liệu | Tiếng Việt |
| Ngôn ngữ sản phẩm | Toàn bộ UI, API message, prompt, test, fixture và AI output dùng tiếng Anh |
| Người dùng | Hai tài khoản seed sẵn có role USER và ADMIN |
| Xác thực | Email/password, BCrypt, JWT access token có hạn 2 giờ, RBAC; frontend lưu token trong sessionStorage |
| AI local | Ollama chạy trên host với model qwen3:4b |
| Chế độ dự phòng | Deterministic fallback; demo vẫn chạy khi Ollama tắt |
| Dữ liệu vào | CV PDF dạng text, tiếng Anh, tối đa 5 MB; JD là text tiếng Anh |
| Dữ liệu lưu | Chỉ lưu kết quả có cấu trúc và metadata; không lưu file hoặc toàn bộ nội dung CV/JD |
| Triển khai | Docker Compose local; không cần máy chủ Internet |
| Mốc khóa hợp đồng M0 | Cuối ngày 3 |
| Mốc khóa tính năng | Cuối ngày 10 |
| Phương thức làm việc | AI-assisted development được phép, nhưng thành viên phải kiểm chứng, test và giải thích được code |

Quyết định trên chỉ được thay đổi bằng Contract Change Request theo mục 8.5. Thành viên không tự thêm tính năng, bảng dữ liệu hoặc endpoint.

---

## 1. Mục tiêu và phạm vi

### 1.1. Bài toán

AI Resume Analyzer giúp một người dùng:

1. Đăng nhập.
2. Tải CV lên để trích xuất dữ liệu và nhận đánh giá.
3. So khớp CV với mô tả công việc.
4. Xem lại lịch sử và chi tiết kết quả.

Quản trị viên theo dõi người dùng, các lần phân tích và chỉ số vận hành AI. Trọng tâm học thuật là pipeline xử lý tài liệu, trích xuất đặc trưng, phân loại, chấm điểm, so khớp và đánh giá chất lượng AI.

### 1.2. Năm user flow duy nhất

| ID | Flow | Kết quả thành công |
| --- | --- | --- |
| UF-01 | User Login | USER hoặc ADMIN nhận JWT và vào đúng màn hình theo role |
| UF-02 | Resume Analysis | USER nhận thông tin trích xuất, lĩnh vực, bằng chứng, điểm, kỹ năng đề xuất và khuyến nghị |
| UF-03 | JD Match | USER nhận điểm phù hợp, kỹ năng khớp/thiếu, từ khóa ATS, điểm mạnh, điểm yếu và khuyến nghị |
| UF-04 | User History | USER chỉ xem danh sách và chi tiết kết quả do mình sở hữu |
| UF-05 | Admin AI Dashboard | ADMIN xem users, analyses và AI metrics |

### 1.3. Phạm vi MVP bắt buộc

- Seed đúng hai tài khoản demo USER và ADMIN.
- Login email/password, BCrypt, JWT access token, RBAC và logout ở frontend bằng cách xóa token.
- Phân tích CV PDF tiếng Anh.
- So khớp CV với JD tiếng Anh.
- Lịch sử và trang chi tiết của USER.
- Trang ADMIN cho users, analyses và AI metrics.
- Ollama qwen3:4b, structured output, validation và deterministic fallback.
- Docker Compose local, automated tests, CI và AI evaluation.
- Bộ dữ liệu giả lập không chứa PII thật.

### 1.4. Tiêu chí không mở rộng phạm vi

Một ý tưởng mới chỉ được xem là bug fix nếu nó làm một acceptance criterion hiện có hoạt động đúng. Mọi thay đổi làm tăng số user flow, endpoint, bảng dữ liệu hoặc màn hình đều là scope change và mặc định bị từ chối trong ba tuần.

### 1.5. Out of Scope

Các mục sau không được tạo P0/P1 task, API, schema, migration, UI, test demo hoặc tiêu chí thành công:

- Registration và Google Login.
- Refresh token và backend logout/revoke.
- Credit, purchase và payment.
- CSV export.
- Marketing landing page và trang profile riêng.
- Recommended courses.
- Phone extraction, degree extraction và candidate level.
- JD preview.
- Rewrite suggestions.
- Complex animations.
- VPS, CD, production deployment và production backup.

### 1.6. Future Work

Chỉ ghi nhận để tham khảo sau môn học, không triển khai trong kế hoạch này:

- OCR cho scanned PDF.
- Fine-tuning model.
- Vietnamese input.
- Real OAuth và real payment.
- Rewrite suggestions có kiểm soát.

---

## 2. Nghiệp vụ, quyền và yêu cầu phi chức năng

### 2.1. Role và quyền

| Tài nguyên/hành động | USER | ADMIN |
| --- | --- | --- |
| Login và xem tài khoản hiện tại | Có | Có |
| Tạo Resume Analysis | Có | Không cần trong demo |
| Tạo JD Match | Có | Không cần trong demo |
| Xem history/detail của chính mình | Có | Có, nếu là dữ liệu do chính ADMIN tạo |
| Xem users toàn hệ thống | Không | Có |
| Xem analyses toàn hệ thống | Không | Có |
| Xem AI metrics | Không | Có |
| Xem dữ liệu của USER khác qua endpoint USER | Không | Không; ADMIN phải dùng endpoint ADMIN |

### 2.2. Business rules

| ID | Quy tắc |
| --- | --- |
| BR-01 | Email login được trim và chuyển lowercase trước khi tra cứu |
| BR-02 | Password chỉ lưu dưới BCrypt hash, không log và không trả về API |
| BR-03 | JWT chứa userId, email, role, issuedAt và expiresAt; thời hạn 2 giờ |
| BR-04 | Frontend lưu access token trong sessionStorage; logout bằng cách xóa token và trạng thái phiên |
| BR-05 | Chỉ nhận một file có MIME PDF, magic bytes hợp lệ và dung lượng không quá 5 MB |
| BR-06 | PDF phải mở được, không encrypted và trích xuất được text có ý nghĩa |
| BR-07 | JD sau trim phải có ít nhất 50 ký tự |
| BR-08 | Kỹ năng phải được chuẩn hóa theo taxonomy, loại trùng không phân biệt hoa thường |
| BR-09 | Mọi score là số nguyên từ 0 đến 100 và được clamp trước khi trả về/lưu |
| BR-10 | Mọi kết quả ghi rõ provider, model, usedFallback và processingMs |
| BR-11 | Kết quả chỉ được lưu sau khi toàn bộ contract hợp lệ; lỗi phải rollback |
| BR-12 | USER chỉ đọc analysis_results có user_id bằng ID trong JWT |
| BR-13 | Danh sách phân trang mặc định page 0, size 10; size tối đa 50 |git switch -c quan-readme
| BR-14 | Double submit phải bị chặn trên UI; backend không tạo bản ghi nếu request trước thất bại |
| BR-15 | Raw CV/JD chỉ tồn tại trong bộ nhớ trong thời gian request và không xuất hiện trong log |

### 2.3. Yêu cầu phi chức năng

| ID | Yêu cầu đo được |
| --- | --- |
| NFR-01 | Rule-only request có p95 dưới 5 giây trên máy demo |
| NFR-02 | Request có Ollama có timeout 60 giây; sau đó tự chuyển fallback |
| NFR-03 | 100% response thành công khớp Pydantic/OpenAPI contract |
| NFR-04 | Hệ thống hoạt động đầy đủ các flow cốt lõi khi Ollama tắt |
| NFR-05 | Không có secret, JWT, password, raw CV hoặc raw JD trong Git và log |
| NFR-06 | Compose khởi động được từ clean machine theo runbook |
| NFR-07 | CI bắt buộc pass trước merge |
| NFR-08 | UI hiển thị loading, success và error bằng tiếng Anh |
| NFR-09 | Các thao tác bàn phím cơ bản và label form phải dùng được |

---

## 3. Kiến trúc, công nghệ và cấu trúc repo

### 3.1. Stack đã khóa

| Layer | Công nghệ | Trách nhiệm |
| --- | --- | --- |
| Frontend | React, TypeScript, Vite | Auth state, upload form, result, history, admin |
| Application API | Java 21, Spring Boot 3, Spring Security, JPA, Flyway | Auth/RBAC, orchestration nghiệp vụ, persistence, public API |
| AI service | Python 3.11, FastAPI, Pydantic, pdfminer.six | PDF parsing, extraction, scoring, matching, Ollama/fallback |
| Database | MySQL 8 | Users và analysis results |
| Local AI | Ollama, qwen3:4b | Structured enrichment trong giới hạn schema |
| Runtime | Docker Compose | Frontend, backend, AI service, database |
| Quality | JUnit, pytest, frontend test runner, Playwright, GitHub Actions | Unit, integration, contract, E2E và CI |

Không thay framework hoặc thêm database/message broker mới trong ba tuần.

### 3.2. Luồng kiến trúc

    Browser
       |
       v
    React frontend
       |
       v
    Spring Boot API -----> MySQL
       |
       v
    FastAPI AI service -----> Ollama on host
       |                         |
       +---- deterministic <-----+
             fallback

Quy tắc phụ thuộc:

- Browser chỉ gọi Spring Boot API.
- Spring Boot chịu trách nhiệm auth, authorization, ownership và persistence.
- FastAPI là stateless, không truy cập database và không xác thực USER.
- Ollama không được truy cập trực tiếp từ frontend hoặc Spring Boot.
- Nếu Ollama không khả dụng hoặc output sai schema, FastAPI trả kết quả fallback hợp lệ.

### 3.3. Cấu trúc repo mục tiêu

    .
    ├── frontend/
    │   ├── src/app/
    │   ├── src/features/auth/
    │   ├── src/features/resume/
    │   ├── src/features/matching/
    │   ├── src/features/history/
    │   └── src/features/admin/
    ├── backend/
    │   └── src/main/java/com/resumeanalyzer/
    │       ├── auth/
    │       ├── analysis/
    │       ├── admin/
    │       ├── client/
    │       └── common/
    ├── ai-service/
    │   ├── app/main.py
    │   ├── app/schemas/
    │   ├── app/document/
    │   ├── app/extraction/
    │   ├── app/scoring/
    │   ├── app/matching/
    │   ├── app/recommendation/
    │   └── app/llm/
    ├── contracts/
    │   ├── openapi/
    │   └── fixtures/
    ├── evaluation/
    │   ├── resumes/
    │   ├── jobs/
    │   ├── pairs/
    │   ├── ground-truth/
    │   └── reports/
    ├── docs/
    ├── .github/
    │   ├── CODEOWNERS
    │   ├── pull_request_template.md
    │   └── workflows/ci.yml
    ├── docker-compose.yml
    ├── .env.example
    ├── AI_USAGE_LOG.md
    └── README.md

Repo hiện tại chỉ là tài liệu tham khảo. Repo nhóm mới được khởi tạo sạch, mỗi người tự triển khai phần được giao, commit bằng tài khoản của mình và chịu trách nhiệm giải thích. Không sửa lịch sử Git, giả ngày commit hoặc chia lại code chỉ để tạo số lượng commit.

---

## 4. Dữ liệu, contract và API

### 4.1. Database V1

Chỉ có hai bảng nghiệp vụ.

#### users

| Cột | Kiểu | Null | Quy tắc |
| --- | --- | --- | --- |
| id | BIGINT | No | Primary key, auto increment |
| email | VARCHAR(190) | No | Unique, lowercase |
| full_name | VARCHAR(120) | No | Tên hiển thị |
| password_hash | VARCHAR(100) | No | BCrypt |
| role | VARCHAR(20) | No | USER hoặc ADMIN |
| created_at | TIMESTAMP | No | UTC |
| updated_at | TIMESTAMP | No | UTC |

Seed idempotent hai tài khoản từ environment variables. Không hard-code mật khẩu trong source.

#### analysis_results

| Cột | Kiểu | Null | Quy tắc |
| --- | --- | --- | --- |
| id | BIGINT | No | Primary key, auto increment |
| user_id | BIGINT | No | Foreign key đến users.id |
| analysis_type | VARCHAR(20) | No | RESUME hoặc MATCH |
| file_name | VARCHAR(255) | No | Chỉ tên file đã sanitize |
| candidate_name | VARCHAR(160) | Yes | Trường truy vấn nhanh |
| candidate_email | VARCHAR(190) | Yes | Trường truy vấn nhanh |
| predicted_field | VARCHAR(60) | Yes | Chỉ dùng RESUME |
| resume_score | INT | Yes | 0–100, chỉ dùng RESUME |
| match_score | INT | Yes | 0–100, chỉ dùng MATCH |
| target_role | VARCHAR(160) | Yes | Chỉ dùng MATCH |
| result_json | JSON | No | Toàn bộ result theo contract |
| ai_provider | VARCHAR(40) | No | OLLAMA hoặc RULE_BASED |
| ai_model | VARCHAR(80) | No | qwen3:4b hoặc deterministic-v1 |
| used_fallback | BOOLEAN | No | Mặc định false |
| processing_ms | BIGINT | No | Lớn hơn hoặc bằng 0 |
| created_at | TIMESTAMP | No | UTC |

Indexes bắt buộc:

- users(email) unique.
- analysis_results(user_id, created_at).
- analysis_results(analysis_type, created_at).
- analysis_results(ai_provider, used_fallback, created_at).

Không lưu raw PDF, extracted full text hoặc JD trong database.

### 4.2. Runtime source of truth

- Pydantic models và OpenAPI do FastAPI sinh là runtime source of truth cho contract AI.
- Spring-generated OpenAPI là runtime source of truth cho public API.
- contracts/openapi/ai-service.json được export và commit sau M0.
- contracts/openapi/public-api.json được export từ Spring Boot và commit sau M0.
- Backend DTO phải có contract test với OpenAPI/fixtures đã khóa.
- TypeScript types được sinh hoặc đối chiếu từ public OpenAPI.
- JSON fixture hợp lệ và fixture lỗi nằm trong contracts/fixtures.
- Tên field dùng camelCase ở JSON; Python dùng alias nếu code nội bộ dùng snake_case.
- Mọi danh sách mặc định là mảng rỗng, không trả null.
- Field optional phải ghi rõ nullable; không tự bỏ field khỏi response.

### 4.3. Shared type

#### ParsedDocument

| Field | Type | Required | Nullable | Default/rule |
| --- | --- | --- | --- | --- |
| fileName | string | Yes | No | Tên file sanitize |
| text | string | Yes | No | Trim, ít nhất 1 ký tự có nghĩa |
| pageCount | integer | Yes | No | Từ 1 trở lên |
| sizeBytes | integer | Yes | No | 1 đến 5,242,880 |

Ví dụ:

    {
      "fileName": "alex_resume.pdf",
      "text": "Alex Morgan\nData Analyst...",
      "pageCount": 2,
      "sizeBytes": 184220
    }

#### ResumeFeatures

| Field | Type | Required | Nullable | Default/rule |
| --- | --- | --- | --- | --- |
| candidateName | string | Yes | Yes | null khi không tìm thấy |
| candidateEmail | string | Yes | Yes | null khi không tìm thấy/hợp lệ |
| skills | string[] | Yes | No | [], canonical và unique |
| predictedField | enum | Yes | No | Unknown nếu chưa đủ bằng chứng |
| fieldEvidence | FieldEvidence[] | Yes | No | [] |

FieldEvidence gồm field: enum, matchedSkills: string[] và confidence: number từ 0 đến 1.

#### ScoreBreakdown

Mọi field đều required, non-null và là integer trong giới hạn của rubric:

- contact: 0–5.
- summary: 0–10.
- skills: 0–15.
- education: 0–10.
- experience: 0–20.
- projects: 0–15.
- achievementsCertifications: 0–10.
- quantifiedImpact: 0–15.
- total: 0–100, bằng tổng tám thành phần.

#### AiMetadata

| Field | Type | Required | Nullable | Rule |
| --- | --- | --- | --- | --- |
| provider | enum OLLAMA hoặc RULE_BASED | Yes | No | Provider cuối cùng tạo output |
| model | string | Yes | No | qwen3:4b hoặc deterministic-v1 |
| usedFallback | boolean | Yes | No | true nếu Ollama thất bại/không dùng được |
| processingMs | integer | Yes | No | Từ 0 trở lên |

#### ResumeAnalysisResult

| Field | Type | Required | Nullable | Default/rule |
| --- | --- | --- | --- | --- |
| fileName | string | Yes | No | Tên file sanitize |
| candidateName | string | Yes | Yes | null nếu thiếu |
| candidateEmail | string | Yes | Yes | null nếu thiếu |
| skills | string[] | Yes | No | [] |
| predictedField | enum | Yes | No | Một field đã khóa |
| fieldEvidence | FieldEvidence[] | Yes | No | [] |
| resumeScore | integer | Yes | No | 0–100 |
| scoreBreakdown | ScoreBreakdown | Yes | No | Tổng bằng resumeScore |
| recommendedSkills | string[] | Yes | No | [], canonical, tối đa 8 |
| recommendations | string[] | Yes | No | [], tiếng Anh, tối đa 8 |
| ai | AiMetadata | Yes | No | Luôn có |

Ví dụ:

    {
      "fileName": "alex_resume.pdf",
      "candidateName": "Alex Morgan",
      "candidateEmail": "alex@example.test",
      "skills": ["Python", "SQL", "Pandas"],
      "predictedField": "Data Science",
      "fieldEvidence": [
        {
          "field": "Data Science",
          "matchedSkills": ["Python", "Pandas"],
          "confidence": 0.8
        }
      ],
      "resumeScore": 71,
      "scoreBreakdown": {
        "contact": 5,
        "summary": 8,
        "skills": 12,
        "education": 8,
        "experience": 15,
        "projects": 10,
        "achievementsCertifications": 5,
        "quantifiedImpact": 8,
        "total": 71
      },
      "recommendedSkills": ["Machine Learning", "Docker"],
      "recommendations": ["Add measurable impact to recent experience."],
      "ai": {
        "provider": "OLLAMA",
        "model": "qwen3:4b",
        "usedFallback": false,
        "processingMs": 3180
      }
    }

#### MatchResult

| Field | Type | Required | Nullable | Default/rule |
| --- | --- | --- | --- | --- |
| fileName | string | Yes | No | Tên file sanitize |
| targetRole | string | Yes | No | Request role hoặc title trích xuất từ JD |
| matchScore | integer | Yes | No | 0–100 |
| matchedSkills | string[] | Yes | No | [] |
| missingSkills | string[] | Yes | No | [] |
| atsKeywords | string[] | Yes | No | [], tối đa 15 |
| strengths | string[] | Yes | No | [], tối đa 6 |
| weaknesses | string[] | Yes | No | [], tối đa 6 |
| recommendations | string[] | Yes | No | [], tối đa 8 |
| ai | AiMetadata | Yes | No | Luôn có |

Ví dụ:

    {
      "fileName": "alex_resume.pdf",
      "targetRole": "Data Analyst",
      "matchScore": 67,
      "matchedSkills": ["Python", "SQL"],
      "missingSkills": ["Power BI"],
      "atsKeywords": ["data visualization", "stakeholder reporting"],
      "strengths": ["Strong SQL coverage."],
      "weaknesses": ["No evidence of Power BI."],
      "recommendations": ["Add a dashboard project with measurable outcomes."],
      "ai": {
        "provider": "RULE_BASED",
        "model": "deterministic-v1",
        "usedFallback": true,
        "processingMs": 740
      }
    }

#### ApiError

| Field | Type | Required | Nullable | Rule |
| --- | --- | --- | --- | --- |
| timestamp | ISO-8601 string | Yes | No | UTC |
| status | integer | Yes | No | HTTP status |
| code | string | Yes | No | Stable machine-readable code |
| message | string | Yes | No | English, an toàn để hiển thị |
| path | string | Yes | No | Request path |
| fieldErrors | object | Yes | No | Mặc định {} |
| requestId | string | Yes | No | Correlation ID, không chứa PII |

Ví dụ:

    {
      "timestamp": "2026-08-21T08:30:00Z",
      "status": 422,
      "code": "TEXT_NOT_EXTRACTABLE",
      "message": "The PDF does not contain readable text.",
      "path": "/api/analyses/resume",
      "fieldErrors": {},
      "requestId": "req-7f13d0"
    }

### 4.4. Public Spring Boot API

| Method và path | Role | Request | Success |
| --- | --- | --- | --- |
| POST /api/auth/login | Public | JSON email:string, password:string | 200 accessToken, tokenType, expiresIn, user |
| GET /api/me | USER, ADMIN | Bearer JWT | 200 id, email, fullName, role |
| POST /api/analyses/resume | USER | multipart file:PDF | 201 id + ResumeAnalysisResult |
| POST /api/analyses/match | USER | multipart file:PDF, jobDescription:string, targetRole:string nullable | 201 id + MatchResult |
| GET /api/analyses | USER, ADMIN | page:int=0, size:int=10, type nullable | 200 paged summaries của chính caller |
| GET /api/analyses/{id} | USER, ADMIN | Path id:long | 200 detail nếu caller sở hữu |
| GET /api/admin/users | ADMIN | page:int=0, size:int=10 | 200 paged users |
| GET /api/admin/analyses | ADMIN | page:int=0, size:int=10, type/provider/fallback nullable | 200 paged system analyses |
| GET /api/admin/metrics | ADMIN | Không | 200 counts, fallbackRate, avgLatencyMs, p95LatencyMs |

Response danh sách summary không chứa resultJson đầy đủ. Detail trả object typed theo analysisType. POST thành công chỉ ghi database một lần.

### 4.5. Internal FastAPI

| Method và path | Request | Success |
| --- | --- | --- |
| GET /health | Không | 200 status, model, ollamaReachable |
| POST /api/analyze-resume | multipart file:PDF | 200 ResumeAnalysisResult |
| POST /api/analyze-match | multipart file:PDF, jobDescription:string, targetRole nullable | 200 MatchResult |

FastAPI chỉ được gọi trong Docker network. Nếu cần internal shared secret, dùng environment variable; không commit secret.

### 4.6. Health check ngoài

| Method và path | Service | Success |
| --- | --- | --- |
| GET /health | Spring Boot | 200 status, database, aiService |

### 4.7. Error contract

| HTTP | Code | Khi dùng |
| --- | --- | --- |
| 400 | MALFORMED_REQUEST | JSON/multipart sai cấu trúc hoặc tham số phân trang sai |
| 401 | BAD_CREDENTIALS | Email/password không đúng |
| 401 | UNAUTHORIZED | JWT thiếu, sai hoặc hết hạn |
| 403 | FORBIDDEN | Sai role hoặc ownership/IDOR |
| 404 | NOT_FOUND | ID hợp lệ nhưng tài nguyên không tồn tại |
| 413 | FILE_TOO_LARGE | PDF vượt 5 MB |
| 422 | INVALID_PDF | MIME/magic bytes không phải PDF |
| 422 | PDF_NOT_READABLE | PDF encrypted hoặc hỏng |
| 422 | TEXT_NOT_EXTRACTABLE | PDF scan/no-text hoặc text không có ý nghĩa |
| 422 | JD_REQUIRED | JD thiếu hoặc ngắn hơn 50 ký tự sau trim |
| 502 | AI_SERVICE_ERROR | AI service và fallback đều không thể tạo output hợp lệ |
| 500 | INTERNAL_ERROR | Database hoặc lỗi nội bộ không lộ chi tiết |

### 4.8. Traceability endpoint

| Endpoint | Flow | Contract/DB | Owner | Test tối thiểu |
| --- | --- | --- | --- | --- |
| POST /api/auth/login | UF-01 | users | TV1 | valid/invalid login |
| GET /api/me | UF-01 | users | TV1 | token và role |
| POST /api/analyses/resume | UF-02 | ResumeAnalysisResult, analysis_results | TV2 | valid + invalid PDF + rollback |
| POST /api/analyses/match | UF-03 | MatchResult, analysis_results | TV4 | valid + missing JD + rollback |
| GET /api/analyses | UF-04 | analysis_results | TV2 | pagination + ownership |
| GET /api/analyses/{id} | UF-04 | analysis_results | TV2 | own result + IDOR |
| GET /api/admin/users | UF-05 | users | TV3 | ADMIN/USER role |
| GET /api/admin/analyses | UF-05 | analysis_results | TV3 | filters + pagination |
| GET /api/admin/metrics | UF-05 | analysis_results | TV3 | aggregate + empty DB |
| Internal analyze-resume | UF-02 | ParsedDocument, ResumeAnalysisResult | TV5 | schema + fallback |
| Internal analyze-match | UF-03 | ParsedDocument, MatchResult | TV5 | schema + fallback |

---

## 5. AI pipeline và thuật toán

### 5.1. Resume Analysis pipeline

1. Validate dung lượng, MIME, magic bytes, encryption và readability.
2. Trích xuất text và page count.
3. Normalize whitespace, Unicode và line breaks.
4. Trích xuất candidateName và candidateEmail bằng rule có kiểm chứng.
5. Trích xuất canonical skills từ taxonomy.
6. Phân loại predictedField và tạo fieldEvidence.
7. Chấm ScoreBreakdown và resumeScore bằng rubric cố định.
8. Sinh recommendedSkills và recommendations.
9. Nếu Ollama sẵn sàng, dùng structured enrichment trong giới hạn schema.
10. Validate Pydantic, sanitize, allowlist và clamp.
11. Nếu Ollama timeout/sai JSON/sai schema, chạy deterministic fallback.
12. Trả result kèm AiMetadata; Spring Boot lưu atomically.

### 5.2. Taxonomy và phân loại

Field enum đã khóa:

- Data Science.
- Web Development.
- Android Development.
- iOS Development.
- UI/UX.
- Unknown.

Taxonomy là file versioned do TV2 sở hữu. Mỗi entry có canonicalName, aliases và fields. So khớp không phân biệt hoa thường và ưu tiên boundary rõ ràng.

Quy tắc phân loại deterministic:

1. Đếm số canonical skills khác nhau khớp với từng field.
2. Field cao nhất phải có ít nhất 2 skills và dẫn field thứ hai ít nhất 1 skill.
3. Nếu không đạt hoặc hòa, predictedField là Unknown.
4. Evidence chỉ chứa skill thực sự có trong CV; không cho LLM tự thêm bằng chứng.

### 5.3. Resume scoring rubric

| Thành phần | Điểm tối đa | Dấu hiệu chính |
| --- | ---: | --- |
| Contact | 5 | Có email hợp lệ và tên có thể nhận diện |
| Summary | 10 | Có professional summary rõ ràng |
| Skills | 15 | Có section và độ phủ canonical skills |
| Education | 10 | Có section giáo dục với thông tin cơ bản |
| Experience | 20 | Có kinh nghiệm, mô tả hành động và tính gần đây |
| Projects | 15 | Có dự án, vai trò/công nghệ/kết quả |
| Achievements/Certifications | 10 | Có thành tích hoặc chứng chỉ có nội dung |
| Quantified impact | 15 | Có số liệu thể hiện tác động |
| Tổng | 100 | Tổng đúng tám thành phần |

Rule engine tạo score nền. Ollama chỉ có thể diễn giải recommendations và không được tự thay đổi breakdown. Mọi điểm được clamp và kiểm tra tổng.

### 5.4. Recommendation

- recommendedSkills là canonical skills liên quan đến predictedField nhưng chưa xuất hiện, tối đa 8.
- recommendations dựa trên các mục rubric còn yếu, tối đa 8.
- Mỗi recommendation là một câu tiếng Anh, cụ thể, không khẳng định thông tin không có trong CV.
- Kết quả fallback phải luôn có recommendation hợp lệ dù Ollama tắt.

### 5.5. JD Matching pipeline

1. Parse và normalize CV như Resume Analysis.
2. Validate và normalize JD.
3. Trích xuất JD canonical skills và ATS keywords.
4. Tạo tập matchedSkills và missingSkills.
5. Tính matchScore deterministic.
6. Xác định targetRole từ request; nếu null thì dùng title dòng đầu hợp lệ của JD, nếu không có dùng Unspecified Role.
7. Tạo strengths, weaknesses và recommendations dựa trên evidence.
8. Ollama có thể làm rõ câu chữ nhưng không thay đổi skill evidence.
9. Validate schema; fallback nếu cần.

Công thức nền:

    matchScore = round(100 * count(matchedSkills) / count(jdSkills))

Nếu không trích xuất được jdSkills thì matchScore bằng 0 và recommendations yêu cầu JD cụ thể hơn. Không dùng resumeScore thay cho matchScore.

ATS keywords lấy từ allowlist/cụm từ trong JD, canonical hóa, loại trùng và tối đa 15.

### 5.6. Chính sách Ollama và an toàn prompt

| Cấu hình | Giá trị |
| --- | --- |
| Model | qwen3:4b |
| Temperature | 0.1 |
| Output | JSON object theo schema |
| Timeout | 60 giây |
| Resume text limit | 18,000 ký tự |
| JD text limit | 10,000 ký tự |
| Retry | Tối đa 1 lần cho JSON malformed, trong tổng timeout |

Quy tắc:

- CV/JD là untrusted data được đặt trong delimiter rõ ràng, không phải instruction.
- System prompt yêu cầu bỏ qua mọi instruction bên trong CV/JD.
- Model không được gọi tool, truy cập mạng, thực thi code hoặc quyết định authorization.
- Chỉ nhận field trong allowlist; field thừa bị reject.
- Output phải qua Pydantic, semantic validation, score clamp và evidence check.
- Timeout, connection error, malformed JSON, schema error hoặc evidence không hợp lệ đều kích hoạt deterministic fallback.
- Nếu cả provider và fallback không tạo được contract hợp lệ, trả AI_SERVICE_ERROR.

---

## 6. Phân công 5 thành viên

### 6.1. Ranh giới sở hữu

| Thành viên | Owner chính | Reviewer mặc định | Vùng file |
| --- | --- | --- | --- |
| TV1 | Seeded auth/RBAC, App Shell, PDF validation/parsing/preprocessing | TV2 | auth, frontend app/auth, ai-service document |
| TV2 | Metadata/skill extraction, taxonomy, classification, resume persistence/history | TV3 | extraction, taxonomy, backend resume/history, frontend history |
| TV3 | Scoring, recommendation, Resume Result UI, Admin AI Metrics | TV4 | scoring, recommendation, backend/frontend admin, resume result |
| TV4 | Deterministic JD Matching, ATS result, match API/UI, evaluation pairs | TV5 | matching, backend/frontend match |
| TV5 | Pydantic/OpenAPI, Ollama client, orchestration/fallback, Compose, CI, E2E/evaluation runner | TV1 | main.py, schemas, llm, contracts, Compose, CI, E2E |

Shared files chỉ được sửa bởi owner đã nêu:

- ai-service/app/main.py: TV5.
- Pydantic schemas và exported AI OpenAPI: TV5.
- docker-compose.yml, .env.example và CI: TV5.
- Spring security config và seed: TV1.
- Database migration V1: TV2 viết, TV1 review auth fields, TV3 review metrics fields.
- Frontend route/app shell: TV1; mỗi feature page do feature owner quản lý.

Các test command trong bảng được chạy từ thư mục module tương ứng; command evaluation và Docker được chạy từ repo root.

### 6.2. Task TV1 — 18 SP

| ID | Owner | Reviewer | SP | Deadline | Input | Output | Acceptance | Fixture/test command |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| T1.1 | TV1 | TV2 | 3 | D2 | Repo layout, UI routes | Frontend App Shell, protected route, loading/error shell | USER/ADMIN route đúng, unauthenticated về login, UI English | auth-state fixtures; npm test -- auth |
| T1.2 | TV1 | TV2 | 4 | D5 | users V1, auth contract | Seed, BCrypt, login, JWT, /api/me, RBAC | Hai seed login được; invalid/expired token 401; role sai 403 | seed env; ./mvnw test -Dtest=Auth* |
| T1.3 | TV1 | TV2 | 4 | D7 | ParsedDocument, PDF rules | File validation module và error mapping | Bắt đúng MIME, magic bytes, size, encrypted/hỏng/no-text | valid/fake/large/encrypted/scanned PDFs; python -m pytest tests/document/test_validation.py |
| T1.4 | TV1 | TV2 | 5 | D8 | PDF fixtures | Text extraction và preprocessing | Trả đúng ParsedDocument; Unicode/whitespace ổn định; không log text | 5 text PDFs; python -m pytest tests/document/test_parser.py |
| T1.5 | TV1 | TV2 | 2 | D12 | Auth/document modules | Security/negative tests và module notes | Bao phủ JWT, RBAC, PDF error paths; owner giải thích được 2 lỗi | ./mvnw test -Dtest=Security*; python -m pytest tests/document |

PR đề xuất: PR-T1A App/Auth, PR-T1B Document Validation, PR-T1C Parsing/Tests.

### 6.3. Task TV2 — 18 SP

| ID | Owner | Reviewer | SP | Deadline | Input | Output | Acceptance | Fixture/test command |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| T2.1 | TV2 | TV3 | 3 | D3 | Field enum, sample CV | Versioned skill taxonomy và aliases | Không trùng canonical key; mọi alias map đúng một canonical skill | taxonomy cases; python -m pytest tests/extraction/test_taxonomy.py |
| T2.2 | TV2 | TV3 | 4 | D7 | ParsedDocument, taxonomy | Name/email/skill extraction | Missing field trả null/[]; skill unique và canonical | 15 resume ground truths; python -m pytest tests/extraction/test_features.py |
| T2.3 | TV2 | TV3 | 3 | D8 | ResumeFeatures | Field classification và evidence | Tie/low evidence thành Unknown; evidence không hallucinate | field cases; python -m pytest tests/extraction/test_classifier.py |
| T2.4 | TV2 | TV3 | 4 | D9 | DB V1, result contracts | Migration, entity, repository, history/detail | Atomic save; pagination; ownership; result type đúng | SQL seed/results; ./mvnw test -Dtest=AnalysisRepository*,History* |
| T2.5 | TV2 | TV3 | 2 | D9 | AI client mock, persistence | POST resume orchestration ở Spring Boot | 201 lưu một record; AI lỗi rollback; response đúng fixture | resume-result.json; ./mvnw test -Dtest=ResumeAnalysis* |
| T2.6 | TV2 | TV3 | 2 | D12 | Module hoàn chỉnh | Contract/integration tests và notes | Skill F1 được báo cáo; endpoint/history tests pass | ./mvnw test -Dtest=History*; python -m pytest tests/extraction |

PR đề xuất: PR-T2A Taxonomy/Extraction, PR-T2B Classification, PR-T2C Persistence/History.

### 6.4. Task TV3 — 18 SP

| ID | Owner | Reviewer | SP | Deadline | Input | Output | Acceptance | Fixture/test command |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| T3.1 | TV3 | TV4 | 3 | D3 | Rubric 100 điểm | Score fixture, invariants và acceptance examples | Mọi breakdown tổng đúng và boundary rõ | scoring-cases.json; python -m pytest tests/scoring/test_contract.py |
| T3.2 | TV3 | TV4 | 4 | D7 | ParsedDocument, ResumeFeatures | Deterministic scoring engine | Cùng input luôn cùng score; 0–100; đúng rubric | 15 resume ground truths; python -m pytest tests/scoring/test_engine.py |
| T3.3 | TV3 | TV4 | 3 | D8 | Score, taxonomy, field | Skill/content recommendation engine | Không đề xuất skill đã có; câu English; giới hạn số lượng | recommendation cases; python -m pytest tests/recommendation |
| T3.4 | TV3 | TV4 | 3 | D9 | ResumeAnalysisResult fixture | Resume upload/result UI | Có loading/error/result, breakdown, evidence và fallback badge | frontend fixtures; npm test -- resume-result |
| T3.5 | TV3 | TV4 | 3 | D10 | users, analysis_results | Admin users/analyses/metrics API và UI | ADMIN xem được; USER 403; empty state đúng; p95 tính đúng | admin seed; ./mvnw test -Dtest=Admin*; npm test -- admin |
| T3.6 | TV3 | TV4 | 2 | D12 | Module hoàn chỉnh | Boundary/security tests và notes | Score invariant, role tests và UI tests pass | python -m pytest tests/scoring; ./mvnw test -Dtest=Admin* |

PR đề xuất: PR-T3A Scoring, PR-T3B Recommendation/Resume UI, PR-T3C Admin Metrics.

### 6.5. Task TV4 — 18 SP

| ID | Owner | Reviewer | SP | Deadline | Input | Output | Acceptance | Fixture/test command |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| T4.1 | TV4 | TV5 | 3 | D3 | Taxonomy, 10 JD | Frozen JD/pair ground truth | Có 10 JD và 10–15 pairs, không PII, expected ranges có lý do | python evaluation/validate_dataset.py |
| T4.2 | TV4 | TV5 | 4 | D7 | ResumeFeatures, JD | Deterministic skill matching và score | Matched/missing disjoint; score đúng công thức; stable | pairs fixtures; python -m pytest tests/matching/test_engine.py |
| T4.3 | TV4 | TV5 | 3 | D8 | Match evidence | ATS keywords, strengths, weaknesses, recommendations | Mọi claim có evidence; arrays unique và giới hạn | matching-cases.json; python -m pytest tests/matching/test_ats.py |
| T4.4 | TV4 | TV5 | 3 | D9 | MatchResult, DB/client mock | POST match API và persistence | JD validation; 201 lưu đúng type; lỗi rollback | match-result.json; ./mvnw test -Dtest=MatchAnalysis* |
| T4.5 | TV4 | TV5 | 3 | D10 | MatchResult fixture | Match form/result UI | Double submit disabled; states English; result đủ field | frontend fixtures; npm test -- matching |
| T4.6 | TV4 | TV5 | 2 | D12 | Module hoàn chỉnh | Matching evaluation và error tests | Range pass/fail rõ; missing JD và empty skills được test | python -m pytest tests/matching; python evaluation/run_evaluation.py --mode rule-only --area matching |

PR đề xuất: PR-T4A Ground Truth/Matching, PR-T4B ATS, PR-T4C Match API/UI.

### 6.6. Task TV5 — 18 SP

| ID | Owner | Reviewer | SP | Deadline | Input | Output | Acceptance | Fixture/test command |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| T5.1 | TV5 | TV1 | 3 | D3 | Mục 4 contracts | Pydantic schemas, OpenAPI export, fixtures | Required/nullable/default đúng; invalid fixture bị reject | python -m pytest tests/contracts; python scripts/export_openapi.py --check |
| T5.2 | TV5 | TV1 | 3 | D7 | Ollama policy, mock server | Ollama client với timeout/JSON mode | Valid JSON parse; timeout/connection/malformed được phân loại | python -m pytest tests/llm/test_client.py |
| T5.3 | TV5 | TV1 | 4 | D8 | Provider modules, contracts | main.py orchestration, validation, fallback | Provider success và mọi failure đều trả schema hợp lệ hoặc 502 | python -m pytest tests/test_orchestration.py |
| T5.4 | TV5 | TV1 | 3 | D5 | Service Dockerfiles, env list | Compose, health checks, seed env, runbook base | Clean start; service health; host Ollama kết nối được | docker compose config; docker compose up --build |
| T5.5 | TV5 | TV1 | 3 | D12 | Test commands, all services | CI pipeline và E2E core flows | Lint/test/build/contract/E2E gates; failure chặn merge | GitHub Actions; npx playwright test |
| T5.6 | TV5 | TV1 | 2 | D13 | Frozen dataset, metric spec | Evaluation runner và report template | So sánh rule-only với Ollama + fallback; có avg/p95/failure cases | python evaluation/run_evaluation.py --mode all |

PR đề xuất: PR-T5A Contracts/Compose, PR-T5B Ollama/Orchestration, PR-T5C CI/E2E/Evaluation.

### 6.7. Kiểm tra cân bằng

| Thành viên | Tổng SP | Core AI | API/UI/Platform | Test/evaluation |
| --- | ---: | --- | --- | --- |
| TV1 | 18 | Document pipeline | Auth/App Shell | Security/PDF |
| TV2 | 18 | Extraction/classification | Persistence/history | Field/skill metrics |
| TV3 | 18 | Scoring/recommendation | Result/Admin | Score/admin |
| TV4 | 18 | Matching/ATS | Match API/UI | Pair evaluation |
| TV5 | 18 | LLM/fallback/contracts | Compose/CI | E2E/evaluation runner |
| Tổng | 90 |  |  |  |

Số dòng code hoặc số commit không phải thước đo công bằng. SP, acceptance evidence, review và khả năng vấn đáp mới là tiêu chí. Người tạo bản prototype không mặc định phải trả lời toàn bộ; mỗi thành viên sở hữu một pipeline, review một pipeline khác và phải hiểu luồng end-to-end.

---

## 7. Dependency, contract freeze và handoff

### 7.1. Mốc M0

| Ngày | Phải khóa |
| --- | --- |
| D1 | Scope, kiến trúc, five flows, stack và ownership |
| D2 | Auth contract, ParsedDocument và database V1 |
| D3 | ResumeFeatures, ResumeAnalysisResult, MatchResult, ApiError, OpenAPI, fixtures và ground truth format |

M0 hoàn thành khi owner và consumer cùng approve contract fixtures. Sau M0, breaking change bắt buộc qua mục 8.5.

### 7.2. Dependency handoff

| Provider | Deliverable | Consumer | Deadline | Consumer làm trước bằng |
| --- | --- | --- | --- | --- |
| TV5 | Pydantic/OpenAPI + valid/error fixtures | TV1–TV4 | D3 | JSON examples trong tài liệu |
| TV1 | ParsedDocument provider | TV2–TV4 | D5 mock, D8 thật | parsed-document.json |
| TV2 | ResumeFeatures + taxonomy | TV3, TV4 | D5 mock, D8 thật | resume-features.json |
| TV3 | Score/recommendation provider | TV5, Resume UI | D6 mock, D8 thật | resume-result.json |
| TV4 | Matching provider | TV5, Match UI | D6 mock, D8 thật | match-result.json |
| TV5 | Ollama orchestration/fallback | TV2–TV4/backend | D6 mock, D8 thật | FastAPI mock adapter |
| TV2 | Persistence/history API | TV3 UI/admin | D6 mock, D9 thật | public API fixtures |

Không consumer nào chờ provider viết xong mới bắt đầu. Consumer phát triển với fixture/mock từ contract đã khóa.

### 7.3. Thứ tự merge

1. Contract và fixture.
2. Provider implementation.
3. Consumer integration.
4. UI integration.
5. E2E và evaluation.

PR consumer không được merge trước contract. UI có thể merge với mock nếu được feature-flag nội bộ và có issue nối API.

---

## 8. Git, review và AI-assisted workflow

### 8.1. Khởi tạo repo và Issue

1. Tạo repo mới với main được bảo vệ.
2. Commit đầu chỉ chứa skeleton, tài liệu, CODEOWNERS, PR template và CI rỗng có kiểm tra cơ bản.
3. Chuyển mỗi dòng T1.1–T5.6 thành một GitHub Issue.
4. Issue phải có ID, owner, reviewer, SP, deadline, input, output, acceptance, fixture, test command và dependency.
5. Dùng labels: member-tv1..tv5, area, contract, blocked, priority-p0, priority-p1.
6. Link PR với Issue và milestone tương ứng.

### 8.2. Branch và commit

- Branch: feat/T2.2-skill-extraction, fix/T4.4-match-rollback, test/T1.5-auth-security.
- Một branch phục vụ một Issue; thời gian mở tối đa 2 ngày.
- Tạo Draft PR trong ngày bắt đầu để reviewer thấy contract/file sẽ thay đổi.
- Commit nhỏ theo ý nghĩa, message tiếng Anh, ví dụ: feat(extraction): normalize skill aliases.
- Không commit trực tiếp main.
- Không force-push sau khi reviewer bắt đầu review nếu chưa thông báo.
- Không dùng tài khoản của người khác và không tạo commit hình thức.

### 8.3. CODEOWNERS và tránh xung đột

- CODEOWNERS phản ánh đúng vùng file mục 6.1.
- PR thay file của module khác cần owner module đó approve.
- Shared file chỉ owner sửa; người cần thay đổi gửi patch/Issue cho owner.
- Migration đã merge không được chỉnh sửa; tạo migration kế tiếp sau khi change request được duyệt.
- Contract file không được đổi cùng PR consumer nếu chưa có contract-change Issue.
- Trước khi mở PR: cập nhật main, resolve conflict trên branch và chạy test vùng ảnh hưởng.

### 8.4. PR template bắt buộc

    Issue:
    Owner:
    Reviewer:
    Story points:
    Contract/fixture used:
    What changed:
    Acceptance evidence:
    Test commands and results:
    Error paths verified:
    Security/PII check:
    AI-assisted code:
    AI output manually verified:
    Screenshots or response samples:

Reviewer phải checkout/chạy ít nhất command chính, kiểm tra acceptance và ghi evidence; chỉ đọc diff là chưa đủ.

### 8.5. Contract Change Request

Breaking change gồm đổi tên/type/nullability/default, endpoint, status code, DB field, scoring rubric hoặc taxonomy format.

Quy trình:

1. Tạo Issue nhãn contract-change, nêu lý do, before/after, affected fixtures và migration.
2. Owner contract và ít nhất một consumer bị ảnh hưởng cùng approve.
3. Tech lead cập nhật dependency/deadline và xác nhận không vượt scope.
4. Merge contract + fixtures trước.
5. Provider và consumer cập nhật ở các PR riêng có link Issue.
6. Nếu không hoàn tất trước feature freeze D10, giữ contract cũ.

### 8.6. AI_USAGE_LOG

Mỗi thành viên ghi:

| Date | Member | Issue/PR | Tool/model | Prompt purpose | Files affected | Verification | Manual changes |
| --- | --- | --- | --- | --- | --- | --- | --- |

Quy tắc:

- Không đưa secret, PII hoặc dữ liệu thật vào công cụ AI.
- Không merge dependency/hàm/API do AI bịa mà chưa kiểm tra documentation và build.
- Không dùng câu “AI generated” thay cho giải thích kỹ thuật.
- Owner đọc toàn bộ diff, chạy test và mô tả ít nhất hai error paths.
- Reviewer có quyền yêu cầu viết lại phần owner không giải thích được.

### 8.7. Daily sync và xử lý thành viên trễ

Daily sync tối đa 15 phút:

- Đã hoàn thành gì kèm link.
- Sẽ hoàn thành gì trong ngày.
- Blocker, dependency và thời điểm cần handoff.

Nếu task có nguy cơ trễ hơn 0.5 ngày:

1. Đánh dấu blocked và báo ngay trong ngày.
2. Reviewer hỗ trợ tối đa 60 phút để thu hẹp nguyên nhân.
3. Chia task theo contract boundary nhưng không đổi owner chịu trách nhiệm.
4. Cắt P1 polish trước; không cắt test, fallback hoặc security.
5. Nếu trễ 1 ngày, tech lead điều phối pair programming và cập nhật Issue/dependency.

---

## 9. Lịch triển khai 3 tuần

### 9.1. Tuần 1 — Foundation và walking skeleton

| Ngày | Mục tiêu | Deliverable bắt buộc |
| --- | --- | --- |
| D1 | Kickoff và repo | Scope/architecture/ownership khóa; repo, Issue, branch rules, skeleton |
| D2 | Contract nền | Auth contract, ParsedDocument, database V1; App Shell; Compose draft |
| D3 | M0 Contract Freeze | Toàn bộ result/error schemas, OpenAPI, fixtures, taxonomy format, evaluation format |
| D4 | Parallel provider/consumer | Auth, PDF, extraction, scoring, matching, UI làm bằng mock |
| D5 | M1 Walking Skeleton | Login → upload sample → mock/early result → save → history chạy qua toàn stack |

Exit tuần 1:

- Hai tài khoản seed login được.
- Services có health check.
- Contract tests pass.
- Một happy path end-to-end dùng fixture hoặc rule đơn giản.
- Không còn quyết định schema/API chưa khóa.

### 9.2. Tuần 2 — Core AI và feature freeze

| Ngày | Mục tiêu | Deliverable bắt buộc |
| --- | --- | --- |
| D6 | Core implementation | Parser, taxonomy, scoring, matching, Ollama mock, UI states |
| D7 | Provider complete | Extraction/scoring/matching và Ollama client có unit test |
| D8 | Integration | Orchestration, Pydantic validation, fallback, real providers |
| D9 | Persistence/UI | Resume/Match API, atomic save, history/detail, result UI |
| D10 | M2 Feature Freeze | Admin users/analyses/metrics, UI integration, tất cả P0 flow hoạt động |

Sau D10 chỉ nhận bug, test, security, documentation và demo hardening. Không thêm feature.

### 9.3. Tuần 3 — Evaluation, hardening và vấn đáp

| Ngày | Mục tiêu | Deliverable bắt buộc |
| --- | --- | --- |
| D11 | Evaluation | Chạy rule-only và Ollama + fallback; tạo báo cáo metrics/failure cases |
| D12 | Security/error/CI | JWT, RBAC, IDOR, PDF, rollback, prompt injection, schema drift, CI/E2E |
| D13 | M3 Clean-machine Demo | Cài/chạy theo README trên máy sạch; kiểm tra Ollama on/off và port override |
| D14 | Documentation/Viva | Sơ đồ, API examples, evaluation report, module notes, tập vấn đáp chéo |
| D15 | M4 Final Rehearsal | Reset data, chạy demo đúng kịch bản, backup offline assets, chốt release tag |

Buffer:

- Mỗi ngày dành 15% thời gian cho review/fix integration.
- D13–D15 không refactor lớn.
- Bug P0: flow không chạy, data leak, fallback hỏng, schema sai.
- Bug P1: kết quả sai đáng kể hoặc UI không thể sử dụng.
- P2 polish chỉ làm khi P0/P1 đã đóng.

---

## 10. Failure, security và recovery matrix

| Tình huống | Expected behavior | Test/evidence | Owner |
| --- | --- | --- | --- |
| File đổi đuôi thành PDF giả | 422 INVALID_PDF, không gọi AI, không lưu DB | fake-pdf fixture | TV1 |
| PDF trên 5 MB | 413 FILE_TOO_LARGE trước parse | oversized generated fixture | TV1 |
| PDF encrypted/hỏng | 422 PDF_NOT_READABLE | encrypted/corrupt fixture | TV1 |
| PDF scan/no-text | 422 TEXT_NOT_EXTRACTABLE | scanned fixture | TV1 |
| Name/email thiếu | null, pipeline vẫn chạy | missing-fields fixture | TV2 |
| Skill alias/ambiguity | Canonical unique; field có thể Unknown | taxonomy boundary cases | TV2 |
| Hai field hòa | Unknown với evidence thật | tie fixture | TV2 |
| Breakdown vượt giới hạn/tổng sai | Validation fail; fallback hoặc 502 | invalid-score fixture | TV3/TV5 |
| Recommendation hallucinate | Reject evidence-dependent item hoặc dùng deterministic item | adversarial fixture | TV3 |
| JD rỗng/ngắn | 422 JD_REQUIRED, không gọi AI | blank/short JD | TV4 |
| JD không có canonical skill | matchScore 0, arrays hợp lệ | generic JD fixture | TV4 |
| Ollama chưa chạy | Fallback, usedFallback true | stop Ollama E2E | TV5 |
| Ollama timeout | Hết 60 giây chuyển fallback | delayed mock | TV5 |
| Ollama invalid JSON/schema | Tối đa 1 retry rồi fallback | malformed/extra-field mock | TV5 |
| Prompt injection trong CV/JD | Coi là data; không tool/code; output allowlist | injection fixture | TV5 |
| JWT thiếu/sai/hết hạn | 401, không lộ chi tiết | security integration tests | TV1 |
| USER gọi ADMIN API | 403 | role test | TV1/TV3 |
| USER đoán ID người khác | 403, không trả metadata | IDOR test | TV2 |
| Double submit | Nút disabled; một request/record | frontend + repository count | TV4 |
| AI thành công nhưng DB save lỗi | 500, transaction rollback, không record dở | repository failure mock | TV2/TV4 |
| OpenAPI/schema drift | CI fail trước merge | snapshot/contract diff | TV5 |
| Port bị chiếm | Runbook có PORT overrides và health check | alternate-port rehearsal | TV5 |
| Máy thiếu RAM cho Ollama | Chạy rule-only fallback và báo badge | low-resource rehearsal | TV5 |
| AI sinh dependency không tồn tại | Build/lockfile/docs verification chặn PR | CI + review checklist | Mọi owner |
| Thành viên trễ | Áp dụng mục 8.7, giữ contract và cắt polish | Issue timeline | Tech lead |

### 10.1. Logging và privacy

Được log:

- requestId, endpoint, status, analysisType.
- provider/model/usedFallback/processingMs.
- Error code và stack trace chỉ ở server log cho lỗi nội bộ.

Không được log:

- Password, password hash, JWT hoặc Authorization header.
- Raw PDF, full extracted text, JD text hoặc prompt chứa dữ liệu người dùng.
- candidateName hoặc candidateEmail trong application log.

File tạm nếu thư viện tạo ra phải ở thư mục tạm riêng và xóa trong finally. Test xác minh cleanup cho success lẫn exception.

---

## 11. Kiểm thử và AI evaluation

### 11.1. Test pyramid

| Layer | Phạm vi | Gate |
| --- | --- | --- |
| Unit | Parser, taxonomy, classifier, scoring, matching, JWT, metrics | Bắt buộc |
| Contract | Pydantic, OpenAPI, Java DTO, TypeScript fixture | Bắt buộc |
| Integration | Spring security, repositories, AI client mock, transactions | Bắt buộc |
| UI component | Forms, states, result rendering, admin | Bắt buộc |
| E2E | Login, Resume, Match, History, Admin, fallback | Bắt buộc trước release |
| Evaluation | Accuracy/F1/range/latency/fallback | Bắt buộc có report |

### 11.2. Dataset

Tối thiểu:

- 15 CV tiếng Anh giả lập dạng text PDF.
- 10 JD tiếng Anh giả lập.
- 10–15 CV–JD pairs.
- Ground truth khóa cuối D3.

Phân bố CV phải có:

- Ít nhất 2 mẫu cho mỗi field không phải Unknown.
- Ít nhất 2 mẫu Unknown/ambiguous.
- Mẫu thiếu name/email, thiếu section, có alias skills và quantified impact.
- Không dùng CV/JD thật hoặc PII thật; dùng domain example.test.

Ground truth gồm:

- candidateName, candidateEmail.
- canonicalSkills.
- predictedField và evidence.
- expected score breakdown/range có lý do.
- Với pair: targetRole, expected matched/missing skills và match score range.

Sau D3 không sửa ground truth chỉ để làm metric đẹp. Mọi sửa cần Issue, reviewer và lý do lỗi nhãn.

### 11.3. Metrics và công thức

Metadata:

- Exact-match accuracy riêng cho candidateName và candidateEmail.
- Báo cáo missing-field false positive.

Skills:

- Precision = TP / (TP + FP).
- Recall = TP / (TP + FN).
- F1 = 2 × precision × recall / (precision + recall).
- Tính micro average toàn dataset và liệt kê alias failure.

Classification:

- Predicted-field accuracy.
- Confusion matrix gồm Unknown.

Scoring:

- Mean absolute error so với expected midpoint.
- Tỷ lệ score nằm trong frozen expected range.
- 100% breakdown đúng tổng và đúng giới hạn.

Matching:

- Precision/recall/F1 cho matchedSkills và missingSkills.
- Tỷ lệ matchScore nằm trong expected range.
- Tính ổn định: cùng input chạy 3 lần phải cùng deterministic score.

AI/runtime:

- JSON-valid rate trước fallback.
- Fallback rate.
- Average latency và p95 latency.
- Failure cases theo loại timeout, connection, malformed JSON, schema và evidence.

### 11.4. So sánh bắt buộc

Báo cáo có hai cấu hình trên cùng frozen dataset:

1. Rule-only.
2. Ollama + validation + fallback.

Mỗi cấu hình ghi commit SHA, máy chạy, model, thời gian, metrics và failure cases. Kết luận phải nói rõ phần nào Ollama cải thiện, phần nào rule đáng tin hơn; không chỉ đưa một score tổng.

### 11.5. Ngưỡng release môn học

- 100% contract fixtures hợp lệ được parse.
- 100% invalid contract fixtures bị reject.
- Metadata exact match tối thiểu 80% trên field có ground truth.
- Skill micro F1 tối thiểu 0.75.
- Predicted-field accuracy tối thiểu 0.70.
- Ít nhất 80% resume scores nằm trong expected range.
- Ít nhất 80% match scores nằm trong expected range.
- Deterministic stability 100%.
- Fallback E2E pass khi Ollama tắt.
- Không còn P0/P1 bug.

Ngưỡng là gate nội bộ, không được che failure case nếu chưa đạt; nhóm ghi nguyên nhân và giới hạn trong report.

### 11.6. Test commands

Frontend:

    cd frontend
    npm ci
    npm test
    npm run build

Backend:

    cd backend
    ./mvnw test
    ./mvnw package

AI service:

    cd ai-service
    python -m pytest

Compose và E2E:

    docker compose config
    docker compose up --build
    npx playwright test

Evaluation:

    python evaluation/run_evaluation.py --mode rule-only
    python evaluation/run_evaluation.py --mode ollama-fallback

Nếu repo dùng tên script khác, TV5 phải khóa tên ở D3 và cập nhật đồng thời README, CI, task command. Không để lệnh giả trong tài liệu cuối.

### 11.7. CI gates

Mỗi PR chạy:

1. Markdown/format check.
2. Frontend install, test và build.
3. Backend tests và package.
4. AI tests.
5. OpenAPI/fixture contract drift check.
6. Secret scan.

Main/release chạy thêm Compose smoke test, E2E và evaluation smoke subset. Full evaluation chạy ở D11 và trước release tag.

---

## 12. Local demo runbook

### 12.1. Prerequisites

- Git.
- Docker Engine/Desktop có Compose.
- Ollama trên host.
- Tối thiểu 8 GB RAM; khuyến nghị 16 GB khi chạy qwen3:4b.
- Ít nhất 10 GB dung lượng trống.

### 12.2. Chuẩn bị model

    ollama pull qwen3:4b
    ollama serve

Kiểm tra:

    ollama list

Nếu Ollama không chạy hoặc máy không đủ tài nguyên, hệ thống vẫn khởi động và dùng fallback.

### 12.3. Environment

.env.example phải chứa key, không chứa giá trị bí mật thật:

    DB_NAME=resume_analyzer
    DB_USER=resume_app
    DB_PASSWORD=change_me
    JWT_SECRET=replace_with_at_least_32_characters
    DEMO_USER_EMAIL=user@demo.local
    DEMO_USER_PASSWORD=UserDemo123!
    DEMO_ADMIN_EMAIL=admin@demo.local
    DEMO_ADMIN_PASSWORD=AdminDemo123!
    OLLAMA_BASE_URL=http://host.docker.internal:11434
    OLLAMA_MODEL=qwen3:4b
    OLLAMA_TIMEOUT_SECONDS=60
    FRONTEND_PORT=5173
    BACKEND_PORT=8080
    AI_SERVICE_PORT=8000
    MYSQL_PORT=3306

Demo credentials chỉ dùng local và phải được ghi trong README.

### 12.4. Start và health

    cp .env.example .env
    docker compose up --build

Health checks:

    curl http://localhost:8080/health
    curl http://localhost:8000/health

Mở frontend tại http://localhost:5173.

### 12.5. Clean database và reseed

Lệnh sau xóa toàn bộ local database volume của dự án; chỉ chạy khi đã xác nhận không cần dữ liệu demo hiện tại:

    docker compose down -v
    docker compose up --build

Seed phải idempotent: start lại không tạo user trùng; clean volume tạo lại đúng hai user.

### 12.6. Port override

Nếu port bị chiếm, sửa các biến PORT trong .env và chạy lại:

    docker compose config
    docker compose up --build

Frontend phải lấy backend base URL từ environment, không hard-code localhost port.

### 12.7. Offline demo assets

Chuẩn bị sẵn trong repo:

- Hai valid text PDFs.
- Một invalid/scanned PDF.
- Hai JD text.
- Frozen result screenshots hoặc JSON chỉ để đối chiếu, không thay cho live demo.
- Docker images/model đã được kiểm tra trên máy demo trước D15.

---

## 13. Kịch bản demo và vấn đáp

### 13.1. Demo 10–12 phút

1. Giới thiệu bài toán, năm flow và kiến trúc.
2. Login bằng USER.
3. Upload CV, xem extraction, field evidence, score breakdown và recommendations.
4. Chạy JD Match, xem score, matched/missing skills và ATS keywords.
5. Mở History và detail.
6. Logout, login ADMIN.
7. Mở users, analyses và AI metrics.
8. Tắt Ollama hoặc dùng cấu hình Ollama unavailable.
9. Chạy lại một analysis, chứng minh usedFallback true và flow vẫn hoàn tất.
10. Trình bày evaluation rule-only so với Ollama + fallback.

Không dùng dữ liệu cá nhân thật. Reset database và kiểm tra credentials trước giờ demo.

### 13.2. Phân vai trình bày

| Thành viên | Phần chính | Phần review chéo phải hiểu |
| --- | --- | --- |
| TV1 | Auth/RBAC và document pipeline | Contracts/Ollama orchestration của TV5 |
| TV2 | Extraction/classification và persistence/history | Scoring/recommendation của TV3 |
| TV3 | Scoring/recommendation và Admin AI Metrics | JD Matching của TV4 |
| TV4 | JD Matching/ATS và pair evaluation | Contracts/fallback của TV5 |
| TV5 | Schemas, Ollama/fallback, Compose, CI/evaluation | Auth/document của TV1 |

### 13.3. Checklist kiến thức chung

Mỗi người phải trả lời được:

- Vì sao tách Spring Boot và FastAPI?
- Dữ liệu đi qua hệ thống theo thứ tự nào?
- Vì sao chỉ có hai bảng và không lưu raw CV/JD?
- JWT/RBAC/ownership ngăn truy cập sai ra sao?
- Pydantic/OpenAPI ngăn schema drift thế nào?
- Fallback kích hoạt khi nào và vì sao demo vẫn deterministic?
- Scoring 100 điểm và matching score khác nhau thế nào?
- Dataset, ground truth, precision/recall/F1 và p95 được tính ra sao?
- Một prompt injection được xử lý thế nào?
- Một lỗi DB hoặc AI được rollback/trả mã lỗi ra sao?
- Phần mình viết, phần mình review, hai error paths và một trade-off.

### 13.4. Câu hỏi theo module

TV1:

- Phân biệt MIME, magic bytes và textless PDF.
- Tại sao frontend logout không cần endpoint server trong MVP?
- Phân biệt 401, 403 và ownership violation.

TV2:

- Canonical skill và alias giải quyết vấn đề gì?
- Khi nào classifier trả Unknown?
- Vì sao result_json vẫn cần các cột truy vấn nhanh?

TV3:

- Chứng minh breakdown luôn tổng 100 tối đa.
- Vì sao LLM không được đổi score?
- Fallback rate và p95 trên Admin metrics được tính thế nào?

TV4:

- Tại sao match score không dùng resume score?
- Xử lý JD không có skill như thế nào?
- Ground truth pair và expected range được khóa ra sao?

TV5:

- Khi nào retry, fallback và 502?
- Pydantic xử lý field thừa/sai type thế nào?
- Compose kết nối Ollama trên host và CI phát hiện contract drift ra sao?

### 13.5. Bằng chứng cá nhân

Mỗi thành viên chuẩn bị:

- Danh sách Issue và PR mình sở hữu.
- Hai commit quan trọng và giải thích diff.
- Test command cùng output.
- Một bug đã tìm/fix.
- Một review có nhận xét kỹ thuật thực chất.
- Một mục AI_USAGE_LOG và cách kiểm chứng.
- Sơ đồ module một trang.

---

## 14. Definition of Ready, Definition of Done, checklist và deliverables

### 14.1. Definition of Ready

Task chỉ được bắt đầu khi:

- Có ID, đúng một owner và ít nhất một reviewer.
- Có deadline và estimate; phạm vi tối đa 2 ngày.
- Input/output và contract đã có hoặc có fixture/mock.
- Dependency và handoff được ghi rõ.
- Acceptance criteria đo được.
- Có fixture/test data.
- Có test command dự kiến.
- Không chứa tính năng ngoài scope.

Nếu thiếu một mục, task ở trạng thái refinement, không in progress.

### 14.2. Definition of Done

Task chỉ done khi:

- Acceptance criteria có evidence.
- Unit/contract/integration/UI test liên quan pass.
- CI pass và không có unresolved review.
- Documentation/OpenAPI/fixture được cập nhật nếu bị ảnh hưởng.
- AI-assisted diff đã được owner kiểm chứng và ghi AI_USAGE_LOG.
- Không secret, PII hoặc raw CV/JD trong source/log/fixture.
- Reviewer đã chạy command chính và ghi kết quả.
- Owner giải thích được ít nhất hai error paths.
- PR đã merge theo đúng dependency order.
- Issue link PR/commit và đóng bởi evidence, không chỉ bằng lời xác nhận.

### 14.3. Deliverables cuối

- Repo mới có lịch sử đóng góp thực chất của 5 người.
- README và local runbook chạy được.
- Kiến trúc và business-flow document.
- OpenAPI/contract fixtures.
- Database migrations và seed.
- Source frontend, backend, AI service.
- Docker Compose và .env.example.
- Automated tests và CI.
- Frozen evaluation dataset/ground truth.
- Evaluation report so sánh hai cấu hình.
- AI_USAGE_LOG.
- Demo script và viva notes.
- Release tag cho bản demo cuối.

---

### 14.4. Day 0 checklist

- [ ] Cả 5 người đọc và đồng ý tài liệu.
- [ ] Gán tên thật cho TV1–TV5.
- [ ] Xác nhận máy demo chạy Docker và Ollama qwen3:4b.
- [ ] Tạo repo mới và bảo vệ main.
- [ ] Tạo CODEOWNERS, PR template và CI skeleton.
- [ ] Tạo 29 Issues từ T1.1 đến T5.6 với đầy đủ metadata.
- [ ] Tạo project board: Backlog, Ready, In Progress, Review, Blocked, Done.
- [ ] Commit bộ fixture giả lập ban đầu, không PII.
- [ ] Xác nhận lịch daily sync, reviewer và deadline D1–D15.
- [ ] Chưa viết feature trước khi contract tương ứng Ready.

### 14.5. Milestone checklist

M0 — cuối D3:

- [ ] Scope/architecture/database/API/result/error contracts đã khóa.
- [ ] OpenAPI và valid/error fixtures đã commit.
- [ ] Ground truth format và taxonomy format đã khóa.

M1 — cuối D5:

- [ ] Login và seeded roles hoạt động.
- [ ] Walking skeleton đi qua frontend, backend, AI mock và database.
- [ ] Compose/health checks hoạt động.

M2 — cuối D10:

- [ ] Resume Analysis, JD Match, History và Admin AI Dashboard hoạt động.
- [ ] Ollama và fallback hoạt động.
- [ ] Feature freeze có hiệu lực; không còn dependency chưa nối.

M3 — cuối D13:

- [ ] Evaluation report có metrics và failure cases.
- [ ] Security/error/contract/E2E tests pass.
- [ ] Clean-machine local demo pass.

M4 — cuối D15:

- [ ] Full demo rehearsal pass, gồm tắt Ollama.
- [ ] Không P0/P1 bug.
- [ ] Docs, evidence cá nhân và viva notes hoàn chỉnh.
- [ ] Tạo release tag.

### 14.6. Success criteria cuối

Dự án hoàn thành khi và chỉ khi:

- Local demo khởi động theo README.
- Hai seeded roles login và RBAC đúng.
- Hai AI flow Resume Analysis và JD Match trả output chuẩn.
- USER history/detail và Admin AI Metrics hoạt động.
- Ollama qwen3:4b hoạt động khi sẵn sàng và fallback hoạt động khi tắt.
- CI, E2E và evaluation gates pass hoặc mọi sai lệch ngưỡng được ghi minh bạch trong report.
- Không có chức năng ngoài scope len vào P0/P1.
- Cả 5 thành viên có 18 SP, Issue/PR/test/review evidence và giải thích được module của mình lẫn luồng chung.

Tài liệu này là baseline triển khai. Khi code, contract, Issue hoặc demo khác tài liệu, nhóm phải sửa sự khác biệt bằng quy trình change request thay vì tự suy đoán.
