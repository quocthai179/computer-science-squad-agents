#!/usr/bin/env python3
"""Append-only lab notebook: research/notebook/YYYY-MM-DD.md.

usage: notebook.py add --source SKILL "text"     (or pipe the text on stdin)
       notebook.py show [--date YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from _lab import find_root, today


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add")
    ad.add_argument("--source", default="note", help="which workflow writes this, e.g. survey, run-exp")
    ad.add_argument("text", nargs="?")
    sh = sub.add_parser("show")
    sh.add_argument("--date", default=None)
    a = ap.parse_args()
    root = find_root(a.root)
    if a.cmd == "show":
        p = root / "notebook" / f"{a.date or today()}.md"
        print(p.read_text(encoding="utf-8") if p.exists() else f"(no notebook page {p.name})")
        return
    text = (a.text if a.text is not None else sys.stdin.read()).strip()
    if not text:
        sys.exit("error: empty note")
    p = root / "notebook" / f"{today()}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    head = "" if p.exists() else f"# {today()}\n"
    stamp = dt.datetime.now().strftime("%H:%M")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"{head}\n## {stamp} · {a.source}\n\n{text}\n")
    print(f"appended to {p}")


if __name__ == "__main__":
    main()
