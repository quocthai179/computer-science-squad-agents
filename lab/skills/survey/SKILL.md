---
name: survey
description: Sourced literature survey of an AI/ML topic with a squad of agents (parallel scouts, readers, one writer, a skeptic). Use for "survey", "literature review", "state of the art", "find papers on", "related work" of a topic; not for a single factual question. Also - khảo sát, tổng quan nghiên cứu, tìm paper về; 文献综述, 调研, 查找论文, 研究现状; revue de littérature, état de l'art, chercher des articles sur; 文献調査, サーベイ, 先行研究, 論文を探す.
argument-hint: "<topic> [--quick]"
---

# /lab:survey

You are the Lead. You coordinate; you do not read papers or write the survey yourself.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Rules that always hold:
- Every statement in the survey has an anchor `[paper-id, location in paper]`.
- At most 5 scouts, at most 1 extra search round, at most 1 skeptic round.
- All handoffs go through files per ${CLAUDE_PLUGIN_ROOT}/playbooks/handoff.md. Read in parallel, write sequentially.
- If subagents cannot be called, work sequentially with the same playbook and say so.

Topic: $ARGUMENTS

## Steps

1. Read `research/PROJECT.md` and `research/lessons/LESSONS.md`. No workspace: tell the user to run `/lab:setup` and stop.
2. Ambiguous topic: ask at most 2 questions. With `--quick`: answer yourself in 10 tool calls (WebSearch, WebFetch), write `research/surveys/<slug>/quick.md` with sources, and skip the steps below.
3. Choose `<slug>`. Split the topic into 3–5 **non-overlapping** angles (for example: foundations; main methods; benchmarks and evaluation; limits and criticism; the last 12 months). Write `research/surveys/<slug>/angles.md`: for each angle one question and its boundary with the others. Budgets per ${CLAUDE_PLUGIN_ROOT}/playbooks/principles.md: narrow topic 2–3 scouts × 12 tool calls; broad 4–5 scouts × 15.
4. Call subagent `lab:scout` **in parallel**, one TASK BRIEF per angle:
   - `output: research/surveys/<slug>/scout-<angle>.jsonl` (and `scout-<angle>.md`);
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/reading.md`;
   - `inputs: research/papers/index.jsonl` (to avoid duplicates);
   - `boundaries`: the other angles belong to other scouts.
5. Merge and de-duplicate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/paper_index.py merge research/surveys/<slug>/scout-*.jsonl --tag survey:<slug>`. Review with `paper_index.py list --tag survey:<slug> --min-relevance 2`.
   An angle whose RECEIPT is `partial` or that has too few papers gets **one** extra scout round.
6. **Stop and wait for the user.** Present 5–8 papers proposed for deep reading (id, year, one line why, relevance), preferring surveys and theses as the backbone. The user edits the list.
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/paper_fetch.py <id...>`. A paper that cannot be downloaded: tell the user and drop it from the deep-read list (never deep-read from an abstract).
8. Call `lab:reader` **in parallel**, one per paper: `inputs: <fulltext path>`, `output: research/papers/cards/<id>.md`, template ${CLAUDE_PLUGIN_ROOT}/templates/<language>/paper-card.md. Then `paper_index.py set <id> pass=2` for each paper with a card.
9. Call `lab:writer` (kind `survey`) with the card paths, `angles.md` and the `scout-*.md` notes; output `evidence.jsonl`, `gaps.md`, `survey.md` in `research/surveys/<slug>/`.
10. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/cite_check.py research/surveys/<slug>/survey.md` and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py research/surveys/<slug>/survey.md`. Errors: send `lab:writer` back once with the script output.
11. Call `lab:skeptic` with artifact type `survey`, review at `research/reviews/survey-<slug>-<YYYY-MM-DD>.md`. Blocking issues: call `lab:writer` back **once** with the review path.
12. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source survey "<topic, number of papers, paths, open questions>"`. Tell the user: a 5-line summary, the path of `survey.md`, the skeptic's verdict, 3–5 open questions, and suggest `/lab:ideate` or `/lab:read-paper <id>`.
