import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "lab" / "scripts"
sys.path.insert(0, str(SCRIPTS))


def run_script(name, *args, cwd, input=None, check=False):
    env = {k: v for k, v in os.environ.items() if k != "LAB_RESEARCH_DIR"}
    r = subprocess.run([sys.executable, str(SCRIPTS / name), *map(str, args)], cwd=cwd, env=env,
                       capture_output=True, text=True, input=input, timeout=120)
    if check and r.returncode != 0:
        raise AssertionError(f"{name} failed ({r.returncode}):\n{r.stdout}\n{r.stderr}")
    return r


@pytest.fixture
def project(tmp_path):
    run_script("init_workspace.py", "--title", "Test project", cwd=tmp_path, check=True)
    return tmp_path


@pytest.fixture
def research(project):
    return project / "research"


PLAN_APPROVED = """---
exp_id: e001
status: approved
prediction: method beats baseline by >= 1 point
confidence: 60
kill_criteria: stop if no gain after 6 runs
primary_metric: acc
protected_files: [eval.py, data/test.jsonl]
seeds: 3
budget_minutes_per_run: 1
max_runs: 8
---

# e001
"""


@pytest.fixture
def experiment(research):
    d = research / "experiments" / "e001"
    d.mkdir(parents=True)
    (d / "PLAN.md").write_text(PLAN_APPROVED, encoding="utf-8")
    return d


def write_runs(exp_dir, runs):
    with (exp_dir / "runs.jsonl").open("w", encoding="utf-8") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
