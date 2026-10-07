---
exp_id: e001-ls
question: Does label smoothing help a small, noisy training set?
status: draft
hypothesis: smoothing the targets reduces overfitting to the 15% flipped labels
prediction: label smoothing 0.2 beats baseline test_acc by >= 0.5 points
confidence: 55
kill_criteria: stop if the 95% CI of the paired difference includes 0 after 3 seeds
primary_metric: test_acc
protected_files: [eval.py]
seeds: 3
budget_minutes_per_run: 5
max_runs: 10
budget_total_hours: 1
---
# e001-ls
