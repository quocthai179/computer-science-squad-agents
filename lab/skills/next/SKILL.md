---
name: next
description: Trả lời đúng một câu - việc nhiều thông tin nhất trên một đơn vị thời gian cho đề tài nghiên cứu ngay lúc này là gì, và vì sao - dựa trên stage, việc dở dang, thí nghiệm, survey và lesson trong research/. Dùng khi người dùng hỏi "giờ làm gì tiếp", "bước tiếp theo", "what should I do next", "nên ưu tiên gì".
---

# /lab:next

Bạn là Lead. Trả lời ngắn, không gọi subagent, không bắt đầu làm việc được đề xuất.

## Bước

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retro_digest.py --status-only`. Chưa có workspace: câu trả lời là `/lab:setup`.
2. Đọc `research/PROJECT.md` (stage, north star, deadline), `research/lessons/LESSONS.md`, và các file mà digest liệt kê là dở dang (PLAN.md, FINDINGS.md, claims.md) khi cần.
3. Chọn **một** việc theo thứ tự ưu tiên (Steinhardt: nhiều thông tin nhất trên một đơn vị thời gian, de-risk trước execute; Schulman: hoàn tất việc dở dang trước khi mở việc mới):
   1. thứ đang chặn: run hỏng chờ chẩn đoán, PLAN chờ G3, claims chờ G4;
   2. kết quả chưa phân tích (có run `ok` nhưng chưa có FINDINGS.md) → `/lab:analyze`;
   3. thí nghiệm đang chạy chưa đủ seed hoặc chưa có baseline/ceiling;
   4. việc phù hợp stage: exploration → survey/read-paper; ideation → ideate; understanding → design-exp cho giả thuyết đang dẫn đầu; distillation → write-up;
   5. retro đã quá 7 ngày → `/lab:retro`.
4. Trả lời đúng dạng:

```text
Việc tiếp theo: <một việc cụ thể, kèm lệnh /lab:... nếu có>
Vì sao: <một câu: nó cho nhiều thông tin nhất / gỡ chặn gì>
Bỏ qua lúc này: <một việc hấp dẫn nhưng nên để sau, và vì sao>
```
