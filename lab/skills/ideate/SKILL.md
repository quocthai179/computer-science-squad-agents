---
name: ideate
description: Tìm và sàng lọc ý tưởng nghiên cứu: ideator sinh idea card Heilmeier từ hạt giống đa dạng (gaps, bất thường, backlog, lợi thế riêng), skeptic chạy novelty protocol tìm prior work, người dùng chấm và chọn (G2). Dùng khi người dùng muốn "tìm ý tưởng", "brainstorm hướng nghiên cứu", "ideate", "research ideas", "đề tài nên làm gì".
argument-hint: "[trọng tâm]"
---

# /lab:ideate

Bạn là Lead. Khung: generate → reflect → evolve → người dùng xếp hạng.

Luật luôn đúng:
- Người dùng chấm và chọn (G2). Xếp hạng của agent chỉ để tham khảo; LLM xếp hạng ý tưởng gần mức ngẫu nhiên.
- Đa dạng hoá **đầu vào**, không sinh thêm mẫu từ cùng một prompt.
- Không ai trong đội tuyên bố novelty. Người dùng chịu trách nhiệm mọi tuyên bố đó.

Trọng tâm: $ARGUMENTS

## Bước

1. Đọc `research/PROJECT.md` (mục "Lợi thế riêng", ràng buộc, compute), `research/lessons/LESSONS.md`, ${CLAUDE_PLUGIN_ROOT}/playbooks/ideation.md. Chưa có workspace: bảo người dùng chạy `/lab:setup` rồi dừng.
2. Gom hạt giống, ghi danh sách đường dẫn: `research/surveys/*/gaps.md`, `research/experiments/*/FINDINGS.md` (mục bất thường, "vì sao không chạy"), `research/ideas/backlog.md`, paper card có mục "Mở khoá bài toán". Thêm một ràng buộc cụ thể, ví dụ "pilot chạy được trong một giờ trên máy hiện có". Hạt giống quá ít (< 3 nguồn): nói với người dùng và đề nghị `/lab:survey` trước, hoặc hỏi họ 2–3 bài toán họ quan tâm.
3. Gọi `lab:ideator` chế độ `generate`: 6–10 card trong `research/ideas/cards/`, template `${CLAUDE_PLUGIN_ROOT}/templates/idea-card.md`.
4. Gọi `lab:skeptic` loại `idea` với đường dẫn các card mới (một skeptic cho cả lô, `budget: 40 tool call`). Review vào `research/reviews/ideas-<YYYY-MM-DD>.md`.
5. Với mỗi dòng `closest_prior_work[<id>]: ...` trong review: chép vào frontmatter `closest_prior_work` của card tương ứng và mục "Phản biện". Card không có dòng đó thì để trống.
6. Gọi `lab:ideator` chế độ `evolve` với đường dẫn review: một vòng gộp, đơn giản hoá, loại bỏ.
7. **G2.** Trình người dùng bảng: id, tên, nhãn safe/ambitious, prediction, phép thử rẻ nhất, prior work gần nhất, lý do thất bại mạnh nhất. **Không** hiện điểm gợi ý của agent trước khi người dùng chấm. Mời người dùng chấm từng card 1–10 và chọn 1–2 card. Phép thử nhanh: "Nếu nhóm khác công bố đúng ý này, bạn có háo hức đọc không?"
8. Ghi `user_score` vào từng card; card được chọn `status: selected`; card bị loại `status: parked` hoặc `killed` kèm lý do. Ghi `research/decisions.md`.
9. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source ideate "<số card>, chọn <ids>"`. Gợi ý: `/lab:design-exp <idea-id>` cho một pilot tối đa một ngày.
