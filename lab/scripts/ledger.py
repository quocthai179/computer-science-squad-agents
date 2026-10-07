#!/usr/bin/env python3
"""Query an experiment's run ledger (experiments/<id>/runs.jsonl) and generate
tables and figures from it. Tables and figures are only ever produced here or by
stats.py, so every number in them traces back to a run id.

usage:
  ledger.py list   --exp ID [--tag T] [--name N] [--status S]
  ledger.py show   RUN_ID
  ledger.py table  --exp ID --metric M [--by name] [--out NAME.md]   -> tables/NAME.md
  ledger.py figure --exp ID --metric M [--by name] [--out NAME.svg]  -> figures/NAME.svg
  ledger.py budget --exp ID      runs used vs PLAN.md max_runs, compute minutes used
"""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

from _lab import exp_dir, find_root, generated_header, read_frontmatter, read_jsonl
from stats import fmt, summarize, summary_table, usable_runs


def cmd_list(d: Path, args) -> None:
    runs = read_jsonl(d / "runs.jsonl")
    for key in ("tag", "name", "status"):
        v = getattr(args, key)
        if v:
            runs = [r for r in runs if str(r.get(key)) == v]
    print("| run_id | name | tag | seed | status | dur (s) | metrics | git |")
    print("|---|---|---|---|---|---|---|---|")
    for r in runs:
        m = ", ".join(f"{k}={fmt(v) if isinstance(v, float) else v}" for k, v in (r.get("metrics") or {}).items())
        git = (r.get("git_sha") or "")[:8] + ("+dirty" if r.get("git_dirty") else "")
        print(f"| {r['run_id']} | {r.get('name', '')} | {r.get('tag', '')} | {r.get('seed', '')} | "
              f"{r.get('status')} | {round(r.get('duration_s') or 0)} | {m} | {git} |")


def cmd_show(root: Path, run_id: str) -> None:
    exp = run_id.rsplit("-r", 1)[0]
    for r in read_jsonl(exp_dir(root, exp) / "runs.jsonl"):
        if r.get("run_id") == run_id:
            print(json.dumps(r, indent=2, ensure_ascii=False))
            return
    sys.exit(f"error: run {run_id} not found")


def svg_bars(groups: dict[str, list[float]], metric: str, title: str) -> str:
    names = sorted(groups)
    stats = {n: summarize(groups[n]) for n in names}
    vals = [v for n in names for v in groups[n]]
    his = [s["hi"] for s in stats.values() if not math.isnan(s["hi"])]
    los = [s["lo"] for s in stats.values() if not math.isnan(s["lo"])]
    top = max(vals + his) if vals else 1.0
    bot = min([0.0] + vals + los)
    span = (top - bot) or 1.0
    W, H, L, B, T = 120 + 110 * len(names), 340, 70, 60, 40
    ph = H - B - T

    def y(v: float) -> float:
        return T + ph * (1 - (v - bot) / span)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<text x="{W / 2}" y="20" text-anchor="middle" font-size="14">{html.escape(title)}</text>',
           f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H - B}" stroke="#333"/>',
           f'<line x1="{L}" y1="{y(0) if bot <= 0 <= top else H - B}" x2="{W - 20}" y2="{y(0) if bot <= 0 <= top else H - B}" stroke="#333"/>']
    for i in range(5):
        v = bot + span * i / 4
        out.append(f'<text x="{L - 6}" y="{y(v) + 4}" text-anchor="end">{fmt(v, 3)}</text>')
        out.append(f'<line x1="{L}" y1="{y(v)}" x2="{W - 20}" y2="{y(v)}" stroke="#eee"/>')
    for i, n in enumerate(names):
        s = stats[n]
        cx = L + 60 + 110 * i
        base = y(max(bot, 0.0)) if bot <= 0 else H - B
        out.append(f'<rect x="{cx - 30}" y="{min(y(s["mean"]), base)}" width="60" height="{abs(base - y(s["mean"]))}" fill="#7a9cc6"/>')
        if not math.isnan(s["lo"]):
            out.append(f'<line x1="{cx}" y1="{y(s["lo"])}" x2="{cx}" y2="{y(s["hi"])}" stroke="#222" stroke-width="1.5"/>')
            for v in (s["lo"], s["hi"]):
                out.append(f'<line x1="{cx - 8}" y1="{y(v)}" x2="{cx + 8}" y2="{y(v)}" stroke="#222" stroke-width="1.5"/>')
        for j, v in enumerate(groups[n]):
            out.append(f'<circle cx="{cx - 12 + 24 * j / max(1, len(groups[n]) - 1)}" cy="{y(v)}" r="2.5" fill="#222"/>')
        out.append(f'<text x="{cx}" y="{H - B + 16}" text-anchor="middle">{html.escape(n)}</text>')
        out.append(f'<text x="{cx}" y="{H - B + 30}" text-anchor="middle" fill="#666">n={s["n"]}</text>')
    out.append(f'<text x="16" y="{T + ph / 2}" transform="rotate(-90 16 {T + ph / 2})" text-anchor="middle">{html.escape(metric)}</text>')
    out.append(f'<text x="{W - 20}" y="{H - 6}" text-anchor="end" fill="#999" font-size="10">mean ± 95% t-CI; dots = seeds</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def cmd_budget(d: Path) -> None:
    plan = read_frontmatter(d / "PLAN.md")
    runs = read_jsonl(d / "runs.jsonl")
    counted = [r for r in runs if r.get("tag") != "smoke"]
    minutes = sum((r.get("duration_s") or 0) for r in runs) / 60
    print(f"runs: {len(counted)} counted (+{len(runs) - len(counted)} smoke) / max_runs={plan.get('max_runs', '?')}")
    print(f"compute: {minutes:.1f} min used / budget_total_hours={plan.get('budget_total_hours', '?')}")
    fails = [r for r in runs if r.get("status") != "ok"]
    print(f"failed/timeout runs: {len(fails)}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--exp", required=True)
    ls.add_argument("--tag")
    ls.add_argument("--name")
    ls.add_argument("--status")
    sh = sub.add_parser("show")
    sh.add_argument("run_id")
    for name in ("table", "figure"):
        p = sub.add_parser(name)
        p.add_argument("--exp", required=True)
        p.add_argument("--metric", required=True)
        p.add_argument("--by", default="name")
        p.add_argument("--out")
    bu = sub.add_parser("budget")
    bu.add_argument("--exp", required=True)
    args = ap.parse_args()

    root = find_root(args.root)
    if args.cmd == "show":
        return cmd_show(root, args.run_id)
    d = exp_dir(root, args.exp)
    if args.cmd == "list":
        return cmd_list(d, args)
    if args.cmd == "budget":
        return cmd_budget(d)
    runs = read_jsonl(d / "runs.jsonl")
    src = f"experiments/{args.exp}/runs.jsonl"
    if args.cmd == "table":
        body = summary_table(runs, args.metric, args.by)
        out = d / "tables" / Path(args.out or f"{args.metric}-by-{args.by}.md").name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(generated_header("ledger.py", src) + body, encoding="utf-8")
        print(body, end="")
    else:
        groups: dict[str, list[float]] = {}
        for r in usable_runs(runs, args.metric):
            groups.setdefault(str(r.get(args.by) or "-"), []).append(float(r["metrics"][args.metric]))
        if not groups:
            sys.exit(f"error: no ok runs with metric '{args.metric}'")
        out = d / "figures" / Path(args.out or f"{args.metric}-by-{args.by}.svg").name
        out.parent.mkdir(parents=True, exist_ok=True)
        svg = svg_bars(groups, args.metric, f"{args.exp}: {args.metric} by {args.by}")
        out.write_text(svg.replace("<svg ", f"<!-- generated by ledger.py from {src} -->\n<svg ", 1), encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
