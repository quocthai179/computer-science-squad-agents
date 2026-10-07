---
name: critique
description: Independent red-team review of a research artifact - idea card, PLAN.md, FINDINGS.md, report draft, survey or paper card. Checks evidence pointers, leakage, baselines, seeds, cherry-picking, numbers versus the ledger, novelty. Use for "review this", "critique", "check my results", "is this result trustworthy". Also - phản biện, soát lỗi thí nghiệm; 评审, 批评性审阅, 检查实验结果; critiquer, relecture critique, ces résultats sont-ils fiables; レビュー, 批評, 実験結果の検証.
argument-hint: "<artifact path> [idea|plan|findings|draft|survey|paper-card]"
---

# /lab:critique

You are the Lead. `skeptic` reviews with an independent context: you give it paths only, **never** your reasoning, a summary or opinions (yours or the author's).

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Input: $ARGUMENTS

## Steps

1. Find the artifact file and its type. If the type is not given, infer it: `ideas/cards/` → idea; `PLAN.md` → plan; `FINDINGS.md` → findings; `reports/` → draft; `surveys/` → survey; `papers/cards/` → paper-card. Not sure: ask one question.
   No `research/`: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/init_workspace.py --project-dir . --lang <language of the user's message if supported, else ${user_config.language}>` to have somewhere to write the review.
2. Find the round: a review for this artifact already exists in `research/reviews/` and the artifact changed since → round 2. There is no round 3: remaining disagreements go to the user.
3. Call `lab:skeptic` with a TASK BRIEF:
   - `objective: review <type> <path>, round <n>`
   - `inputs: <artifact path>` (plus the round-1 review for round 2)
   - `output: research/reviews/<slug>-<YYYY-MM-DD>.md`, template `${CLAUDE_PLUGIN_ROOT}/templates/<language>/review.md`
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/review.md`
   - `budget: 30 tool calls`
   If subagents cannot be called: review it yourself with the same playbook and say plainly that the review is **not** independent.
4. For text artifacts (findings, draft, survey) you may also run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint_report.py <file>` and include its result.
5. Read the review file. Tell the user, briefly:
   - the verdict and a one-sentence reason;
   - **the list of blocking issues**, one per line, each naming the defect (for example: leakage, missing baseline, single seed, cherry-picking, a number not in the ledger, missing prior work) with its location;
   - the most important alternative explanation;
   - the review path.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source critique "<artifact>: <verdict>, <n> blocking issues"`.

Never edit the artifact yourself. The user (or the workflow that owns the artifact) decides what to fix.
