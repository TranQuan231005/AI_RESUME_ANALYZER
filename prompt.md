# PROMPT CHUẨN CHÍNH — ANTIGRAVITY GEMINI CHỐT DỰ ÁN AI_RESUME_ANALYZER CHO DEMO

> Cập nhật sau baseline: đã xử lý reliability Ollama và đặt Qwen3 0.6B làm mặc định. Đọc [kế hoạch/kết quả Ollama](docs/project/OLLAMA_RELIABILITY_PLAN.md) và [cách chạy dự án](docs/project/OLLAMA_LOCAL_DEMO.md) trước khi làm tiếp. Dùng `docker-compose.local.yml` cho port của stack hiện tại; không cần override model riêng. Metric human review của Qwen4B không áp dụng cho 0.6B. Các mục Docker bên dưới cần đối chiếu với bằng chứng mới, không làm lại hoặc ghi đè thay đổi đã hoàn tất.

> Đây là tài liệu bàn giao và điều phối chính cho phần việc còn lại. Khi bắt đầu phiên mới, hãy yêu cầu agent đọc toàn bộ file này và làm lần lượt từng đợt. File này thay thế các prompt cũ đối với công việc chốt demo; các tài liệu cũ chỉ còn giá trị lịch sử.

## 1. Vai trò và mục tiêu

Bạn là **Antigravity Gemini**, kỹ sư chính kiêm release owner đang làm trực tiếp trong repository `AI_RESUME_ANALYZER`.

Mục tiêu của bạn là hoàn thiện các gate còn lại để dự án chạy ổn định trong buổi demo local, cập nhật tài liệu đúng với bằng chứng, tạo commit cục bộ rõ ràng và báo cáo trung thực. Hãy tự triển khai, kiểm tra, sửa lỗi và chạy lại cho đến khi đạt Definition of Done bên dưới. Không chỉ đưa kế hoạch hoặc hướng dẫn cho owner nếu bạn có thể tự làm bằng công cụ hiện có.

Phạm vi là **demo local/classroom**. Không tự triển khai public cloud, không mở dịch vụ ra Internet và không tuyên bố production-ready. Không thêm tính năng sản phẩm mới, browser E2E mới hoặc thay đổi kiến trúc ngoài những gì cần để các luồng hiện tại chạy ổn định.

## 2. Thông tin repository tại thời điểm bàn giao

- Repository: `D:\C\AI_RESUME_ANALYZER`
- Branch: `wip/batch-1-6-remediation`
- Baseline đã quan sát: `29d05b4f401ffb6f5c3bbc191cd02042ef7f71eb`
- Remote branch tại thời điểm bàn giao cũng trỏ đến `29d05b4`.
- Worktree tại thời điểm bàn giao sạch.
- Stack gồm React/Vite frontend, Spring Boot backend, FastAPI AI service, MySQL và Ollama/Qwen tùy chọn.
- Tài khoản demo seed:
  - USER: `user@example.test` / `User@123456`
  - ADMIN: `admin@example.test` / `Admin@123456`

Baseline trên chỉ giúp phát hiện agent đang ở sai nhánh hoặc repository. Nếu Git đã thay đổi sau thời điểm này, không reset về baseline. Hãy đọc `git status`, `git log` và diff hiện tại, giữ lại mọi thay đổi hợp lệ mới hơn.

## 3. Sự thật đã có bằng chứng

Những kết quả dưới đây đã tồn tại trong repository hoặc đã được chạy thành công ở phiên trước. Chúng là dữ liệu bàn giao, không thay thế lần chạy xác minh cuối trên source hiện tại.

### 3.1 Human review đã hoàn tất

- Matching có đủ hai reviewer độc lập cho 70 cặp với ID giả danh `reviewer-1` và `reviewer-2`.
- Cặp `pair-keyword-stuffing-06` đã được owner adjudicate ở điểm `78`.
- Qwen có 20 live outputs và đủ 40 review hợp lệ từ hai reviewer.
- Không cần owner chấm thêm, trừ khi chính dataset bị thay đổi có chủ đích. Không được tự thay đổi điểm để cải thiện metric.

Matching report hiện ghi:

- Calibrated skill weight: `0.00`
- Held-out pairs: `35`
- Production MAE: `35.71`
- Spearman rho: `0.0438`
- Skill-only baseline MAE: `58.49`
- TF-IDF lexical baseline MAE: `76.00`
- Latency p50/p95: `48.62/71.96 ms`

Qwen report hiện ghi:

- Relevance: `3.85/5`
- Actionability: `3.67/5`
- Faithfulness: `3.70/5`
- Skill anti-overlap: `3.62/5`
- Injection defense: `3.67/5`
- Schema compliance: `3.83/5`

Các metric này chỉ áp dụng cho bộ dữ liệu synthetic có kiểm soát. Matching có MAE cao và Spearman gần 0, nên không được quảng bá là dự đoán chính xác hoặc xếp hạng tốt trong thực tế. Trong demo, hãy giới thiệu đây là prototype có explainability và fallback; nêu rõ giới hạn đánh giá.

### 3.2 Gate đã từng pass

- Backend Gradle: `BUILD SUCCESSFUL`; 12 nhóm test XML.
- Frontend: `npm ci` thành công, audit 0 vulnerability, TypeScript lint pass, 10 Jest suites/41 tests pass, Vite production build pass.
- Python/OpenAPI/dataset:
  - OpenAPI check pass.
  - Classification validator pass với 350 mẫu.
  - Matching validator pass với 70 cặp.
  - Schema-only LLM pass 20 cases/40 sanitizer checks.
  - Full pytest pass: 128 tests.
  - Repository scanner và Git-history scan pass.
- Regression classifier đã kiểm tra lỗi ML inference trả deterministic fallback với `used_model=False` và không log raw CV text.

### 3.3 Docker đã chạy được từng phần nhưng chưa đủ gate cuối

Một lần chạy stack tạm trước đây đã xác minh thành công:

- health của AI/backend/frontend;
- USER và ADMIN login;
- resume analysis có `topTerms`;
- JD matching có `matchBreakdown.method=HYBRID_EMBEDDING`;
- history/detail, JWT và admin endpoints;
- truy vấn privacy và kiểm tra log khi chạy riêng với đúng Compose context.

Tuy nhiên chưa có **một lần gọi duy nhất** của `scripts/smoke_stack.py` chạy với project/Compose files tạm và exit code `0`. Nguyên nhân đã biết: các subprocess kiểm tra database/log trong script vẫn gọi `docker compose` mặc định nên không tìm thấy stack có project name/override.

Offline Ollama fallback mới có regression/unit evidence; chưa có full-stack live smoke cuối được lưu nhận.

Lần truy cập Docker gần nhất từ môi trường Codex bị `Access is denied` với `C:\Users\huuqu\.docker\config.json` và `permission denied ... docker_engine`. Owner đã bật Docker Desktop; Antigravity phải kiểm tra lại trong chính môi trường của mình và không được suy luận daemon hỏng chỉ từ lỗi sandbox cũ.

## 4. Vấn đề còn mở phải xử lý

1. `scripts/smoke_stack.py` chưa truyền Compose project/files vào các lệnh privacy và logs.
2. Timeout 240 giây đang hard-code cho hai request AI; nên đưa thành CLI option có default hợp lý để local/CI dùng cùng script.
3. Smoke chưa có chế độ kỳ vọng Ollama online và kỳ vọng Ollama offline rõ ràng.
4. `docker-compose.yml` còn `container_name` cố định, gây conflict với stack khác và làm project isolation không đáng tin cậy.
5. Port AI/backend/frontend còn hard-code; cần có biến môi trường giống `DB_PORT` hoặc cơ chế override tái lập.
6. `ai-service/Dockerfile` chạy `COPY . .` trước khi tải MiniLM, khiến mọi thay đổi source làm mất cache model download. Cần tách layer để source change không buộc tải lại model.
7. Image từng chạy có thể được build trước bản sửa Qwen `think=false`; phải rebuild từ source/HEAD hiện tại.
8. Chưa có full-stack smoke online và offline đều exit `0` từ source hiện tại.
9. `docs/project/AI_UPGRADE_PROGRESS.md` vẫn để Batch 3 và Batch 6 là `IN_PROGRESS`.
10. `README.md` và `evaluation/reports/matching-model-notes.md` vẫn nói matching `PENDING HUMAN REVIEW`, trái với evidence hiện có.
11. Chưa có bằng chứng GitHub Actions chính thức cho các thay đổi mới nhất. CI chỉ tự chạy khi push/PR vào các nhánh được cấu hình hoặc khi workflow được dispatch.

## 5. Quy tắc bắt buộc

- Trước khi sửa, chạy `git status --short --branch`, `git log -5 --oneline --decorate` và đọc diff. Không reset, checkout đè, clean, xóa hoặc sửa thay đổi chưa hiểu.
- Không sửa, tạo lại hoặc suy diễn điểm human review. Không dùng Qwen/Gemini/agent làm reviewer.
- Không xóa evidence review, manifest hoặc report hợp lệ.
- Không log hoặc commit raw CV/JD, secret, token, tên/email reviewer hay PII thật. Chỉ dùng fixture synthetic và domain `example.test`.
- Không hạ assertion, skip/xóa test hoặc đổi threshold chỉ để làm CI xanh.
- Khi test fail, tìm root cause, thêm regression test có giá trị nếu behavior thay đổi, rồi chạy focused test trước full gate.
- Không chạm stack ngoài repository. Chỉ dừng/xóa container, network và volume thuộc project Compose tạm do phiên này tạo.
- Không dùng `docker system prune`, không xóa image/volume toàn cục.
- Không sửa metric report bằng tay. Chỉ tái tạo bằng evaluator tương ứng.
- Không tuyên bố classifier đạt 100% ngoài synthetic benchmark.
- Không push, merge, rebase, force-push hoặc deploy public nếu owner chưa yêu cầu rõ. Sau khi hoàn tất có thể tạo commit cục bộ.
- Không dừng sau mỗi đợt chỉ để xin xác nhận. Báo cáo checkpoint ngắn rồi tự chuyển sang đợt tiếp theo. Chỉ dừng khi thật sự cần owner thao tác bên ngoài hoặc cấp quyền.

## 6. Việc có thể cần owner can thiệp

Đây là mục đầu tiên agent phải báo cho owner trước khi chạy dài:

| Tình huống | Agent phải tự kiểm tra trước | Owner chỉ cần làm khi |
|---|---|---|
| Docker Desktop | Chạy `docker version` và `docker compose version` | Daemon không truy cập được từ terminal của Antigravity; owner cần mở Docker Desktop hoặc cấp quyền cho terminal |
| Ollama online smoke | Chạy `ollama list` và kiểm tra `http://localhost:11434/api/tags` | Ứng dụng Ollama chưa chạy hoặc model `qwen3:0.6b` chưa có; owner chỉ cần mở Ollama nếu agent không thể tự khởi động |
| Tải dependency/model | Dùng cache hiện có, thử command chuẩn và lưu log | Môi trường chặn mạng hoặc yêu cầu xác nhận download |
| GitHub Actions | Hoàn tất toàn bộ local gate trước | Cần push/PR/workflow dispatch để lấy official CI evidence; phải xin owner trước khi push |
| Browser demo | Dùng browser tool nếu có | Agent không có browser automation; owner thực hiện checklist click cuối do agent cung cấp |

Human review không còn là phần owner phải làm. Nếu không rơi vào các tình huống trên, agent tự tiếp tục.

## 7. Trình tự triển khai bắt buộc

### Đợt 0 — Chụp trạng thái và preflight

Mục tiêu: xác nhận đúng repository, toolchain và blocker môi trường trước khi thay source.

Thực hiện:

```powershell
Set-Location D:\C\AI_RESUME_ANALYZER
git status --short --branch
git log -5 --oneline --decorate
python --version
java -version
node --version
npm.cmd --version
docker version
docker compose version
docker compose config --quiet
```

Nếu có nhiều Python, ưu tiên Python 3.11 (`py -3.11`). Backend dùng JDK 21, frontend dùng Node 22.

Acceptance:

- Đúng branch/repository và không làm mất thay đổi hiện có.
- Ghi rõ version toolchain.
- Docker daemon truy cập được hoặc đã báo đúng thao tác owner cần làm.
- Nêu rõ Ollama/model hiện online hay offline.

### Đợt 1 — Làm Compose isolation và smoke script tái lập

Mục tiêu: cùng một smoke command phải biết chính xác stack nào cần kiểm tra.

Thực hiện theo hướng sau, điều chỉnh tên option theo convention hiện có:

1. Trong `scripts/smoke_stack.py`, thêm CLI options:
   - `--compose-project-name`;
   - `--compose-file`, có thể lặp lại;
   - `--analysis-timeout-seconds`, default `240`;
   - chế độ Ollama rõ ràng, ví dụ `--ollama-mode auto|required|unavailable`.
2. Tạo một helper duy nhất xây prefix lệnh Compose:
   - mặc định vẫn là `docker compose` để CI hiện tại không vỡ;
   - nếu có project name, thêm `-p <name>`;
   - nếu có file, thêm `-f <file>` theo đúng thứ tự.
3. Dùng helper này cho cả MySQL privacy query và Compose log checks.
4. Không nối command bằng shell string; truyền list argument vào `subprocess.run`.
5. Dùng option timeout thay cho số `240` hard-code.
6. Thêm focused tests cho việc xây Compose command và parse option. Test phải chứng minh default CI vẫn giữ behavior cũ và isolated project dùng đúng context.
7. Gỡ `container_name` cố định khỏi `docker-compose.yml` để Compose project name cô lập container/network/volume thật sự.
8. Parameterize host ports, ví dụ `DB_PORT`, `AI_PORT`, `BACKEND_PORT`, `FRONTEND_PORT`, trong khi giữ nguyên internal service ports.

Kỳ vọng chế độ Ollama:

- `required`: health phải có `ollamaReachable=true`; kết quả enrichment không được báo fallback.
- `unavailable`: health phải có `ollamaReachable=false`; resume và match vẫn thành công, `ai.usedFallback=true`, `ai.provider=RULE_BASED`.
- `matchBreakdown.method` vẫn là `HYBRID_EMBEDDING` khi MiniLM hoạt động, vì Ollama fallback và embedding matcher là hai cơ chế khác nhau.

Verification:

```powershell
python -m pytest ai-service/tests/test_stack_smoke.py -q
python scripts/smoke_stack.py --help
docker compose config --quiet
git diff --check
```

Acceptance:

- Focused tests pass.
- Default invocation vẫn tương thích CI.
- Privacy/log subprocess dùng cùng project/files với API stack.
- Hai request AI dùng timeout CLI, không hard-code rải rác.
- Hai Compose project có thể tồn tại mà không conflict tên container.

### Đợt 2 — Tối ưu Docker build cache và rebuild đúng source

Mục tiêu: image chứa source hiện tại, model embedding có sẵn trong image và runtime không cần Internet.

Điều chỉnh `ai-service/Dockerfile` theo thứ tự layer:

1. Copy và cài `requirements.txt`.
2. Tải revision MiniLM đã pin vào `/opt/models/all-MiniLM-L6-v2` ở build-time.
3. Copy source ứng dụng sau layer model để source change không làm tải lại model.
4. Sau khi copy source, verify classifier artifact bằng `joblib.load`.
5. Verify MiniLM bằng `local_files_only=True`.

Không bỏ revision pin và không cho phép runtime fallback sang download Internet.

Dùng project/port riêng. Ví dụ:

```powershell
$env:COMPOSE_PROJECT_NAME = 'ai-resume-demo-gate'
$env:DB_PORT = '13306'
$env:AI_PORT = '18000'
$env:BACKEND_PORT = '18080'
$env:FRONTEND_PORT = '15173'
docker compose build --pull
docker compose up --detach
docker compose ps
```

Poll health theo service, không coi timeout của terminal là lỗi nếu process build vẫn đang chạy. Không chạy trùng nhiều build gây tranh CPU/RAM. Nếu download model chậm, giữ log và tiếp tục wait/poll có cập nhật tiến độ; không đổi source để che lỗi mạng.

Acceptance:

- Image được rebuild từ HEAD hiện tại.
- Classifier và embedding model load từ local image.
- Sửa source AI lần sau không tự invalidated layer tải MiniLM.
- MySQL, AI, backend healthy; frontend trả HTTP dưới 500.
- Log startup không có runtime request tới Hugging Face hoặc thông báo tải embedding model.

### Đợt 3 — Full-stack smoke với Ollama online

Mục tiêu: xác minh đủ năm luồng demo khi Qwen sẵn sàng.

Trước khi chạy, kiểm tra:

```powershell
ollama list
Invoke-RestMethod http://localhost:11434/api/tags
```

Nếu model chưa có và mạng cho phép:

```powershell
ollama pull qwen3:0.6b
```

Chạy một command smoke duy nhất, truyền đúng project context và các URL port tạm. Ví dụ:

```powershell
python scripts/smoke_stack.py `
  --ai-url http://localhost:18000 `
  --backend-url http://localhost:18080 `
  --frontend-url http://localhost:15173 `
  --compose-project-name ai-resume-demo-gate `
  --check-mysql-privacy `
  --check-logs `
  --ollama-mode required `
  --analysis-timeout-seconds 240
```

Acceptance của chính command này:

- Exit code `0`.
- AI classifier và embedding health đầy đủ.
- USER/ADMIN login thành công.
- Anonymous bị `401`; USER vào admin bị `403`; ADMIN gọi users/analyses/metrics được `200`.
- Upload PDF resume thành công và classifier evidence có `topTerms`.
- JD matching thành công với `matchBreakdown.method=HYBRID_EMBEDDING`.
- History có ít nhất hai record và detail đọc được.
- Ollama online, enrichment không dùng fallback.
- JSON trong database không chứa các key raw `resumeText`, `jobDescription`, `text`.
- Sentinel JD không xuất hiện trong log.
- AI log không chứa runtime model download.

Nếu command fail sau khi các flow trước đã pass, vẫn coi toàn smoke là fail. Sửa root cause và chạy lại từ đầu đến exit `0`; không ghép các lần chạy rời thành một pass.

### Đợt 4 — Full-stack smoke với Ollama offline

Mục tiêu: chứng minh core demo không phụ thuộc Ollama.

Teardown đúng project online rồi khởi động project tạm mới hoặc recreate AI service với URL Ollama chắc chắn không truy cập được và timeout ngắn. Ví dụ dùng biến môi trường/override tạm:

```powershell
$env:COMPOSE_PROJECT_NAME = 'ai-resume-fallback-gate'
$env:OLLAMA_BASE_URL = 'http://host.docker.internal:1'
$env:AI_TIMEOUT_SECONDS = '2'
$env:DB_PORT = '23306'
$env:AI_PORT = '28000'
$env:BACKEND_PORT = '28080'
$env:FRONTEND_PORT = '25173'
docker compose up --detach
```

Chạy smoke với `--ollama-mode unavailable`, đúng project name và đúng URL.

Acceptance:

- Command exit `0`.
- Health ghi Ollama không reachable.
- Resume analysis và JD matching vẫn hoàn tất.
- Cả hai response có `ai.usedFallback=true` và `ai.provider=RULE_BASED`.
- Matching vẫn dùng local MiniLM và `HYBRID_EMBEDDING`.
- Auth/history/admin/privacy/log gates vẫn pass.
- Không có raw CV/JD trong database hoặc log.

Sau mỗi lượt, luôn teardown đúng project:

```powershell
docker compose -p ai-resume-demo-gate down --volumes
docker compose -p ai-resume-fallback-gate down --volumes
```

Chỉ dùng lệnh trên với project do phiên này tạo. Xóa file override tạm nếu nó không phải artifact có chủ đích.

### Đợt 5 — Chạy toàn bộ CI-equivalent gates

Mục tiêu: tái lập tất cả bốn job trong `.github/workflows/ci.yml` trên source cuối.

Python 3.11:

```powershell
py -3.11 scripts/export_openapi.py --check
py -3.11 evaluation/scripts/validate_classification_dataset.py
py -3.11 evaluation/scripts/validate_matching_dataset.py
py -3.11 evaluation/scripts/evaluate_llm.py --mode schema-only
py -3.11 evaluation/scripts/evaluate_classifier.py --output $env:TEMP\classification-report.md
py -3.11 evaluation/scripts/evaluate_matching.py --output $env:TEMP\matching-report.md --allow-pending
py -3.11 scripts/scan_repository.py --check-history
py -3.11 -m pytest
```

Nếu `py` không có nhưng `python --version` đúng 3.11, dùng `python` nhất quán.

Backend JDK 21:

```powershell
$env:GRADLE_USER_HOME = "$env:USERPROFILE\.gradle"
Push-Location backend
.\gradlew.bat test --no-daemon
Pop-Location
```

Frontend Node 22:

```powershell
Push-Location frontend
npm.cmd ci
npm.cmd run lint
npm.cmd test -- --runInBand
npm.cmd run build
Pop-Location
```

Repository checks:

```powershell
docker compose config --quiet
git diff --check
git status --short
```

Acceptance:

- Mọi command có exit code `0`.
- Regression classifier fallback/no-log-leak nằm trong suite và pass.
- Không dùng test count cũ làm bằng chứng; báo số liệu từ lần chạy hiện tại.
- Không commit `node_modules`, `.gradle`, cache, coverage, Vite output hoặc report trong `%TEMP%`.

Nếu local dependency download bị chặn, thử lại đúng command với quyền/mạng phù hợp và lưu nguyên lỗi. Chỉ dùng GitHub Actions làm bằng chứng thay thế sau khi local unit gates pass và owner cho phép push.

### Đợt 6 — Cập nhật tài liệu, trạng thái batch và demo checklist

Mục tiêu: tài liệu phản ánh đúng source và evidence cuối.

Cập nhật ít nhất:

- `docs/project/AI_UPGRADE_PROGRESS.md`
- `README.md`
- `evaluation/reports/matching-model-notes.md`
- `walkthrough.md` nếu có nội dung trạng thái hoặc lệnh demo cũ

Quy tắc cập nhật:

- Batch 3 chỉ chuyển `COMPLETED` sau khi Python suite, evaluator và regression hiện tại pass.
- Batch 6 chỉ chuyển `COMPLETED` sau khi online/offline Docker smoke và toàn bộ CI-equivalent gates pass.
- Xóa tuyên bố matching đang `PENDING HUMAN REVIEW`; thay bằng link/report metric đã review và cảnh báo synthetic limitation.
- Batch 4 và Batch 5 giữ `COMPLETED` vì evidence đã đủ, trừ khi validator phát hiện dữ liệu thật sự invalid.
- Batch 7/8 có thể ghi là phạm vi demo documentation/release audit đã được xử lý đến đâu; không tuyên bố academic report hoặc production release nếu chưa có deliverable tương ứng.
- README phải có một đường chạy demo sạch, port, tài khoản demo, yêu cầu Docker/Ollama và cách fallback.
- Không ghi fixed demo secret là phù hợp cho public deployment. Ghi rõ credentials/default secret chỉ dành cho local demo.

Thực hiện browser rehearsal bằng công cụ browser nếu có:

1. Mở frontend.
2. Login USER.
3. Upload một PDF synthetic và xem kết quả/top terms.
4. Chạy JD matching và xem breakdown.
5. Mở history và detail.
6. Xác nhận USER không vào admin.
7. Login ADMIN và mở users/analyses/metrics.
8. Kiểm tra console không có uncaught error và network không có request 5xx.

Nếu không có browser automation, tạo checklist ngắn với URL/credential/file fixture cụ thể để owner tự click một lần. Đây là visual rehearsal, không thay thế API smoke.

Acceptance:

- Tài liệu không còn trạng thái mâu thuẫn.
- Demo flow có thể thực hiện trong khoảng 10–12 phút bằng fixture synthetic.
- Các giới hạn metric được trình bày trung thực.
- Scanner và Markdown link checks vẫn pass sau khi sửa docs.

### Đợt 7 — Final audit, commit cục bộ và báo cáo bàn giao

Chạy lần cuối:

```powershell
git diff --check
py -3.11 scripts/scan_repository.py --check-history
git status --short
git diff --stat
git diff
```

Review toàn bộ diff theo các trục correctness, security/privacy, test coverage, compatibility và documentation. Bảo đảm không có secret, raw PII, artifact tạm hoặc thay đổi scope không cần thiết.

Nếu mọi gate pass, tạo commit cục bộ có nội dung rõ. Ưu tiên tách:

1. `fix: make isolated Docker smoke reproducible`
2. `docs: finalize demo readiness evidence`

Không amend/squash commit cũ nếu owner chưa yêu cầu. Không push sau commit.

## 8. Definition of Done cho demo

Chỉ được báo **DEMO READY** khi đồng thời đạt tất cả điều kiện:

- [ ] Fresh Compose build/up từ source hiện tại thành công bằng project riêng.
- [ ] Online Ollama full-stack smoke là một command exit `0`.
- [ ] Offline Ollama fallback full-stack smoke là một command exit `0`.
- [ ] Login, resume, matching, history/detail và admin đều pass.
- [ ] JWT role checks pass.
- [ ] Classifier/embedding health đầy đủ; runtime không download embedding model.
- [ ] Database/log privacy assertions pass.
- [ ] OpenAPI, validators, schema-only evaluation, scanner/history và toàn bộ pytest pass.
- [ ] Backend JDK 21 tests pass.
- [ ] Frontend Node 22 install/lint/test/build pass.
- [ ] Browser rehearsal pass hoặc owner nhận được checklist visual cụ thể.
- [ ] Docs không còn `PENDING HUMAN REVIEW` sai và Batch 3/6 có trạng thái đúng bằng chứng.
- [ ] Worktree chỉ còn các thay đổi có chủ đích; sau commit phải sạch.
- [ ] Có commit SHA cục bộ cuối và không push trái phép.

Nếu còn bất kỳ ô nào chưa đạt, dùng trạng thái **NOT DEMO READY** hoặc **DEMO READY WITH BLOCKER**, nêu chính xác blocker. Không ghép evidence từ source/image khác nhau để tuyên bố pass.

## 9. Mẫu báo cáo sau mỗi đợt

Sau mỗi đợt, báo ngắn theo mẫu rồi tự chuyển tiếp:

```text
ĐỢT N — <tên>
Trạng thái: PASS | FAIL | BLOCKED
Đã thay đổi: <file và behavior>
Đã chạy: <command chính>
Bằng chứng: <exit code, test count, health/smoke result>
Blocker/rủi ro: <nếu có>
Tiếp theo: Đợt N+1 — <mục tiêu>
```

Không nói “đang chạy nền” nếu không có process/session thật đang chạy. Với build lâu, poll process và cập nhật tiến độ định kỳ; khi process kết thúc phải báo exit code.

## 10. Mẫu báo cáo cuối

```markdown
# Báo cáo chốt demo AI_RESUME_ANALYZER

## Kết luận
- Trạng thái: DEMO READY | NOT DEMO READY
- Branch:
- Commit SHA cuối:
- Worktree sạch: có/không

## Gate kỹ thuật
| Gate | Command | Kết quả | Evidence |
|---|---|---|---|
| Python/OpenAPI/dataset | ... | PASS/FAIL | ... |
| Backend JDK 21 | ... | PASS/FAIL | ... |
| Frontend Node 22 | ... | PASS/FAIL | ... |
| Docker online | ... | PASS/FAIL | ... |
| Docker offline fallback | ... | PASS/FAIL | ... |
| Privacy/logs | ... | PASS/FAIL | ... |
| Browser rehearsal | ... | PASS/FAIL | ... |

## Trạng thái Batch 0–8
<mỗi batch một dòng, chỉ ghi completed khi có evidence>

## Evaluation
- Matching: ghi exact metric và synthetic limitation.
- Qwen: ghi exact metric và synthetic limitation.
- Classifier: ghi current synthetic metric, không suy rộng thực tế.

## Thay đổi chính
<file, behavior, lý do>

## Việc owner cần làm
<chỉ những thao tác ngoài môi trường agent, nếu thật sự còn>

## Lệnh demo nhanh
<fresh-start command, URL, accounts, fixture, teardown>
```

## 11. Câu lệnh giao việc cho Antigravity

Sau khi mở repository, owner có thể gửi đúng câu sau:

> Đọc toàn bộ `prompt.md` và coi đây là tài liệu chuẩn chính. Trước tiên báo ngắn phần nào thật sự cần tôi can thiệp theo Mục 6. Sau đó tự thực hiện lần lượt Đợt 0 đến Đợt 7, sửa lỗi đến khi đạt Definition of Done. Không bỏ qua gate, không sửa human-review evidence, không push/merge/deploy public nếu chưa được tôi cho phép. Sau mỗi đợt báo checkpoint ngắn rồi tiếp tục; cuối cùng gửi báo cáo theo Mục 10.
