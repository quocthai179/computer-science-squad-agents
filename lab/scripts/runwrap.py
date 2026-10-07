#!/usr/bin/env python3
"""Run one experiment command and record it in experiments/<id>/runs.jsonl.

usage: runwrap.py --exp ID --name VARIANT [--tag smoke|baseline|ceiling|main|ablation]
                  [--seed N] [--config FILE] [--timeout-min M] [--note TEXT]
                  [--after-review] -- COMMAND [ARGS ...]

Refuses to run (exit 3) when:
  - PLAN.md has no `prediction` or no `kill_criteria`           (predict before running)
  - PLAN.md `status` is not approved/running                    (gate G3)
  - a non-smoke run is requested before any successful smoke run
  - the PLAN.md `max_runs` budget is used up
  - the last 3 runs all failed (fix limit) -- pass --after-review only after the
    user has read the diagnosis and said to continue

The command receives LAB_EXP, LAB_RUN_ID, LAB_RUN_DIR, LAB_SEED and LAB_METRICS_FILE.
It reports metrics either by printing lines `LAB_METRIC name=value` or by writing a
JSON object to $LAB_METRICS_FILE. The JSON file wins when both give the same name.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from _lab import append_jsonl, exp_dir, find_root, is_blank, now_iso, read_frontmatter, read_jsonl

METRIC_RE = re.compile(r"^\s*LAB_METRIC\s+([\w./-]+)\s*=\s*(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?|nan|inf|-inf)\s*$")
TAGS = ("smoke", "baseline", "ceiling", "main", "ablation")
REFUSE = 3


def refuse(msg: str) -> None:
    print(f"runwrap: REFUSED: {msg}", file=sys.stderr)
    sys.exit(REFUSE)


def git_info(cwd: Path) -> tuple[str | None, bool | None]:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None
    st = subprocess.run(["git", "status", "--porcelain", "--", ".", ":(exclude)research"],
                        cwd=cwd, capture_output=True, text=True).stdout
    return sha, bool(st.strip())


def next_run_id(exp: str, runs: list[dict]) -> str:
    nums = [int(m.group(1)) for r in runs if (m := re.search(r"-r(\d+)$", str(r.get("run_id", ""))))]
    return f"{exp}-r{(max(nums) + 1) if nums else 1:03d}"


def check_gates(plan: dict, runs: list[dict], tag: str, after_review: bool) -> None:
    if not plan:
        refuse("PLAN.md missing or has no frontmatter. Write it with /lab:design-exp first.")
    for key in ("prediction", "kill_criteria"):
        if is_blank(plan.get(key)):
            refuse(f"PLAN.md has no `{key}`. Write it down before running anything.")
    status = str(plan.get("status", "")).lower()
    if status not in ("approved", "running"):
        refuse(f"PLAN.md status is '{status or 'missing'}'. Gate G3: the user must approve the plan first.")
    if tag != "smoke" and plan.get("smoke_required", True) is not False:
        if not any(r.get("tag") == "smoke" and r.get("status") == "ok" for r in runs):
            refuse("no successful smoke run yet. Run the smoke checklist first with --tag smoke.")
    max_runs = plan.get("max_runs")
    if tag != "smoke" and isinstance(max_runs, int):
        used = sum(1 for r in runs if r.get("tag") != "smoke")
        if used >= max_runs:
            refuse(f"run budget used up ({used}/{max_runs}). Ask the user before raising max_runs in PLAN.md.")
    tail = runs[-3:]
    if len(tail) == 3 and all(r.get("status") != "ok" for r in tail) and not after_review:
        refuse("the last 3 runs failed. Stop, write the diagnosis, and report to the user (fix limit).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    ap.add_argument("--exp", required=True)
    ap.add_argument("--name", required=True, help="variant label, e.g. baseline, ceiling, method-lr3e-4")
    ap.add_argument("--tag", default="main", choices=TAGS)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--config")
    ap.add_argument("--timeout-min", type=float)
    ap.add_argument("--note", default="")
    ap.add_argument("--after-review", action="store_true")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    cmd = args.cmd[1:] if args.cmd[:1] == ["--"] else args.cmd
    if not cmd:
        ap.error("missing command after --")

    root = find_root(args.root)
    d = exp_dir(root, args.exp)
    ledger = d / "runs.jsonl"
    runs = read_jsonl(ledger)
    plan = read_frontmatter(d / "PLAN.md")
    check_gates(plan, runs, args.tag, args.after_review)

    run_id = next_run_id(args.exp, runs)
    run_dir = d / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = run_dir / "metrics.json"

    config_hash = None
    if args.config:
        cfg = Path(args.config)
        if not cfg.is_file():
            refuse(f"config not found: {cfg}")
        config_hash = hashlib.sha256(cfg.read_bytes()).hexdigest()[:16]
        shutil.copyfile(cfg, run_dir / ("config" + cfg.suffix))

    timeout_min = args.timeout_min or plan.get("budget_minutes_per_run")
    timeout_s = float(timeout_min) * 60 if isinstance(timeout_min, (int, float)) else None
    if args.tag == "smoke" and timeout_s:
        timeout_s = min(timeout_s, 15 * 60)

    sha, dirty = git_info(Path.cwd())
    env = dict(os.environ, LAB_EXP=args.exp, LAB_RUN_ID=run_id, LAB_RUN_DIR=str(run_dir),
               LAB_METRICS_FILE=str(metrics_file), PYTHONUNBUFFERED="1")
    if args.seed is not None:
        env["LAB_SEED"] = str(args.seed)

    print(f"runwrap: {run_id} [{args.tag}] {args.name} seed={args.seed} timeout={timeout_s and round(timeout_s)}s",
          file=sys.stderr)
    started, t0 = now_iso(), time.time()
    metrics: dict[str, float] = {}
    timed_out = threading.Event()
    with (run_dir / "log.txt").open("w", encoding="utf-8") as log:
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                                    text=True, errors="replace", bufsize=1)
        except FileNotFoundError as e:
            proc = None
            log.write(f"runwrap: cannot start command: {e}\n")
            exit_code = 127
        if proc is not None:
            timer = None
            if timeout_s:
                def kill() -> None:
                    timed_out.set()
                    proc.kill()
                timer = threading.Timer(timeout_s, kill)
                timer.start()
            assert proc.stdout is not None
            for line in proc.stdout:
                sys.stdout.write(line)
                log.write(line)
                m = METRIC_RE.match(line)
                if m:
                    metrics[m.group(1)] = float(m.group(2))
            exit_code = proc.wait()
            if timer:
                timer.cancel()

    if metrics_file.exists():
        try:
            data = json.loads(metrics_file.read_text(encoding="utf-8"))
            metrics.update({k: float(v) for k, v in data.items() if isinstance(v, (int, float))})
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            print(f"runwrap: warning: unreadable {metrics_file}: {e}", file=sys.stderr)

    status = "timeout" if timed_out.is_set() else ("ok" if exit_code == 0 else "failed")
    rec = {
        "run_id": run_id, "exp": args.exp, "name": args.name, "tag": args.tag, "seed": args.seed,
        "cmd": cmd, "config": args.config, "config_hash": config_hash, "git_sha": sha, "git_dirty": dirty,
        "started_at": started, "ended_at": now_iso(), "duration_s": round(time.time() - t0, 2),
        "exit_code": exit_code, "status": status, "metrics": metrics,
        "log": str((run_dir / "log.txt").relative_to(root)), "note": args.note,
    }
    append_jsonl(ledger, rec)
    print(f"runwrap: {run_id} {status} exit={exit_code} metrics={json.dumps(metrics)}", file=sys.stderr)
    if dirty:
        print("runwrap: warning: working tree had uncommitted changes; commit before main runs", file=sys.stderr)
    sys.exit(0 if status == "ok" else 1)


if __name__ == "__main__":
    main()
