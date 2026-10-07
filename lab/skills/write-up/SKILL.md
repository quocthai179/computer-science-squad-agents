---
name: write-up
description: Write up research (course report, paper draft, technical blog) starting from an approved claims.md (G4), with writer drafting, scripts checking citations and numbers, skeptic checking claims against evidence, and an explain-back before submission (G5). Use for "write the report", "write the paper", "write up the results". Also - viết báo cáo, viết paper; 撰写报告, 写论文, 整理实验结果; rédiger le rapport, rédiger l'article; レポートを書く, 論文を書く, 結果をまとめる.
argument-hint: "<course-report|paper-draft|blog> [slug]"
---

# /lab:write-up

You are the Lead. Claims first, prose second. `writer` is the only writer.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Rules that always hold:
- No prose before the user approves `claims.md` (G4).
- A claim without enough evidence goes back to experiments; it is not papered over.
- Numbers only from script-generated `tables/`; citations must resolve; no placeholders; at most 2 review rounds.

Input: $ARGUMENTS

## Steps

1. Read `research/PROJECT.md` (language, constraints on AI use), ${CLAUDE_PLUGIN_ROOT}/playbooks/writing.md, the relevant `FINDINGS.md` files, surveys and cards. Choose `<slug>`; folder `research/reports/<slug>/`.
2. Write `claims.md` with the user from ${CLAUDE_PLUGIN_ROOT}/templates/<language>/claims.md: 1–3 claims, each pointing to `[run:...]`, `tables/...`, `figures/...` or `[@paper-id, location]`, with status `supported|partial|unsupported` and limits; `audience`; `idea:` if the report comes from an idea card. You check that each pointer exists.
3. **G4.** The user approves `claims.md` → set `status: approved`, record in `research/decisions.md`. A claim marked `unsupported` that the user still wants to keep: suggest running more experiments, or demoting it to an "open question".
4. Call `lab:writer` with kind `report`: `inputs: claims.md` and every file it points to; `output: research/reports/<slug>/draft.md`; the report kind from the argument; the language from `PROJECT.md` (or the language the claims or the user ask for).
5. Run:
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/cite_check.py research/reports/<slug>/draft.md`
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py research/reports/<slug>/draft.md`
   Errors: send `lab:writer` back with the script output. Network blocked: run `cite_check.py --offline` and tell the user the online part was not checked.
6. Call `lab:skeptic` with type `draft`, giving the paths of `draft.md` and `claims.md`. Blocking issues: `lab:writer` fixes, then skeptic round 2. Disagreement after round 2: the user decides.
7. When clean: `lab:writer` produces `final.md` (a clean copy of the draft). Run the two scripts again on `final.md`.
8. **G5. Explain-back.** Ask the user 3 questions about the report itself: why the main claim holds; what would refute it; the biggest limitation. Any part the user cannot explain: mark it and suggest they rewrite it themselves. Remind them to state the level of AI assistance as the course or venue requires.
9. Record in `research/decisions.md` (G5) and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source write-up "<slug>: <status>"`.
