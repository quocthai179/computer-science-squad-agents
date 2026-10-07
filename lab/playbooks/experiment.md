# Experiment playbook

Neural net *hỏng trong im lặng* (Karpathy). Playbook này tồn tại để lỗi lộ ra sớm và rẻ.

## Vòng thí nghiệm

```text
PLAN.md → G3 (người dùng duyệt) → smoke → baseline + ceiling → runs có kiểm soát
       → analyst: FINDINGS.md → skeptic → người dùng quyết → (thêm run | đổi giả thuyết | đóng)
```

## Thiết kế (`/lab:design-exp`)

1. **Một câu hỏi.** Thí nghiệm trả lời đúng một câu hỏi. Hai câu hỏi thì hai PLAN.
2. **Dự đoán trước.** `prediction` có hướng và độ lớn ("B hơn A ≥ 2 điểm"), `confidence` 0–100. Ghi vào calibration.
3. **Kill criteria trước.** "Nếu sau N run / H giờ mà ... thì dừng."
4. **Baseline và ceiling** (Steinhardt): baseline đơn giản nhất không phụ thuộc input, baseline chuẩn theo paper gần nhất, ceiling là bản "ăn gian" cho biết trần. Khoảng giữa baseline và ceiling là phần thưởng khả dĩ.
5. **Ba nhóm hyperparameter** (Tuning Playbook): scientific (đang nghiên cứu), nuisance (phải tune để so sánh công bằng: tune *cả* baseline), fixed.
6. **Seed.** So sánh chính cần ≥ 3 seed (Bouthillier et al.). Một seed chỉ dùng cho smoke và exploration.
7. **File được bảo vệ.** Liệt kê code eval, code metric, test data trong `protected_files`. Hook chặn sửa khi plan `approved`/`running`.
8. **Thứ tự de-risk** theo information rate: bước dễ hỏng nhất và rẻ nhất đi trước.
9. **Phác kết quả trước** (Silver): bảng và hình mong đợi.
10. **Ngân sách**: `budget_minutes_per_run`, `budget_total_hours`, `max_runs` theo compute profile trong `PROJECT.md`.

## Leakage checklist (Kapoor & Narayanan)

- [ ] không có tách train/test rõ ràng
- [ ] tiền xử lý (normalize, impute, chọn feature, vocabulary) fit trên toàn bộ dữ liệu thay vì chỉ train
- [ ] chọn model, early stopping hoặc tune hyperparameter trên test set
- [ ] trùng lặp hoặc gần-trùng giữa train và test (dedup?)
- [ ] feature không hợp lệ: thông tin không có ở thời điểm dự đoán, proxy của nhãn
- [ ] tập test không đại diện cho phân phối mà claim nói tới
- [ ] phụ thuộc thời gian: train dùng dữ liệu tương lai so với test
- [ ] phụ thuộc nhóm: cùng người/bệnh nhân/tài liệu ở cả train và test

## Chạy (`/lab:run-exp`)

Mọi run đi qua `runwrap.py`:

```bash
python3 <plugin>/scripts/runwrap.py --exp <id> --name <variant> --tag <smoke|baseline|ceiling|main|ablation> --seed <n> [--config cfg.yaml] -- <lệnh train>
```

Script train báo metric bằng một trong hai cách:

- in dòng `LAB_METRIC val_acc=0.8312` (dòng cuối cùng của mỗi tên thắng);
- ghi JSON `{"val_acc": 0.8312}` vào file `$LAB_METRICS_FILE`.

Script nên đọc seed từ `$LAB_SEED`.

Thứ tự cứng:

1. **Smoke** (`--tag smoke`, tập con, vài phút): từng mục smoke checklist trong PLAN.md. runwrap từ chối run thật khi chưa có smoke `ok`.
2. **Baseline** và **ceiling**, đủ seed.
3. **Run chính**: mỗi lần đổi một thứ so với baseline.

Luật:

- Commit code trước run chính; runwrap cảnh báo khi working tree bẩn.
- Lỗi: đọc log, chẩn đoán, sửa *code*, chạy lại. Tối đa 3 lần cho cùng một lỗi; runwrap từ chối sau 3 run hỏng liên tiếp. Hết lượt thì halt-and-report kèm chẩn đoán.
- Không bao giờ "sửa" bằng cách đổi eval, metric, test data hay giảm độ khó bài toán.
- Không xoá run hỏng khỏi ledger. Run hỏng là dữ liệu.
- Hết ngân sách (`max_runs`, giờ) thì dừng và báo; chỉ người dùng nâng ngân sách.

## Phân tích (`/lab:analyze`)

1. `ledger.py table` và `stats.py summary` cho mọi variant; `stats.py compare` cho từng so sánh chính (ghép theo seed).
2. `ledger.py figure` cho hình chính.
3. FINDINGS.md bốn mục: dữ liệu cho thấy gì; *không* cho thấy gì; giải thích thay thế chưa bị loại; thí nghiệm kế tiếp nhiều thông tin nhất.
4. Đối chiếu prediction, resolve calibration.
5. Cảnh giác: CI chứa 0; n < 3; cherry-pick seed hoặc checkpoint; metric chính đổi giữa chừng; kết quả tốt bất thường (nghi leakage trước khi ăn mừng).

## "Thử X không chạy" (Steinhardt, Silver)

Kết quả âm gần như không có thông tin nếu không biết *vì sao*. Mỗi kết quả âm cần ít nhất một giả thuyết về nguyên nhân và một cách kiểm rẻ.
