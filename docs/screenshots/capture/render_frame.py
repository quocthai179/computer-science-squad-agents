#!/usr/bin/env python3
"""Render a pyte frame JSON (from tui_capture.py) to a terminal-window HTML page.

usage: render_frame.py FRAME.json OUT.html [--title T] [--crop-top N] [--crop-bottom N] [--trim]
"""
import argparse, html, json, unicodedata

NAMED = {
    "black": "#1d1f21", "red": "#e06c75", "green": "#98c379", "yellow": "#e5c07b", "blue": "#61afef",
    "magenta": "#c678dd", "cyan": "#56b6c2", "white": "#d7dae0", "brightblack": "#7f848e",
    "brightred": "#ff7b86", "brightgreen": "#b5e890", "brightyellow": "#ffd88a", "brightblue": "#82c4ff",
    "brightmagenta": "#de9cf0", "brightcyan": "#7fd7e3", "brightwhite": "#ffffff",
    "bfightmagenta": "#de9cf0", "brown": "#e5c07b",
}
FG, BG = "#d7dae0", "#16181d"


def color(c, default):
    if c in (None, "default"):
        return default
    if c in NAMED:
        return NAMED[c]
    if len(c) == 6:
        try:
            int(c, 16)
            return "#" + c
        except ValueError:
            pass
    return default


ap = argparse.ArgumentParser()
ap.add_argument("frame")
ap.add_argument("out")
ap.add_argument("--title", default="claude — lab")
ap.add_argument("--crop-top", type=int, default=0)
ap.add_argument("--crop-bottom", type=int, default=0)
ap.add_argument("--trim", action="store_true", help="drop blank rows at the end")
ap.add_argument("--hide-row-containing", action="append", default=[])
ap.add_argument("--dim-input", action="store_true")
a = ap.parse_args()

rows = json.load(open(a.frame))["rows"]
rows = rows[a.crop_top: len(rows) - a.crop_bottom if a.crop_bottom else None]
rows = [r for r in rows if not any(h in "".join(c[0] for c in r) for h in a.hide_row_containing)]
if a.trim:
    while rows and not "".join(c[0] for c in rows[-1]).strip():
        rows.pop()
# collapse runs of blank rows to one
_c, _blank = [], 0
for r in rows:
    b = not "".join(c[0] for c in r).strip()
    _blank = _blank + 1 if b else 0
    if _blank <= 1:
        _c.append(r)
rows = _c
# the input box row (between the last two horizontal rules) only ever holds the TUI's dimmed
# suggestion in these captures (nothing was typed); pyte drops the dim attribute, so grey it out
rules = [i for i, r in enumerate(rows) if "".join(c[0] for c in r).strip().startswith("────")]
dim_rows = set(range(rules[-2] + 1, rules[-1])) if len(rules) >= 2 and a.dim_input else set()

lines = []
for ri, r in enumerate(rows):
    out, cur, buf = [], None, ""
    for ch, fg, bg, bold, it, rev in r:
        ch = unicodedata.normalize("NFC", ch or " ")
        f, b = color(fg, FG), color(bg, "transparent")
        if ri in dim_rows:
            f = "#6b7280"
        if rev:
            f, b = (b if b != "transparent" else BG), f
        style = f"color:{f};" + (f"background:{b};" if b != "transparent" else "") + \
                ("font-weight:700;" if bold else "") + ("font-style:italic;" if it else "")
        if style != cur:
            if buf:
                out.append(f'<span style="{cur}">{html.escape(buf)}</span>')
            cur, buf = style, ""
        buf += ch or " "
    if buf:
        out.append(f'<span style="{cur}">{html.escape(buf.rstrip())}</span>')
    lines.append("".join(out) or "&nbsp;")

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body{{margin:0;background:#0b0c10;padding:28px;display:inline-block}}
.win{{background:{BG};border-radius:12px;box-shadow:0 18px 50px rgba(0,0,0,.55);overflow:hidden;border:1px solid #2a2d35;display:inline-block}}
.bar{{height:34px;background:#23262e;display:flex;align-items:center;padding:0 14px;gap:8px;position:relative}}
.dot{{width:12px;height:12px;border-radius:50%}}
.title{{position:absolute;left:0;right:0;text-align:center;color:#9aa0ab;font:13px Inter,sans-serif}}
pre{{margin:0;padding:14px 18px 18px;font:14.5px/1.38 'Liberation Mono','DejaVu Sans Mono',monospace;color:{FG};white-space:pre}}
</style></head><body><div class="win"><div class="bar"><span class="dot" style="background:#ff5f57"></span>
<span class="dot" style="background:#febc2e"></span><span class="dot" style="background:#28c840"></span>
<div class="title">{html.escape(a.title)}</div></div><pre>{chr(10).join(lines)}</pre></div></body></html>"""
open(a.out, "w").write(page)
