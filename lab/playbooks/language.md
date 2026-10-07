# Language

The plugin supports five languages: **English (`en`, the default), Vietnamese (`vi`), Chinese (`zh`, Simplified), French (`fr`) and Japanese (`ja`)**.

## What is localised and what is not

| Localised (follows the project language) | Never translated |
|---|---|
| Content of everything you write into `research/`: `PROJECT.md`, paper cards, idea cards, `PLAN.md`, `FINDINGS.md`, `claims.md`, surveys, reviews, reports, retros, notebook entries | Frontmatter **keys** and their fixed values (`status: approved`, `label: safe`, `verdict: reject`, `stage: exploration`, `pass: 2`) |
| Headings and prose of the templates (`templates/<lang>/`) | JSONL field names, file and directory names, ids (`e001-ls`, `i003-...`), `[@paper-id, loc]` and `[run:<id>]` anchors |
| Your replies to the user | Code, commands, metric names printed as `LAB_METRIC name=value` |

Instructions, playbooks and the output of the scripts are in English. Relay script messages to the user in the user's language.

## Which language to use

Resolve in this order and stop at the first hit:

1. `language:` in `research/PROJECT.md` (blank or a placeholder counts as unset).
2. The plugin option, written `${user_config.language}` in skills and agents. Claude Code substitutes it only after the user has saved a value; while it is unset the text stays as the literal `${user_config.language}`, which you treat as unset.
3. English.

`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lang.py get --default '${user_config.language}'` does exactly this (it ignores an unresolved placeholder). `lang.py set <lang>` changes the project language.

**Replies in chat** follow the language the user writes in, even when it differs from the project language. If the user writes in a language outside the five, answer in it if you can, but write workspace files in the project language and say so once.

**Handoff.** The Lead puts `language: <code>` in every TASK BRIEF. A subagent without that line resolves the language itself (steps 1–3).

## Writing in a non-English language

- Use the template of that language (`templates/<lang>/<name>`); the Lead or the script has already placed it. Keep its headings; they are translated and the structure is identical across languages.
- Keep widely used English ML terms as they are when that is normal practice in the language (baseline, ablation, seed, fine-tuning, loss, leakage, checkpoint, benchmark, prompt). Translate everything else.
- Quotes from papers are verbatim in the paper's own language, at most 25 words, never translated inside quotation marks. Put your translation or paraphrase outside the quotes.
- Chinese means Simplified characters unless `PROJECT.md` says otherwise. Japanese uses the polite form (です・ます). French uses the formal register (vous). Vietnamese follows the register of the user's notes.
- Numbers: keep the decimal separator exactly as it appears in the tables the scripts generate (`0.913`). Copy numbers; never retype them in a different convention. `lint_report.py` understands `0.913`, `0,913`, `12,5 %`, `12.5%`, `１２．５％` and `1 234,5`.
- Do not mix languages inside one sentence beyond the English terms above.
- A report in a different language from the project (for example an English paper draft in a Vietnamese project) is allowed when `claims.md` or the TASK BRIEF says so. The claims, evidence pointers and anchors stay the same.

## Style skills

If the user has an installed skill for the style of reports in that language (for example a topic-research-report skill for Vietnamese course reports), follow it for the prose of `/lab:write-up`. The plugin's own rules (claims first, anchors, numbers from tables) still win.

## Adding a language

1. Add the code to `SUPPORTED_LANGS`, `LANG_NAMES` and `_LANG_ALIASES` in `scripts/_lab.py`.
2. Create `templates/<lang>/` with all 13 templates (the test `tests/test_i18n.py` checks that frontmatter keys, placeholders, heading counts and checklists match English).
3. Add the language's novelty claims, placeholders and the "Next steps" heading to `lint_report.py` and `retro_digest.py`, with tests.
4. Add trigger keywords to the skill descriptions and a `README.<lang>.md`.
