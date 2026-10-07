# Writing playbook

## Claim trước, prose sau

1. `claims.md` có trước mọi prose (Peyton Jones, Nanda). Một bài, một ý chính; 1–3 claim cụ thể.
2. Mỗi claim trỏ tới bằng chứng: `[run:<exp>-r003]`, `tables/<file>`, `figures/<file>`, `[@paper-id, §n]`.
3. Trạng thái: `supported` / `partial` / `unsupported`. `unsupported` không được viết thành prose khẳng định.
4. Limitations là mục bắt buộc.
5. G4: người dùng duyệt `claims.md` trước khi `writer` viết.

## Viết (writer)

- Nén thành bullet trước, viết prose sau.
- Người đọc lên trước: ai đọc, họ đã biết gì (trường `audience`).
- Contributions dẫn dắt bài; related work để sau.
- Số liệu: copy từ `tables/` do script sinh, kèm tham chiếu bảng; không tự tính, không làm tròn khác bảng.
- Citation dạng `[@paper-id, vị trí]`; id phải có trong `papers/index.jsonl` hoặc `papers/refs.bib`.
- Không viết "novel", "đầu tiên", "SOTA", "mới lạ" khi idea card chưa có `closest_prior_work`.
- Không placeholder trong bản cuối.
- Survey là sản phẩm *chưng cất* (Olah & Carter, Research Debt): taxonomy, so sánh, mâu thuẫn, khoảng trống — không phải danh sách tóm tắt từng paper.

## Báo cáo môn học tiếng Việt

Theo style của skill `topic-research-report` nếu có: mở bằng BLUF (kết luận trước), cấu trúc Pyramid, văn xuôi cho phần giải thích, bảng cho so sánh. Giữ thuật ngữ tiếng Anh. Sơ đồ dùng Mermaid nếu skill `mermaid-diagrams` có sẵn.

## Kiểm trước khi review

```bash
python3 <plugin>/scripts/cite_check.py <file>
python3 <plugin>/scripts/lint_report.py <file>
```

Cả hai phải sạch trước khi gọi `skeptic` vòng cuối.

## Reproducibility checklist (Pineau, rút gọn)

- [ ] mô tả rõ model, thuật toán, giả định
- [ ] dữ liệu: nguồn, split, tiền xử lý, số mẫu
- [ ] hyperparameter: phạm vi đã thử, cách chọn, giá trị cuối
- [ ] số seed, cách báo cáo variance (mean ± CI)
- [ ] compute: phần cứng, thời gian
- [ ] code và config truy được về git SHA trong ledger
- [ ] metric định nghĩa rõ; eval protocol không đổi giữa các variant

## Explain-back (G5)

Trước khi nộp, Lead hỏi người dùng 3 câu về chính báo cáo (vì sao claim C1 đứng vững, điều gì sẽ bác bỏ nó, giới hạn lớn nhất). Người dùng không giải thích được phần nào thì phần đó chưa sẵn sàng.

Ghi rõ mức hỗ trợ của AI theo quy định môn học hoặc venue.
