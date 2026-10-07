#!/usr/bin/env python3
"""Show or set the language of the research workspace.

usage:
  lang.py get [--default CODE]     print the language code that applies (PROJECT.md, then --default, then en)
  lang.py name [--default CODE]    print the language's own name, e.g. 日本語
  lang.py set LANG                 write `language:` into research/PROJECT.md (accepts 'Vietnamese', 'fr', '日本語' ...)
  lang.py list                     supported languages

Supported: en (default), vi, zh (Simplified Chinese), fr, ja.
"""

from __future__ import annotations

import argparse

from _lab import (DEFAULT_LANG, LANG_NAMES, SUPPORTED_LANGS, die, find_root, normalize_lang,
                  resolve_language, set_frontmatter_field)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("get", "name"):
        p = sub.add_parser(name)
        p.add_argument("--default", help="plugin-level default (the user_config.language option)")
    st = sub.add_parser("set")
    st.add_argument("lang")
    sub.add_parser("list")
    a = ap.parse_args()

    if a.cmd == "list":
        for code in SUPPORTED_LANGS:
            print(f"{code}\t{LANG_NAMES[code]}{'\t(default)' if code == DEFAULT_LANG else ''}")
        return
    if a.cmd == "set":
        code = normalize_lang(a.lang)
        if not code:
            die(f"unsupported language '{a.lang}'. Supported: {', '.join(SUPPORTED_LANGS)}")
        root = find_root(a.root)
        set_frontmatter_field(root / "PROJECT.md", "language", code)
        print(f"language: {code} ({LANG_NAMES[code]}) written to {root / 'PROJECT.md'}")
        return
    root = find_root(a.root, must_exist=False)
    code = resolve_language(root if (root / "PROJECT.md").exists() else None, default=a.default)
    print(code if a.cmd == "get" else LANG_NAMES[code])


if __name__ == "__main__":
    main()
