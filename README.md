# AI Resume Analyzer

AI Resume Analyzer là một dự án demo local theo kế hoạch 3 tuần, tập trung vào việc phân tích CV, so khớp với mô tả công việc (JD), và cung cấp lịch sử kết quả cho người dùng cũng như dashboard cho quản trị viên.

> README này là skeleton ban đầu để chuẩn hóa repo và làm nền cho việc phát triển tiếp theo. Nội dung có thể được cập nhật khi từng module chính thức được triển khai.

## 1. Tóm tắt dự án

Dự án nhằm giúp người dùng:

- đăng nhập bằng email/password
- tải lên CV PDF dạng tiếng Anh
- trích xuất thông tin từ CV
- đánh giá CV theo tiêu chí nội dung, kỹ năng và độ phù hợp
- so khớp với mô tả công việc (JD)
- xem lịch sử phân tích và chi tiết kết quả
- đối với admin, theo dõi người dùng, analyses và AI metrics

## 2. Trạng thái hiện tại của repo

Hiện tại, nhánh main đang ở trạng thái khởi đầu và chưa triển khai đầy đủ kiến trúc theo kế hoạch. Các thành phần hiện có chủ yếu là:

- tài liệu kế hoạch: `KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md`
- scaffold frontend cơ bản cho auth state và route bảo vệ:
  - `frontend/src/context/AuthContext.tsx`
  - `frontend/src/components/ProtectedRoute.tsx`

Các module sau vẫn chưa được dựng đầy đủ:

- backend Java Spring Boot
- AI service Python FastAPI
- MySQL schema và migrations
- Docker Compose runtime
- UI feature modules theo user flow
- automated test và CI

## 3. Mục tiêu nghiệp vụ

### User flows chính

1. User Login
2. Resume Analysis
3. JD Match
4. User History
5. Admin AI Dashboard

### Role và quyền

- USER: đăng nhập, tạo analysis, xem lịch sử của mình
- ADMIN: xem users, analyses và AI metrics

## 4. Kiến trúc đề xuất

### Stack chính

| Layer | Công nghệ | Mục đích |
| --- | --- | --- |
| Frontend | React + TypeScript + Vite | UI auth, upload CV, result, history, admin |
| Backend API | Java 21 + Spring Boot 3 + Spring Security + JPA | Auth, RBAC, orchestration, persistence |
| AI Service | Python 3.11 + FastAPI + Pydantic + pdfminer.six | trích xuất CV, chấm điểm, matching |
| Database | MySQL 8 | lưu users và analysis results |
| Local AI | Ollama + qwen3:4b | structured enrichment |
| Runtime | Docker Compose | chạy local toàn hệ thống |
| Quality | JUnit, pytest, Playwright, GitHub Actions | test và CI |

### Luồng kiến trúc

```text
Browser
  -> React frontend
  -> Spring Boot API -> MySQL
  -> FastAPI AI service -> Ollama
                        \-> deterministic fallback
```

## 5. Ràng buộc kế hoạch và phạm vi

Dự án tuân theo các quy định trong kế hoạch 3 tuần:

- chỉ triển khai MVP theo 5 user flow chính
- không mở rộng thêm registration, refresh token, payment, landing page, v.v.
- toàn bộ UI, API message, prompt, test, fixture và AI output dùng tiếng Anh
- dữ liệu lưu chỉ chứa kết quả có cấu trúc, không lưu file CV/JD gốc
- demo chạy local bằng Docker Compose, không cần Internet

## 6. Yêu cầu chức năng bắt buộc

- Seed 2 tài khoản demo: USER và ADMIN
- Login email/password với BCrypt + JWT access token 2 giờ
- RBAC theo role
- Upload CV PDF tối đa 5 MB, tiếng Anh
- Trích xuất text từ PDF và xử lý dạng có cấu trúc
- So khớp CV với JD tiếng Anh
- Hiển thị score, skill match/missing, ATS keywords, recommendations
- User history và admin dashboard
- Fallback deterministic khi Ollama không khả dụng

## 7. Repository structure mục tiêu

```text
.
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── backend/
│   └── src/main/java/com/resumeanalyzer/
├── ai-service/
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
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
├── docker-compose.yml
├── .env.example
├── AI_USAGE_LOG.md
├── KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md
├── README.md
└── .gitignore
```

## 8. Phân công và workflow phát triển

- Mỗi thành viên triển khai phần theo chức năng được giao
- Mỗi task cần có test xác thực
- Mọi thay đổi phải phù hợp với scope đã định trong kế hoạch
- AI-assisted development được phép, nhưng cần kiểm chứng và giải thích code

## 9. Roadmap dự kiến

### Giai đoạn 1: Foundation

- setup repo và cấu trúc dự án
- thiết lập frontend auth và route guard
- thiết lập backend skeleton
- thiết lập AI service skeleton
- cấu hình Docker Compose và env

### Giai đoạn 2: Core feature

- đăng nhập và RBAC
- upload CV và parse PDF
- resume analysis
- JD matching
- user history/detail

### Giai đoạn 3: Admin + Quality

- admin dashboard
- metrics và monitoring
- test automation
- CI/CD local validation
- demo runbook

## 10. Hướng dẫn khởi động (skeleton)

### Yêu cầu môi trường

- Node.js 18+
- Java 21
- Python 3.11
- Docker + Docker Compose
- Ollama với model `qwen3:4b`

### Bước khởi động dự kiến

```bash
# frontend
cd frontend
npm install
npm run dev

# backend
cd backend
./gradlew bootRun

# ai service
cd ai-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

> Các lệnh trên chỉ là skeleton và sẽ được cập nhật khi dự án hoàn thiện hơn.

## 11. Ghi chú

- Đây là README khởi đầu, không phải bản hoàn chỉnh của sản phẩm.
- Tất cả nội dung hiện tại cần được đồng bộ với tiến độ thực tế của repo sau mỗi milestone.
- Bản cuối của README nên phản ánh kiến trúc đã triển khai, API contract, setup thực tế và hướng dẫn chạy local chính xác.

## 12. Tài liệu tham khảo

- `KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md`
- `frontend/src/context/AuthContext.tsx`
- `frontend/src/components/ProtectedRoute.tsx`

## 13. Trạng thái hiện tại

Status: In progress / initial scaffold

- tài liệu kế hoạch đã hoàn tất
- frontend auth route scaffold đã có
- backend, AI service, database và toàn bộ flow nghiệp vụ chưa triển khai

---

Dự án cần được cập nhật thường xuyên theo tiến độ thực tế để đảm bảo README luôn là nguồn tham khảo đáng tin cậy cho team.
