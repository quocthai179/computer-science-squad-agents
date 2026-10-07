#!/usr/bin/env python3
"""Create the research/ workspace (idempotent; never overwrites existing files).

usage: init_workspace.py [--project-dir DIR] [--title TITLE] [--lang LANG] [--no-claude-md]

--lang picks the language of the generated files: en (default), vi, zh, fr, ja.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from _lab import (DEFAULT_LANG, LANG_NAMES, SUPPORTED_LANGS, TEMPLATES, normalize_lang, die, resolve_language,
                  template_path, today)

DIRS = [
    "notebook",
    "papers/raw",
    "papers/cards",
    "surveys",
    "ideas/cards",
    "experiments",
    "reports",
    "reviews",
    "lessons/retros",
]

# workspace path -> template file name
FILES = {
    "PROJECT.md": "PROJECT.md",
    "decisions.md": "decisions.md",
    "ideas/backlog.md": "backlog.md",
    "lessons/LESSONS.md": "LESSONS.md",
    "lessons/squad-issues.md": "squad-issues.md",
}

EMPTY = ["papers/index.jsonl", "papers/refs.bib", "lessons/calibration.jsonl"]

GITIGNORE = """# lab plugin: large or regenerable files
papers/raw/
experiments/*/runs/
"""

BEGIN, END = "<!-- lab:begin -->", "<!-- lab:end -->"


def claude_md_block(lang: str) -> str:
    text = (TEMPLATES / "CLAUDE-snippet.md").read_text(encoding="utf-8").strip()
    return text.replace("{{language}}", f"{lang} ({LANG_NAMES[lang]})")


def upsert_claude_md(project_dir: Path, lang: str) -> str:
    path = project_dir / "CLAUDE.md"
    block = f"{BEGIN}\n{claude_md_block(lang)}\n{END}"
    if not path.exists():
        path.write_text(block + "\n", encoding="utf-8")
        return "created"
    text = path.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
        if new == text:
            return "unchanged"
        path.write_text(new, encoding="utf-8")
        return "updated"
    path.write_text(text.rstrip() + "\n\n" + block + "\n", encoding="utf-8")
    return "appended"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project-dir", default=".", help="repo root that will contain research/")
    ap.add_argument("--title", default="", help="project title written into PROJECT.md")
    ap.add_argument("--lang", help="en (default), vi, zh, fr, ja; also accepts names like 'French' or '日本語'")
    ap.add_argument("--no-claude-md", action="store_true", help="do not touch CLAUDE.md")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    root = project / "research"
    if args.lang and not normalize_lang(args.lang):
        die(f"unsupported language '{args.lang}'. Supported: {', '.join(SUPPORTED_LANGS)}")
    # an existing workspace keeps its language unless --lang is given
    lang = resolve_language(root if (root / "PROJECT.md").exists() else None, default=DEFAULT_LANG, explicit=args.lang)
    created = []

    for d in DIRS:
        p = root / d
        if not p.exists():
            p.mkdir(parents=True)
            created.append(f"{d}/")

    for rel, tpl in FILES.items():
        p = root / rel
        if p.exists():
            continue
        text = template_path(tpl, lang).read_text(encoding="utf-8")
        text = text.replace("{{date}}", today()).replace("{{title}}", args.title or "<title>")
        text = text.replace("{{language}}", lang)
        p.write_text(text, encoding="utf-8")
        created.append(rel)

    for rel in EMPTY:
        p = root / rel
        if not p.exists():
            p.touch()
            created.append(rel)

    gi = root / ".gitignore"
    if not gi.exists():
        gi.write_text(GITIGNORE, encoding="utf-8")
        created.append(".gitignore")

    nb = root / "notebook" / f"{today()}.md"
    if not nb.exists():
        nb.write_text(f"# {today()}\n", encoding="utf-8")
        created.append(f"notebook/{nb.name}")

    claude = "skipped" if args.no_claude_md else upsert_claude_md(project, lang)

    print(f"workspace: {root} (language: {lang}, {LANG_NAMES[lang]})")
    print("created: " + (", ".join(created) if created else "nothing (already initialised)"))
    print(f"CLAUDE.md: {claude}")


if __name__ == "__main__":
    main()
