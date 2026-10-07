---
name: critique
description: Phản biện độc lập (red-team review) một artifact nghiên cứu: idea card, PLAN.md, FINDINGS.md, bản nháp báo cáo, survey hoặc paper card. Kiểm con trỏ bằng chứng, leakage, baseline, seed, cherry-pick, con số so với ledger, novelty. Dùng khi người dùng muốn "review", "phản biện", "critique", "soát lỗi thí nghiệm", "kiểm tra kết quả này có đáng tin không".
argument-hint: "<đường dẫn artifact> [idea|plan|findings|draft|survey|paper-card]"
---

# /lab:critique

Bạn là Lead. `skeptic` review bằng context độc lập: bạn chỉ đưa đường dẫn, **không** đưa lập luận, tóm tắt hay ý kiến của bạn hay của tác giả.

Đầu vào: $ARGUMENTS

## Bước

1. Xác định file artifact và loại. Không ghi loại thì suy ra: `ideas/cards/` → idea; `PLAN.md` → plan; `FINDINGS.md` → findings; `reports/` → draft; `surveys/` → survey; `papers/cards/` → paper-card. Không chắc: hỏi một câu.
   Chưa có `research/`: chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_workspace.py --project-dir .` để có chỗ ghi review.
2. Xác định vòng: đã có review cho artifact này trong `research/reviews/` và artifact đã sửa sau đó → vòng 2. Vòng 3 không tồn tại: còn bất đồng thì đưa người dùng quyết.
3. Gọi `lab:skeptic` với TASK BRIEF:
   - `objective: review <loại> <đường dẫn>, vòng <n>`
   - `inputs: <đường dẫn artifact>` (cộng review vòng 1 nếu là vòng 2)
   - `output: research/reviews/<slug>-<YYYY-MM-DD>.md`, template `${CLAUDE_PLUGIN_ROOT}/templates/review.md`
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/review.md`
   - `budget: 30 tool call`
   Không gọi được subagent: tự review theo cùng playbook và nói rõ rằng review **không** độc lập.
4. Với artifact dạng văn bản (findings, draft, survey) có thể chạy thêm `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py <file>` và đưa kết quả vào câu trả lời.
5. Đọc file review. Trả cho người dùng, ngắn gọn:
   - verdict và một câu lý do;
   - **danh sách lỗi chặn**, mỗi lỗi một dòng gọi đúng tên lỗi (ví dụ: leakage, thiếu baseline, chỉ một seed, cherry-pick, con số không có trong ledger, thiếu prior work) kèm vị trí;
   - giải thích thay thế quan trọng nhất;
   - đường dẫn review.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source critique "<artifact>: <verdict>, <n> lỗi chặn"`.

Không tự sửa artifact. Người dùng (hoặc workflow sở hữu artifact) quyết định sửa gì.
