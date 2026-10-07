---
name: next
description: Answer in exactly one sentence - what is the most informative thing per unit time to do next on this research project, and why - based on the stage, unfinished work, experiments, surveys and lessons in research/. Use for "what should I do next", "next step", "what to prioritise". Also - giờ làm gì tiếp, bước tiếp theo; 下一步做什么, 该优先做什么; que faire ensuite, prochaine étape; 次に何をすべきか, 優先順位.
---

# /lab:next

You are the Lead. Answer briefly, call no subagents, and do not start the work you suggest.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

## Steps

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retro_digest.py --status-only`. No workspace: the answer is `/lab:setup`.
2. Read `research/PROJECT.md` (stage, north star, deadline), `research/lessons/LESSONS.md`, and the files the digest lists as unfinished (PLAN.md, FINDINGS.md, claims.md) when needed.
3. Choose **one** item in this priority order (Steinhardt: most information per unit time, de-risk before execute; Schulman: finish unfinished work before opening new work):
   1. whatever is blocking: a failed run waiting for diagnosis, a PLAN waiting for G3, claims waiting for G4;
   2. results not yet analysed (`ok` runs but no FINDINGS.md) → `/lab:analyze`;
   3. a running experiment without enough seeds or without baseline/ceiling;
   4. work that fits the stage: exploration → survey/read-paper; ideation → ideate; understanding → design-exp for the leading hypothesis; distillation → write-up;
   5. the last retro is more than 7 days old → `/lab:retro`.
4. Answer in exactly this form, in the user's language:

```text
Next: <one concrete thing, with the /lab:... command if any>
Why: <one sentence: it gives the most information / unblocks what>
Skip for now: <one tempting thing that should wait, and why>
```
