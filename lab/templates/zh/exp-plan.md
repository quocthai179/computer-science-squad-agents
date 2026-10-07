---
exp_id: <exp-id>
question: <本实验要回答的问题>
status: draft             # draft | approved | running | closed  （G3：只有用户能改为 approved）
idea: <idea-id 或留空>
hypothesis: <假设>
prediction: <方向和幅度，例如“B 比 A 高 >= 2 个准确率点”>
confidence: <0-100>
kill_criteria: <如果……在……之后，则停止>
primary_metric: <与 runwrap 记录的名称完全一致，例如 val_acc>
metric_direction: max     # max | min
protected_files: []       # 评测、指标、测试数据：status 为 approved/running 时 hook 会阻止修改
seeds: 3
budget_minutes_per_run: 30
budget_total_hours: 4
max_runs: 20
estimate_hours: <你对人力时间的估计>
smoke_required: true
approved_at:
---

# <exp-id>：<问题>

## 评测协议

<训练/验证/测试数据、划分方式、主要和次要指标及其计算方法>

## 基线

- 最简单的（与输入无关）：<例如：多数类、训练集均值>
- 标准的（来自最接近的论文）：<...>

## 上限（ceiling）

<哪种“作弊”版本能给出上限：oracle 特征、在测试集上训练、更大的模型……>

## 超参数

| 类别 | 参数 | 取值 / 范围 |
|---|---|---|
| scientific（研究对象） | | |
| nuisance（为公平比较而调） | | |
| fixed（固定） | | |

## 冒烟检查清单（Karpathy）

- [ ] 亲眼查看 20 个样本及其标签
- [ ] 用最简单的基线跑通端到端骨架
- [ ] 初始化时的 loss 符合预期（例如 ln(类别数)）
- [ ] 能在一个小 batch 上过拟合
- [ ] 与输入无关的基线给出预期数值
- [ ] 固定种子两次结果一致

## 风险消除顺序

> Steinhardt：单位时间信息量最大的步骤——最容易失败且最便宜的——先做。

1.
2.
3.

## 预期结果

> 运行前先画出将出现在 FINDINGS.md 中的表格和图。

| variant | primary_metric（均值 ± CI，3 个种子） |
|---|---|
| baseline | |
| method | |

## 威胁

- 数据泄漏（Kapoor & Narayanan）：
- 基线调参不足：
- 指标与目标不一致：
