#!/usr/bin/env python3
"""Check that every citation in a Markdown/LaTeX document resolves.

usage: cite_check.py FILE [FILE ...] [--root DIR] [--offline]

Recognised citation forms:
  [@paper-id]  [@paper-id, §3.2]  [@a; @b, Tab. 2]     (pandoc style, used by the plugin)
  \\cite{a,b}  \\citep{a}  \\citet{a}                   (LaTeX)
  arXiv:2401.12345   doi:10.1234/abc                   (bare identifiers)
  [run:e001-r003]                                      (run anchors into a ledger)

A paper key resolves when it is an id in papers/index.jsonl or a key in
papers/refs.bib. Online (default) each resolved paper is then confirmed to exist via
arXiv, doi.org or Semantic Scholar. Exit 1 when anything fails to resolve.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from _lab import find_root, parse_arxiv_id, read_jsonl

UA = "lab-research-squad/0.1 (Claude Code plugin)"
PANDOC_BLOCK = re.compile(r"\[(@[^\]]+)\]")
PANDOC_KEY = re.compile(r"(?:^|[;\s])-?@([\w][\w.:/-]*[\w])")
LATEX = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]+)\}")
ARXIV_BARE = re.compile(r"\barXiv:\s*(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", re.I)
DOI_BARE = re.compile(r"\bdoi:\s*(10\.\d{4,9}/[^\s\]\),;]+)", re.I)
RUN = re.compile(r"\[run:([\w.-]+-r\d+)\]")


def extract(text: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {"key": set(), "arxiv": set(), "doi": set(), "run": set()}
    # ignore fenced code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for block in PANDOC_BLOCK.findall(text):
        for k in PANDOC_KEY.findall(block):
            out["key"].add(k)
    for group in LATEX.findall(text):
        out["key"].update(k.strip() for k in group.split(",") if k.strip())
    out["arxiv"].update(ARXIV_BARE.findall(text))
    out["doi"].update(d.rstrip(".") for d in DOI_BARE.findall(text))
    out["run"].update(RUN.findall(text))
    return out


def bib_entries(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = {}
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        fields = {k.lower(): v.strip().strip("{}") for k, v in re.findall(r"(\w+)\s*=\s*\{(.*?)\}\s*,?\s*$", m.group(2), re.M)}
        entries[m.group(1)] = fields
    return entries


def http_json(url: str) -> dict | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def arxiv_exists(ids: list[str]) -> set[str]:
    found: set[str] = set()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(chunk), "max_results": len(chunk)})
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                root = ET.fromstring(r.read())
        except (urllib.error.URLError, ET.ParseError, TimeoutError) as e:
            raise RuntimeError(f"arXiv API unreachable: {e}") from e
        for e in root.findall("a:entry", ns):
            aid = parse_arxiv_id(e.findtext("a:id", "", ns) or "")
            if aid and (e.findtext("a:title", "", ns) or "").strip():
                found.add(aid)
        time.sleep(3)
    return found


def doi_exists(doi: str) -> bool:
    req = urllib.request.Request("https://doi.org/" + urllib.parse.quote(doi), method="HEAD",
                                 headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status < 400
    except urllib.error.HTTPError as e:
        return e.code in (403, 405, 429)  # publisher blocks HEAD/bots but the DOI resolved
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError("doi.org unreachable")


def s2_title_exists(title: str) -> bool:
    q = urllib.parse.urlencode({"query": title, "limit": 3, "fields": "title"})
    data = http_json("https://api.semanticscholar.org/graph/v1/paper/search?" + q)
    if data is None:
        raise RuntimeError("Semantic Scholar unreachable")
    norm = re.sub(r"[^a-z0-9]", "", title.lower())
    return any(re.sub(r"[^a-z0-9]", "", (p.get("title") or "").lower()) == norm for p in data.get("data") or [])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--root")
    ap.add_argument("--offline", action="store_true", help="only check local resolution")
    args = ap.parse_args()

    root = find_root(args.root)
    index = {r["id"]: r for r in read_jsonl(root / "papers" / "index.jsonl") if r.get("id")}
    bib = bib_entries(root / "papers" / "refs.bib")
    cites: dict[str, set[str]] = {"key": set(), "arxiv": set(), "doi": set(), "run": set()}
    for f in args.files:
        for k, v in extract(Path(f).read_text(encoding="utf-8", errors="replace")).items():
            cites[k] |= v

    problems: list[str] = []
    warnings: list[str] = []
    to_arxiv: dict[str, str] = {}
    to_doi: dict[str, str] = {}
    to_title: dict[str, str] = {}

    for key in sorted(cites["key"]):
        rec = index.get(key)
        b = bib.get(key)
        if not rec and not b:
            problems.append(f"[@{key}] is not in papers/index.jsonl or papers/refs.bib")
            continue
        if rec and not (root / "papers" / "cards" / f"{key}.md").exists():
            warnings.append(f"[@{key}] has no paper card: cited without a pass-2 read")
        aid = parse_arxiv_id(str((rec or {}).get("arxiv") or "")) or parse_arxiv_id(str((b or {}).get("eprint") or "")) \
            or parse_arxiv_id(str((rec or {}).get("url") or (b or {}).get("url") or ""))
        doi = (rec or {}).get("doi") or (b or {}).get("doi")
        if aid:
            to_arxiv[key] = aid
        elif doi:
            to_doi[key] = doi
        else:
            to_title[key] = (rec or {}).get("title") or (b or {}).get("title") or key

    for aid in sorted(cites["arxiv"]):
        to_arxiv[f"arXiv:{aid}"] = aid
    for doi in sorted(cites["doi"]):
        to_doi[f"doi:{doi}"] = doi

    ledgers: dict[str, set[str]] = {}
    for run in sorted(cites["run"]):
        exp = run.rsplit("-r", 1)[0]
        if exp not in ledgers:
            ledgers[exp] = {r.get("run_id") for r in read_jsonl(root / "experiments" / exp / "runs.jsonl")}
        ok = run in ledgers[exp]
        if not ok:
            problems.append(f"[run:{run}] not found in experiments/{exp}/runs.jsonl")

    if not args.offline:
        try:
            found = arxiv_exists(sorted(set(to_arxiv.values()))) if to_arxiv else set()
            for k, aid in to_arxiv.items():
                if aid not in found:
                    problems.append(f"{k}: arXiv {aid} does not exist")
            for k, doi in to_doi.items():
                if not doi_exists(doi):
                    problems.append(f"{k}: DOI {doi} does not resolve")
            for k, title in to_title.items():
                if not s2_title_exists(title):
                    warnings.append(f"[@{k}] no arXiv/DOI and title not found on Semantic Scholar: {title!r}")
        except RuntimeError as e:
            warnings.append(f"online check incomplete: {e}. Re-run later or with --offline.")

    print(f"citations: {len(cites['key'])} keys, {len(cites['arxiv'])} bare arXiv, "
          f"{len(cites['doi'])} bare DOI, {len(cites['run'])} run anchors")
    for p in problems:
        print(f"ERROR   {p}")
    for w in warnings:
        print(f"warning {w}")
    if not problems:
        print("OK: every citation resolves" + (" locally (offline mode)" if args.offline else ""))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
