---
exp_id: <exp-id>
question: <the question this experiment answers>
status: draft             # draft | approved | running | closed  (G3: only the user moves it to approved)
idea: <idea-id or empty>
hypothesis: <hypothesis>
prediction: <direction and size, e.g. "B beats A by >= 2 accuracy points">
confidence: <0-100>
kill_criteria: <if ... after ... then stop>
primary_metric: <name exactly as runwrap records it, e.g. val_acc>
metric_direction: max     # max | min
protected_files: []       # eval, metric, test data: the hook blocks edits while status is approved/running
seeds: 3
budget_minutes_per_run: 30
budget_total_hours: 4
max_runs: 20
estimate_hours: <your estimate of the human time>
smoke_required: true
approved_at:
---

# <exp-id>: <question>

## Eval protocol

<train/val/test data, split, primary and secondary metrics, how they are computed>

## Baselines

- simplest (independent of the input): <e.g. majority class, mean of train>
- standard (from the closest paper): <...>

## Ceiling

<which "cheating" variant shows the upper bound: oracle features, train on test, a larger model...>

## Hyperparameters

| kind | parameter | value / range |
|---|---|---|
| scientific (being studied) | | |
| nuisance (tune for a fair comparison) | | |
| fixed | | |

## Smoke checklist (Karpathy)

- [ ] look at 20 samples and labels with your own eyes
- [ ] end-to-end skeleton runs with the simplest baseline
- [ ] loss at initialisation matches expectation (e.g. ln(number of classes))
- [ ] can overfit one small batch
- [ ] input-independent baseline gives the expected number
- [ ] a fixed seed gives the same result twice

## De-risking order

> Steinhardt: the step with the most information per unit time — the one most likely to fail and cheapest — goes first.

1.
2.
3.

## Expected results

> Sketch the table and figures that will appear in FINDINGS.md before running.

| variant | primary_metric (mean ± CI, 3 seeds) |
|---|---|
| baseline | |
| method | |

## Threats

- leakage (Kapoor & Narayanan):
- poorly tuned baseline:
- metric misaligned with the goal:
