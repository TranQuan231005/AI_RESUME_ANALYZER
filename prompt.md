# Prompt hoàn tất và chốt dự án AI_RESUME_ANALYZER

Bạn đang làm việc trong repository `AI_RESUME_ANALYZER`. Mục tiêu là hoàn tất các merge gate còn lại, ghi nhận evidence trung thực, và chỉ đề xuất chốt dự án khi mọi điều kiện bên dưới đạt.

## Quy tắc bắt buộc

- Không tự tạo, sửa, suy diễn hoặc điền điểm human review.
- Không công bố MAE, Spearman, alpha, hay LLM quality metrics khi review gate chưa đủ.
- Không ghi CV/JD raw text, email reviewer, tên reviewer hoặc secret vào log, report, fixture hay Git.
- Không dừng hoặc xóa stack cũ tại `E:\AI-RESUME`; đó là project khác.
- Không commit, push, merge hoặc force-push nếu owner chưa yêu cầu rõ.
- Báo cáo rõ command đã chạy, kết quả, lỗi, và phần nào còn chờ owner.

## Owner cần can thiệp trước

1. Chỉ định hai reviewer độc lập, sử dụng duy nhất ID `reviewer-1` và `reviewer-2`.
2. Hai reviewer chấm độc lập tất cả 70 matching pairs; owner nhập `adjudicatedScore` cho mọi cặp chênh lệch trên 15 điểm.
3. Sau khi Qwen live output được tạo, hai reviewer chấm đủ 20 cases theo template CSV.
4. Owner xác nhận token từng xuất hiện trong lịch sử Git đã được revoke, nếu token đó còn hiệu lực ở hệ thống bên ngoài.

Không tiếp tục các bước phụ thuộc human review cho đến khi owner cung cấp dữ liệu review thực tế. Vẫn hoàn tất mọi kiểm tra kỹ thuật độc lập khác.

## Trạng thái đã hoàn thành

- Classifier có deterministic fallback an toàn; lỗi ML inference không log nội dung CV.
- Matching evaluator chặn metric nếu không đủ đúng 70 review hợp lệ.
- Classifier evaluator dùng cùng held-out split gồm 100 samples/sáu nhãn cho heuristic và ML.
- LLM schema-only chạy 20 cases và 40 sanitizer checks, không gọi Ollama.
- Scanner chặn `file:///`, kiểm tra relative links, secrets/PII evaluation và Git history.
- Manual PDF fixtures đã được thay bằng text-PDF synthetic, parse được và chỉ có email `example.test`.
- CI có Compose full-stack API gate qua `scripts/smoke_stack.py`.
- Backend có `/health`.
- Focused regression tests, scanner history, OpenAPI và dataset validators đã pass.

## 1. Hoàn tất Docker full-stack acceptance

Máy có một stack khác ở `E:\AI-RESUME` chiếm port mặc định. Khi cần chạy local smoke, dùng override port riêng; không thay đổi stack cũ.

Tạo hoặc dùng tạm override sau:

```yaml
services:
  mysql:
    ports: !override
      - "13306:3306"
  ai-service:
    ports: !override
      - "18000:8000"
  backend:
    ports: !override
      - "18080:8080"
  frontend:
    ports: !override
      - "15173:5173"
```

Chạy:

```powershell
docker compose -f docker-compose.yml -f docker-compose.smoke.override.yml up --build --detach
python scripts/smoke_stack.py --ai-url http://localhost:18000 --backend-url http://localhost:18080 --frontend-url http://localhost:15173 --check-mysql-privacy --check-logs
```

Xác nhận:

- MySQL, AI, backend healthy; frontend process reachable.
- USER và ADMIN login thành công.
- JWT: anonymous không vào analyses; USER không vào admin.
- Resume analysis có `topTerms`.
- JD matching có `matchBreakdown.method = HYBRID_EMBEDDING`.
- History/detail và admin users/analyses/metrics thành công.
- JSON database không chứa key raw `resumeText`, `jobDescription`, `text`.
- Compose log không chứa sentinel JD của smoke.
- AI runtime không tải embedding model từ Internet.
- Khi Ollama không sẵn sàng, core flow dùng deterministic fallback thay vì fail.

Nếu smoke fail, đọc full Compose logs, sửa nguyên nhân, thêm regression test phù hợp, chạy lại focused test và smoke. Sau khi có kết quả, dọn riêng stack test:

```powershell
docker compose -f docker-compose.yml -f docker-compose.smoke.override.yml down --volumes
```

Xóa file override tạm nếu file đó không phải artifact được chấp thuận để commit.

## 2. Chạy toàn bộ technical gates

Chạy trên Python 3.11, JDK 21, Node 22:

```powershell
python scripts/scan_repository.py --check-history
python scripts/export_openapi.py --check
python evaluation/scripts/validate_classification_dataset.py
python evaluation/scripts/validate_matching_dataset.py
python evaluation/scripts/evaluate_llm.py --mode schema-only
python evaluation/scripts/evaluate_classifier.py --output $env:TEMP/classification-report.md
python evaluation/scripts/evaluate_matching.py --output $env:TEMP/matching-report.md --allow-pending
python -m pytest
```

```powershell
cd backend
./gradlew test --no-daemon
```

```powershell
cd frontend
npm ci
npm run lint
npm test -- --runInBand
npm run build
```

Trong Git Bash, dùng đường dẫn `/d/C/AI_RESUME_ANALYZER/...` và `./gradlew`, không dùng `D:\...`.

Không coi historical test totals là evidence. Chỉ ghi số liệu từ lần chạy hiện tại.

## 3. Hoàn tất matching human review khi owner cung cấp dữ liệu

Review data được lưu trong:

```text
evaluation/datasets/matching/pairs.jsonl
```

Mỗi pair phải có:

```json
{
  "reviewed": true,
  "reviewerScores": [
    {"reviewerId": "reviewer-1", "score": 0},
    {"reviewerId": "reviewer-2", "score": 0}
  ],
  "adjudicatedScore": 0
}
```

- Điểm phải là integer 0–100.
- Hai ID phải khác nhau.
- `adjudicatedScore` chỉ bắt buộc khi chênh lệch trên 15.
- Không lưu reviewer name/email.

Sau khi dữ liệu đầy đủ:

```powershell
python evaluation/scripts/validate_matching_dataset.py
python evaluation/scripts/evaluate_matching.py --output evaluation/reports/matching.md
```

Chỉ commit report matching nếu evaluator thành công và không còn `PENDING HUMAN REVIEW`.

## 4. Hoàn tất Qwen live review khi owner cung cấp reviewer

Tạo 20 output live synthetic:

```powershell
python evaluation/scripts/evaluate_llm.py --mode live --output evaluation/reviews/llm-live-outputs.jsonl
```

Output bắt buộc có `caseId`, `modelVersion`, `promptVersion`, `timestamp` và JSON output. Copy template:

```text
evaluation/datasets/llm/human_review_template.csv
```

Lưu review tại:

```text
evaluation/reviews/llm-human-reviews.csv
```

Mỗi case có đúng hai review với `reviewer-1`/`reviewer-2`; metadata phải khớp live output. Chạy:

```powershell
python evaluation/scripts/summarize_llm_reviews.py --live-output evaluation/reviews/llm-live-outputs.jsonl --reviews evaluation/reviews/llm-human-reviews.csv --output evaluation/reports/llm.md
```

Không dùng Qwen làm reviewer. Chỉ công bố LLM metric sau khi script pass toàn bộ 20 case.

## 5. Cập nhật tài liệu và final review

Sau mỗi gate pass, cập nhật đúng evidence hiện tại trong:

- `walkthrough.md`
- `docs/project/AI_UPGRADE_PROGRESS.md`
- `README.md` nếu lệnh vận hành thay đổi

Không đổi Batch 4/5 sang completed nếu human review chưa đủ. Không đổi Batch 6 sang completed nếu Docker full-stack smoke và toàn bộ CI-equivalent checks chưa pass.

Thực hiện final review:

```powershell
git diff --check
git status --short
python scripts/scan_repository.py --check-history
```

Kiểm tra rằng worktree chỉ có source, test, report, review evidence và documentation có chủ đích; không có cache, `node_modules`, `.gradle`, output tạm, secret, raw CV/JD hoặc PII.

## Điều kiện chốt dự án

Chỉ đề xuất merge khi đồng thời đạt:

1. Full-stack Docker API smoke pass.
2. Scanner, OpenAPI, Python pytest, backend JDK 21 tests, frontend Node 22 lint/test/build pass.
3. Git diff không có whitespace lỗi hay artifact tạm.
4. Matching report có metric chỉ khi đủ 70 human review hợp lệ.
5. LLM report có metric chỉ khi đủ 20 output và hai reviewer hợp lệ mỗi case.
6. Tài liệu phản ánh đúng evidence thực tế.
7. Owner đã xác nhận token cũ được revoke nếu áp dụng.

Nếu bất kỳ điều kiện nào chưa đạt, báo cáo rõ blocker và không tuyên bố dự án sẵn sàng merge.
