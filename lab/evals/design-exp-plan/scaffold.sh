#!/usr/bin/env bash
set -euo pipefail
R=research
mkdir -p $R/experiments $R/ideas/cards $R/reviews $R/papers/cards $R/notebook $R/lessons
: > $R/papers/index.jsonl
: > $R/lessons/calibration.jsonl
printf '# Lessons\n' > $R/lessons/LESSONS.md
printf '# Decisions\n' > $R/decisions.md
cat > $R/PROJECT.md <<'X'
---
title: Regularisation for small-data text classification
stage: understanding
north_star: find which cheap regularisers help fine-tuning on < 5k examples
language: en
compute_gpu: 1x RTX 3060 12GB
compute_max_minutes_per_run: 20
compute_hours_per_week: 6
---
# Regularisation for small-data text classification
Code: train.py (fine-tunes a small transformer, prints test accuracy), eval.py (computes accuracy), data/tinysent/{train,test}.jsonl.
X
cat > $R/ideas/cards/i001-label-smoothing.md <<'X'
---
id: i001-label-smoothing
title: Label smoothing for 1k-example sentiment fine-tuning
label: safe
status: selected
prediction: label smoothing 0.1 improves test accuracy by >= 1 point
confidence: 60
closest_prior_work: "[@1512.00567] introduced label smoothing for ImageNet; small-data text not studied there"
user_score: 7
---
# i001-label-smoothing
Cheapest test: 3 seeds x (baseline, ls=0.1) on TinySent, 20 min per run.
X
