#!/usr/bin/env python3
"""PreToolUse hook: block hand edits to files only scripts may write.

Blocked for Edit / Write / MultiEdit / NotebookEdit:
  research/experiments/<id>/runs.jsonl, runs/**, tables/**, figures/**
      (written only by runwrap.py, ledger.py, stats.py)
  any path listed in `protected_files` of an experiment PLAN.md whose status is
      approved or running (eval code, metric code, test data)

Reads the hook event JSON on stdin. Exit 2 blocks the call and shows stderr to Claude.
Anything unexpected exits 0 so the hook never breaks unrelated work.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lab import read_frontmatter  # noqa: E402

GENERATED = re.compile(r"(^|/)research/experiments/[^/]+/(runs\.jsonl$|runs/|tables/|figures/)")


def project_root(start: Path) -> Path | None:
    for d in [start, *start.parents]:
        if (d / "research" / "PROJECT.md").is_file():
            return d
    return None


def check(event: dict) -> str | None:
    if event.get("tool_name") not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        return None
    ti = event.get("tool_input") or {}
    fp = ti.get("file_path") or ti.get("notebook_path")
    if not fp:
        return None
    cwd = Path(event.get("cwd") or ".")
    path = Path(fp) if Path(fp).is_absolute() else cwd / fp
    path = path.resolve()
    if GENERATED.search(path.as_posix()):
        return (f"{fp} is generated from the run ledger. Do not edit it by hand: use runwrap.py to record runs "
                f"and ledger.py / stats.py to (re)generate tables and figures.")
    root = project_root(path.parent) or project_root(cwd.resolve())
    if root is None:
        return None
    for plan in (root / "research" / "experiments").glob("*/PLAN.md"):
        fm = read_frontmatter(plan)
        if str(fm.get("status", "")).lower() not in ("approved", "running"):
            continue
        prot = fm.get("protected_files") or []
        if isinstance(prot, str):
            prot = [prot]
        for p in prot:
            pp = (root / str(p)).resolve()
            if path == pp or pp in path.parents:
                return (f"{fp} is a protected file of experiment {plan.parent.name} (eval/metric/test data) while "
                        f"the plan is {fm.get('status')}. Changing it mid-experiment invalidates comparisons. "
                        f"Stop and ask the user; a change needs a new plan version.")
    return None


def main() -> None:
    try:
        event = json.load(sys.stdin)
        reason = check(event)
    except Exception:  # noqa: BLE001 - never break the session because of the guard itself
        sys.exit(0)
    if reason:
        print(f"lab guard: {reason}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
