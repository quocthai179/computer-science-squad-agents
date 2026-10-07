#!/usr/bin/env python3
"""Lint a report, survey or FINDINGS file before it goes to review or to gate G5.

usage: lint_report.py FILE [FILE ...] [--root DIR] [--sources GLOB ...]
                      [--no-numbers] [--allow-novelty]

Errors (exit 1):
  placeholder   TODO/TBD/XXX/FIXME, "Conclusions Here", "[citation needed]", "???",
                and unfilled template slots such as <tên paper> or <result>
  number        a decimal or percentage that appears in no evidence file:
                experiments/*/tables/*.md, experiments/*/runs.jsonl metrics,
                papers/cards/*.md, surveys/*/evidence.jsonl, plus --sources
  novelty       "novel", "the first", "SOTA", "state of the art", "đầu tiên", "mới lạ",
                "chưa ai" ... unless the idea card named by `idea:` in the claims.md
                next to FILE has `closest_prior_work` filled in (or --allow-novelty)

Skip a single line with an HTML comment containing `lint-ignore`.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

from _lab import find_root, is_blank, read_frontmatter

PLACEHOLDER = [
    (re.compile(r"\b(TODO|TBD|FIXME|XXX)\b"), "placeholder marker"),
    (re.compile(r"conclusions?\s+here|insert\s+\w+(\s+\w+)?\s+here|lorem ipsum", re.I), "template filler"),
    (re.compile(r"\[(citation needed|cần dẫn nguồn|cite)\]", re.I), "missing citation"),
    (re.compile(r"\?\?\?"), "???"),
]
ANGLE = re.compile(r"<(?!!--)(?!/)([^<>\n]{1,80})>")
HTML_TAG = re.compile(
    r"^(a|abbr|b|br|center|code|dd|del|details|div|dl|dt|em|figcaption|figure|hr|i|img|ins|kbd|li|mark|ol|p|"
    r"picture|pre|q|s|samp|small|source|span|strong|sub|summary|sup|table|tbody|td|th|thead|tr|u|ul|var|video)"
    r"(\s+[a-zA-Z:-]+(=(\"[^\"]*\"|'[^']*'|\S+))?)*\s*/?$", re.I | re.A)

NOVELTY = re.compile(
    r"\bnovel(ty)?\b|\bthe first\b|\bfirst (to|work|method|approach|paper)\b|\bSOTA\b|"
    r"state[- ]of[- ]the[- ]art|\bunprecedented\b|\bgroundbreaking\b|"
    r"(công trình|phương pháp|nghiên cứu|cách tiếp cận|kết quả) đầu tiên|là đầu tiên|"
    r"mới lạ|chưa (ai|từng có ai|có công trình nào)|vượt (qua )?SOTA",
    re.I,
)

NUM = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)+|\d+)(\s?%)?(?![\w])")
STRIP = [
    re.compile(r"```.*?```", re.S),
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"\]\([^)]*\)"),                 # link targets
    re.compile(r"\[(?:@|run:|table:|fig:)[^\]]*\]"),  # citation / anchor brackets
    re.compile(r"https?://\S+"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"§\s*\d+(\.\d+)*"),
    re.compile(r"\b(Tab|Table|Fig|Figure|Eq|Section|Sec|Bảng|Hình|Mục|Phụ lục|Appendix)\.?\s*[A-Z]?\d+(\.\d+)*", re.I),
    re.compile(r"\bv\d+(\.\d+)+\b"),
    re.compile(r"\b\d{4}\.\d{4,5}(v\d+)?\b"),  # arXiv ids
    re.compile(r"\b[\w-]+-r\d{3}\b"),          # run ids
]


def mask(text: str) -> str:
    """Blank out non-prose spans while keeping offsets and line numbers."""
    for pat in STRIP:
        text = pat.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    return text


def interpretations(tok: str) -> list[float]:
    """Read a token both as 1,234.5 (English) and 1.234,5 (Vietnamese) notation.
    A thousands separator only counts when it forms proper 3-digit groups."""
    vals = []
    for dec, thou in ((".", ","), (",", ".")):
        if thou in tok and not re.fullmatch(rf"[1-9]\d{{0,2}}(\{thou}\d{{3}})+(\{dec}\d+)?", tok):
            continue
        s = tok.replace(thou, "")
        if s.count(dec) <= 1:
            try:
                vals.append(float(s.replace(dec, ".")))
            except ValueError:
                pass
    return vals


def decimals(tok: str, value: float) -> int:
    m = re.search(r"[.,](\d+)$", tok)
    if not m:
        return 0
    return len(m.group(1)) if value != int(value) or len(m.group(1)) != 3 else 0


def evidence_values(root: Path, extra: list[str]) -> list[float]:
    vals: list[float] = []

    def from_text(t: str) -> None:
        for m in NUM.finditer(t):
            vals.extend(interpretations(m.group(1)))

    files = glob.glob(str(root / "experiments" / "*" / "tables" / "*.md"))
    files += glob.glob(str(root / "papers" / "cards" / "*.md"))
    files += glob.glob(str(root / "surveys" / "*" / "evidence.jsonl"))
    for g in extra:
        files += glob.glob(g, recursive=True)
    for f in files:
        from_text(Path(f).read_text(encoding="utf-8", errors="replace"))
    for led in glob.glob(str(root / "experiments" / "*" / "runs.jsonl")):
        for line in Path(led).read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            vals.extend(float(v) for v in (rec.get("metrics") or {}).values() if isinstance(v, (int, float)))
    return vals


def number_ok(tok: str, pct: bool, evidence: list[float]) -> bool:
    for x in interpretations(tok):
        d = decimals(tok, x)
        for v in evidence:
            for cand in (v, v * 100, v / 100) if pct or d else (v,):
                if round(cand, d) == round(x, d):
                    return True
    return False


def should_check(tok: str, pct: bool) -> bool:
    if pct:
        return True
    vals = interpretations(tok)
    return bool(vals) and all(v != int(v) for v in vals)


def novelty_allowed(path: Path, root: Path) -> bool:
    claims = path.parent / "claims.md"
    idea = read_frontmatter(claims).get("idea") if claims.exists() else None
    if is_blank(idea):
        return False
    card = root / "ideas" / "cards" / f"{idea}.md"
    return card.exists() and not is_blank(read_frontmatter(card).get("closest_prior_work"))


def lint(path: Path, root: Path, evidence: list[float] | None, allow_novelty: bool) -> list[str]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    masked = mask(raw)
    raw_lines = raw.splitlines()
    errs: list[str] = []
    nov_ok = allow_novelty or novelty_allowed(path, root)
    for n, line in enumerate(masked.splitlines(), 1):
        if "lint-ignore" in (raw_lines[n - 1] if n - 1 < len(raw_lines) else ""):
            continue
        for pat, what in PLACEHOLDER:
            for m in pat.finditer(line):
                errs.append(f"{path}:{n}: placeholder: {what} '{m.group(0)}'")
        for m in ANGLE.finditer(line):
            inner = m.group(1).strip()
            if not HTML_TAG.match(inner) and not re.fullmatch(r"https?://\S+|[\w.+-]+@[\w.-]+", inner):
                errs.append(f"{path}:{n}: placeholder: unfilled slot '<{inner}>'")
        if not nov_ok:
            for m in NOVELTY.finditer(line):
                if m.group(0).strip():
                    errs.append(f"{path}:{n}: novelty: '{m.group(0).strip()}' needs a checked closest prior "
                                f"work (idea card `closest_prior_work`) or must be removed")
        if evidence is not None:
            for m in NUM.finditer(line):
                tok, pct = m.group(1), bool(m.group(2))
                if should_check(tok, pct) and not number_ok(tok, pct, evidence):
                    errs.append(f"{path}:{n}: number: '{tok}{m.group(2) or ''}' is not in any table, ledger or "
                                f"paper card; generate it with ledger.py/stats.py or cite its source")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--root")
    ap.add_argument("--sources", nargs="*", default=[], help="extra evidence globs")
    ap.add_argument("--no-numbers", action="store_true")
    ap.add_argument("--allow-novelty", action="store_true")
    args = ap.parse_args()
    root = find_root(args.root)
    evidence = None if args.no_numbers else evidence_values(root, args.sources)
    errs = []
    for f in args.files:
        errs += lint(Path(f), root, evidence, args.allow_novelty)
    for e in errs:
        print(e)
    print(f"{len(errs)} problem(s)" if errs else "OK: no placeholders, unsourced numbers or unchecked novelty claims")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
