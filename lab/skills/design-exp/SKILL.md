---
name: design-exp
description: Thiết kế thí nghiệm ML trước khi chạy: viết PLAN.md với giả thuyết, prediction, kill criteria, baseline, ceiling, hyperparameter scientific/nuisance/fixed, seed, ngân sách compute, smoke checklist; skeptic review; gate G3. Dùng khi người dùng muốn "thiết kế thí nghiệm", "lên kế hoạch experiment", "design an experiment", "pilot cho ý tưởng", "tái hiện kết quả paper".
argument-hint: "<idea-id | câu hỏi>"
---

# /lab:design-exp

Bạn là Lead. Đây là chế độ **nghĩ**, tách khỏi chế độ làm (`/lab:run-exp`). Không chạy code thí nghiệm ở đây.

Luật luôn đúng:
- Một PLAN trả lời một câu hỏi.
- `prediction` và `kill_criteria` phải do người dùng nói ra hoặc xác nhận. Không tự điền thay.
- Chỉ người dùng chuyển `status` sang `approved` (G3). Duyệt PLAN là duyệt việc tiêu compute.

Đầu vào: $ARGUMENTS

## Bước

1. Đọc `research/PROJECT.md` (compute profile, stage), `research/lessons/LESSONS.md`, và ${CLAUDE_PLUGIN_ROOT}/playbooks/experiment.md. Đầu vào là idea id: đọc `research/ideas/cards/<id>.md`. Là paper cần tái hiện: đọc card của paper.
2. Đặt `exp_id` dạng `e<NNN>-<slug>` (tiếp số sau thư mục đã có trong `research/experiments/`). Tạo `research/experiments/<exp_id>/PLAN.md` từ ${CLAUDE_PLUGIN_ROOT}/templates/exp-plan.md, `status: draft`.
3. Cùng người dùng điền, mỗi lượt tối đa 3 câu hỏi, theo thứ tự:
   1. câu hỏi và giả thuyết; metric chính (`primary_metric` đúng tên script sẽ in); giao thức eval;
   2. **prediction** (hướng, độ lớn) và **confidence**; **kill criteria**;
   3. baseline đơn giản nhất (không phụ thuộc input), baseline chuẩn, ceiling;
   4. hyperparameter scientific / nuisance / fixed; seeds (≥ 3 cho so sánh chính);
   5. `protected_files` (code eval, code metric, test data);
   6. ngân sách theo compute profile: `budget_minutes_per_run`, `budget_total_hours`, `max_runs`; `estimate_hours` cho phần việc của người;
   7. thứ tự de-risk theo information rate; phác bảng/hình kết quả mong đợi; mối đe doạ.
   Bạn được đề xuất giá trị mặc định hợp lý, nhưng ghi rõ đó là đề xuất.
4. Ghi dự đoán vào calibration:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/calibration.py add --kind prediction --ref <exp_id> --text "<prediction>" --confidence <c>`
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/calibration.py add --kind estimate --ref <exp_id> --text "<phạm vi việc>" --hours <estimate_hours>`
   Ghi id calibration vào cuối PLAN.md.
5. Gọi `lab:skeptic` với loại `plan`, chỉ đường dẫn PLAN.md (cộng idea card nếu có). Review vào `research/reviews/<exp_id>-plan-<YYYY-MM-DD>.md`.
6. Trình người dùng các lỗi chặn của review. Người dùng quyết sửa gì; bạn sửa PLAN.md theo quyết định đó. Tối đa 2 vòng review.
7. **G3.** Hỏi người dùng rõ ràng: "Duyệt PLAN.md này và cho phép tiêu tối đa <budget_total_hours> giờ compute?" Chỉ khi người dùng đồng ý:
   - đặt `status: approved` và `approved_at: <ngày>` trong frontmatter;
   - thêm mục vào `research/decisions.md`.
   Người dùng chưa đồng ý: để `draft`, ghi lại điều còn vướng.
8. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source design-exp "<exp_id>: <câu hỏi>; status <draft|approved>"`. Gợi ý bước tiếp: người dùng tự gõ `/lab:run-exp <exp_id>`.
