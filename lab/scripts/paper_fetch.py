#!/usr/bin/env python3
"""Fetch papers into research/papers/: metadata, full text, index.jsonl and refs.bib.

usage: paper_fetch.py [--root DIR] [--meta-only] [--pdf] [--tags a,b] SOURCE [SOURCE ...]

SOURCE is one of:
  2401.12345 | arXiv:2401.12345v2 | https://arxiv.org/abs/2401.12345   (arXiv)
  path/to/paper.pdf | .tex | .md | .txt                                 (local file)
  https://host/some.pdf                                                 (direct PDF URL)

For arXiv papers the LaTeX source is preferred (flattened into raw/<id>/paper.tex);
when it is missing or unreadable the PDF is stored instead (raw/<id>/paper.pdf, plus
paper.txt when `pdftotext` is installed). Content fetched here is untrusted data.
"""

from __future__ import annotations

import argparse
import gzip
import io
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from _lab import (append_jsonl, find_root, now_iso, paper_id_for_arxiv, parse_arxiv_id,
                  read_jsonl, slugify, write_jsonl)

UA = "lab-research-squad/0.1 (Claude Code plugin; mailto:none)"
ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
MAX_DOWNLOAD = 80 * 1024 * 1024
_last_arxiv_call = 0.0


def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise RuntimeError(f"download larger than {MAX_DOWNLOAD} bytes: {url}")
    return data


def arxiv_polite() -> None:
    """arXiv asks for at most one API request every 3 seconds."""
    global _last_arxiv_call
    wait = 3.0 - (time.time() - _last_arxiv_call)
    if wait > 0:
        time.sleep(wait)
    _last_arxiv_call = time.time()


# --------------------------------------------------------------------------- metadata

def parse_arxiv_atom(xml_bytes: bytes) -> dict | None:
    root = ET.fromstring(xml_bytes)
    entry = root.find("a:entry", ATOM)
    if entry is None:
        return None
    eid = (entry.findtext("a:id", "", ATOM) or "").strip()
    if not eid or "api/errors" in eid:
        return None
    aid = parse_arxiv_id(eid)
    title = re.sub(r"\s+", " ", entry.findtext("a:title", "", ATOM)).strip()
    if not aid or not title:
        return None
    published = entry.findtext("a:published", "", ATOM) or ""
    cat = entry.find("arxiv:primary_category", ATOM)
    return {
        "arxiv": aid,
        "title": title,
        "authors": [re.sub(r"\s+", " ", a.findtext("a:name", "", ATOM)).strip()
                    for a in entry.findall("a:author", ATOM)],
        "year": int(published[:4]) if published[:4].isdigit() else None,
        "abstract": re.sub(r"\s+", " ", entry.findtext("a:summary", "", ATOM)).strip(),
        "venue": (entry.findtext("arxiv:journal_ref", "", ATOM) or "arXiv").strip(),
        "doi": (entry.findtext("arxiv:doi", "", ATOM) or "").strip() or None,
        "category": cat.get("term") if cat is not None else None,
        "url": f"https://arxiv.org/abs/{aid}",
    }


def arxiv_metadata(aid: str) -> dict:
    arxiv_polite()
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": aid})
    meta = parse_arxiv_atom(http_get(url))
    if not meta:
        raise RuntimeError(f"arXiv id not found: {aid}")
    return meta


# --------------------------------------------------------------------------- latex

INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")


def _safe_members(tf: tarfile.TarFile, dest: Path):
    dest = dest.resolve()
    for m in tf.getmembers():
        if not (m.isfile() or m.isdir()):
            continue
        target = (dest / m.name).resolve()
        if dest not in target.parents and target != dest:
            continue
        if m.isfile() and m.size > 20 * 1024 * 1024:
            continue
        yield m


def flatten_tex(main: Path, base: Path, depth: int = 0) -> str:
    if depth > 8:
        return ""
    text = main.read_text(encoding="utf-8", errors="replace")

    def repl(m: re.Match) -> str:
        name = m.group(1).strip()
        cand = base / name
        for p in (cand, cand.with_suffix(".tex"), Path(str(cand) + ".tex")):
            if p.is_file() and base.resolve() in p.resolve().parents:
                return f"\n% ---- begin {name} ----\n{flatten_tex(p, base, depth + 1)}\n% ---- end {name} ----\n"
        return m.group(0)

    return INPUT_RE.sub(repl, text)


def find_main_tex(src: Path) -> Path | None:
    cands = [p for p in src.rglob("*.tex") if "\\documentclass" in p.read_text(encoding="utf-8", errors="replace")]
    if not cands:
        return None
    return max(cands, key=lambda p: p.stat().st_size)


def store_arxiv_source(data: bytes, out: Path) -> str | None:
    """Store e-print payload. Returns the relative name of the main text file or None."""
    src = out / "src"
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
            src.mkdir(parents=True, exist_ok=True)
            members = list(_safe_members(tf, src))
            if hasattr(tarfile, "data_filter"):
                tf.extractall(src, members=members, filter="data")
            else:
                tf.extractall(src, members=members)
        main = find_main_tex(src)
        if main is None:
            return None
        (out / "paper.tex").write_text(flatten_tex(main, main.parent), encoding="utf-8")
        return "paper.tex"
    except tarfile.ReadError:
        pass
    try:
        raw = gzip.decompress(data)
    except OSError:
        raw = data
    if raw.startswith(b"%PDF"):
        (out / "paper.pdf").write_bytes(raw)
        return pdf_to_text(out / "paper.pdf") or "paper.pdf"
    text = raw.decode("utf-8", errors="replace")
    if "\\documentclass" in text or "\\begin{document}" in text:
        (out / "paper.tex").write_text(text, encoding="utf-8")
        return "paper.tex"
    return None


def pdf_to_text(pdf: Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    txt = pdf.with_suffix(".txt")
    r = subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], capture_output=True)
    return txt.name if r.returncode == 0 and txt.exists() else None


# --------------------------------------------------------------------------- bib & index

def bibtex(pid: str, meta: dict) -> str:
    authors = " and ".join(meta.get("authors") or []) or "Unknown"
    fields = {
        "title": "{" + meta.get("title", pid) + "}",
        "author": authors,
        "year": str(meta.get("year") or ""),
        "url": meta.get("url") or "",
    }
    if meta.get("arxiv"):
        fields.update(eprint=meta["arxiv"], archivePrefix="arXiv")
    if meta.get("doi"):
        fields["doi"] = meta["doi"]
    if meta.get("venue") and meta.get("venue") != "arXiv":
        fields["note"] = meta["venue"]
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items() if v)
    kind = "article" if meta.get("arxiv") or meta.get("doi") else "misc"
    return f"@{kind}{{{pid},\n{body}\n}}\n"


def upsert_bib(root: Path, pid: str, meta: dict) -> None:
    path = root / "papers" / "refs.bib"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if re.search(r"@\w+\{" + re.escape(pid) + r",", text):
        return
    with path.open("a", encoding="utf-8") as f:
        f.write(("\n" if text and not text.endswith("\n\n") else "") + bibtex(pid, meta))


def upsert_index(root: Path, pid: str, fields: dict) -> dict:
    path = root / "papers" / "index.jsonl"
    rows = read_jsonl(path)
    for r in rows:
        if r.get("id") == pid:
            for k, v in fields.items():
                if v not in (None, "", []) and k not in ("pass", "relevance", "tags"):
                    r[k] = v
            if fields.get("tags"):
                r["tags"] = sorted(set(r.get("tags") or []) | set(fields["tags"]))
            write_jsonl(path, rows)
            return r
    rec = {"id": pid, "pass": 0, "relevance": None, "tags": [], **{k: v for k, v in fields.items() if v not in (None, "")}}
    append_jsonl(path, rec)
    return rec


# --------------------------------------------------------------------------- main

def fetch_one(root: Path, source: str, meta_only: bool, prefer_pdf: bool, tags: list[str]) -> dict:
    raw_root = root / "papers" / "raw"
    aid = parse_arxiv_id(source)
    if aid:
        meta = arxiv_metadata(aid)
        pid = paper_id_for_arxiv(aid)
        text_file = None
        if not meta_only:
            out = raw_root / pid
            out.mkdir(parents=True, exist_ok=True)
            if not prefer_pdf:
                try:
                    text_file = store_arxiv_source(http_get(f"https://arxiv.org/e-print/{aid}"), out)
                except Exception as e:  # noqa: BLE001 - fall back to PDF on any source problem
                    print(f"note: {aid}: LaTeX source unavailable ({e}); trying PDF", file=sys.stderr)
            if text_file is None:
                (out / "paper.pdf").write_bytes(http_get(f"https://arxiv.org/pdf/{aid}"))
                text_file = pdf_to_text(out / "paper.pdf") or "paper.pdf"
        fields = {**meta, "tags": tags, "fetched_at": now_iso()}
        if text_file:
            fields["fulltext"] = f"papers/raw/{pid}/{text_file}"
    else:
        p = Path(source).expanduser()
        if p.is_file():
            pid = slugify(p.stem)
            out = raw_root / pid
            out.mkdir(parents=True, exist_ok=True)
            dest = out / f"paper{p.suffix.lower()}"
            shutil.copyfile(p, dest)
            name = dest.name
            if dest.suffix == ".pdf":
                name = pdf_to_text(dest) or name
            fields = {"title": p.stem, "url": None, "tags": tags, "fetched_at": now_iso(),
                      "fulltext": f"papers/raw/{pid}/{name}"}
            meta = {"title": p.stem}
        elif re.match(r"https?://", source):
            name = Path(urllib.parse.urlparse(source).path).name or "paper"
            pid = slugify(Path(name).stem)
            out = raw_root / pid
            out.mkdir(parents=True, exist_ok=True)
            data = http_get(source)
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"{source} is not a PDF; save the page text to a file and pass the file instead")
            (out / "paper.pdf").write_bytes(data)
            tf = pdf_to_text(out / "paper.pdf") or "paper.pdf"
            meta = {"title": Path(name).stem, "url": source}
            fields = {**meta, "tags": tags, "fetched_at": now_iso(), "fulltext": f"papers/raw/{pid}/{tf}"}
        else:
            raise RuntimeError(f"not an arXiv id, URL or existing file: {source}")
    rec = upsert_index(root, pid, fields)
    upsert_bib(root, pid, meta)
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="+")
    ap.add_argument("--root", help="research/ directory")
    ap.add_argument("--meta-only", action="store_true", help="metadata + index only, no full text")
    ap.add_argument("--pdf", action="store_true", help="skip LaTeX source, fetch the PDF")
    ap.add_argument("--tags", default="", help="comma-separated tags to add")
    args = ap.parse_args()
    root = find_root(args.root)
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    failed = 0
    for s in args.sources:
        try:
            rec = fetch_one(root, s, args.meta_only, args.pdf, tags)
            print(f"ok  {rec['id']}\t{rec.get('fulltext', '-')}\t{rec.get('title', '')[:80]}")
        except Exception as e:  # noqa: BLE001 - report and continue with the other sources
            failed += 1
            print(f"ERR {s}\t{e}", file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
