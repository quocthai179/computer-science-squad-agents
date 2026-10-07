import json
import sys

from conftest import PLAN_APPROVED, run_script

PY = sys.executable


def ledger(exp):
    return [json.loads(l) for l in (exp / "runs.jsonl").read_text().splitlines() if l.strip()]


def wrap(project, *args):
    return run_script("runwrap.py", "--exp", "e001", *args, cwd=project)


def test_refuses_draft_plan(project, experiment):
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace("status: approved", "status: draft"))
    r = wrap(project, "--name", "x", "--tag", "smoke", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "G3" in r.stderr
    assert not (experiment / "runs.jsonl").exists()


def test_refuses_without_prediction_or_kill_criteria(project, experiment):
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace(
        "prediction: method beats baseline by >= 1 point", "prediction: <hướng và độ lớn>"))
    r = wrap(project, "--name", "x", "--tag", "smoke", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "prediction" in r.stderr
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace("kill_criteria: stop if no gain after 6 runs\n", ""))
    r = wrap(project, "--name", "x", "--tag", "smoke", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "kill_criteria" in r.stderr


def test_smoke_first_then_main_with_metrics(project, experiment):
    r = wrap(project, "--name", "baseline", "--tag", "baseline", "--seed", "0", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "smoke" in r.stderr

    r = wrap(project, "--name", "smoke", "--tag", "smoke", "--", PY, "-c", "print('LAB_METRIC loss=2.30')")
    assert r.returncode == 0, r.stderr
    code = ("import json,os; print('LAB_METRIC acc=0.5'); print('LAB_METRIC acc=0.81'); "
            "json.dump({'f1': 0.7}, open(os.environ['LAB_METRICS_FILE'], 'w')); "
            "print('seed', os.environ['LAB_SEED'])")
    r = wrap(project, "--name", "baseline", "--tag", "baseline", "--seed", "7", "--", PY, "-c", code)
    assert r.returncode == 0, r.stderr
    rows = ledger(experiment)
    assert [x["run_id"] for x in rows] == ["e001-r001", "e001-r002"]
    last = rows[-1]
    assert last["metrics"] == {"acc": 0.81, "f1": 0.7}
    assert last["status"] == "ok" and last["seed"] == 7 and last["tag"] == "baseline"
    assert "seed 7" in (project / "research" / last["log"]).read_text()


def test_failure_limit_and_after_review(project, experiment):
    assert wrap(project, "--name", "s", "--tag", "smoke", "--", PY, "-c", "pass").returncode == 0
    for _ in range(3):
        r = wrap(project, "--name", "m", "--seed", "0", "--", PY, "-c", "raise SystemExit(1)")
        assert r.returncode == 1
    r = wrap(project, "--name", "m", "--seed", "0", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "last 3 runs failed" in r.stderr
    r = wrap(project, "--name", "m", "--seed", "0", "--after-review", "--", PY, "-c", "pass")
    assert r.returncode == 0
    assert [x["status"] for x in ledger(experiment)] == ["ok", "failed", "failed", "failed", "ok"]


def test_max_runs_budget(project, experiment):
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace("max_runs: 8", "max_runs: 1"))
    assert wrap(project, "--name", "s", "--tag", "smoke", "--", PY, "-c", "pass").returncode == 0
    assert wrap(project, "--name", "m", "--seed", "0", "--", PY, "-c", "pass").returncode == 0
    r = wrap(project, "--name", "m", "--seed", "1", "--", PY, "-c", "pass")
    assert r.returncode == 3 and "budget" in r.stderr


def test_timeout_is_recorded(project, experiment):
    r = wrap(project, "--name", "s", "--tag", "smoke", "--timeout-min", "0.02", "--",
             PY, "-c", "import time; time.sleep(30)")
    assert r.returncode == 1
    assert ledger(experiment)[-1]["status"] == "timeout"


def test_missing_command_binary(project, experiment):
    r = wrap(project, "--name", "s", "--tag", "smoke", "--", "definitely-not-a-binary-xyz")
    assert r.returncode == 1
    assert ledger(experiment)[-1]["exit_code"] == 127
