# Review playbook (skeptic)

Mục tiêu là sự thật, không phải sự hài lòng của tác giả. Chạy phần ứng với loại artifact, cộng phần "Mọi artifact".

## Mọi artifact

- Nhận định nào không có con trỏ bằng chứng? → **lỗi chặn**.
- Con trỏ có đúng không: mở `[@paper-id]` card hoặc full text, mở `[run:...]` trong ledger, mở bảng. Chọn ít nhất 5 con trỏ để kiểm (hoặc tất cả nếu ít hơn).
- Với mỗi claim: quan sát này dễ xảy ra hơn dưới giả thuyết của tác giả, hay dưới một giải thích nhàm chán hơn?
- Placeholder, con số không có trong bảng nào (chạy `lint_report.py` nếu brief cho phép Bash; không thì kiểm tay).

## idea

- Novelty protocol (playbooks/ideation.md): giả định đã có người làm; ≥ 3 query; mỗi card một dòng `closest_prior_work[<idea-id>]: ...` trong review.
- Prediction đo được không? Phép thử rẻ nhất có thật sự ≤ 1 ngày không?
- Lý do mạnh nhất khiến ý tưởng thất bại.

## plan

- Leakage checklist (playbooks/experiment.md).
- Baseline có được tune ngang bằng không (nuisance hyperparameter cho cả baseline)?
- Có baseline không phụ thuộc input và ceiling không?
- Metric chính đo đúng thứ claim nói tới không?
- Đủ seed? Ngân sách có đủ cho đủ seed của mọi variant không?
- `protected_files` có liệt kê code eval và test data không?
- Kill criteria có thật sự kích hoạt được không?

## findings

- Mỗi con số trong FINDINGS.md có trong `tables/` và khớp `runs.jsonl` không?
- So sánh chính có ≥ 3 seed, ghép theo seed? CI có chứa 0 không?
- Cherry-pick: chọn seed tốt nhất, checkpoint tốt nhất trên test, chỉ báo một phần variant?
- Run hỏng/timeout có bị bỏ qua mà không nói không?
- Metric chính có đổi so với PLAN.md không? Eval có đổi giữa các run không (config_hash, git_sha)?
- Kết quả tốt bất thường → nghi leakage trước.
- "Không cho thấy gì" có trung thực không?

## draft

- Bốn bệnh của paper ML (Lipton & Steinhardt): giải thích lẫn suy đoán; không tách nguồn gốc cải thiện; toán để gây ấn tượng; lạm dụng thuật ngữ.
- Mỗi claim trong `claims.md` có xuất hiện đúng mức (không phóng đại từ `partial` thành khẳng định)?
- Limitations có thật không, hay chỉ cho có?
- Reproducibility checklist (playbooks/writing.md).
- Từ ngữ novelty khi chưa có prior work.

## survey

- Nhận định nào thiếu neo, hoặc neo vào paper chưa có card (chỉ đọc lượt 1)?
- Nguồn yếu: blog thay cho paper gốc; preprint được trình bày như kết quả đã xác nhận.
- Góc bị bỏ sót: phản biện, kết quả âm, benchmark khác, 12 tháng gần nhất.
- Mục "điểm mâu thuẫn" có thật sự đối chiếu hai nguồn không?

## paper-card

- Trích dẫn có đúng nguyên văn và đúng vị trí không (mở full text kiểm 2–3 chỗ)?
- Bốn câu hỏi hoài nghi có được trả lời bằng bằng chứng từ paper không?

## Giới hạn của chính skeptic

Cùng họ model với tác giả có thể chung điểm mù. Bù lại bằng rubric cụ thể và kiểm con trỏ thật. Không có lỗi chặn thì nói là không có, và liệt kê đã kiểm những gì. Không khen cho có.
