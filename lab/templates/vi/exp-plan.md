---
exp_id: <exp-id>
question: <câu hỏi thí nghiệm trả lời>
status: draft             # draft | approved | running | closed  (G3: chỉ người dùng chuyển sang approved)
idea: <idea-id hoặc trống>
hypothesis: <giả thuyết>
prediction: <hướng và độ lớn, ví dụ "B hơn A ≥ 2 điểm accuracy">
confidence: <0-100>
kill_criteria: <nếu ... sau ... thì dừng>
primary_metric: <tên metric đúng như runwrap ghi, ví dụ val_acc>
metric_direction: max     # max | min
protected_files: []       # eval, metric, test data: hook chặn sửa khi status approved/running
seeds: 3
budget_minutes_per_run: 30
budget_total_hours: 4
max_runs: 20
estimate_hours: <ước lượng thời gian người làm>
smoke_required: true
approved_at:
---

# <exp-id>: <câu hỏi>

## Giao thức eval

<dữ liệu train/val/test, split, metric chính và metric phụ, cách tính>

## Baseline

- đơn giản nhất (không phụ thuộc input): <ví dụ: dự đoán lớp đa số, mean của train>
- chuẩn (theo paper gần nhất): <...>

## Ceiling

<bản "ăn gian" nào cho biết trần: oracle feature, train trên test, model lớn hơn...>

## Hyperparameter

| loại | tham số | giá trị / phạm vi |
|---|---|---|
| scientific (đang nghiên cứu) | | |
| nuisance (tune để so sánh công bằng) | | |
| fixed | | |

## Smoke checklist (Karpathy)

- [ ] nhìn tận mắt 20 mẫu dữ liệu và nhãn
- [ ] skeleton end-to-end chạy với baseline đơn giản nhất
- [ ] loss lúc khởi tạo đúng kỳ vọng (ví dụ ln(số lớp))
- [ ] overfit được một batch nhỏ
- [ ] baseline không phụ thuộc input cho đúng con số dự kiến
- [ ] seed cố định cho cùng kết quả hai lần

## Thứ tự de-risk

> Steinhardt: bước nhiều thông tin nhất trên một đơn vị thời gian, dễ hỏng nhất, rẻ nhất làm trước.

1.
2.
3.

## Kết quả mong đợi

> Phác bảng và hình sẽ xuất hiện trong FINDINGS.md trước khi chạy.

| variant | primary_metric (mean ± CI, 3 seeds) |
|---|---|
| baseline | |
| method | |

## Mối đe doạ

- leakage (Kapoor & Narayanan):
- baseline tune kém:
- metric lệch mục tiêu:
