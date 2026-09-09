# Phân công thành viên — AI Resume Analyzer

Tài liệu này là bản phân công cập nhật theo source hiện tại. Mã `TV1`–`TV5` là mã vai trò.

## Phạm vi chung

Năm thành viên cùng chịu trách nhiệm hiểu luồng end-to-end, review chéo, chuẩn bị demo và giải thích giới hạn của hệ thống. Mỗi thành viên sở hữu phần chính của mình, nhưng không được thay đổi contract chung mà không cập nhật các consumer liên quan.

| Mã | Phạm vi sở hữu | Reviewer chéo |
|---|---|---|
| TV1 | Auth, security, App Shell và PDF | TV2 |
| TV2 | Extraction, taxonomy, persistence và history | TV3 |
| TV3 | Scoring, recommendation, Resume UI và Admin | TV4 |
| TV4 | AI matching CV–JD, embedding và matching evaluation | TV5 |
| TV5 | ML classifier, Ollama/LLM, orchestration, Docker và CI | TV1 |

## TV1 — Auth, security, App Shell và PDF

### Nhiệm vụ

- Xây dựng frontend App Shell và protected routes.
- Xử lý login, logout và session state.
- Seed tài khoản USER/ADMIN.
- BCrypt password hashing, JWT access token và RBAC.
- Bảo vệ `/api/auth/login`, `/api/me` và các endpoint theo role.
- Kiểm tra ownership khi USER xem history/detail.
- Kiểm tra file PDF: MIME type, magic bytes, kích thước, PDF hỏng, encrypted và không có text.
- Parse PDF và preprocessing text, Unicode và whitespace.
- Không log raw CV hoặc raw JD.
- Viết security tests và PDF negative tests.
- Review phần persistence và extraction của TV2.

### Đầu ra

- Auth/App Shell frontend.
- Backend security, seed và authentication.
- `ai-service/app/document/`.
- Auth/PDF fixtures và tests.

## TV2 — Extraction, taxonomy, persistence và history

### Nhiệm vụ

- Xây dựng taxonomy kỹ năng và aliases.
- Chuẩn hóa canonical skill và loại trùng.
- Trích xuất tên, email, kỹ năng, sections và evidence.
- Xử lý missing field bằng `null` hoặc `[]`.
- Xây dựng field classification và trả `Unknown` khi evidence thấp.
- Thiết kế migration, entity, repository và persistence service.
- Lưu kết quả có cấu trúc; không lưu PDF hoặc raw CV/JD.
- Xây dựng history/detail API, pagination và ownership filtering.
- Bảo đảm atomic save và rollback khi AI service lỗi.
- Viết extraction, taxonomy, persistence và history tests.
- Review scoring/recommendation của TV3.

### Đầu ra

- `ai-service/app/extraction/`.
- Backend entity, repository, migration và history.
- Taxonomy fixtures.
- Extraction/persistence tests.

## TV3 — Scoring, recommendation, Resume UI và Admin

### Nhiệm vụ

- Xây dựng rubric chấm CV tối đa 100 điểm.
- Bảo đảm breakdown tổng đúng và điểm nằm trong 0–100.
- Tính các nhóm contact, summary, skills, education, experience, projects, achievements/certifications và quantified impact.
- Xây dựng recommendation engine có evidence.
- Không đề xuất lại kỹ năng đã có.
- Xây dựng Resume Result UI với loading, success, error, breakdown, evidence và fallback badge.
- Xây dựng Admin API/UI cho users, analyses và metrics.
- Bảo đảm USER không truy cập admin endpoint.
- Viết scoring, recommendation, admin và UI tests.
- Review matching của TV4.

### Đầu ra

- `ai-service/app/scoring/`.
- `ai-service/app/recommendation/`.
- Resume result components.
- Admin dashboard.
- Scoring/admin fixtures và tests.

## TV4 — AI matching CV–JD, embedding và evaluation

### Nhiệm vụ

- Xây dựng pipeline matching CV–JD.
- Chuẩn hóa kỹ năng CV/JD và xử lý aliases.
- Chia CV/JD thành chunk.
- Tạo embedding bằng `sentence-transformers/all-MiniLM-L6-v2`.
- Tính cosine similarity và skill coverage.
- Kết hợp điểm theo cấu hình runtime:

  `match score = 0.7 × skill score + 0.3 × semantic score`.

- Trả về matched skills, missing skills, top terms, ATS keywords, strengths, weaknesses, recommendations và match breakdown.
- Ghi rõ `HYBRID_EMBEDDING` khi embedding hoạt động.
- Dùng `SKILL_ONLY` khi embedding không khả dụng.
- Xử lý JD không có skill, dữ liệu thiếu, skill trùng và khác cách viết.
- Tích hợp match API, persistence và match form/result UI.
- Chuẩn bị dataset matching 70 cặp.
- Quản lý form, CSV, validator và evidence human review matching.
- Chạy calibration, held-out evaluation và latency evaluation.
- Báo cáo MAE, Spearman, p50/p95 và breakdown theo scenario.
- Viết matching engine, embedding, ATS và evaluation tests.
- Review LLM integration của TV5.

### Lưu ý evaluation

TV4 không tự tạo điểm human review. TV4 chỉ chuẩn bị công cụ và tổng hợp điểm do reviewer độc lập cung cấp.

Báo cáo calibration hiện có thể sử dụng cấu hình tạm khác metadata runtime. Khi trình bày phải phân biệt metric evaluator với cấu hình production trong `ai-service/models/matching/metadata.json`.

### Đầu ra

- `ai-service/app/matching/`.
- `ai-service/models/matching/metadata.json`.
- `evaluation/datasets/matching/`.
- `evaluation/scripts/evaluate_matching.py`.
- Matching reports, review evidence và tests.

## TV5 — ML classifier, Ollama/LLM, orchestration, Docker và CI

### ML classifier

- Xây dựng TF-IDF vectorizer và Logistic Regression classifier.
- Phân loại Data Science, Web Development, Android Development, iOS Development, UI/UX và `Unknown`.
- Calibrate OOD/Unknown threshold.
- Lưu artifact model bằng joblib và metadata version/seed/parameters.
- Trả về predicted field, confidence, influential terms, evidence và `usedModel`.
- Fallback deterministic khi artifact thiếu, hỏng hoặc inference lỗi.
- Không log raw CV khi inference lỗi.
- Đánh giá trên 50 in-domain và 50 OOD held-out samples.
- Viết regression tests cho inference exception và fallback.

### Ollama/LLM

- Xây dựng Ollama client, warmup, timeout và keep-alive.
- Dùng Qwen3 **0.6B** làm model runtime mặc định.
- Tắt thinking bằng `think=false`.
- Giới hạn prompt và validate/sanitize JSON output.
- Phân loại connection, timeout, malformed JSON, schema và evidence errors.
- Trả deterministic fallback khi Ollama không sẵn sàng.
- Ghi provider, model, usedFallback và processingMs.
- Không log prompt, CV, JD hoặc raw generated text.
- Quản lý output và metadata của LLM evaluation.

Human review Qwen4B là evidence lịch sử của output 4B; không dùng điểm đó để kết luận chất lượng 0.6B. Muốn đánh giá 0.6B phải sinh output mới và review mới.

### Orchestration, Docker và CI

- Điều phối pipeline trong `ai-service/app/main.py`.
- Health endpoint cho classifier, embedding và Ollama.
- Dockerfile AI service và embedding model build-time.
- Docker Compose, environment variables và healthchecks.
- OpenAPI export/check.
- Full-stack smoke cho login, resume, matching, history/detail, admin, JWT và privacy.
- CI jobs cho Python, classifier artifact, schema-only LLM, OpenAPI, scanner và Docker runtime.
- Viết orchestration, fallback, Docker và CI tests.
- Review security/document boundary của TV1.

### Đầu ra

- `ai-service/app/ml/`.
- `ai-service/app/llm/`.
- `ai-service/app/main.py`.
- `ai-service/models/classifier/`.
- `evaluation/datasets/classification/`.
- `evaluation/scripts/evaluate_classifier.py` và `evaluate_llm.py`.
- Dockerfile, Compose và CI workflow.

## Nguyên tắc phối hợp

- TV1–TV3 cung cấp contract và dữ liệu đầu vào ổn định cho TV4/TV5.
- TV4 sở hữu logic matching; TV5 chỉ tích hợp matching vào orchestration.
- TV5 sở hữu classifier runtime và LLM; TV2 không tự sửa classifier artifact nếu không phối hợp TV5.
- Human reviewer là người cung cấp điểm; thành viên không tự chấm thay reviewer.
- Mọi thay đổi OpenAPI, schema, metadata model hoặc matching weights phải cập nhật test và tài liệu liên quan.
- Demo và bảo vệ là trách nhiệm chung của cả nhóm.

## Giới hạn cần ghi trong báo cáo

- Dữ liệu classifier/matching chủ yếu là synthetic.
- Điểm human review LLM hiện gắn với Qwen4B, không áp dụng cho Qwen3 0.6B.
- Matching runtime và calibration report phải được đối chiếu riêng.
- Điểm matching không phải xác suất được tuyển dụng.
- Fallback bảo đảm hệ thống tiếp tục chạy, không chứng minh chất lượng tương đương LLM.
