from conftest import run_script


def test_init_creates_tree_and_is_idempotent(tmp_path):
    r = run_script("init_workspace.py", "--title", "Đề tài X", cwd=tmp_path, check=True)
    root = tmp_path / "research"
    for rel in ["PROJECT.md", "decisions.md", "ideas/backlog.md", "lessons/LESSONS.md",
                "lessons/squad-issues.md", "papers/index.jsonl", "papers/refs.bib",
                "lessons/calibration.jsonl", ".gitignore", "papers/cards", "lessons/retros"]:
        assert (root / rel).exists(), rel
    assert "title: Đề tài X" in (root / "PROJECT.md").read_text(encoding="utf-8")
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert claude.count("<!-- lab:begin -->") == 1

    (root / "PROJECT.md").write_text("custom", encoding="utf-8")
    r = run_script("init_workspace.py", cwd=tmp_path, check=True)
    assert "already initialised" in r.stdout
    assert (root / "PROJECT.md").read_text(encoding="utf-8") == "custom"
    assert (tmp_path / "CLAUDE.md").read_text(encoding="utf-8").count("<!-- lab:begin -->") == 1


def test_init_appends_to_existing_claude_md(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# My repo\n\nrules\n", encoding="utf-8")
    run_script("init_workspace.py", cwd=tmp_path, check=True)
    text = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert text.startswith("# My repo") and "<!-- lab:end -->" in text


def test_notebook_append(project):
    run_script("notebook.py", "add", "--source", "survey", "first note", cwd=project, check=True)
    run_script("notebook.py", "add", "--source", "retro", cwd=project, input="second note", check=True)
    pages = list((project / "research" / "notebook").glob("*.md"))
    assert len(pages) == 1
    text = pages[0].read_text(encoding="utf-8")
    assert "first note" in text and "second note" in text and "· survey" in text


def test_scripts_fail_cleanly_without_workspace(tmp_path):
    r = run_script("ledger.py", "list", "--exp", "e1", cwd=tmp_path)
    assert r.returncode == 2 and "/lab:setup" in r.stderr
