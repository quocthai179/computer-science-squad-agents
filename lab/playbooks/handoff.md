# Handoff: TASK BRIEF và RECEIPT

Subagent khởi động với context trống: nó không thấy hội thoại và không thấy file Lead đã đọc. Nó có nạp `CLAUDE.md` của repo. `TASK BRIEF` vì thế phải tự đứng được.

## TASK BRIEF (Lead → subagent)

```text
TASK BRIEF
objective:   <một câu, kết quả cần có>
inputs:      <đường dẫn file; không dán nội dung>
output:      <đường dẫn và template phải theo>
playbook:    <đường dẫn tuyệt đối tới playbook liên quan>
boundaries:  <không làm gì; phạm vi nguồn, thời gian>
budget:      <số tool call, phút compute, số vòng>
stop_when:   <điều kiện xong>; halt-and-report nếu <điều kiện>
```

Luật viết brief:

- `objective` là kết quả, không phải hoạt động: "danh sách 10–20 paper về X có điểm relevance" chứ không phải "tìm hiểu về X".
- `inputs` chỉ là đường dẫn. Dán nội dung vào brief làm hỏng nguyên tắc "file là giao thức" và làm phình context.
- `boundaries` nói rõ góc nào thuộc agent khác để tránh trùng việc giữa các scout chạy song song.
- `budget` là trần cứng. Agent hết ngân sách thì dừng và trả `status: partial`.
- Gửi đường dẫn tuyệt đối tới template và playbook, vì subagent không biết thư mục plugin.

## RECEIPT (subagent → Lead)

```text
RECEIPT
status:      done | partial | blocked
outputs:     <đường dẫn>
findings:    <tối đa 3 dòng>
open:        <câu hỏi, nghi ngờ>
confidence:  low | medium | high, kèm lý do
escalate:    none | model | user: <cần gì>
```

Luật nhận receipt:

- Lead đọc file trong `outputs`, không tin `findings` thay cho file.
- `status: blocked` hoặc `escalate: user` → Lead đưa lên người dùng, không tự đoán.
- `escalate: model` → gọi lại cùng brief với `model: opus`, một lần.
- Receipt không theo mẫu, hoặc agent làm việc ngoài `boundaries` → ghi một dòng vào `research/lessons/squad-issues.md`.

## Ghi chép

Sau mỗi workflow Lead ghi một mục notebook:

```bash
python3 <plugin>/scripts/notebook.py add --source <skill> "<3–6 dòng: làm gì, ra artifact nào, còn mở gì>"
```
