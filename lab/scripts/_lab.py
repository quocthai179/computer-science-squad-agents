"""Shared helpers for the lab plugin scripts. Python stdlib only.

Every script finds the research workspace the same way:
  1. --root <dir> (the research/ directory itself), if given
  2. $LAB_RESEARCH_DIR, if set
  3. walk up from the current directory looking for research/PROJECT.md
  4. fall back to ./research
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = PLUGIN_ROOT / "templates"

# --------------------------------------------------------------------------- languages
# Instructions (agents, skills, playbooks, script output) are English. What is localised is the
# content written into the workspace: templates and everything the agents write from them.
# Machine keys (frontmatter keys, JSONL fields, file names, ids, [@..]/[run:..] anchors) never change.
SUPPORTED_LANGS = ("en", "vi", "zh", "fr", "ja")
DEFAULT_LANG = "en"
LANG_NAMES = {"en": "English", "vi": "Tiếng Việt", "zh": "中文（简体）", "fr": "Français", "ja": "日本語"}
_LANG_ALIASES = {
    "en": "en", "eng": "en", "english": "en", "en-us": "en", "en-gb": "en",
    "vi": "vi", "vie": "vi", "vietnamese": "vi", "tiếng việt": "vi", "tieng viet": "vi", "vi-vn": "vi",
    "zh": "zh", "chinese": "zh", "中文": "zh", "汉语": "zh", "漢語": "zh", "zh-cn": "zh", "zh-hans": "zh",
    "zh-tw": "zh", "zh-hant": "zh", "zh-sg": "zh", "simplified chinese": "zh", "mandarin": "zh",
    "fr": "fr", "fra": "fr", "french": "fr", "français": "fr", "francais": "fr", "fr-fr": "fr", "fr-ca": "fr",
    "ja": "ja", "jp": "ja", "jpn": "ja", "japanese": "ja", "日本語": "ja", "ja-jp": "ja",
}


def normalize_lang(value) -> str | None:
    """'Vietnamese', 'vi-VN', 'français', '日本語' ... -> 'vi'/'fr'/'ja'; None when unknown or blank."""
    if value is None:
        return None
    key = str(value).strip().strip("\"'").lower().replace("_", "-")
    return _LANG_ALIASES.get(key)


def resolve_language(root: Path | None, default: str | None = None, explicit: str | None = None) -> str:
    """Order: explicit value -> `language:` in research/PROJECT.md -> default -> English."""
    # an unset plugin option reaches skills and agents as the literal text `${user_config.language}`
    if default is not None and ("${" in str(default) or "user_config" in str(default)):
        default = None
    for cand in (explicit, (read_frontmatter(root / "PROJECT.md").get("language") if root else None), default):
        if cand is None or is_blank(cand):
            continue
        code = normalize_lang(cand)
        if code:
            return code
        die(f"unsupported language '{cand}'. Supported: {', '.join(SUPPORTED_LANGS)}")
    return DEFAULT_LANG


def template_path(name: str, lang: str = DEFAULT_LANG) -> Path:
    """templates/<lang>/<name>, falling back to English when a translation is missing."""
    p = TEMPLATES / lang / name
    return p if p.exists() else TEMPLATES / DEFAULT_LANG / name


# --------------------------------------------------------------------------- workspace

def find_root(explicit: str | None = None, must_exist: bool = True) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
    elif os.environ.get("LAB_RESEARCH_DIR"):
        root = Path(os.environ["LAB_RESEARCH_DIR"]).expanduser().resolve()
    else:
        root = None
        here = Path.cwd().resolve()
        for d in [here, *here.parents]:
            if (d / "research" / "PROJECT.md").is_file():
                root = d / "research"
                break
        if root is None:
            root = here / "research"
    if must_exist and not root.is_dir():
        die(f"research workspace not found at {root}. Run /lab:setup first.")
    return root


def exp_dir(root: Path, exp_id: str) -> Path:
    d = root / "experiments" / exp_id
    if not d.is_dir():
        die(f"experiment '{exp_id}' not found at {d}")
    return d


# --------------------------------------------------------------------------- io

def die(msg: str, code: int = 2) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def now_iso() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def today() -> str:
    return _dt.date.today().isoformat()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with path.open(encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warning: {path}:{n}: bad JSON line skipped ({e})", file=sys.stderr)
    return out


def append_jsonl(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, recs: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def generated_header(script: str, source: str) -> str:
    return (f"<!-- generated by {script} from {source} at {now_iso()}. "
            f"Do not edit by hand; re-run the script. -->\n")


# --------------------------------------------------------------------------- frontmatter

_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)


def _parse_scalar(v: str) -> Any:
    v = v.strip()
    if not v:
        return ""
    if v[0] in "\"'" and v[-1] == v[0] and len(v) >= 2:
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x) for x in _split_list(inner)]
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d*(e-?\d+)?", low):
        return float(v)
    return v


def _split_list(s: str) -> list[str]:
    parts, cur, q = [], "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
        elif ch in "\"'":
            q = ch
            cur += ch
        elif ch == ",":
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a flat YAML subset: `key: value`, `[a, b]` lists, `- item` lists,
    and `# comments` after unquoted values. Returns (meta, body)."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, Any] = {}
    last_key = None
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"\s+-\s+(.*)", line) or re.match(r"-\s+(.*)", line)
        if item and last_key is not None:
            if not isinstance(meta.get(last_key), list):
                meta[last_key] = []
            meta[last_key].append(_parse_scalar(_strip_comment(item.group(1))))
            continue
        kv = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)", line)
        if kv:
            last_key = kv.group(1)
            meta[last_key] = _parse_scalar(_strip_comment(kv.group(2)))
    return meta, text[m.end():]


def _strip_comment(v: str) -> str:
    """Drop a trailing `# comment`, also after a closing quote or bracket (`[a, b]   # note`)."""
    v = v.strip()
    if not v or v.startswith("#"):
        return ""
    if v[0] in "\"'":
        end = v.find(v[0], 1)
        return v[: end + 1] if end > 0 else v
    if v[:1] == "[":
        end = v.rfind("]", 0, v.find(" #") if " #" in v else len(v))
        return v[: end + 1] if end > 0 else v
    return re.sub(r"\s+#.*$", "", v)


def read_frontmatter(path: Path) -> dict:
    if not path.exists():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8"))[0]


def set_frontmatter_field(path: Path, key: str, value: str) -> None:
    """Replace (or add) one `key: value` line inside the frontmatter block."""
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        die(f"{path} has no frontmatter block")
    block = m.group(1)
    pat = re.compile(rf"^{re.escape(key)}\s*:.*$", re.M)
    if pat.search(block):
        block = pat.sub(f"{key}: {value}", block, count=1)
    else:
        block = block + f"\n{key}: {value}"
    path.write_text(f"---\n{block}\n---\n" + text[m.end():], encoding="utf-8")


def is_blank(v: Any) -> bool:
    """True for empty values and unfilled template placeholders like `<...>`."""
    if v is None:
        return True
    if isinstance(v, (list, tuple)):
        return len(v) == 0
    s = str(v).strip()
    return s == "" or bool(re.fullmatch(r"<[^>]*>|\.\.\.|TODO|TBD|\?+", s, re.I))


# --------------------------------------------------------------------------- ids

def slugify(s: str, maxlen: int = 60) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:maxlen].strip("-") or "item"


ARXIV_NEW = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
ARXIV_OLD = re.compile(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?")


def parse_arxiv_id(s: str) -> str | None:
    """Return a bare arXiv id (no version) from an id or arxiv.org URL, else None."""
    s = s.strip()
    m = re.search(r"arxiv\.org/(?:abs|pdf|e-print|html)/([^\s?#]+)", s)
    if m:
        s = m.group(1)
        if s.endswith(".pdf"):
            s = s[:-4]
    s = re.sub(r"^arxiv:", "", s, flags=re.I)
    m = ARXIV_NEW.fullmatch(s) or ARXIV_OLD.fullmatch(s)
    return m.group(1) if m else None


def paper_id_for_arxiv(aid: str) -> str:
    return aid.replace("/", "_")
