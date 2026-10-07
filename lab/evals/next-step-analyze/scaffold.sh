#!/usr/bin/env bash
set -euo pipefail
R=research
mkdir -p $R/experiments/e001-ls $R/ideas/cards $R/surveys $R/reports $R/lessons/retros $R/notebook
cat > $R/PROJECT.md <<'X'
---
title: Regularisation for small-data text classification
stage: understanding
north_star: find which cheap regularisers help fine-tuning on < 5k examples
---
# Regularisation for small-data text classification
X
printf '# Lessons\n' > $R/lessons/LESSONS.md
: > $R/lessons/calibration.jsonl
cat > $R/experiments/e001-ls/PLAN.md <<'X'
---
exp_id: e001-ls
status: running
prediction: label smoothing 0.1 beats baseline by >= 1 point
kill_criteria: stop if no gain after 6 main runs
primary_metric: test_acc
seeds: 3
max_runs: 12
---
# e001-ls
X
cat > $R/experiments/e001-ls/runs.jsonl <<'X'
{"run_id": "e001-ls-r001", "name": "smoke", "tag": "smoke", "seed": 0, "status": "ok", "metrics": {"test_acc": 0.55}, "started_at": "2026-10-01T10:00:00", "duration_s": 60}
{"run_id": "e001-ls-r002", "name": "baseline", "tag": "baseline", "seed": 0, "status": "ok", "metrics": {"test_acc": 0.812}, "started_at": "2026-10-01T11:00:00", "duration_s": 1100}
{"run_id": "e001-ls-r003", "name": "baseline", "tag": "baseline", "seed": 1, "status": "ok", "metrics": {"test_acc": 0.806}, "started_at": "2026-10-01T11:20:00", "duration_s": 1100}
{"run_id": "e001-ls-r004", "name": "baseline", "tag": "baseline", "seed": 2, "status": "ok", "metrics": {"test_acc": 0.815}, "started_at": "2026-10-01T11:40:00", "duration_s": 1100}
{"run_id": "e001-ls-r005", "name": "ls0.1", "tag": "main", "seed": 0, "status": "ok", "metrics": {"test_acc": 0.824}, "started_at": "2026-10-01T12:00:00", "duration_s": 1100}
{"run_id": "e001-ls-r006", "name": "ls0.1", "tag": "main", "seed": 1, "status": "ok", "metrics": {"test_acc": 0.819}, "started_at": "2026-10-01T12:20:00", "duration_s": 1100}
{"run_id": "e001-ls-r007", "name": "ls0.1", "tag": "main", "seed": 2, "status": "ok", "metrics": {"test_acc": 0.828}, "started_at": "2026-10-01T12:40:00", "duration_s": 1100}
X
cat > $R/ideas/cards/i002-mixup.md <<'X'
---
id: i002-mixup
title: Token-level mixup
status: proposed
---
# i002-mixup
X
