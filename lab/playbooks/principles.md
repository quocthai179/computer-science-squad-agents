# Principles

Mười ba nguyên tắc thiết kế của Research Squad. Mọi skill và agent tuân theo chúng; khi hai luật xung đột, luật đứng trước thắng.

1. **Người giữ taste, agent giữ thông lượng.** Năm gate G1–G5 do người dùng quyết. Agent không tự chọn bài toán và không tự tuyên bố novelty.
2. **Mọi con số truy về một run, mọi nhận định truy về một nguồn.** Bảng và hình do script sinh từ ledger. Citation phải resolve. Trích dẫn kèm vị trí trong paper: `[@paper-id, §3.2]`.
3. **Dự đoán trước, chạy sau.** `PLAN.md` thiếu `prediction` và `kill_criteria` thì `runwrap.py` từ chối chạy.
4. **Việc nhiều thông tin nhất trên một đơn vị thời gian đi trước.** De-risk rồi mới execute.
5. **Baseline và ceiling trước phương pháp. Mỗi lần đổi một thứ.**
6. **Người phản biện không thấy lập luận của tác giả.** `skeptic` chỉ nhận đường dẫn artifact, tối đa hai vòng.
7. **File là bộ nhớ và là giao thức bàn giao.** Subagent ghi artifact, trả về `RECEIPT` ngắn kèm đường dẫn.
8. **Đọc song song, viết tuần tự.** Mỗi artifact chỉ một người viết.
9. **Mọi vòng lặp có trần:** số scout, số tool call, số vòng review, số lần sửa lỗi, phút compute.
10. **Luật phải luôn đúng thì giao cho script hoặc hook, không giao cho prompt.**
11. **Viết sớm; claim dẫn dắt thí nghiệm.**
12. **Kinh nghiệm phải cộng dồn:** lesson có bằng chứng → `LESSONS.md` → playbook → prompt của agent.
13. **Tăng tốc phần cơ học, không thay phần hiểu.** Người dùng phải giải thích lại được mọi thứ mang tên mình.

## Gate

| Gate | Khi nào | Người dùng quyết | Ghi ở đâu |
|---|---|---|---|
| G1 | sau `/lab:setup` | bài toán và tiêu chí thành công | `PROJECT.md`, `decisions.md` |
| G2 | sau `/lab:ideate` | ý tưởng nào đáng một pilot | idea card `status: selected`, `user_score` |
| G3 | trước `/lab:run-exp` | duyệt `PLAN.md` = duyệt tiêu compute | `PLAN.md` `status: approved`, `approved_at` |
| G4 | trước khi viết prose | duyệt `claims.md` | `claims.md` `status: approved` |
| G5 | trước khi nộp hoặc chia sẻ | đọc bản cuối và explain-back | `decisions.md` |

Chỉ main session (Lead) dừng ở gate, vì subagent không hỏi được người dùng. Lead không bao giờ tự chuyển một trạng thái gate thay người dùng: phải có câu trả lời rõ ràng của người dùng trong hội thoại.

## Stage (Nanda)

| stage | north star | dấu hiệu đang kẹt |
|---|---|---|
| ideation | chọn bài toán đáng làm | đọc mãi không chọn |
| exploration | thu thông tin, có nhiều bit mới mỗi giờ | tưởng mình đang "chứng minh" khi chưa có giả thuyết |
| understanding | thuyết phục chính mình về một giả thuyết | chạy thêm run mà không có dự đoán |
| distillation | nén thành sự thật chặt chẽ và truyền đạt | viết mà claim chưa có bằng chứng |

## Định tuyến model và ngân sách

| mức việc | chạy bằng | ví dụ |
|---|---|---|
| cơ học | script | parse metadata, resolve citation, tổng hợp log |
| chuẩn | `sonnet` | `scout`, `reader`, `experimenter`, `analyst` |
| phán đoán | `opus` hoặc model của main session | `skeptic`, `ideator`, `writer`, debug khó |

Khi `RECEIPT` có `escalate: model`, Lead gọi lại agent đó với tham số `model: opus`.

Ngân sách khởi điểm (chỉnh theo log):

- câu hỏi sự kiện đơn lẻ: Lead tự trả lời, không gọi đội;
- chủ đề hẹp: 2–3 `scout`, mỗi scout tối đa 12 tool call;
- survey rộng: 4–5 `scout`, mỗi scout tối đa 15 tool call; đọc sâu 5–8 paper;
- sửa lỗi một run: tối đa 3 lần; review: tối đa 2 vòng; survey: tối đa 1 vòng tìm bổ sung.

## Đường lui

Không gọi được subagent (ví dụ ở bề mặt không hỗ trợ): Lead tự làm tuần tự theo cùng playbook, vẫn ghi cùng artifact, và nói rõ với người dùng rằng phản biện không còn độc lập.
