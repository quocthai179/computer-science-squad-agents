---
name: run-exp
description: Chạy một thí nghiệm đã được duyệt (G3) qua experimenter, theo thứ tự smoke → baseline → ceiling → run chính, mọi run ghi vào ledger bằng runwrap.py. Tiêu compute nên chỉ chạy khi người dùng gõ lệnh.
argument-hint: "<exp-id> [smoke|baseline|main|all]"
disable-model-invocation: true
---

# /lab:run-exp

Bạn là Lead. `experimenter` làm; bạn giữ gate, ngân sách và báo cáo.

Luật luôn đúng:
- Chỉ chạy khi `PLAN.md` có `status: approved` hoặc `running`. Không thì dừng và chỉ người dùng tới `/lab:design-exp`.
- Mọi run đi qua `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/runwrap.py`. runwrap từ chối (exit 3) là tín hiệu dừng, không phải chướng ngại để lách.
- Sửa lỗi tối đa 3 lần; không bao giờ đổi eval, metric hay test data.

Đầu vào: $ARGUMENTS (mặc định phạm vi `all`)

## Bước

1. Đọc `research/experiments/<exp_id>/PLAN.md`. Kiểm `status`, `prediction`, `kill_criteria`. Xem ngân sách đã dùng: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py budget --exp <exp_id>`.
2. Nếu `status: approved`: đổi thành `running`.
3. Gọi `lab:experimenter` với TASK BRIEF:
   - `objective`: chạy phạm vi <smoke|baseline|main|all> của <exp_id>
   - `inputs: research/experiments/<exp_id>/PLAN.md`, code liên quan
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/experiment.md`
   - `runwrap: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/runwrap.py --exp <exp_id> ...`
   - `budget`: số run còn lại và phút compute còn lại theo `ledger.py budget`
   - `stop_when`: xong phạm vi; halt-and-report khi runwrap từ chối, sau 3 lần sửa không xong, hoặc khi chạm kill criteria
4. Đọc RECEIPT và `ledger.py list --exp <exp_id>`. Kiểm: smoke `ok` có trước run thật; số seed mỗi variant; run hỏng có được báo không.
5. RECEIPT `blocked`: đọc `diagnosis.md` (nếu có) và trình người dùng: triệu chứng, đã thử gì, lựa chọn. Chỉ khi người dùng nói tiếp tục mới gọi lại experimenter với ghi chú "người dùng đã đọc chẩn đoán, được dùng --after-review".
   runwrap báo hết ngân sách: hỏi người dùng có nâng `max_runs` / `budget_total_hours` không; chỉ sửa PLAN.md khi người dùng đồng ý, và ghi `decisions.md`.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source run-exp "<exp_id>: <run ids>, <ok/failed>, <phút compute>"`.
7. Báo người dùng: run id đã chạy, trạng thái, ngân sách còn lại, và gợi ý `/lab:analyze <exp_id>`. **Không** diễn giải kết quả ở đây; đó là việc của `analyst`.
