# Roadmap triển khai dự án AI Resume Analyzer theo từng ngày

Tài liệu này là roadmap chi tiết từ đầu đến cuối dự án, với dạng như sau:
- D1..D15 là mốc thời gian chính
- Mỗi ngày có: owner, reviewer, dependency, công việc cụ thể, output cần giao, done criteria
- Mỗi thành viên biết mình phải làm gì ở mỗi ngày và cần giao output cho ai

---

## 1. Quy tắc điều phối dự án

### Thứ tự ưu tiên triển khai
1. TV5 làm trước
2. TV1 làm tiếp
3. TV2 làm tiếp
4. TV3 làm tiếp
5. TV4 làm tiếp
6. TV5 hỗ trợ hardening, CI, demo ở cuối

### Quy tắc phụ thuộc
- Không có task nào được bắt đầu nếu đầu vào chưa có từ người trước
- Một TV chỉ làm phần thuộc ownership của mình
- Mỗi task phải có output giao rõ ràng cho task sau
- Mỗi milestone phải có done criteria trước khi sang giai đoạn tiếp theo
- D1–D3 là giai đoạn khóa scope, kiến trúc và contract; D4 trở đi là giai đoạn build thực tế

### Quy tắc gate hợp đồng và approval
- M0 là cổng bắt đầu build: không ai bắt đầu implement logic chính nếu contract chưa được TV5 + TV1 + TV2 + TV3 + TV4 đồng thuận
- Sau khi D3 freeze contract, người tiêu thụ có thể bắt đầu triển khai theo fixture/mock từ contract đã khóa, nhưng không được thay đổi schema mà không qua Contract Change Request
- Mỗi output giao phải có định nghĩa rõ: input, output, validation, error payload, reviewer và done criteria
- Nếu schema thay đổi sau D3, phải tạo Contract Change Request mới, cập nhật fixture, cập nhật API contract và được team đồng thuận trước khi triển khai tiếp
- Mọi việc làm thêm ngoài scope MVP đều bị coi là scope change và mặc định không được chấp nhận trong 3 tuần

### Quy tắc “không block lẫn nhau”
- TV5 cung cấp contract baseline trước cho TV1, TV2, TV3, TV4
- TV1 chỉ bắt đầu auth/PDF khi ParsedDocument và auth contract đã được chốt
- TV2 chỉ bắt đầu extraction/persistence khi taxonomy và ResumeFeatures đã được freeze
- TV3 chỉ bắt đầu score/result khi input từ TV1/TV2 đã ổn định
- TV4 chỉ bắt đầu matching khi JD dataset và contract đã được freeze
- TV5 là người giữ chuẩn CI, schema và orchestration cuối cùng để không có drift giữa các module

---

## 2. Bản đồ ownership theo nhóm

| Thành viên | Owner chính | Reviewer mặc định | Chủ nhiệm phần chính |
| --- | --- | --- | --- |
| TV1 | Auth, App Shell, PDF validation/parsing | TV2 | login, JWT, RBAC, ParsedDocument |
| TV2 | Taxonomy, extraction, persistence/history | TV3 | ResumeFeatures, DB V1, history |
| TV3 | Scoring, recommendation, result UI, admin | TV4 | score, recommendation, admin dashboard |
| TV4 | Matching, JD comparison, ATS | TV5 | match engine, ATS, evaluation |
| TV5 | Contracts, OpenAPI, Ollama/fallback, Compose, CI | TV1 | schemas, AI orchestration, demo |

### 2.1. Issue board mapping bắt buộc

Mỗi ngày không phải là một danh sách chung; mỗi ngày là một bundle của các issue theo task ID ở kế hoạch. Mỗi issue phải có:
- owner
- reviewer
- deadline
- input
- output
- acceptance
- fixture/test command
- dependency

| Issue bundle | Owner chính | Reviewer | Mốc | Output cốt lõi |
| --- | --- | --- | --- | --- |
| T1.1–T1.5 | TV1 | TV2 | D2–D12 | Auth + App shell + PDF pipeline |
| T2.1–T2.6 | TV2 | TV3 | D3–D12 | Taxonomy + extraction + persistence/history |
| T3.1–T3.6 | TV3 | TV4 | D3–D12 | Scoring + recommendation + admin/result UI |
| T4.1–T4.6 | TV4 | TV5 | D3–D12 | Matching + ATS + evaluation |
| T5.1–T5.6 | TV5 | TV1 | D3–D13 | Contracts + Ollama/fallback + CI/E2E |

> Bản roadmap này chỉ là “daily execution view”; bản issue chính thức theo ID task mới là nguồn kiểm soát thực thi và review.

---

## 3. Roadmap chi tiết theo từng ngày

### D1 — Kickoff + khóa scope và kiến trúc

Issue IDs ưu tiên: T1.1, T2.1, T3.1, T4.1, T5.1

#### TV1
- [ ] Cùng team xác nhận scope MVP
- [ ] Đồng thuận mô hình auth và route shell
- [ ] Xác nhận frontend route yêu cầu cho USER/ADMIN
- [ ] Review ownership với TV2 và TV5
- [ ] Output: roadmap auth/app shell đầu tiên, không làm cạnh scope

Reviewer: TV2
Phụ thuộc: không có
Done criteria:
- [ ] Scope và ownership được thống nhất
- [ ] Không có tính năng ngoài MVP được thêm

#### TV2
- [ ] Đồng thuận dữ liệu đầu vào/đầu ra giữa CV/JD và extraction
- [ ] Review taxonomy scope với TV3/TV4
- [ ] Output: khung dữ liệu extraction và ownership

Reviewer: TV3
Phụ thuộc: không có
Done criteria:
- [ ] Mô tả rõ vực extraction và taxonomy

#### TV3
- [ ] Chốt score rubric và các tiêu chí đánh giá
- [ ] Review với TV4 về output scoring cần cho matching
- [ ] Output: khung score/criteria

Reviewer: TV4
Phụ thuộc: TV2 + TV5
Done criteria:
- [ ] Chốt rubric và output score nghĩa là gì

#### TV4
- [ ] Xác nhận JD matching cần thứ gì từ CV và taxonomy
- [ ] Review dataset và evaluation requirements
- [ ] Output: khung matching input

Reviewer: TV5
Phụ thuộc: TV2 + TV5
Done criteria:
- [ ] Hiểu rõ JD và output cần cho matching

#### TV5
- [ ] Khóa contract architecture và OpenAPI baseline
- [ ] Xác nhận shared schema đầu tiên
- [ ] Output: cấu trúc contract, lỗi, output schema baseline

Reviewer: TV1
Phụ thuộc: không có
Done criteria:
- [ ] Contract baseline được team đồng thuận

---

### D2 — Contract foundation + repo skeleton

Issue IDs ưu tiên: T1.1, T2.1, T3.1, T4.1, T5.1

#### TV5 (owner chính)
- [x] Tạo Pydantic schemas: Auth, ParsedDocument, ResumeFeatures, ResumeAnalysisResult, MatchResult, ApiError
- [x] Export OpenAPI baseline
- [x] Tạo valid/error fixtures công khai
- [x] Định nghĩa contract request/response mẫu
- [x] Cấu hình docker-compose.yml, .env.example, env list
- [x] Đặt baseline CI và health-check
- [x] Output: contract chuẩn để các TV khác dùng

Reviewer: TV1
Phụ thuộc: không có
Done criteria:
- [x] Contract được review và dùng làm nền cho các module khác
- [x] Các fixture valid/error được làm sẵn

#### TV1
- [ ] Review contract auth + PDF với TV5
- [ ] Khởi tạo frontend app shell
- [ ] Tạo route cơ bản: login, dashboard, history, admin
- [ ] Output: app shell skeleton

Reviewer: TV2
Phụ thuộc: TV5 contract
Done criteria:
- [ ] Frontend app shell tồn tại và route cơ bản chạy được

#### TV2
- [ ] Review schema data model với TV5
- [ ] Draft taxonomy và field enum
- [ ] Output: taxonomy skeleton và data model draft

Reviewer: TV3
Phụ thuộc: TV5 contract
Done criteria:
- [ ] Field/skill names đã thống nhất

#### TV3
- [ ] Review schema score và output format với TV5
- [ ] Output: score invariant draft

Reviewer: TV4
Phụ thuộc: TV5 contract
Done criteria:
- [ ] Score contract tường minh và không mơ hồ

#### TV4
- [ ] Review contract matching với TV5
- [ ] Output: match output draft và JD dataset structure

Reviewer: TV5
Phụ thuộc: TV5 contract
Done criteria:
- [ ] Match input/output định nghĩa rõ

---

### D3 — M0 contract freeze

Issue IDs ưu tiên: T1.2, T2.1, T3.1, T4.1, T5.1

#### TV5 (owner chính)
- [x] Finalize Pydantic/OpenAPI cho toàn bộ flow
- [x] Chốt valid/error fixtures
- [x] Kiểm tra required/nullable/default đúng
- [x] Tạo danh sách approval mặc định cho từng contract: Auth, ParsedDocument, ResumeFeatures, ScoreResult, MatchResult, ApiError
- [x] Output: freeze contract toàn dự án

Reviewer: TV1 + TV2 + TV3 + TV4
Phụ thuộc: D2 đã có baseline
Done criteria:
- [x] Không còn thay đổi schema không rõ lý do
- [x] TV1, TV2, TV3, TV4 đồng thuận
- [x] M0 approval gate được ký xong trước khi sang D4
- [x] Nếu có schema thay đổi sau D3, phải mở Contract Change Request mới

#### TV1
- [ ] Chốt ParsedDocument contract
- [ ] Chốt PDF validation/error contract
- [ ] Review với TV2: ParsedDocument có đủ dữ liệu cho extraction
- [ ] Output: document contract approved

Reviewer: TV2
Phụ thuộc: TV5 schema
Done criteria:
- [ ] ParsedDocument format được chốt
- [ ] Error code từng loại PDF rõ ràng
- [ ] Approval cho document contract đã hoàn tất

#### TV2
- [ ] Chốt taxonomy + aliases
- [ ] Chốt ResumeFeatures schema
- [ ] Review với TV3 và TV4: ResumeFeatures đủ cho scoring và matching
- [ ] Output: taxonomy + ResumeFeatures freeze

Reviewer: TV3
Phụ thuộc: TV5 + TV1 contract
Done criteria:
- [ ] ResumeFeatures ready để các nhóm khác dùng

#### TV3
- [ ] Chốt score contract và boundary cases
- [ ] Review contract với TV5 và TV2
- [ ] Output: score format freeze

Reviewer: TV4
Phụ thuộc: TV2 + TV5
Done criteria:
- [ ] Score contract rõ và không phụ thuộc mock

#### TV4
- [ ] Chốt ground truth JD/pair format
- [ ] Review match output với TV5
- [ ] Output: JD match contract freeze

Reviewer: TV5
Phụ thuộc: TV2 + TV5
Done criteria:
- [ ] Match result format rõ và chuẩn hóa

---

### D4 — Frontend app shell + auth screen

Issue IDs ưu tiên: T1.1, T1.2, T5.4

#### TV1 (owner chính)
- [ ] Hoàn thiện App Shell
- [ ] Tạo route login / protected route
- [ ] Redirect user chưa auth về login
- [ ] Redirect role sai về đúng dashboard
- [ ] Tạo loading/error state tiếng Anh
- [ ] Output: frontend shell ready

Reviewer: TV2
Phụ thuộc: D3 contract freeze
Done criteria:
- [ ] USER/ADMIN route đúng
- [ ] Auth UI chạy với mock hoặc token placeholder

#### TV5
- [ ] Review auth mock contract và error responses
- [ ] Output: auth contract confirm

Reviewer: TV1
Phụ thuộc: D3
Done criteria:
- [ ] Contract auth rõ trước khi TV1 code backend

#### TV2
- [ ] Review app shell với role flow để chuẩn hóa history/admin UI
- [ ] Output: confirmation về route chuẩn cho UI

Reviewer: TV3
Phụ thuộc: D3
Done criteria:
- [ ] Không có route conflict

---

### D5 — Auth backend chính thức

Issue IDs ưu tiên: T1.2, T2.4, T5.4

#### TV1 (owner chính)
- [ ] Seed users USER và ADMIN
- [ ] Implement BCrypt password hashing
- [ ] Implement login API
- [ ] Implement JWT access token 2 giờ
- [ ] Implement /api/me
- [ ] Implement RBAC
- [ ] Invalid/expired token trả 401
- [ ] Wrong role trả 403
- [ ] Logout frontend xóa sessionStorage
- [ ] Output: auth backend ready

Reviewer: TV2
Phụ thuộc: D3 contract freeze
Done criteria:
- [ ] Hai seed account login thành công
- [ ] Invalid token/test được pass

#### TV2
- [ ] Review auth contract với TV1 để tên trường đúng
- [ ] Output: confirm auth data model

Reviewer: TV3
Phụ thuộc: D3
Done criteria:
- [ ] Auth fields không mâu thuẫn với DB model

#### TV5
- [ ] Review OpenAPI auth contract và error payload
- [ ] Output: auth contract sign-off

Reviewer: TV1
Phụ thuộc: D3
Done criteria:
- [ ] Error response chuẩn hóa

---

### D6 — PDF validation + ParsedDocument

Issue IDs ưu tiên: T1.3, T1.4, T2.2, T5.2

#### TV1 (owner chính)
- [ ] Validate PDF: size, MIME, magic bytes, encrypted, damaged, no text
- [ ] Map lỗi đúng loại
- [ ] Extract text từ PDF
- [ ] Preprocess Unicode/whitespace
- [ ] Tạo ParsedDocument output chuẩn
- [ ] Không log raw text hoặc raw CV
- [ ] Output: ParsedDocument ready

Reviewer: TV2
Phụ thuộc: D3 contract freeze
Done criteria:
- [ ] PDF valid/invalid cases pass
- [ ] ParsedDocument output đúng schema

#### TV2
- [ ] Review ParsedDocument vs extraction requirements
- [ ] Output: confirmation dữ liệu đủ dùng cho extraction

Reviewer: TV3
Phụ thuộc: D3
Done criteria:
- [ ] Không thiếu trường cần thiết cho extraction

#### TV5
- [ ] Review document error contract và schema
- [ ] Output: document contract sign-off

Reviewer: TV1
Phụ thuộc: D3
Done criteria:
- [ ] Error payload chuẩn hóa

---

### D7 — Taxonomy + extraction draft

Issue IDs ưu tiên: T2.1, T2.2, T3.2, T4.2, T5.2

#### TV2 (owner chính)
- [ ] Tạo taxonomy canonical skill aliases
- [ ] Không trùng canonical name
- [ ] Extract name/email/skills từ ParsedDocument
- [ ] Output: ResumeFeatures draft và skill taxonomy

Reviewer: TV3
Phụ thuộc: D6 ParsedDocument ready
Done criteria:
- [ ] Skill canonical unique
- [ ] Name/email extraction hoạt động trên fixture

#### TV1
- [ ] Review extraction input từ ParsedDocument
- [ ] Output: confirm input chuẩn

Reviewer: TV2
Phụ thuộc: D6
Done criteria:
- [ ] Không có fields bị thiếu

#### TV3
- [ ] Review taxonomy để chuẩn hóa scoring baseline
- [ ] Output: score taxonomy mapping draft

Reviewer: TV4
Phụ thuộc: D6
Done criteria:
- [ ] Không có mismatch giữa skill name và score rubric

---

### D8 — DB V1 + ownership + history

Issue IDs ưu tiên: T2.3, T2.4, T2.5, T3.3, T4.3, T5.3

#### TV2 (owner chính)
- [ ] Tạo migration DB V1 cho users và analysis_results
- [ ] Implement repository/history/detail API
- [ ] Giới hạn quyền sở hữu: USER chỉ xem dữ liệu của chính mình
- [ ] Pagination mặc định page 0 size 10
- [ ] Output: persistence/history ready

Reviewer: TV3
Phụ thuộc: D7 ResumeFeatures draft
Done criteria:
- [ ] Owner check và history detail pass

#### TV1
- [ ] Review auth-owner match với DB user
- [ ] Output: confirm user_id và role đúng

Reviewer: TV2
Phụ thuộc: D5 auth
Done criteria:
- [ ] userId trong JWT khớp với DB

#### TV3
- [ ] Review history và admin data requirements
- [ ] Output: list field cần cho admin dashboard

Reviewer: TV4
Phụ thuộc: D7
Done criteria:
- [ ] History format phù hợp với UI chờ

---

### D9 — Scoring engine + result contract

Issue IDs ưu tiên: T3.1, T3.2, T3.4, T4.4, T5.3

#### TV3 (owner chính)
- [ ] Implement scoring engine 0–100
- [ ] Score rule rõ và deterministic
- [ ] Tạo ResumeAnalysisResult schema
- [ ] Output: score result contract

Reviewer: TV4
Phụ thuộc: TV2 ResumeFeatures ready
Done criteria:
- [ ] Score stable và hợp lệ
- [ ] Score breakdown rõ ràng

#### TV2
- [ ] Review input field từ ResumeFeatures và evidence format
- [ ] Output: confirm fields đủ cho scoring

Reviewer: TV3
Phụ thuộc: D8
Done criteria:
- [ ] không thiếu input cần thiết

#### TV5
- [ ] Review schema result và error payload
- [ ] Output: sign-off result contract

Reviewer: TV3
Phụ thuộc: D3
Done criteria:
- [ ] Response contract chuẩn

---

### D10 — Recommendation + resume result UI

Issue IDs ưu tiên: T3.3, T3.4, T3.5, T4.5, T5.3

#### TV3 (owner chính)
- [ ] Build recommendation engine
- [ ] Build resume result UI
- [ ] Hiển thị breakdown, evidence, fallback badge
- [ ] Output: result page ready

Reviewer: TV4
Phụ thuộc: D9 scoring result ready
Done criteria:
- [ ] Result UI thành công trên fixtures

#### TV1
- [ ] Review auth gating cho result page
- [ ] Output: protected route đồng bộ với result page

Reviewer: TV3
Phụ thuộc: D5
Done criteria:
- [ ] Không có route bypass

#### TV2
- [ ] Review detail dữ liệu hiển thị cho user
- [ ] Output: history detail accuracy

Reviewer: TV3
Phụ thuộc: D8
Done criteria:
- [ ] Data hiển thị đúng với DB

---

### D11 — JD dataset + matching engine

Issue IDs ưu tiên: T4.1, T4.2, T4.3, T2.1, T5.2

#### TV4 (owner chính)
- [ ] Tạo frozen JD dataset + pair ground truth
- [ ] Implement skill matching engine
- [ ] Tạo ATS keyword/strengths/weaknesses output
- [ ] Output: match engine ready

Reviewer: TV5
Phụ thuộc: TV2 ResumeFeatures ready
Done criteria:
- [ ] Match output stable và deterministic

#### TV2
- [ ] Review taxonomy mapping với JD matching
- [ ] Output: skill normalization review

Reviewer: TV4
Phụ thuộc: D7
Done criteria:
- [ ] Không có mismatch canonical names

#### TV5
- [ ] Review output schema cho match result
- [ ] Output: match contract sign-off

Reviewer: TV4
Phụ thuộc: D3
Done criteria:
- [ ] Match result contract chuẩn hóa

---

### D12 — Match API/UI + evaluation draft

Issue IDs ưu tiên: T4.4, T4.5, T4.6, T2.6, T3.6, T5.5

#### TV4 (owner chính)
- [ ] Build match API và persistence
- [ ] Build match result UI
- [ ] Disable double submit
- [ ] Output: match result page ready

Reviewer: TV5
Phụ thuộc: D11 match engine ready
Done criteria:
- [ ] JD match page hoạt động và result đúng

#### TV3
- [ ] Review result UI consistency với resume result
- [ ] Output: UI style and flow alignment

Reviewer: TV4
Phụ thuộc: D10
Done criteria:
- [ ] Kết quả UX nhất quán

#### TV5
- [ ] Review match result contract và fallback response
- [ ] Output: orchestration contract ready

Reviewer: TV4
Phụ thuộc: D3
Done criteria:
- [ ] Match API mẫu hợp contract

---

### D13 — AI orchestration + fallback

Issue IDs ưu tiên: T5.2, T5.3, T5.6, T1.5, T2.6, T3.6

#### TV5 (owner chính)
- [x] Implement Ollama client với timeout và JSON mode
- [ ] Implement orchestration + validation + deterministic fallback
- [ ] Output: AI pipeline stable

Reviewer: TV1
Phụ thuộc: D12 match + D9 score
Done criteria:
- [ ] AI fail case vẫn trả schema hợp lệ

#### TV1
- [ ] Review error handling khi AI fail
- [ ] Output: frontend states for fallback

Reviewer: TV2
Phụ thuộc: D12
Done criteria:
- [ ] UI báo trạng thái fallback rõ ràng

#### TV2
- [ ] Review AI output data consistency
- [ ] Output: ensure extraction/analyzer data valid

Reviewer: TV3
Phụ thuộc: D9
Done criteria:
- [ ] Data không vi phạm schema

---

### D14 — Integration + security + CI

Issue IDs ưu tiên: T5.4, T5.5, T1.5, T2.6, T3.6, T4.6

#### TV5 (owner chính)
- [ ] CI pipeline toàn stack
- [ ] Contract validation
- [ ] E2E smoke test
- [ ] Output: release gate ready

Reviewer: TV1
Phụ thuộc: D13
Done criteria:
- [ ] CI pass và chặn merge khi fail

#### TV1
- [ ] Security và auth integration test
- [ ] Output: auth/security sign-off

Reviewer: TV2
Phụ thuộc: D5
Done criteria:
- [ ] 401/403/role check pass

#### TV2
- [ ] Review ownership, pagination, rollback test
- [ ] Output: backend integrity check

Reviewer: TV3
Phụ thuộc: D8
Done criteria:
- [ ] Data access đúng không bị IDOR

#### TV3
- [ ] Review admin/metrics/security
- [ ] Output: admin flow sign-off

Reviewer: TV4
Phụ thuộc: D10
Done criteria:
- [ ] Admin dashboard không lộ dữ liệu sai

#### TV4
- [ ] Review matching + ATS + evaluation negative paths
- [ ] Output: evaluation ready

Reviewer: TV5
Phụ thuộc: D12
Done criteria:
- [ ] Matching errors handled

---

### D15 — Demo hardening + final rehearsal

Issue IDs ưu tiên: T5.5, T5.6, T1.5, T2.6, T3.6, T4.6

#### TV5
- [ ] Runbook clean-machine
- [ ] Compose smoke demo
- [ ] AI on/off validation
- [ ] Output: final demo infrastructure ready

Reviewer: TV1
Phụ thuộc: D14
Done criteria:
- [ ] Demo chạy được từ môi trường sạch

#### TV1
- [ ] Final auth/demo flow check
- [ ] Output: final auth flow sign-off

Reviewer: TV2
Phụ thuộc: D14
Done criteria:
- [ ] Login, roles, routes pass

#### TV2
- [ ] Final data/history check
- [ ] Output: data integrity sign-off

Reviewer: TV3
Phụ thuộc: D14
Done criteria:
- [ ] History/detail đúng

#### TV3
- [ ] Final score/result/admin check
- [ ] Output: result and admin sign-off

Reviewer: TV4
Phụ thuộc: D14
Done criteria:
- [ ] UI/score đúng và không có bug rõ

#### TV4
- [ ] Final match evaluation + ATS check
- [ ] Output: match demo sign-off

Reviewer: TV5
Phụ thuộc: D14
Done criteria:
- [ ] Matching flow chạy ổn định

---

## 4. Done gate summary theo từng mốc

### Gate M0 – D3
- [ ] TV5 freeze contract
- [ ] TV1 freeze ParsedDocument + auth contract
- [ ] TV2 freeze ResumeFeatures + taxonomy
- [ ] TV3 freeze score result contract
- [ ] TV4 freeze match result contract
- [ ] Tất cả các consumer review và approve đúng schema
- [ ] Không còn pending change request chưa xử lý
- [ ] D4 bắt đầu chỉ sau khi M0 được ký đóng

### Gate M1 – D10
- [ ] Auth flow pass
- [ ] PDF parse pass
- [ ] Extraction pass
- [ ] Score flow pass
- [ ] Result UI pass

### Gate M2 – D12
- [ ] Matching pass
- [ ] History pass
- [ ] Admin pass
- [ ] AI fallback pass

### Gate M3 – D15
- [ ] CI pass
- [ ] E2E pass
- [ ] Demo pass
- [ ] Docs ready

---

## 5. Bản tóm tắt cuối cho lead

- TV5 luôn đi đầu ở contract + infra + CI
- TV1 đi tiếp ở auth + PDF + ParsedDocument
- TV2 tạo dữ liệu cốt lõi cho scoring và matching
- TV3 xây result và admin sau khi có input từ TV1 + TV2
- TV4 xây matching kế thừa ResumeFeatures từ TV2
- TV5 lại đóng vai trò cuối với orchestration/fallback/demo

Nói ngắn gọn: roadmap này cho lead biết rõ từng ngày ai làm gì, ai review, phụ thuộc gì, và phải giao output gì để không bị block nhau.

## 5. Bản tóm tắt cuối cho lead

- TV5 luôn đi đầu ở contract + infra + CI
- TV1 đi tiếp ở auth + PDF + ParsedDocument
- TV2 tạo dữ liệu cốt lõi cho scoring và matching
- TV3 xây result và admin sau khi có input từ TV1 + TV2
- TV4 xây matching kế thừa ResumeFeatures từ TV2
- TV5 lại đóng vai trò cuối với orchestration/fallback/demo

Nói ngắn gọn: roadmap này cho lead biết rõ từng ngày ai làm gì, ai review, phụ thuộc gì, và phải giao output gì để không bị block nhau.
