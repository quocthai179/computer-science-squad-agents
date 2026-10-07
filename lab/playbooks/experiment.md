# Experiment playbook

Neural nets fail silently (Karpathy). This playbook exists so that failures surface early and cheaply.

## The loop

```text
PLAN.md → G3 (the user approves) → smoke → baseline + ceiling → controlled runs
       → analyst: FINDINGS.md → skeptic → the user decides → (more runs | change hypothesis | close)
```

## Design (`/lab:design-exp`)

1. **One question.** An experiment answers exactly one question. Two questions, two PLANs.
2. **Prediction first.** `prediction` has a direction and a size ("B beats A by ≥ 2 points") and a `confidence` 0–100. Log it in calibration.
3. **Kill criteria first.** "If after N runs / H hours ... then stop."
4. **Baseline and ceiling** (Steinhardt): the simplest input-independent baseline, the standard baseline from the closest paper, and a ceiling that "cheats" to show the upper bound. The gap between baseline and ceiling is the room for reward.
5. **Three groups of hyperparameters** (Tuning Playbook): scientific (being studied), nuisance (must be tuned for a fair comparison: tune the baseline *too*), fixed.
6. **Seeds.** A main comparison needs ≥ 3 seeds (Bouthillier et al.). One seed is for smoke and exploration only.
7. **Protected files.** List eval code, metric code and test data in `protected_files`. The hook blocks edits while the plan is `approved`/`running`.
8. **De-risking order** by information rate: the step most likely to fail and cheapest goes first.
9. **Sketch the result first** (Silver): the expected tables and figures.
10. **Budget**: `budget_minutes_per_run`, `budget_total_hours`, `max_runs` from the compute profile in `PROJECT.md`.

## Leakage checklist (Kapoor & Narayanan)

- [ ] no clear train/test split
- [ ] preprocessing (normalisation, imputation, feature selection, vocabulary) fitted on all the data instead of train only
- [ ] model selection, early stopping or hyperparameter tuning on the test set
- [ ] duplicates or near-duplicates between train and test (dedup?)
- [ ] illegitimate features: information unavailable at prediction time, proxies of the label
- [ ] test set not representative of the distribution the claim is about
- [ ] temporal dependence: train uses data from the future relative to test
- [ ] group dependence: the same person/patient/document in both train and test

## Running (`/lab:run-exp`)

Every run goes through `runwrap.py`:

```bash
python3 <plugin>/scripts/runwrap.py --exp <id> --name <variant> --tag <smoke|baseline|ceiling|main|ablation> --seed <n> [--config cfg.yaml] -- <train command>
```

The training script reports metrics in one of two ways:

- print a line `LAB_METRIC val_acc=0.8312` (the last line of each name wins);
- write JSON `{"val_acc": 0.8312}` to the file `$LAB_METRICS_FILE`.

The script should read its seed from `$LAB_SEED`.

Fixed order:

1. **Smoke** (`--tag smoke`, a subset, a few minutes): each item of the smoke checklist in PLAN.md. runwrap refuses real runs until an `ok` smoke run exists.
2. **Baseline** and **ceiling**, all seeds.
3. **Main runs**: change one thing at a time relative to the baseline.

Rules:

- Commit the code before main runs; runwrap warns when the working tree is dirty.
- Failure: read the log, diagnose, fix the *code*, rerun. At most 3 attempts for one failure; runwrap refuses after 3 failed runs in a row. Then halt and report with the diagnosis.
- Never "fix" by changing the eval, the metric, the test data or the difficulty of the problem.
- Never delete failed runs from the ledger. A failed run is data.
- Out of budget (`max_runs`, hours): stop and report; only the user raises the budget.

## Analysis (`/lab:analyze`)

1. `ledger.py table` and `stats.py summary` for every variant; `stats.py compare` for each main comparison (paired by seed).
2. `ledger.py figure` for the main figure.
3. FINDINGS.md has four parts: what the data shows; what it does *not* show; alternative explanations not yet ruled out; the most informative next experiment.
4. Compare with the prediction and resolve the calibration entry.
5. Watch for: a CI that contains 0; n < 3; cherry-picked seeds or checkpoints; a primary metric changed midway; an unusually good result (suspect leakage before celebrating).

## "Trying X did not work" (Steinhardt, Silver)

A negative result carries almost no information unless you know *why*. Every negative result needs at least one hypothesis about the cause and one cheap way to test it.
