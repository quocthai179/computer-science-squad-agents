#!/usr/bin/env python3
"""Lint a report, survey or FINDINGS file before it goes to review or to gate G5.

usage: lint_report.py FILE [FILE ...] [--root DIR] [--sources GLOB ...]
                      [--no-numbers] [--allow-novelty]

Errors (exit 1):
  placeholder   TODO/TBD/XXX/FIXME, "Conclusions Here", "[citation needed]", "???",
                and unfilled template slots such as <paper title> or <result>
  number        a decimal or percentage that appears in no evidence file:
                experiments/*/tables/*.md, experiments/*/runs.jsonl metrics,
                papers/cards/*.md, surveys/*/evidence.jsonl, plus --sources
  novelty       "novel", "the first", "SOTA", "state of the art" and their Vietnamese, Chinese,
                French and Japanese equivalents (đầu tiên, 首次, le premier, 初めて ...) unless the idea card named by `idea:` in the claims.md
                next to FILE has `closest_prior_work` filled in (or --allow-novelty)

Skip a single line with an HTML comment containing `lint-ignore`.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

from _lab import find_root, is_blank, read_frontmatter

PLACEHOLDER = [
    (re.compile(r"\b(TODO|TBD|FIXME|XXX)\b"), "placeholder marker"),
    (re.compile(r"conclusions?\s+here|insert\s+\w+(\s+\w+)?\s+here|lorem ipsum|kết luận ở đây|"
                r"此处(填写|填入|添加)|在此(填写|填入)|待(补充|填写|完善)|"
                r"conclusions?\s+ici|à (compléter|remplir)\b|insérer\s+\w+(\s+\w+)?\s+ici|"
                r"ここに(結論|記入|記載|入力)|(要記入|未記入|記入予定)", re.I), "template filler"),
    (re.compile(r"\[(citation needed|cần dẫn nguồn|cite|citation nécessaire|source nécessaire|需要引用|引用待补|"
                r"要出典|引用必要)\]", re.I), "missing citation"),
    (re.compile(r"\?\?\?"), "???"),
]
ANGLE = re.compile(r"<(?!!--)(?!/)([^<>\n]{1,80})>")
HTML_TAG = re.compile(
    r"^(a|abbr|b|br|center|code|dd|del|details|div|dl|dt|em|figcaption|figure|hr|i|img|ins|kbd|li|mark|ol|p|"
    r"picture|pre|q|s|samp|small|source|span|strong|sub|summary|sup|table|tbody|td|th|thead|tr|u|ul|var|video)"
    r"(\s+[a-zA-Z:-]+(=(\"[^\"]*\"|'[^']*'|\S+))?)*\s*/?$", re.I | re.A)

NOVELTY = re.compile(
    # English
    r"\bnovel(ty)?\b|\bthe first\b|\bfirst (to|work|method|approach|paper)\b|\bSOTA\b|"
    r"state[- ]of[- ]the[- ]art|\bunprecedented\b|\bgroundbreaking\b|"
    # Vietnamese
    r"(công trình|phương pháp|nghiên cứu|cách tiếp cận|kết quả) đầu tiên|là đầu tiên|"
    r"mới lạ|chưa (ai|từng có ai|có công trình nào)|vượt (qua )?SOTA|"
    # Chinese
    r"首(次|个|创)|第一个|前所未有|全新的?方法|最先进|最新水平|开创性|开拓性|颠覆性|新颖|无人(做过|研究)|"
    # French (\"état de l'art\" alone means \"literature review\", so only the claims are flagged)
    r"\bnovat(eur|eurs|rice|rices)\b|\binédit(e|s|es)?\b|\ble premier\b|\bla première\b|\bpremier(e)? à\b|"
    r"\bsans précédent\b|\brévolutionnaire\b|(dépasse|surpasse|bat|nouvel) l[’']état de l[’']art|"
    r"nouvel état de l[’']art|"
    # Japanese
    r"初(めて|の)|新規(性|な手法)|斬新|画期的|前例(のない|がない)|最先端|世界初|誰も(行って|試して)いない|"
    r"SOTAを(上回|超え|更新)",
    re.I,
)

# ASCII-only boundaries: in Chinese and Japanese a digit sits directly next to letters (精度は0.913です).
# The percent sign may follow a space, a no-break space or a narrow no-break space (French: "12,5 %"),
# or be full-width (％).
NUM = re.compile(r"(?<![A-Za-z0-9_.,])(\d+(?:[.,]\d+)+|\d+)([\s\u00a0\u202f]?[%％])?(?![A-Za-z0-9_])")
_FR_THOUSANDS = re.compile(r"(?<=\d)[\u00a0\u202f](?=\d{3}(?!\d))|(?<![\d.,])(\d{1,3}) (?=\d{3}[.,]\d)")


def norm_numbers(line: str) -> str:
    """Full-width digits to ASCII, and French '1 234,5' (space / no-break space grouping) to '1234,5'."""
    line = unicodedata.normalize("NFKC", line)
    line = _FR_THOUSANDS.sub(lambda m: m.group(1) or "", line)
    return line
STRIP = [
    re.compile(r"```.*?```", re.S),
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"\]\([^)]*\)"),                 # link targets
    re.compile(r"\[(?:@|run:|table:|fig:)[^\]]*\]"),  # citation / anchor brackets
    re.compile(r"https?://\S+"),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"§\s*\d+(\.\d+)*"),
    re.compile(r"\b(Tab|Table|Tableau|Fig|Figure|Eq|Équation|Section|Sec|Bảng|Hình|Mục|Phụ lục|Appendix|Annexe)"
               r"\.?\s*[A-Z]?\d+(\.\d+)*", re.I),
    re.compile(r"(表|图|圖|図|第|附录|附錄|付録|節|章)\s*[A-Z]?\d+(\.\d+)*"),
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
        for m in NUM.finditer(norm_numbers(t)):
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
            for m in NUM.finditer(norm_numbers(line)):
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
