import json

from conftest import PLAN_APPROVED, run_script


def guard(project, tool, path):
    event = {"tool_name": tool, "tool_input": {"file_path": str(path)}, "cwd": str(project)}
    return run_script("guard_generated.py", cwd=project, input=json.dumps(event))


def test_blocks_generated_files(project, experiment):
    for rel in ["tables/acc.md", "figures/acc.svg", "runs.jsonl", "runs/e001-r001/metrics.json"]:
        r = guard(project, "Write", experiment / rel)
        assert r.returncode == 2 and "lab guard" in r.stderr, rel
    r = guard(project, "Edit", "research/experiments/e001/tables/x.md")   # relative path
    assert r.returncode == 2


def test_allows_normal_files(project, experiment):
    for p in [experiment / "FINDINGS.md", experiment / "PLAN.md", project / "train.py"]:
        assert guard(project, "Write", p).returncode == 0
    assert guard(project, "Read", experiment / "tables" / "acc.md").returncode == 0


def test_protected_files_depend_on_plan_status(project, experiment):
    (project / "data").mkdir()
    assert guard(project, "Edit", project / "eval.py").returncode == 2
    assert guard(project, "Write", project / "data" / "test.jsonl").returncode == 2
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace("status: approved", "status: draft"))
    assert guard(project, "Edit", project / "eval.py").returncode == 0


def test_garbage_input_never_blocks(project):
    r = run_script("guard_generated.py", cwd=project, input="not json")
    assert r.returncode == 0


def test_protected_files_with_trailing_comment_in_plan(project, experiment):
    (experiment / "PLAN.md").write_text(PLAN_APPROVED.replace(
        "protected_files: [eval.py, data/test.jsonl]", "protected_files: [eval.py]   # eval, metric, test data"))
    assert guard(project, "Edit", project / "eval.py").returncode == 2
