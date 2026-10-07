---
name: analyze
description: Phân tích kết quả một thí nghiệm từ run ledger: bảng và hình do script sinh, thống kê nhiều seed, FINDINGS.md (dữ liệu cho thấy gì, không cho thấy gì, giải thích thay thế, thí nghiệm kế tiếp), skeptic review, đối chiếu dự đoán. Dùng khi người dùng muốn "phân tích kết quả", "analyze results", "kết quả thí nghiệm nói gì", "so sánh các run".
argument-hint: "<exp-id>"
---

# /lab:analyze

Bạn là Lead. `analyst` phân tích; `skeptic` phản biện; người dùng quyết định.

Luật luôn đúng:
- Mọi con số trong FINDINGS.md nằm trong `tables/` do `ledger.py`/`stats.py` sinh, kèm `[run:...]`.
- Người chạy thí nghiệm không tự chấm kết quả: không gọi `experimenter` ở đây.

Đầu vào: $ARGUMENTS

## Bước

1. Đọc `research/experiments/<exp_id>/PLAN.md` và `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py list --exp <exp_id>`. Chưa có run `ok` ngoài smoke: dừng, gợi ý `/lab:run-exp`.
2. Xác định các so sánh chính từ PLAN.md (baseline vs method, ceiling, ablation).
3. Gọi `lab:analyst` với TASK BRIEF:
   - `inputs: PLAN.md, runs.jsonl` của <exp_id>; danh sách cặp so sánh; `primary_metric`
   - `output: research/experiments/<exp_id>/FINDINGS.md`, template `${CLAUDE_PLUGIN_ROOT}/templates/findings.md`; `tables/`, `figures/` do script sinh
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/experiment.md`
   - đường dẫn tuyệt đối `${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py`, `stats.py`, `lint_report.py`
4. Gọi `lab:skeptic` với loại `findings`, chỉ đường dẫn FINDINGS.md, PLAN.md, runs.jsonl. Review vào `research/reviews/<exp_id>-findings-<YYYY-MM-DD>.md`.
5. Trình người dùng: 5 dòng tóm tắt FINDINGS, bảng chính (copy từ `tables/`), verdict skeptic và lỗi chặn, và đối chiếu với prediction.
6. **Người dùng quyết** một trong ba:
   - cần thêm bằng chứng → gợi ý run cụ thể, quay lại `/lab:run-exp`;
   - đổi giả thuyết → `/lab:design-exp` với PLAN mới (PLAN cũ giữ nguyên);
   - đủ, hoặc chạm kill criteria → đóng: `status: closed` trong PLAN.md, kết luận và "vì sao" trong FINDINGS.md.
7. Resolve calibration theo id ghi cuối PLAN.md: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/calibration.py resolve <id> --outcome <true|false|partial>`; với estimate, hỏi người dùng số giờ thực rồi `--actual-hours`.
8. Ghi `research/decisions.md` và `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source analyze "<exp_id>: <kết luận một câu>; quyết định: <...>"`.
