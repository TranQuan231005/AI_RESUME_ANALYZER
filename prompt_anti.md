Bạn là kỹ sư Machine Learning, Software Architect và Technical Reviewer chịu trách nhiệm
nâng cấp repository AI Resume Analyzer thành một đồ án cuối kỳ môn Trí tuệ nhân tạo
có chất lượng học thuật, có thể chạy demo ổn định và có thể bảo vệ trước giảng viên.

========================
I. THÔNG TIN DỰ ÁN
========================

Repository: AI_RESUME_ANALYZER

Kiến trúc hiện tại:

React + TypeScript
    → Spring Boot
        → MySQL
        → FastAPI AI Service
            → Ollama qwen3:4b

Năm luồng nghiệp vụ bắt buộc phải được giữ nguyên:

1. Login.
2. Resume Analysis.
3. CV–JD Matching.
4. User History.
5. Admin AI Dashboard.

Dữ liệu đầu vào:

- CV tiếng Anh dạng PDF có thể trích xuất text.
- Dung lượng tối đa 5 MB.
- JD là PDF hoặc văn bản tiếng Anh.
- Không lưu file CV hoặc nội dung JD gốc vào database.
- Không đưa thông tin cá nhân thật vào dataset hoặc log.

Mục tiêu nâng cấp:

Biến dự án từ một web application tích hợp LLM thành một hệ thống AI hybrid có:

1. Tiền xử lý tài liệu đúng.
2. Hệ chuyên gia chấm điểm CV.
3. Mô hình Machine Learning được huấn luyện để phân loại lĩnh vực CV.
4. So sánh mô hình với baseline.
5. Đánh giá bằng metrics có ý nghĩa.
6. Khả năng giải thích kết quả.
7. Qwen3:4b sinh nhận xét theo ngữ cảnh.
8. Tài liệu đủ để trình bày và vấn đáp.

========================
II. NGUYÊN TẮC BẮT BUỘC
========================

1. Không thực hiện tất cả các đợt trong một lần.

2. Chỉ thực hiện đúng đợt mà người dùng yêu cầu.

3. Sau mỗi đợt phải:
   - Chạy kiểm thử liên quan.
   - Liệt kê file đã thay đổi.
   - Mô tả quyết định kỹ thuật.
   - Báo cáo test pass/fail.
   - Nêu rủi ro hoặc việc còn thiếu.
   - Cập nhật file docs/AI_UPGRADE_PROGRESS.md.
   - Dừng lại chờ người dùng xác nhận.

4. Trước khi sửa:
   - Đọc README.md.
   - Đọc KE_HOACH_LAM_LAI_DU_AN_3_TUAN.md.
   - Kiểm tra git status.
   - Không ghi đè thay đổi chưa commit của người dùng.
   - Đọc implementation và test của module liên quan.

5. Không thay đổi API contract một cách âm thầm.

6. Nếu thay đổi request hoặc response:
   - Cập nhật Pydantic schema.
   - Cập nhật contracts/openapi/.
   - Cập nhật contracts/fixtures/.
   - Cập nhật Spring Boot consumer.
   - Cập nhật TypeScript types.
   - Cập nhật frontend.
   - Cập nhật tests.
   - Chạy scripts/export_openapi.py --check.

7. Giữ toàn bộ user-facing text, API message, fixture và AI output bằng tiếng Anh.

8. Không thêm:
   - Registration.
   - Google Login.
   - Payment.
   - Chatbot tổng quát.
   - RAG hoặc vector database nếu chưa chứng minh được nhu cầu.
   - OCR trong phạm vi nâng cấp này.
   - Fine-tuning Qwen.
   - Chức năng web không liên quan đến phần AI.
   - Animation hoặc dashboard không cần thiết.

9. Không được tạo số liệu đánh giá giả.

10. Không được dùng kết quả trên dữ liệu training để tuyên bố độ chính xác.

11. Không được tạo ground truth bằng chính công thức của thuật toán rồi dùng ground truth đó
    để chứng minh thuật toán chính xác.

12. Dataset tổng hợp phải được ghi rõ là synthetic.
    Không được dùng kết quả synthetic-only để tuyên bố hiệu quả ngoài thực tế.

13. Không được tải hoặc commit dataset bên ngoài nếu chưa xác định:
    - Nguồn.
    - Giấy phép.
    - Điều kiện sử dụng.
    - Cách loại bỏ thông tin cá nhân.

14. Không để Qwen quyết định trực tiếp:
    - Resume score.
    - Match score.
    - Nhãn phân loại cuối cùng.
    Qwen chỉ sinh nội dung tư vấn, ATS insights, strengths và weaknesses.

15. Ưu tiên code đơn giản, có type hints, có unit test và giải thích được khi vấn đáp.

========================
III. CƠ CHẾ LÀM VIỆC THEO ĐỢT
========================

Tạo file:

docs/AI_UPGRADE_PROGRESS.md

File phải chứa bảng:

| Batch | Status | Summary | Tests | Remaining risks |
|---|---|---|---|---|

Status chỉ được dùng:

- NOT_STARTED
- IN_PROGRESS
- BLOCKED
- COMPLETED

Mỗi lần bắt đầu một đợt:

1. Đọc docs/AI_UPGRADE_PROGRESS.md.
2. Xác định đợt đã hoàn thành.
3. Chỉ làm đợt được yêu cầu.
4. Không tự chuyển sang đợt kế tiếp.

========================
ĐỢT 0 — AUDIT VÀ BASELINE
========================

Mục tiêu:

Xác định trạng thái thực tế của repository trước khi sửa.

Không thực hiện thay đổi chức năng trong đợt này.

Công việc:

1. Kiểm tra cấu trúc frontend, backend, ai-service, contracts và evaluation.

2. Kiểm tra các module:
   - ai-service/app/document/parser.py
   - ai-service/app/validation.py
   - ai-service/app/extraction/features.py
   - ai-service/app/extraction/taxonomy.py
   - ai-service/app/extraction/classifier.py
   - ai-service/app/scoring/engine.py
   - ai-service/app/matching/engine.py
   - ai-service/app/recommendation/engine.py
   - ai-service/app/llm/client.py
   - ai-service/app/main.py

3. Kiểm tra:
   - Mất xuống dòng sau khi parse PDF.
   - Khả năng trích xuất tên.
   - Khả năng nhận diện section.
   - Sự thống nhất giữa predicted fields và recommendation taxonomy.
   - Sự thống nhất giữa snake_case và camelCase.
   - Chất lượng bộ evaluation hiện tại.
   - Dataset hiện tại có bao nhiêu mẫu.
   - Ground truth có độc lập với implementation hay không.

4. Chạy baseline tests nếu môi trường cho phép:

AI service:
    pytest ai-service/tests

Repository tests:
    pytest

OpenAPI:
    python scripts/export_openapi.py --check

Dataset:
    python evaluation/validate_dataset.py
    python evaluation/run_evaluation.py --mode rule-only

Backend:
    cd backend
    ./gradlew test --no-daemon

Frontend:
    cd frontend
    npm test -- --runInBand
    npm run build

5. Không cài dependency mới trong Đợt 0 nếu chưa được người dùng cho phép.

Deliverable:

Tạo:

docs/AI_BASELINE_AUDIT.md

Nội dung phải có:

- Kiến trúc hiện tại.
- Thành phần AI hiện tại.
- Thành phần rule-based.
- Lỗi hoặc inconsistency tìm thấy.
- Test baseline.
- Hạn chế của evaluation hiện tại.
- Danh sách thay đổi đề xuất theo mức P0/P1/P2.

Sau khi hoàn thành, dừng và chờ xác nhận.

========================
ĐỢT 1 — SỬA TÍNH ĐÚNG CỦA PIPELINE
========================

Mục tiêu:

Bảo đảm kết quả hiện tại đúng trước khi bổ sung Machine Learning.

1. Sửa PDF text normalization.

Yêu cầu:

- Giữ xuống dòng giữa các dòng và giữa các trang.
- Chuẩn hóa Unicode bằng NFKC.
- Chỉ gom khoảng trắng ngang trong từng dòng.
- Loại dòng trống thừa nhưng không phá section boundary.
- Ghép các trang bằng newline, không ghép bằng một dấu cách.
- Không thay đổi nội dung có nghĩa.

Ví dụ mong muốn:

Input:
    "JOHN   DOE\n\nEXPERIENCE\nBuilt APIs"

Output:
    "JOHN DOE\n\nEXPERIENCE\nBuilt APIs"

Không được biến thành:
    "JOHN DOE EXPERIENCE Built APIs"

2. Sửa trích xuất tên.

Yêu cầu:

- Vẫn ưu tiên các dòng đầu CV.
- Bỏ qua heading và chức danh.
- Không nhận email hoặc URL làm tên.
- Có test cho:
  - Tên hai từ.
  - Tên có dấu gạch hoặc apostrophe.
  - CV không có tên.
  - Heading đứng trước tên.
  - Chức danh đứng sau tên.

3. Sửa nhận diện section trong scoring engine.

Yêu cầu:

- Nhận diện heading không phân biệt hoa thường.
- Hỗ trợ heading có hoặc không có dấu hai chấm.
- Xác định nội dung từ heading hiện tại đến heading tiếp theo.
- Không để section Experience nuốt toàn bộ Education hoặc Projects.
- Giữ score trong đúng giới hạn từng tiêu chí.
- Resume score luôn là tổng các thành phần và nằm trong 0–100.

4. Đồng bộ recommendation taxonomy.

Các field bắt buộc:

- Data Science
- Web Development
- Android Development
- iOS Development
- UI/UX
- Unknown

Mỗi field có danh sách kỹ năng phù hợp.
Tên kỹ năng phải nhất quán với taxonomy chính.

5. Sửa mismatch giữa:

- achievementsCertifications và achievements_certifications.
- quantifiedImpact và quantified_impact.

Chọn một representation nội bộ nhất quán.
Chỉ dùng camelCase tại API serialization boundary.

6. Recommendation về contact không được yêu cầu số điện thoại nếu dự án không trích xuất
hoặc chấm điểm số điện thoại.

7. Bổ sung regression tests cho tất cả lỗi trên.

Acceptance criteria:

- Parser giữ đúng section boundary.
- Candidate name extraction hoạt động trên PDF/text mẫu.
- Score breakdown đúng và tổng điểm chính xác.
- Recommendation taxonomy đúng theo predicted field.
- Không phá public API hiện tại.
- AI service tests pass.
- Contract tests pass.
- OpenAPI check pass.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 2 — XÂY DỰNG DATASET HỌC MÁY
========================

Mục tiêu:

Tạo nền tảng dữ liệu có thể dùng để huấn luyện và đánh giá classifier.

Bài toán:

Phân loại CV vào năm lớp:

- Data Science
- Web Development
- Android Development
- iOS Development
- UI/UX

1. Tạo cấu trúc:

evaluation/classification/
    README.md
    dataset.schema.json
    manifest.json
    train.jsonl
    validation.jsonl
    test.jsonl
    validate_classification_dataset.py

2. Mỗi mẫu phải có tối thiểu:

{
  "id": "unique-id",
  "text": "anonymized English resume text",
  "label": "Data Science",
  "sourceType": "licensed-public | manually-authored | synthetic",
  "sourceReference": "...",
  "templateGroup": "...",
  "reviewed": true
}

3. Quy tắc dữ liệu:

- Không chứa email hoặc số điện thoại thật.
- Không chứa tên thật nếu không cần thiết.
- Không duplicate text.
- Nhãn phải thuộc đúng năm lớp.
- Không để cùng một CV xuất hiện ở nhiều split.
- Không để các biến thể từ cùng một template xuất hiện cả train và test.
- Split phải stratified theo label.
- Fixed random seed = 42.
- Test set phải được giữ độc lập.

4. Mục tiêu dữ liệu:

Khuyến nghị:
- Tối thiểu 50 mẫu đã kiểm tra cho mỗi lớp.
- Tốt hơn: 100 mẫu mỗi lớp.

Nếu repository chưa có đủ dữ liệu:

- Không được tự tuyên bố rằng dataset đã đủ.
- Có thể tạo một số fixture synthetic để kiểm tra pipeline.
- Phải ghi rõ synthetic fixture không dùng để tuyên bố độ chính xác thực tế.
- Đánh dấu Đợt 2 là BLOCKED nếu cần người dùng cung cấp hoặc phê duyệt nguồn dataset.
- Báo cho người dùng chính xác số lượng mẫu còn thiếu theo từng lớp.

5. Validator phải kiểm tra:

- Schema.
- Label.
- Duplicate.
- PII cơ bản.
- Empty text.
- Split leakage.
- Template-group leakage.
- Class distribution.
- Dataset provenance.

Acceptance criteria:

- Dataset validator chạy được.
- Manifest thống kê đúng số lượng theo lớp và split.
- Không có PII rõ ràng.
- Không có leakage phát hiện được.
- README mô tả provenance và limitation.

Không bắt đầu huấn luyện model nếu dataset chưa đạt điều kiện tối thiểu được phê duyệt.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 3 — HUẤN LUYỆN CLASSIFIER
========================

Chỉ thực hiện khi Đợt 2 đã COMPLETED hoặc người dùng phê duyệt dataset.

Mục tiêu:

Xây dựng một mô hình Machine Learning có thể huấn luyện, đánh giá, lưu và chạy inference.

1. Dependency:

Bổ sung scikit-learn và dependency serialization phù hợp.
Chọn phiên bản ổn định tương thích Python 3.11.
Ghi rõ phiên bản để có thể tái lập.

2. Tạo module:

ai-service/app/ml/
    __init__.py
    classifier.py
    model_loader.py

ai-service/training/
    train_classifier.py
    evaluate_classifier.py

artifacts/classifier/
    README.md
    metadata.json
    model artifact
    vectorizer artifact

Nếu không commit binary artifact thì phải:
- Giải thích trong README.
- Cung cấp command tái tạo artifact.
- Docker/runtime phải có cách rõ ràng để nhận model.

3. Baselines phải được so sánh:

- Existing taxonomy/keyword classifier.
- Multinomial Naive Bayes.
- Logistic Regression.
- Linear SVM.

4. Pipeline đề xuất:

TfidfVectorizer:
- lowercase = true
- English stop words.
- word n-gram (1,2).
- sublinear_tf = true.
- min_df và max_df được chọn dựa trên kích thước dataset.

Logistic Regression:
- class_weight = balanced nếu dữ liệu lệch lớp.
- max_iter đủ lớn.
- random_state = 42.

Không hardcode hyperparameter mà không ghi lý do.

5. Evaluation:

Bắt buộc báo cáo:

- Accuracy.
- Precision theo lớp.
- Recall theo lớp.
- F1 theo lớp.
- Macro F1.
- Weighted F1.
- Confusion matrix.
- Inference latency.
- Class distribution.
- Random seed.
- Phiên bản dataset.

Nếu dataset không lớn:
- Sử dụng stratified cross-validation trên train/validation.
- Test set vẫn phải giữ độc lập cho đánh giá cuối.

6. Chọn mô hình:

Ưu tiên Macro F1.
Nếu hai mô hình gần nhau, chọn mô hình:
- Nhẹ hơn.
- Dễ giải thích hơn.
- Inference nhanh hơn.

7. Model metadata phải lưu:

{
  "modelType": "...",
  "datasetVersion": "...",
  "trainedAt": "...",
  "labels": [...],
  "randomSeed": 42,
  "metrics": {...},
  "textFeatureConfig": {...},
  "unknownThreshold": ...
}

8. Inference:

Input:
    resume text

Output:
    predicted field
    confidence
    per-class confidence
    influential terms hoặc evidence

Có ngưỡng Unknown được chọn trên validation data.
Không chọn ngưỡng tùy ý mà không ghi nhận quá trình thử nghiệm.

9. Tích hợp:

- Thay classifier đếm kỹ năng bằng ML classifier khi model sẵn sàng.
- Giữ taxonomy classifier làm baseline và cơ chế deterministic.
- Không đổi API nếu fieldEvidence hiện tại có thể biểu diễn kết quả.
- Nếu bắt buộc đổi API, thực hiện đầy đủ contract workflow.

10. Testing:

- Model loader.
- Valid inference.
- Unknown threshold.
- Stable class labels.
- Missing artifact behavior.
- Invalid model metadata.
- Không train full model trong unit tests.
- Training reproducibility test với fixture nhỏ.

Acceptance criteria:

- Training command chạy được.
- Evaluation command chạy được.
- Kết quả có report thật.
- Model inference được tích hợp.
- API tests pass.
- Docker/runtime biết cách tải model.
- Không phá năm user flow.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 4 — NÂNG CẤP CV–JD MATCHING
========================

Mục tiêu:

Nâng matching từ exact skill overlap thành matching kết hợp lexical evidence và semantic evidence.

Điều kiện:

Không triển khai semantic scoring như một điểm chính thức nếu chưa có ground truth độc lập
do con người đánh giá.

1. Giữ các thành phần giải thích được:

SkillCoverage =
    matched JD skills / all recognized JD skills

Matched skills và missing skills phải tiếp tục được trả về.

2. Nghiên cứu hai baseline:

- TF-IDF cosine similarity.
- Sentence embedding cosine similarity.

3. Nếu sử dụng sentence-transformers:

- Chọn model nhỏ, chạy được local CPU, ví dụ một model MiniLM phù hợp.
- Ghi rõ model name và version/revision.
- Kiểm tra kích thước dependency và Docker image.
- Không để production tự tải model âm thầm mà không có hướng dẫn.
- Có cache và startup validation rõ ràng.

4. Công thức thử nghiệm:

FinalScore =
    alpha × SkillCoverageScore
    + beta × SemanticSimilarityScore

Trong đó:

alpha + beta = 1

Không mặc định khẳng định 0.6/0.4 là tối ưu.
Hệ số phải được chọn trên validation set.

5. Ground truth matching phải do con người gán:

Mỗi cặp CV–JD cần:

- Human match score.
- Required skills.
- Preferred skills.
- Explanation.
- Reviewer count hoặc review status.

6. Evaluation:

- MAE giữa predicted score và human score.
- Spearman correlation.
- Skill precision/recall/F1.
- Latency.
- Error analysis cho ít nhất:
  - Paraphrase.
  - Missing required skill.
  - Keyword stuffing.
  - CV khác lĩnh vực.
  - JD không có kỹ năng rõ ràng.

7. Explainability:

Kết quả nên thể hiện:

- Overall match score.
- Skill coverage.
- Semantic similarity.
- Matched skills.
- Missing skills.
- Lý do chính ảnh hưởng đến điểm.

Nếu thêm field mới vào response:
- Cập nhật toàn bộ contract, backend, frontend và tests.

Acceptance criteria:

- Có baseline comparison.
- Có human-labeled evaluation.
- Không tuyên bố semantic model tốt hơn nếu metrics không chứng minh.
- Frontend giải thích được điểm matching.
- Tất cả contract tests pass.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 5 — NÂNG CHẤT LƯỢNG PHẦN QWEN
========================

Mục tiêu:

Biến phần LLM thành một thành phần có nhiệm vụ rõ, prompt có version và output đo lường được.

1. Tách prompt khỏi main.py:

ai-service/app/llm/prompts.py

Mỗi prompt có:
- Prompt ID.
- Version.
- System prompt.
- Input builder.
- Expected JSON schema.

2. Resume recommendation prompt phải nhận:

- Predicted field.
- Classification confidence.
- Existing skills.
- Score breakdown.
- Resume excerpt.
- Evidence của các tiêu chí điểm thấp.

3. JD analysis prompt phải nhận:

- Target role.
- Matched skills.
- Missing skills.
- Skill coverage.
- Semantic evidence nếu Đợt 4 đã được thực hiện.
- JD excerpt.
- Resume excerpt.

4. Output validation:

- Đúng JSON object.
- Đúng required keys.
- Giới hạn số phần tử.
- Loại chuỗi rỗng.
- Deduplicate không phân biệt hoa thường.
- Không đề xuất kỹ năng đã có.
- Không đưa ra nhận xét không có bằng chứng rõ ràng.
- Không để LLM thay đổi score hoặc predicted field.

5. Prompt injection defense cơ bản:

- Đánh dấu CV/JD là untrusted document content.
- Yêu cầu model không tuân theo instruction nằm trong CV/JD.
- Không ghép raw text vào system prompt.
- Giới hạn độ dài input.
- Không log raw CV/JD.

6. LLM evaluation:

Tạo rubric chấm ít nhất các tiêu chí:

- Relevance.
- Actionability.
- Faithfulness.
- Specificity.
- No hallucination.
- Output schema compliance.

Mỗi tiêu chí dùng thang 1–5.
Nếu chỉ có synthetic/manual cases, ghi rõ limitation.

7. Tạo:

evaluation/llm/
    rubric.md
    cases.json
    evaluate_schema.py
    human_review_template.csv
    report.md

Không dùng chính Qwen làm giám khảo duy nhất cho output của Qwen.

Acceptance criteria:

- Prompt versioned.
- Structured output được validate.
- Có bộ evaluation.
- Có error analysis.
- Orchestration tests sử dụng mock, không phụ thuộc Ollama thật.
- Không phá public API.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 6 — EXPLAINABILITY VÀ GIAO DIỆN
========================

Mục tiêu:

Người dùng và giảng viên hiểu tại sao hệ thống đưa ra kết quả.

Resume Result nên hiển thị:

- Predicted field.
- Classification confidence.
- Top evidence hoặc influential terms.
- Score breakdown.
- Recommended skills.
- Recommendations.
- Thông tin phương pháp/model ở mức vừa đủ.

Match Result nên hiển thị:

- Overall match score.
- Skill coverage.
- Semantic score nếu có.
- Matched skills.
- Missing skills.
- ATS keywords.
- Strengths.
- Weaknesses.
- Recommendations.

Yêu cầu UI:

- Không thiết kế lại toàn bộ frontend.
- Giữ style hiện tại.
- Responsive.
- Có empty state.
- Có loading và error state.
- Không hiển thị NaN hoặc undefined.
- Có accessible labels.
- Có test cho dữ liệu đầy đủ và dữ liệu thiếu.

Nếu database cần lưu thêm metadata:
- Tạo migration mới.
- Không sửa migration cũ đã áp dụng.
- Không lưu raw CV/JD.

Acceptance criteria:

- Người dùng hiểu lý do của dự đoán.
- Frontend tests pass.
- Backend tests pass.
- Contract tests pass.
- Không phá history/admin.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 7 — BÁO CÁO HỌC THUẬT VÀ VẤN ĐÁP
========================

Mục tiêu:

Hoàn thiện tài liệu đủ để bảo vệ đồ án.

Tạo:

docs/AI_METHODOLOGY.md
docs/AI_EVALUATION.md
docs/AI_LIMITATIONS.md
docs/VIVA_QUESTIONS_AND_ANSWERS.md
docs/DEMO_SCRIPT.md

1. AI_METHODOLOGY.md:

- Phát biểu bài toán.
- Kiến trúc hybrid.
- Tiền xử lý.
- TF-IDF.
- Logistic Regression/SVM.
- Công thức cosine similarity nếu có.
- Hệ chuyên gia chấm điểm.
- Vai trò Qwen.
- Pseudocode.
- Sơ đồ Mermaid.
- Lý do chọn thuật toán.

2. AI_EVALUATION.md:

- Dataset.
- Provenance.
- Train/validation/test split.
- Baselines.
- Metrics.
- Confusion matrix.
- Matching evaluation.
- LLM rubric.
- Error analysis.
- Không phóng đại kết quả.

3. AI_LIMITATIONS.md:

- Dataset nhỏ.
- Domain limitation.
- English-only.
- Text PDF only.
- Taxonomy coverage.
- Bias.
- LLM hallucination risk.
- Không dùng cho quyết định tuyển dụng tự động.
- Future work.

4. VIVA_QUESTIONS_AND_ANSWERS.md:

Chuẩn bị ít nhất 25 câu hỏi và câu trả lời, gồm:

- AI nằm ở đâu?
- Nhóm tự xây dựng phần nào?
- Vì sao chọn TF-IDF?
- Vì sao chọn Logistic Regression hoặc SVM?
- Tại sao không dùng neural network?
- Accuracy khác F1 như thế nào?
- Vì sao dùng Macro F1?
- Overfitting là gì?
- Làm sao tránh data leakage?
- Unknown threshold được chọn thế nào?
- Confusion matrix nói lên điều gì?
- Match score được tính thế nào?
- Cosine similarity là gì?
- Qwen làm gì?
- Vì sao không để Qwen tính score?
- Làm sao đánh giá recommendation?
- Làm sao kiểm soát hallucination?
- Hệ thống có bias không?
- Dữ liệu có vi phạm riêng tư không?
- Hạn chế lớn nhất là gì?
- Baseline là gì?
- Kết quả nào chứng minh mô hình tốt hơn?
- Nếu Ollama không chạy thì sao?
- Nếu CV khác lĩnh vực thì sao?
- Có thể triển khai thực tế không?

Câu trả lời phải dựa trên code và số liệu thật của dự án.

5. DEMO_SCRIPT.md:

Kịch bản demo 7–10 phút:

- 1 phút: bài toán.
- 1 phút: kiến trúc.
- 2 phút: Resume Analysis.
- 2 phút: CV–JD Matching.
- 1 phút: evaluation.
- 1 phút: explainability.
- Thời gian còn lại: kết luận.

6. README:

Cập nhật README để mô tả đúng:
- Thành phần ML.
- Dataset.
- Training.
- Evaluation.
- Demo commands.
- Không gọi rule-based logic là trained AI model.

Sau khi hoàn thành, cập nhật progress và dừng.

========================
ĐỢT 8 — KIỂM THỬ CUỐI VÀ RELEASE AUDIT
========================

Mục tiêu:

Xác minh toàn bộ repository có thể tái lập và demo.

1. Chạy:

Frontend:
    npm test -- --runInBand
    npm run build

Backend:
    ./gradlew test --no-daemon

AI service:
    pytest ai-service/tests

Repository:
    pytest

Contracts:
    python scripts/export_openapi.py --check

Evaluation:
    python evaluation/validate_dataset.py
    python evaluation/run_evaluation.py --mode rule-only
    chạy classification validator
    chạy classifier evaluation
    chạy matching evaluation nếu có
    chạy LLM schema evaluation

Docker:
    docker compose config

2. Kiểm tra:

- Clean setup instructions.
- Dependency pinning.
- Model artifact hoặc model build command.
- Dataset availability.
- Không có secret.
- Không có raw PII.
- Không có file tạm lớn.
- Không có đường dẫn tuyệt đối của máy developer.
- Không có test phụ thuộc internet không được ghi rõ.
- Không có metric không thể tái tạo.
- Không có tài liệu nói khác implementation.

3. Tạo:

docs/FINAL_RELEASE_AUDIT.md

Báo cáo:

- Test matrix.
- Pass/fail.
- Known limitations.
- Demo prerequisites.
- Commands chạy demo.
- Model và dataset version.
- Các vấn đề còn lại trước khi nộp.

Không push GitHub, tạo PR hoặc thay đổi repository settings nếu người dùng chưa yêu cầu rõ.

========================
IV. THỨ TỰ ƯU TIÊN
========================

P0 — bắt buộc:

1. Sửa parser và scoring correctness.
2. Đồng bộ taxonomy và field names.
3. Xây dataset hợp lệ.
4. Huấn luyện classifier.
5. Có baseline comparison.
6. Có metrics và confusion matrix.
7. Có tài liệu phương pháp và vấn đáp.

P1 — nên làm:

8. Explainability.
9. Human-labeled CV–JD evaluation.
10. Semantic matching.
11. LLM evaluation rubric.

P2 — chỉ làm nếu còn thời gian:

12. Cải thiện visualization.
13. Thử thêm model.
14. Tối ưu latency sâu hơn.

Nếu thời gian không đủ, ưu tiên hoàn thiện P0 thay vì bắt đầu nhiều P1/P2 nhưng không đánh giá được.

========================
V. MẪU BÁO CÁO SAU MỖI ĐỢT
========================

Sau mỗi đợt, trả lời đúng cấu trúc:

## Batch N — Result

### Outcome
Mô tả kết quả chính.

### Changed files
Liệt kê từng file và lý do thay đổi.

### Technical decisions
Nêu các quyết định và trade-off.

### Tests
Liệt kê command và kết quả pass/fail.

### Metrics
Chỉ ghi metrics thật có thể tái tạo.

### Risks and limitations
Nêu vấn đề còn lại.

### Contract impact
Ghi rõ:
- No contract change
hoặc
- Các contract đã thay đổi và consumer đã cập nhật.

### Next batch
Mô tả đợt tiếp theo nhưng không tự thực hiện.

Sau đó dừng và chờ lệnh của người dùng.

========================
VI. LỆNH KHỞI ĐẦU
========================

Bây giờ chỉ thực hiện Đợt 0 — Audit và Baseline.

Không sửa logic ứng dụng trong đợt này.
Không tự động chuyển sang Đợt 1.