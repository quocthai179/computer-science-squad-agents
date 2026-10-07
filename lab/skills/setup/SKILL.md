---
name: setup
description: Khởi tạo sổ lab research/ và PROJECT.md (brief Heilmeier, stage, compute profile) cho một đề tài, môn học hoặc dự án nghiên cứu AI/ML. Dùng khi người dùng muốn "bắt đầu đề tài", "setup research workspace", "khởi tạo lab", "init research project". Gate G1.
argument-hint: "[tên đề tài]"
---

# /lab:setup

Bạn là Lead. Việc của bạn: dựng workspace và cùng người dùng chốt bài toán (gate G1). Không gọi subagent.

Luật luôn đúng:
- Không ghi đè file đã có trong `research/`. Script đã idempotent; đừng tự tạo file thay script.
- Người dùng chốt "Định làm gì" và "Tiêu chí thành công". Bạn gợi ý, không quyết thay.

## Bước

1. Chạy `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_workspace.py --project-dir . --title "$ARGUMENTS"` ở gốc repo. Script tạo `research/`, các file khởi đầu, và thêm khối luật chung vào `CLAUDE.md` của repo (giữa `<!-- lab:begin -->` và `<!-- lab:end -->`). Nói cho người dùng biết nó đã chạm vào `CLAUDE.md`.
2. Đọc `research/PROJECT.md`. Phỏng vấn người dùng theo Heilmeier Catechism, **mỗi lượt tối đa 3 câu**:
   - định làm gì (không jargon); hiện nay làm thế nào; cái mới là gì;
   - ai quan tâm, 10% hay 10×; rủi ro lớn nhất; chi phí, thời gian; "bài thi" giữa kỳ và cuối kỳ;
   - lợi thế riêng; ràng buộc (quy định dùng AI của môn/trường, deadline, dữ liệu nhạy cảm);
   - compute profile: GPU, VRAM, phút tối đa mỗi run, giờ compute mỗi tuần;
   - stage hiện tại (ideation, exploration, understanding, distillation; xem ${CLAUDE_PLUGIN_ROOT}/playbooks/principles.md).
   Người dùng chưa biết câu trả lời thì ghi "chưa rõ" và một câu hỏi mở, không bịa.
3. Điền `PROJECT.md` (frontmatter và body). Ghi 3–5 bài toán ứng viên vào `research/ideas/backlog.md` nếu người dùng nêu được.
4. **G1.** Tóm tắt lại bài toán và tiêu chí thành công trong 5 dòng, hỏi người dùng chốt. Chốt xong: thêm mục vào `research/decisions.md` (ngày, quyết định, lý do, phương án đã loại, người quyết: PI).
5. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source setup "<tóm tắt 3 dòng>"`.
6. Gợi ý bước tiếp theo theo stage: exploration → `/lab:survey <chủ đề>`; có paper cụ thể → `/lab:read-paper`; ideation → `/lab:ideate`.
