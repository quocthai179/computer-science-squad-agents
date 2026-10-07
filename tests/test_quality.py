import json

from conftest import run_script, write_runs


def setup_evidence(research):
    d = research / "experiments" / "e001"
    (d / "tables").mkdir(parents=True)
    (d / "tables" / "acc.md").write_text("| baseline | 3 | 0.7123 |\n| method | 3 | 0.7467 |\n")
    write_runs(d, [{"run_id": "e001-r002", "status": "ok", "metrics": {"acc": 0.7467}}])
    (research / "papers" / "cards" / "1706.03762.md").write_text("BLEU 28.4 on WMT14 EN-DE\n")
    with (research / "papers" / "index.jsonl").open("a") as f:
        f.write(json.dumps({"id": "1706.03762", "title": "Attention Is All You Need", "arxiv": "1706.03762"}) + "\n")
    return d


def test_lint_clean_report(project, research):
    setup_evidence(research)
    rpt = research / "reports" / "r1"
    rpt.mkdir(parents=True)
    (rpt / "draft.md").write_text(
        "# Kết quả\n\nMethod đạt 0.7467 so với 0,7123 của baseline [run:e001-r002] (74,67%).\n"
        "Transformer đạt 28.4 BLEU [@1706.03762, Table 2]. Chạy 3 seed vào 2026-10-07, xem §4.2 và Table 3.\n"
        "Bước đầu tiên là đọc dữ liệu.\n<!-- note: TODO ignored inside comments -->\n"
        "Một con số tự do 12.5 lint-ignore <!-- lint-ignore -->\n")
    r = run_script("lint_report.py", rpt / "draft.md", cwd=project)
    assert r.returncode == 0, r.stdout


def test_lint_catches_problems(project, research):
    setup_evidence(research)
    rpt = research / "reports" / "r1"
    rpt.mkdir(parents=True)
    (rpt / "draft.md").write_text(
        "# Draft\n\nOur novel method is state-of-the-art.\n"
        "Accuracy improves to 0.812.\n"
        "Conclusions Here\n"
        "Kết quả: <kết quả cụ thể>. TODO viết tiếp.\n"
        "Đây là phương pháp đầu tiên làm việc này.\n")
    r = run_script("lint_report.py", rpt / "draft.md", cwd=project)
    assert r.returncode == 1
    out = r.stdout
    assert "novelty: 'novel'" in out and "state-of-the-art" in out and "phương pháp đầu tiên" in out
    assert "number: '0.812'" in out
    assert "Conclusions Here" in out and "<kết quả cụ thể>" in out and "TODO" in out


def test_lint_novelty_allowed_after_prior_work_check(project, research):
    setup_evidence(research)
    rpt = research / "reports" / "r1"
    rpt.mkdir(parents=True)
    (rpt / "claims.md").write_text("---\nidea: i001\nstatus: approved\n---\n")
    card = research / "ideas" / "cards" / "i001.md"
    card.write_text("---\nid: i001\nclosest_prior_work: <skeptic điền>\n---\n")
    (rpt / "draft.md").write_text("A novel twist.\n")
    assert run_script("lint_report.py", rpt / "draft.md", cwd=project).returncode == 1
    card.write_text("---\nid: i001\nclosest_prior_work: \"[@1706.03762] differs in X\"\n---\n")
    assert run_script("lint_report.py", rpt / "draft.md", cwd=project).returncode == 0


def test_cite_check_offline(project, research):
    setup_evidence(research)
    doc = research / "reports" / "d.md"
    (research / "reports").mkdir(exist_ok=True)
    doc.write_text("Good [@1706.03762, §3]. Also [run:e001-r002].\n```\n[@ignored-in-code]\n```\n")
    r = run_script("cite_check.py", doc, "--offline", cwd=project)
    assert r.returncode == 0, r.stdout
    doc.write_text("Bad [@made-up-2024; @1706.03762] and [run:e001-r999] and \\cite{ghost}.\n")
    r = run_script("cite_check.py", doc, "--offline", cwd=project)
    assert r.returncode == 1
    assert "made-up-2024" in r.stdout and "e001-r999" in r.stdout and "ghost" in r.stdout
    assert "1706.03762" not in r.stdout.split("ERROR", 1)[1].split("\n")[0]


def test_calibration_cycle(project):
    c = lambda *a: run_script("calibration.py", *a, cwd=project, check=True)  # noqa: E731
    assert c("add", "--kind", "prediction", "--ref", "e001", "--text", "B>A", "--confidence", "80").stdout.strip() == "c001"
    c("add", "--kind", "prediction", "--ref", "e002", "--text", "C>A", "--confidence", "60")
    c("add", "--kind", "estimate", "--ref", "e001", "--text", "pilot", "--hours", "2")
    assert "c003" in c("open").stdout
    c("resolve", "c001", "--outcome", "true")
    c("resolve", "c002", "--outcome", "false")
    c("resolve", "c003", "--actual-hours", "5")
    rep = c("report").stdout
    # Brier = ((0.8-1)^2 + (0.6-0)^2) / 2 = 0.2
    assert "Brier 0.200" in rep and "hit rate 50%" in rep and "median 2.50×" in rep
    bad = run_script("calibration.py", "add", "--kind", "prediction", "--ref", "x", "--text", "y", cwd=project)
    assert bad.returncode != 0


def test_retro_digest(project, research, experiment):
    write_runs(experiment, [{"run_id": "e001-r001", "status": "ok", "started_at": "2999-01-01T00:00:00",
                             "duration_s": 120, "tag": "smoke"}])
    (research / "reports" / "course").mkdir(parents=True)
    (research / "reports" / "course" / "claims.md").write_text("x")
    r = run_script("retro_digest.py", "--days", "7", cwd=project, check=True)
    out = r.stdout
    assert "experiment e001: status=approved, runs=1" in out
    assert "report course: claims, no final.md" in out
    assert "e001: 1 runs" in out and "no previous retro" in out
    r = run_script("retro_digest.py", "--status-only", cwd=project, check=True)
    assert "Open work" in r.stdout and "Runs in window" not in r.stdout


def test_number_interpretations():
    from lint_report import interpretations, should_check
    assert interpretations("0.812") == [0.812]
    assert interpretations("0,7123") == [0.7123]
    assert sorted(interpretations("4.000")) == [4.0, 4000.0]
    assert sorted(interpretations("1,234")) == [1.234, 1234.0]
    assert should_check("0.812", False) and not should_check("4.000", False) and not should_check("42", False)
    assert should_check("42", True)
