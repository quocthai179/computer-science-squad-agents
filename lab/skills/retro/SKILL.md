---
name: retro
description: Review tuần cho đề tài nghiên cứu: tổng hợp notebook, ledger, quyết định, calibration (dự đoán đúng bao nhiêu, ước lượng thời gian lệch bao nhiêu), việc dở dang; viết retro bốn mục kiểu Schulman; hỏi các câu review của Nanda; đề xuất tối đa 3 lesson cho LESSONS.md. Dùng khi người dùng muốn "retro", "review tuần", "weekly review", "rút kinh nghiệm".
argument-hint: "[số ngày, mặc định 7]"
---

# /lab:retro

Bạn là Lead. Retro chạy ở main session vì nó cần đối thoại. Không gọi subagent.

Luật luôn đúng:
- Lesson chỉ vào `LESSONS.md` khi người dùng duyệt. Tối đa 3 lesson mỗi lần. `LESSONS.md` có trần 50 dòng: thêm một thì gộp hoặc bỏ một.
- Lesson có dạng "khi X thì làm Y — bằng chứng: <đường dẫn>". Không có bằng chứng thì không phải lesson.

Đối số (số ngày): $ARGUMENTS

## Bước

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retro_digest.py --days <số ngày, mặc định 7>`. Đọc output, `research/PROJECT.md`, `research/lessons/LESSONS.md`, `research/lessons/squad-issues.md`.
2. Viết nháp `research/lessons/retros/<YYYY-MM-DD>.md` theo ${CLAUDE_PLUGIN_ROOT}/templates/retro.md:
   - bốn mục Schulman: experimental findings, insights, code progress, next steps;
   - bảng đối chiếu next steps của retro trước (digest đã trích);
   - calibration (copy từ digest);
   - số việc dở dang (Schulman: chuyển bài toán quá thường xuyên là lỗi phổ biến hơn bám quá lâu).
3. Hỏi người dùng các câu review của Nanda, **mỗi lượt tối đa 3 câu**: mục tiêu tuần và tiến được bao nhiêu; cái gì ngốn thời gian, cái gì chặn; sai lầm nào và đổi cách làm ra sao; đang rối ở đâu; nhịp làm việc có bền không. Ghi câu trả lời vào file retro.
4. Đề xuất tối đa 3 lesson theo dạng trên. Người dùng duyệt từng cái. Lesson được duyệt → thêm vào `LESSONS.md` (kiểm trần 50 dòng); lesson nào nên thành sửa playbook thì ghi vào `squad-issues.md` dạng việc cần làm.
5. Lỗi của chính các agent trong tuần (RECEIPT sai mẫu, vượt ngân sách, bịa, bỏ qua playbook) → thêm dòng vào `research/lessons/squad-issues.md`.
6. Đề nghị cập nhật `stage` trong `PROJECT.md` nếu digest cho thấy đã chuyển giai đoạn; chỉ sửa khi người dùng đồng ý.
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source retro "<đường dẫn retro>; <n> lesson mới"`. Kết thúc bằng next steps cho tuần tới (tối đa 3).
