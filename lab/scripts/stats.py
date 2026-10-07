#!/usr/bin/env python3
"""Small, dependency-free statistics for experiment ledgers.

usage:
  stats.py summary --exp ID --metric M [--by name] [--out tables/FILE.md]
  stats.py compare --exp ID --metric M --a NAME --b NAME [--out tables/FILE.md]
      paired-by-seed comparison of variant B against variant A

Only runs with status "ok" and tag other than "smoke" are used. 95% intervals:
t-interval for means, percentile bootstrap (fixed seed) for paired differences.
"""

from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
from pathlib import Path

from _lab import exp_dir, find_root, generated_header, read_jsonl

# two-sided 95% Student-t critical values, df = 1..30; df > 30 uses 1.96
_T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
        2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
        2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def t_crit(df: int) -> float:
    if df < 1:
        return float("nan")
    return _T95[df - 1] if df <= 30 else 1.96


def summarize(xs: list[float]) -> dict:
    n = len(xs)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "std": float("nan"), "lo": float("nan"), "hi": float("nan")}
    m = statistics.fmean(xs)
    if n == 1:
        return {"n": 1, "mean": m, "std": float("nan"), "lo": float("nan"), "hi": float("nan")}
    sd = statistics.stdev(xs)
    h = t_crit(n - 1) * sd / math.sqrt(n)
    return {"n": n, "mean": m, "std": sd, "lo": m - h, "hi": m + h}


def bootstrap_ci(xs: list[float], n_boot: int = 10000, alpha: float = 0.05, seed: int = 0) -> tuple[float, float]:
    if len(xs) < 2:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    k = len(xs)
    means = sorted(statistics.fmean(rng.choices(xs, k=k)) for _ in range(n_boot))
    lo = means[int((alpha / 2) * n_boot)]
    hi = means[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return lo, hi


def paired(a: dict, b: dict) -> dict:
    """a, b: {seed: value}. Difference is b - a on common seeds."""
    seeds = sorted(set(a) & set(b), key=str)
    diffs = [b[s] - a[s] for s in seeds]
    s = summarize(diffs)
    blo, bhi = bootstrap_ci(diffs)
    return {
        "seeds": seeds, "diffs": diffs, "n": len(diffs), "mean_diff": s["mean"], "t_lo": s["lo"],
        "t_hi": s["hi"], "boot_lo": blo, "boot_hi": bhi,
        "b_wins": sum(d > 0 for d in diffs), "ties": sum(d == 0 for d in diffs),
        "only_a": sorted(set(a) - set(b), key=str), "only_b": sorted(set(b) - set(a), key=str),
    }


def fmt(x: float, digits: int = 4) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:.{digits}g}"


def usable_runs(runs: list[dict], metric: str) -> list[dict]:
    return [r for r in runs if r.get("status") == "ok" and r.get("tag") != "smoke"
            and isinstance((r.get("metrics") or {}).get(metric), (int, float))]


def summary_table(runs: list[dict], metric: str, by: str = "name") -> str:
    groups: dict[str, list[dict]] = {}
    for r in usable_runs(runs, metric):
        groups.setdefault(str(r.get(by) or "-"), []).append(r)
    lines = [f"| {by} | n | mean {metric} | std | 95% CI | runs |", "|---|---|---|---|---|---|"]
    for g in sorted(groups):
        rs = groups[g]
        s = summarize([float(r["metrics"][metric]) for r in rs])
        ci = f"[{fmt(s['lo'])}, {fmt(s['hi'])}]"
        ids = ", ".join(r["run_id"] for r in rs)
        warn = " ⚠ n<3" if s["n"] < 3 else ""
        lines.append(f"| {g} | {s['n']}{warn} | {fmt(s['mean'])} | {fmt(s['std'])} | {ci} | {ids} |")
    if len(lines) == 2:
        lines.append(f"| (no ok runs with metric '{metric}') | | | | | |")
    return "\n".join(lines) + "\n"


def compare_table(runs: list[dict], metric: str, a: str, b: str) -> str:
    use = usable_runs(runs, metric)
    av = {r.get("seed"): float(r["metrics"][metric]) for r in use if r.get("name") == a}
    bv = {r.get("seed"): float(r["metrics"][metric]) for r in use if r.get("name") == b}
    p = paired(av, bv)
    out = [f"Paired comparison on `{metric}`: **{b}** minus **{a}**, matched by seed.", "",
           "| n pairs | mean diff | 95% t-CI | 95% bootstrap CI | B better | ties |",
           "|---|---|---|---|---|---|",
           f"| {p['n']} | {fmt(p['mean_diff'])} | [{fmt(p['t_lo'])}, {fmt(p['t_hi'])}] | "
           f"[{fmt(p['boot_lo'])}, {fmt(p['boot_hi'])}] | {p['b_wins']}/{p['n']} | {p['ties']} |", ""]
    out.append("| seed | " + a + " | " + b + " | diff |")
    out.append("|---|---|---|---|")
    for s, d in zip(p["seeds"], p["diffs"]):
        out.append(f"| {s} | {fmt(av[s])} | {fmt(bv[s])} | {fmt(d)} |")
    notes = []
    if p["n"] < 3:
        notes.append(f"only {p['n']} paired seed(s): not enough for a main comparison (need >= 3)")
    if p["only_a"] or p["only_b"]:
        notes.append(f"unpaired seeds ignored: {a}={p['only_a']} {b}={p['only_b']}")
    if p["n"] >= 2 and p["t_lo"] <= 0 <= p["t_hi"]:
        notes.append("the 95% t-interval of the difference includes 0")
    if notes:
        out.append("")
        out.extend(f"- note: {n}" for n in notes)
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary")
    s.add_argument("--exp", required=True)
    s.add_argument("--metric", required=True)
    s.add_argument("--by", default="name")
    s.add_argument("--out")
    c = sub.add_parser("compare")
    c.add_argument("--exp", required=True)
    c.add_argument("--metric", required=True)
    c.add_argument("--a", required=True)
    c.add_argument("--b", required=True)
    c.add_argument("--out")
    args = ap.parse_args()

    root = find_root(args.root)
    d = exp_dir(root, args.exp)
    runs = read_jsonl(d / "runs.jsonl")
    if args.cmd == "summary":
        body = summary_table(runs, args.metric, args.by)
    else:
        body = compare_table(runs, args.metric, args.a, args.b)
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = d / "tables" / out.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(generated_header("stats.py", f"experiments/{args.exp}/runs.jsonl") + body, encoding="utf-8")
        print(f"wrote {out}", file=sys.stderr)
    print(body, end="")


if __name__ == "__main__":
    main()
