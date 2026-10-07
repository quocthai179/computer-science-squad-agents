---
name: write-up
description: Viết báo cáo nghiên cứu (báo cáo môn học, draft paper, blog kỹ thuật) đi từ claims.md đã duyệt (G4), writer viết, kiểm citation và con số bằng script, skeptic soát claim với bằng chứng, explain-back trước khi nộp (G5). Dùng khi người dùng muốn "viết báo cáo", "viết paper", "write up results", "báo cáo môn học", "draft the paper".
argument-hint: "<course-report|paper-draft|blog> [slug]"
---

# /lab:write-up

Bạn là Lead. Claim trước, prose sau. `writer` là người viết duy nhất.

Luật luôn đúng:
- Không prose nào trước khi người dùng duyệt `claims.md` (G4).
- Claim thiếu bằng chứng thì quay lại thí nghiệm, không viết lấp.
- Số liệu chỉ từ `tables/` do script sinh; citation phải resolve; không placeholder; review tối đa 2 vòng.

Đầu vào: $ARGUMENTS

## Bước

1. Đọc `research/PROJECT.md` (ngôn ngữ, ràng buộc về dùng AI), ${CLAUDE_PLUGIN_ROOT}/playbooks/writing.md, các `FINDINGS.md`, survey và card liên quan. Đặt `<slug>`; thư mục `research/reports/<slug>/`.
2. Cùng người dùng viết `claims.md` từ ${CLAUDE_PLUGIN_ROOT}/templates/claims.md: 1–3 claim, mỗi claim trỏ tới `[run:...]`, `tables/...`, `figures/...` hoặc `[@paper-id, vị trí]`, trạng thái `supported|partial|unsupported`, giới hạn; `audience`; `idea:` nếu báo cáo đi ra từ một idea card. Bạn kiểm từng con trỏ có tồn tại.
3. **G4.** Người dùng duyệt `claims.md` → đặt `status: approved`, ghi `research/decisions.md`. Claim `unsupported` mà người dùng vẫn muốn giữ: đề nghị chạy thêm thí nghiệm, hoặc hạ thành "câu hỏi mở".
4. Gọi `lab:writer` loại việc `report`: `inputs: claims.md` và mọi file nó trỏ tới; `output: research/reports/<slug>/draft.md`; kiểu báo cáo theo đối số; ngôn ngữ theo `PROJECT.md`.
5. Chạy:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/cite_check.py research/reports/<slug>/draft.md`
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py research/reports/<slug>/draft.md`
   Có lỗi: gửi lại `lab:writer` kèm output script. Mạng bị chặn: chạy `cite_check.py --offline` và báo người dùng phần online chưa kiểm.
6. Gọi `lab:skeptic` loại `draft` với đường dẫn `draft.md` và `claims.md`. Lỗi chặn: `lab:writer` sửa, rồi skeptic vòng 2. Sau vòng 2 còn bất đồng: đưa người dùng quyết.
7. Khi sạch: `lab:writer` tạo `final.md` (bản sạch của draft). Chạy lại hai script trên `final.md`.
8. **G5. Explain-back.** Hỏi người dùng 3 câu về chính báo cáo: vì sao claim chính đứng vững; điều gì sẽ bác bỏ nó; giới hạn lớn nhất. Phần nào người dùng không giải thích được: đánh dấu và đề nghị họ tự viết lại phần đó. Nhắc ghi rõ mức hỗ trợ của AI theo quy định môn học hoặc venue.
9. Ghi `research/decisions.md` (G5) và `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source write-up "<slug>: <trạng thái>"`.
