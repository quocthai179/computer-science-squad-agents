#!/usr/bin/env python3
"""Collect the raw material for a weekly retro (/lab:retro) and for /lab:next.

usage: retro_digest.py [--days 7] [--root DIR] [--status-only]

Prints Markdown: project stage, open work, runs and compute in the window,
decisions, notebook pages, calibration, last retro's next steps, LESSONS.md size.
--status-only prints just the project stage and open work (used by /lab:next).
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import re
from pathlib import Path

from _lab import find_root, read_frontmatter, read_jsonl
from calibration import report as calib_report

LESSON_CAP = 50
# the "Next steps" heading of retro.md in en / vi / zh / fr / ja
NEXT_STEPS_HEADING = r"(next steps|bước tiếp|việc tiếp|下一步|下一步行动|prochaines? étapes|次のステップ|今後の予定)"


def section(text: str, heading_re: str) -> str:
    m = re.search(rf"^##+[ \t]*(?:{heading_re})[^\n]*\n(?P<body>.*?)(?=^##\s|\Z)", text, re.M | re.S | re.I)
    return m.group("body").strip() if m else ""


def open_work(root: Path) -> list[str]:
    items = []
    for plan in sorted(glob.glob(str(root / "experiments" / "*" / "PLAN.md"))):
        fm = read_frontmatter(Path(plan))
        st = str(fm.get("status", "draft"))
        if st != "closed":
            exp = Path(plan).parent
            n = len(read_jsonl(exp / "runs.jsonl"))
            has_findings = (exp / "FINDINGS.md").exists()
            items.append(f"experiment {exp.name}: status={st}, runs={n}, FINDINGS.md={'yes' if has_findings else 'no'}")
    for card in sorted(glob.glob(str(root / "ideas" / "cards" / "*.md"))):
        st = str(read_frontmatter(Path(card)).get("status", ""))
        if st in ("selected", "pilot"):
            items.append(f"idea {Path(card).stem}: status={st}")
    for rep in sorted(glob.glob(str(root / "reports" / "*"))):
        p = Path(rep)
        if p.is_dir() and not (p / "final.md").exists():
            stage = "draft" if (p / "draft.md").exists() else "claims" if (p / "claims.md").exists() else "empty"
            items.append(f"report {p.name}: {stage}, no final.md")
    for sv in sorted(glob.glob(str(root / "surveys" / "*"))):
        p = Path(sv)
        if p.is_dir() and not (p / "survey.md").exists():
            items.append(f"survey {p.name}: no survey.md yet")
    return items


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--status-only", action="store_true")
    a = ap.parse_args()
    root = find_root(a.root)
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    proj = read_frontmatter(root / "PROJECT.md")

    print(f"# Digest since {since}\n")
    print(f"- project: {proj.get('title', '?')} | stage: {proj.get('stage', '?')} | "
          f"north star: {proj.get('north_star', '?')}")
    work = open_work(root)
    print(f"\n## Open work ({len(work)})\n")
    print("\n".join(f"- {w}" for w in work) or "- none")
    if a.status_only:
        return

    print("\n## Runs in window\n")
    total_min = 0.0
    for led in sorted(glob.glob(str(root / "experiments" / "*" / "runs.jsonl"))):
        runs = [r for r in read_jsonl(Path(led)) if str(r.get("started_at", ""))[:10] >= since]
        if not runs:
            continue
        mins = sum(r.get("duration_s") or 0 for r in runs) / 60
        total_min += mins
        by: dict[str, int] = {}
        for r in runs:
            by[r.get("status", "?")] = by.get(r.get("status", "?"), 0) + 1
        print(f"- {Path(led).parent.name}: {len(runs)} runs {by}, {mins:.0f} min")
    print(f"- total compute: {total_min:.0f} min")

    dec = root / "decisions.md"
    if dec.exists():
        text = dec.read_text(encoding="utf-8")
        recent = [m for m in re.findall(r"^##\s*(\d{4}-\d{2}-\d{2}.*)$", text, re.M) if m[:10] >= since]
        print(f"\n## Decisions in window ({len(recent)})\n")
        print("\n".join(f"- {d}" for d in recent) or "- none")

    pages = sorted(p for p in (root / "notebook").glob("*.md") if p.stem[:10] >= since and re.match(r"\d{4}-\d{2}-\d{2}$", p.stem))
    print(f"\n## Notebook pages ({len(pages)})\n")
    for p in pages:
        body = p.read_text(encoding="utf-8")
        print(f"### {p.stem}\n\n{body[:3000]}{' …(truncated)' if len(body) > 3000 else ''}\n")

    print(calib_report(read_jsonl(root / "lessons" / "calibration.jsonl"), since))

    retros = sorted((root / "lessons" / "retros").glob("*.md")) if (root / "lessons" / "retros").exists() else []
    print("## Last retro's next steps\n")
    if retros:
        nxt = section(retros[-1].read_text(encoding="utf-8"), NEXT_STEPS_HEADING)
        print(f"(from {retros[-1].name})\n\n{nxt or '(section not found)'}")
    else:
        print("- no previous retro")

    lessons = root / "lessons" / "LESSONS.md"
    n = sum(1 for ln in lessons.read_text(encoding="utf-8").splitlines() if ln.strip().startswith("- ")) if lessons.exists() else 0
    print(f"\n## LESSONS.md\n\n- {n} lesson lines (cap {LESSON_CAP}){' — AT CAP: merge or drop one before adding' if n >= LESSON_CAP else ''}")
    issues = root / "lessons" / "squad-issues.md"
    if issues.exists():
        k = len(re.findall(r"^- \[ \]", issues.read_text(encoding="utf-8"), re.M))
        print(f"- open squad issues: {k}")


if __name__ == "__main__":
    main()
