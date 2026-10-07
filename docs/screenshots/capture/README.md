# Regenerating the screenshots

The screenshots in `docs/screenshots/` come from real runs. Claude Code ran with the `lab` plugin inside a pseudo-terminal, [pyte](https://github.com/selectel/pyte) emulated the screen, and each chosen frame was rendered to HTML and photographed with Playwright. Nothing was typed into or edited on the captured screens. The only rendering change is that the input-box row is drawn grey, because pyte drops the "dim" attribute that Claude Code uses for its suggested next prompt.

| Image | What ran | Input |
|---|---|---|
| `critique-running.png`, `critique-verdict.png` | `/lab:critique research/experiments/e001-grm/FINDINGS.md` | `lab/evals/critique-planted-bugs/scaffold.sh`: a report with five planted defects |
| `read-running.png`, `read-card.png` | `/lab:read-paper papers-inbox/toy-paper.md` | `lab/evals/read-paper-card/scaffold.sh`: a synthetic paper written for the eval |
| `guardrails.png`, `stats.png` | `runwrap.py`, `ledger.py`, `stats.py` in bash | `ls-project/`: a toy pure-Python logistic regression |

## Steps

```bash
pip install pyte                     # plus Node with playwright and a Chromium
mkdir grm-project && (cd grm-project && bash ../lab/evals/critique-planted-bugs/scaffold.sh && git init -q)

# Claude Code session (accepts the trust dialog, types the prompt, snapshots every 2 s)
python3 tui_capture.py --plugin-dir ./lab --cwd grm-project --out frames-critique \
  --cols 118 --rows 46 --prompt "/lab:critique research/experiments/e001-grm/FINDINGS.md"

# bash session for the guardrail images (needs ls-project/ with train.py and research/experiments/e001-ls/PLAN.md)
LAB_SCRIPTS=$PWD/lab/scripts python3 shell_capture.py --cwd ls-project --out guard.json --cmds cmds-guard.txt --rows 30

# render a frame
python3 render_frame.py frames-critique/frame-0040.json out.html --trim --dim-input --title "~/grm-project — claude"
node shot.js out.html out.png
```

Fonts: Liberation Mono (it has the precomposed Vietnamese glyphs), with DejaVu Sans Mono as fallback for block characters.
