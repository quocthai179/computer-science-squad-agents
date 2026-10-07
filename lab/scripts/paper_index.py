#!/usr/bin/env python3
"""Maintain research/papers/index.jsonl.

usage:
  paper_index.py merge FILE.jsonl [FILE.jsonl ...] [--tag survey-slug]
      Merge scout output into the index, de-duplicating by arXiv id, DOI, then
      normalised title. Keeps the highest relevance and the furthest reading pass.
  paper_index.py list [--min-relevance N] [--tag T] [--pass N] [--limit N]
  paper_index.py set ID key=value [key=value ...]
      e.g. `set 2401.12345 pass=2 relevance=3 tags=+moe`

Scout lines look like:
  {"title": "...", "year": 2024, "venue": "...", "url": "...", "arxiv": "2401.12345",
   "doi": null, "angle": "benchmarks", "relevance": 2, "five_c": {...}, "why": "..."}
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _lab import (find_root, now_iso, paper_id_for_arxiv, parse_arxiv_id, read_jsonl,
                  slugify, write_jsonl)


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def key_of(rec: dict) -> tuple[str | None, str | None, str]:
    aid = parse_arxiv_id(str(rec.get("arxiv") or "")) or parse_arxiv_id(str(rec.get("url") or ""))
    doi = (rec.get("doi") or "").lower().strip() or None
    return aid, doi, norm_title(rec.get("title", ""))


def new_id(rec: dict, taken: set[str]) -> str:
    aid, doi, _ = key_of(rec)
    if aid:
        pid = paper_id_for_arxiv(aid)
    else:
        first = (rec.get("authors") or ["x"])[0].split()[-1] if rec.get("authors") else ""
        pid = slugify(f"{first} {rec.get('year') or ''} {rec.get('title', '')}", 50)
    base, n = pid, 2
    while pid in taken:
        pid = f"{base}-{n}"
        n += 1
    return pid


def merge(root: Path, files: list[str], tag: str | None) -> None:
    path = root / "papers" / "index.jsonl"
    rows = read_jsonl(path)
    by_arxiv = {}
    by_doi = {}
    by_title = {}
    for r in rows:
        a, d, t = key_of(r)
        if a:
            by_arxiv[a] = r
        if d:
            by_doi[d] = r
        if t:
            by_title[t] = r
    taken = {r["id"] for r in rows}
    added = updated = 0
    for f in files:
        for rec in read_jsonl(Path(f)):
            if not rec.get("title"):
                print(f"skip (no title) in {f}: {json.dumps(rec)[:80]}", file=sys.stderr)
                continue
            a, d, t = key_of(rec)
            hit = (a and by_arxiv.get(a)) or (d and by_doi.get(d)) or (t and by_title.get(t))
            tags = set(rec.get("tags") or [])
            if rec.get("angle"):
                tags.add(f"angle:{rec['angle']}")
            if tag:
                tags.add(tag)
            if hit:
                hit["relevance"] = max(hit.get("relevance") or 0, rec.get("relevance") or 0)
                hit["pass"] = max(hit.get("pass") or 0, 1)
                hit["tags"] = sorted(set(hit.get("tags") or []) | tags)
                for k in ("year", "venue", "url", "doi", "authors"):
                    if not hit.get(k) and rec.get(k):
                        hit[k] = rec[k]
                if a and not hit.get("arxiv"):
                    hit["arxiv"] = a
                notes = hit.setdefault("scout_notes", [])
                if rec.get("why") and rec["why"] not in notes:
                    notes.append(rec["why"])
                updated += 1
                continue
            pid = new_id(rec, taken)
            taken.add(pid)
            new = {
                "id": pid, "title": rec["title"], "authors": rec.get("authors") or [],
                "year": rec.get("year"), "venue": rec.get("venue"), "url": rec.get("url"),
                "arxiv": a, "doi": rec.get("doi"), "pass": 1,
                "relevance": rec.get("relevance"), "tags": sorted(tags),
                "five_c": rec.get("five_c"), "scout_notes": [rec["why"]] if rec.get("why") else [],
                "added_at": now_iso(),
            }
            rows.append(new)
            if a:
                by_arxiv[a] = new
            if d:
                by_doi[d.lower()] = new
            by_title[t] = new
            added += 1
    write_jsonl(path, rows)
    print(f"index: {len(rows)} papers (+{added} new, {updated} merged duplicates)")


def list_rows(root: Path, args) -> None:
    rows = read_jsonl(root / "papers" / "index.jsonl")
    if args.min_relevance is not None:
        rows = [r for r in rows if (r.get("relevance") or 0) >= args.min_relevance]
    if args.tag:
        rows = [r for r in rows if args.tag in (r.get("tags") or [])]
    if args.pass_ is not None:
        rows = [r for r in rows if (r.get("pass") or 0) == args.pass_]
    rows.sort(key=lambda r: (-(r.get("relevance") or 0), -(r.get("year") or 0)))
    print("| id | year | rel | pass | title |\n|---|---|---|---|---|")
    for r in rows[: args.limit]:
        print(f"| {r['id']} | {r.get('year') or ''} | {r.get('relevance') if r.get('relevance') is not None else ''} "
              f"| {r.get('pass') or 0} | {(r.get('title') or '')[:90]} |")


def set_fields(root: Path, pid: str, pairs: list[str]) -> None:
    path = root / "papers" / "index.jsonl"
    rows = read_jsonl(path)
    row = next((r for r in rows if r.get("id") == pid), None)
    if row is None:
        sys.exit(f"error: no paper with id {pid}")
    for p in pairs:
        if "=" not in p:
            sys.exit(f"error: expected key=value, got {p}")
        k, v = p.split("=", 1)
        if k == "tags":
            items = [t for t in v.split(",") if t]
            if all(t[0] in "+-" for t in items):
                cur = set(row.get("tags") or [])
                for t in items:
                    (cur.add if t[0] == "+" else cur.discard)(t[1:])
            else:
                cur = set(items)  # plain list replaces the tags
            row["tags"] = sorted(cur)
        elif k in ("pass", "relevance", "year"):
            row[k] = int(v)
        else:
            row[k] = v
    write_jsonl(path, rows)
    print(json.dumps(row, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("files", nargs="+")
    m.add_argument("--tag")
    ls = sub.add_parser("list")
    ls.add_argument("--min-relevance", type=int)
    ls.add_argument("--tag")
    ls.add_argument("--pass", dest="pass_", type=int)
    ls.add_argument("--limit", type=int, default=50)
    st = sub.add_parser("set")
    st.add_argument("id")
    st.add_argument("pairs", nargs="+")
    args = ap.parse_args()
    root = find_root(args.root)
    if args.cmd == "merge":
        merge(root, args.files, args.tag)
    elif args.cmd == "list":
        list_rows(root, args)
    else:
        set_fields(root, args.id, args.pairs)


if __name__ == "__main__":
    main()
