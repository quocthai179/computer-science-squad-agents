---
exp_id: <exp-id>
question: <この実験が答える問い>
status: draft             # draft | approved | running | closed  （G3：approved にできるのはユーザーのみ）
idea: <idea-id または空>
hypothesis: <仮説>
prediction: <方向と大きさ。例：「B が A を正解率で 2 ポイント以上上回る」>
confidence: <0-100>
kill_criteria: <…が…の後に…なら中止>
primary_metric: <runwrap が記録する名前と完全に一致させる。例：val_acc>
metric_direction: max     # max | min
protected_files: []       # 評価、指標、テストデータ：status が approved/running の間は hook が編集を拒否
seeds: 3
budget_minutes_per_run: 30
budget_total_hours: 4
max_runs: 20
estimate_hours: <人間の作業時間の見積もり>
smoke_required: true
approved_at:
---

# <exp-id>：<問い>

## 評価プロトコル

<学習/検証/テストデータ、分割、主指標と副指標、その計算方法>

## ベースライン

- 最も単純なもの（入力に依存しない）：<例：多数派クラス、学習データの平均>
- 標準的なもの（最も近い論文のもの）：<...>

## 上限（ceiling）

<どの「ズル」版が上限を示すか：オラクル特徴、テストで学習、より大きなモデルなど>

## ハイパーパラメータ

| 種類 | パラメータ | 値 / 範囲 |
|---|---|---|
| scientific（研究対象） | | |
| nuisance（公平な比較のために調整） | | |
| fixed（固定） | | |

## スモークチェックリスト（Karpathy）

- [ ] 20 個のサンプルとラベルを自分の目で見る
- [ ] 最も単純なベースラインでエンドツーエンドの骨組みが動く
- [ ] 初期化時の loss が期待どおり（例：ln(クラス数)）
- [ ] 小さな 1 バッチを過学習できる
- [ ] 入力に依存しないベースラインが想定どおりの値を出す
- [ ] シードを固定すると 2 回とも同じ結果になる

## リスク低減の順序

> Steinhardt：単位時間あたりの情報量が最大のステップ（最も壊れやすく、最も安いもの）を先に行う。

1.
2.
3.

## 期待する結果

> 実行する前に、FINDINGS.md に載る表と図のスケッチを描く。

| variant | primary_metric（平均 ± CI、3 シード） |
|---|---|
| baseline | |
| method | |

## 脅威

- リーク（Kapoor & Narayanan）：
- ベースラインのチューニング不足：
- 指標が目的とずれている：
