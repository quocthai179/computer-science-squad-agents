---
name: survey
description: Khảo sát tài liệu có nguồn cho một chủ đề AI/ML bằng đội agent (scout song song, reader, writer, skeptic). Dùng khi người dùng muốn "khảo sát", "tổng quan nghiên cứu", "survey", "literature review", "tìm paper về", "state of the art", "related work" của một chủ đề. Không dùng cho câu hỏi sự kiện đơn lẻ.
argument-hint: "<chủ đề> [--quick]"
---

# /lab:survey

Bạn là Lead. Bạn điều phối, không tự đọc paper và không tự viết survey.

Luật luôn đúng:
- Mỗi nhận định trong survey có neo `[@paper-id, vị trí trong paper]`.
- Tối đa 5 scout, tối đa 1 vòng tìm bổ sung, tối đa 1 vòng skeptic.
- Mọi bàn giao qua file theo ${CLAUDE_PLUGIN_ROOT}/playbooks/handoff.md. Đọc song song, viết tuần tự.
- Không gọi được subagent thì tự làm tuần tự theo cùng playbook và nói rõ điều đó.

Chủ đề: $ARGUMENTS

## Bước

1. Đọc `research/PROJECT.md` và `research/lessons/LESSONS.md`. Chưa có workspace: bảo người dùng chạy `/lab:setup` rồi dừng.
2. Chủ đề mơ hồ: hỏi tối đa 2 câu. Có `--quick`: tự trả lời trong 10 tool call (WebSearch, WebFetch), ghi `research/surveys/<slug>/quick.md` có nguồn, bỏ các bước dưới.
3. Đặt `<slug>`. Tách 3–5 góc nhìn **không chồng lấn** (ví dụ: nền tảng; phương pháp chính; benchmark và cách đánh giá; giới hạn và phản biện; diễn biến 12 tháng gần nhất). Ghi `research/surveys/<slug>/angles.md`: mỗi góc một câu hỏi và ranh giới với góc khác. Ngân sách theo ${CLAUDE_PLUGIN_ROOT}/playbooks/principles.md: chủ đề hẹp 2–3 scout × 12 tool call; rộng 4–5 scout × 15 tool call.
4. Gọi **song song** subagent `lab:scout`, mỗi góc một TASK BRIEF:
   - `output: research/surveys/<slug>/scout-<angle>.jsonl` (và `scout-<angle>.md`);
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/reading.md`;
   - `inputs: research/papers/index.jsonl` (để tránh trùng);
   - `boundaries`: các góc còn lại thuộc scout khác.
5. Gộp và khử trùng: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/paper_index.py merge research/surveys/<slug>/scout-*.jsonl --tag survey:<slug>`. Xem `paper_index.py list --tag survey:<slug> --min-relevance 2`.
   Góc nào RECEIPT `partial` hoặc quá ít paper: được **một** vòng scout bổ sung cho góc đó.
6. **Dừng chờ người dùng.** Trình 5–8 paper đề xuất đọc sâu (id, năm, một câu vì sao, relevance), ưu tiên survey và thesis làm xương sống. Người dùng sửa danh sách.
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/paper_fetch.py <id...>`. Paper không tải được: báo người dùng, bỏ khỏi danh sách đọc sâu (không đọc sâu từ abstract).
8. Gọi **song song** `lab:reader`, mỗi paper một reader: `inputs: <fulltext path>`, `output: research/papers/cards/<id>.md`, template ${CLAUDE_PLUGIN_ROOT}/templates/paper-card.md. Sau đó `paper_index.py set <id> pass=2` cho từng paper đã có card.
9. Gọi `lab:writer` (loại việc `survey`) với đường dẫn các card, `angles.md`, các `scout-*.md`; output `evidence.jsonl`, `gaps.md`, `survey.md` trong `research/surveys/<slug>/`.
10. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/cite_check.py research/surveys/<slug>/survey.md` và `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py research/surveys/<slug>/survey.md`. Lỗi: gửi lại `lab:writer` một lần kèm output của script.
11. Gọi `lab:skeptic` với loại artifact `survey`, review ghi `research/reviews/survey-<slug>-<YYYY-MM-DD>.md`. Có lỗi chặn: gọi lại `lab:writer` **một** lần kèm đường dẫn review.
12. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source survey "<chủ đề, số paper, đường dẫn, câu hỏi mở>"`. Trả cho người dùng: 5 dòng tóm tắt, đường dẫn `survey.md`, verdict của skeptic, 3–5 câu hỏi mở, và gợi ý `/lab:ideate` hoặc `/lab:read-paper <id>`.
