#!/usr/bin/env python3
"""Calibration log: predictions vs outcomes, time estimates vs actual time.
Stored in research/lessons/calibration.jsonl.

usage:
  calibration.py add --kind prediction --ref e001 --text "B beats A by >=2 pts" --confidence 70
  calibration.py add --kind estimate   --ref e001 --text "pilot run end-to-end" --hours 4
  calibration.py resolve c007 --outcome true|false|partial [--actual-hours 6.5] [--note "..."]
  calibration.py open
  calibration.py report [--since YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys

from _lab import append_jsonl, find_root, now_iso, read_jsonl, write_jsonl

OUTCOME = {"true": 1.0, "false": 0.0, "partial": 0.5}


def path_of(root):
    return root / "lessons" / "calibration.jsonl"


def next_id(rows: list[dict]) -> str:
    nums = [int(m.group(1)) for r in rows if (m := re.fullmatch(r"c(\d+)", str(r.get("id", ""))))]
    return f"c{(max(nums) + 1) if nums else 1:03d}"


def cmd_add(root, a) -> None:
    rows = read_jsonl(path_of(root))
    if a.kind == "prediction" and a.confidence is None:
        sys.exit("error: a prediction needs --confidence (0-100)")
    if a.kind == "estimate" and a.hours is None:
        sys.exit("error: an estimate needs --hours")
    rec = {"id": next_id(rows), "kind": a.kind, "ref": a.ref, "text": a.text, "created_at": now_iso(),
           "status": "open"}
    if a.confidence is not None:
        if not 0 <= a.confidence <= 100:
            sys.exit("error: --confidence must be 0-100")
        rec["confidence"] = a.confidence
    if a.hours is not None:
        rec["estimate_hours"] = a.hours
    append_jsonl(path_of(root), rec)
    print(rec["id"])


def cmd_resolve(root, a) -> None:
    rows = read_jsonl(path_of(root))
    row = next((r for r in rows if r.get("id") == a.id), None)
    if row is None:
        sys.exit(f"error: no calibration entry {a.id}")
    if row["kind"] == "prediction":
        if a.outcome is None:
            sys.exit("error: resolving a prediction needs --outcome")
        row["outcome"] = a.outcome
    if a.actual_hours is not None:
        row["actual_hours"] = a.actual_hours
    if row["kind"] == "estimate" and row.get("actual_hours") is None:
        sys.exit("error: resolving an estimate needs --actual-hours")
    row["status"] = "resolved"
    row["resolved_at"] = now_iso()
    if a.note:
        row["note"] = a.note
    write_jsonl(path_of(root), rows)
    print(f"{a.id} resolved")


def cmd_open(root) -> None:
    for r in read_jsonl(path_of(root)):
        if r.get("status") == "open":
            extra = f"{r.get('confidence')}%" if r["kind"] == "prediction" else f"{r.get('estimate_hours')}h"
            print(f"{r['id']}\t{r['kind']}\t{r.get('ref')}\t{extra}\t{r.get('text')}")


def report(rows: list[dict], since: str | None = None) -> str:
    if since:
        rows = [r for r in rows if str(r.get("created_at", ""))[:10] >= since]
    preds = [r for r in rows if r["kind"] == "prediction" and r.get("status") == "resolved"]
    ests = [r for r in rows if r["kind"] == "estimate" and r.get("status") == "resolved"]
    open_n = sum(1 for r in rows if r.get("status") == "open")
    out = ["## Calibration", ""]
    if preds:
        ys = [OUTCOME[r["outcome"]] for r in preds]
        ps = [r["confidence"] / 100 for r in preds]
        brier = statistics.fmean((p - y) ** 2 for p, y in zip(ps, ys))
        out.append(f"- predictions resolved: {len(preds)}; hit rate {statistics.fmean(ys):.0%}; "
                   f"mean stated confidence {statistics.fmean(ps):.0%}; Brier {brier:.3f} "
                   f"(0 = perfect, 0.25 = always saying 50%)")
        out += ["", "| confidence | n | stated | observed |", "|---|---|---|---|"]
        buckets: dict[int, list[tuple[float, float]]] = {}
        for p, y in zip(ps, ys):
            buckets.setdefault(min(9, int(p * 10)), []).append((p, y))
        for b in sorted(buckets):
            items = buckets[b]
            out.append(f"| {b * 10}–{b * 10 + 10}% | {len(items)} | {statistics.fmean(p for p, _ in items):.0%} | "
                       f"{statistics.fmean(y for _, y in items):.0%} |")
    else:
        out.append("- no resolved predictions yet")
    out.append("")
    if ests:
        ratios = [r["actual_hours"] / r["estimate_hours"] for r in ests if r.get("estimate_hours")]
        if ratios:
            out.append(f"- time estimates resolved: {len(ratios)}; actual/estimate median {statistics.median(ratios):.2f}×, "
                       f"mean {statistics.fmean(ratios):.2f}×, worst {max(ratios):.2f}×")
    else:
        out.append("- no resolved time estimates yet")
    out.append(f"- still open: {open_n}")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add")
    ad.add_argument("--kind", choices=["prediction", "estimate"], required=True)
    ad.add_argument("--ref", required=True)
    ad.add_argument("--text", required=True)
    ad.add_argument("--confidence", type=float)
    ad.add_argument("--hours", type=float)
    rs = sub.add_parser("resolve")
    rs.add_argument("id")
    rs.add_argument("--outcome", choices=list(OUTCOME))
    rs.add_argument("--actual-hours", type=float)
    rs.add_argument("--note")
    sub.add_parser("open")
    rp = sub.add_parser("report")
    rp.add_argument("--since")
    a = ap.parse_args()
    root = find_root(a.root)
    if a.cmd == "add":
        cmd_add(root, a)
    elif a.cmd == "resolve":
        cmd_resolve(root, a)
    elif a.cmd == "open":
        cmd_open(root)
    else:
        print(report(read_jsonl(path_of(root)), a.since), end="")


if __name__ == "__main__":
    main()
