# Ideation playbook

Khung: generate → reflect → rank → evolve → meta-review (AI co-scientist), với người dùng là người xếp hạng.

## Hạt giống đa dạng

Sinh thêm mẫu từ cùng một prompt chỉ cho ra bản trùng (Si et al. 2024: rất ít ý tưởng không trùng nhau trong hàng nghìn mẫu). Đa dạng hoá *đầu vào*:

- `research/surveys/*/gaps.md` và mục câu hỏi mở của survey;
- bất thường và "vì sao không chạy" trong `experiments/*/FINDINGS.md` cũ;
- `research/ideas/backlog.md` (Hamming: 10–20 bài toán quan trọng);
- mục "Lợi thế riêng" trong `PROJECT.md`;
- một ràng buộc cụ thể, ví dụ "pilot chạy được trong một giờ trên máy hiện có";
- "replicate rồi extend" một paper đã có card: điểm khởi đầu hợp lệ cho người mới (Nanda, Silver).

Mỗi idea card ghi `seeds:` để biết nó sinh từ đâu.

## Chất lượng một idea card

- Goal-driven hơn idea-driven (Schulman): nói rõ mục tiêu nó phục vụ.
- "10% hay 10×?" Cải tiến càng nhỏ, phương pháp càng phải đơn giản.
- Có `prediction` đo được và phép thử rẻ nhất ≤ 1 ngày.
- Có kill criteria.
- Nhãn `safe` hoặc `ambitious`; một lô nên có cả hai.

## Novelty protocol (skeptic)

1. Giả định đã có người làm.
2. Tìm prior work gần nhất: ít nhất 3 query khác nhau (thuật ngữ của ý tưởng, thuật ngữ của lĩnh vực lân cận, mô tả bằng lời thường).
3. Nếu ánh xạ phương pháp gần như một-một, nói thẳng và ghi ánh xạ.
4. Ghi trong review một dòng `closest_prior_work[<idea-id>]: ...` cho mỗi card, kể cả khi kết luận là "không tìm thấy gì gần" (ghi query đã dùng). Lead chép dòng đó vào frontmatter `closest_prior_work` của card; `lint_report.py` dựa vào trường này.
5. Nêu lý do mạnh nhất khiến ý tưởng thất bại.

Gupta & Pruthi: một phần đáng kể tài liệu nghiên cứu do LLM sinh bị chuyên gia xác định là vay mượn không ghi nguồn, và công cụ tự động không bắt được. Người dùng chịu trách nhiệm mọi tuyên bố novelty.

## Xếp hạng

LLM xếp hạng ý tưởng chỉ khớp người ở mức gần ngẫu nhiên. Agent có thể đưa thứ tự gợi ý kèm lý do, nhưng **G2 do người dùng chấm 1–10** (`user_score`) trước khi xem điểm gợi ý nếu được.

Phép thử nhanh (Olah): nếu nhóm khác công bố đúng ý này, bạn có háo hức đọc không?

## Sau G2

Ý tưởng được chọn đi thẳng sang pilot tối đa một ngày (`/lab:design-exp`), vì ý tưởng hay trên giấy thường tụt điểm sau khi thực thi (Si et al. 2025). Ý tưởng bị loại vẫn giữ card với `status: killed` và lý do.
