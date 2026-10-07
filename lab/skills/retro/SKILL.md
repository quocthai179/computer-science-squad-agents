---
name: retro
description: Weekly review of a research project - collects the notebook, ledger, decisions, calibration (how often predictions were right, how far time estimates were off) and unfinished work; writes the four-part Schulman retro; asks Nanda's review questions; proposes at most 3 lessons for LESSONS.md. Use for "retro", "weekly review", "lessons learned". Also - review tuần, rút kinh nghiệm; 每周复盘, 总结经验; rétrospective hebdomadaire, bilan de la semaine; 週次の振り返り, レトロスペクティブ.
argument-hint: "[days, default 7]"
---

# /lab:retro

You are the Lead. The retro runs in the main session because it needs a conversation. Do not call subagents.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Rules that always hold:
- A lesson enters `LESSONS.md` only when the user approves it. At most 3 lessons per retro. `LESSONS.md` is capped at 50 lines: adding one means merging or dropping one.
- A lesson has the form "when X do Y — evidence: <path>". With no evidence it is not a lesson.

Argument (number of days): $ARGUMENTS

## Steps

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retro_digest.py --days <number of days, default 7>`. Read the output, `research/PROJECT.md`, `research/lessons/LESSONS.md` and `research/lessons/squad-issues.md`.
2. Draft `research/lessons/retros/<YYYY-MM-DD>.md` from ${CLAUDE_PLUGIN_ROOT}/templates/<language>/retro.md:
   - Schulman's four parts: experimental findings, insights, code progress, next steps;
   - the table checking last retro's next steps (the digest already extracted them);
   - calibration (copy from the digest);
   - the number of unfinished items (Schulman: switching problems too often is a more common mistake than sticking too long).
3. Ask the user Nanda's review questions, **at most 3 per turn**: the goal this week and how far it got; what took time and what blocked; mistakes and what to change so they do not repeat; where you are confused; whether the pace is sustainable. Record the answers in the retro file.
4. Propose at most 3 lessons in the form above. The user approves each. An approved lesson goes into `LESSONS.md` (check the 50-line cap); a lesson that should become a playbook fix goes into `squad-issues.md` as a to-do.
5. Mistakes of the agents themselves this week (malformed RECEIPT, over budget, invention, ignored playbook) → add lines to `research/lessons/squad-issues.md`.
6. Offer to update `stage` in `PROJECT.md` if the digest shows a stage change; edit only if the user agrees.
7. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source retro "<retro path>; <n> new lessons"`. End with next steps for the coming week (at most 3).
