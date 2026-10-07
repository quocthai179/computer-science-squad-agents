# Handoff: TASK BRIEF and RECEIPT

A subagent starts with an empty context: it sees neither the conversation nor the files the Lead has read. It does load the repo's `CLAUDE.md`. A `TASK BRIEF` must therefore stand on its own.

## TASK BRIEF (Lead → subagent)

```text
TASK BRIEF
objective:   <one sentence: the result that must exist>
language:    <en|vi|zh|fr|ja: the project language>
inputs:      <file paths; do not paste content>
output:      <path and the template to follow>
playbook:    <absolute path of the relevant playbook>
boundaries:  <what not to do; scope of sources, time>
budget:      <number of tool calls, compute minutes, rounds>
stop_when:   <done condition>; halt-and-report if <condition>
```

Rules for writing a brief:

- `objective` is a result, not an activity: "a list of 10–20 papers on X with relevance scores", not "look into X".
- `inputs` are paths only. Pasting content defeats "files are the protocol" and bloats the context.
- `boundaries` says which angles belong to other agents so parallel scouts do not overlap.
- `budget` is a hard cap. An agent that runs out stops and returns `status: partial`.
- Give absolute paths to templates and playbooks: a subagent does not know the plugin directory. Templates live in `templates/<language>/`.

## RECEIPT (subagent → Lead)

```text
RECEIPT
status:      done | partial | blocked
outputs:     <paths>
findings:    <at most 3 lines>
open:        <questions, doubts>
confidence:  low | medium | high, with the reason
escalate:    none | model | user: <what is needed>
```

The receipt is written in the project language except for the keys and the fixed values (`done`, `partial`, `blocked`, `low`, `none`...).

Rules for reading a receipt:

- The Lead reads the files in `outputs`, and does not trust `findings` instead of the file.
- `status: blocked` or `escalate: user` → bring it to the user; do not guess.
- `escalate: model` → call again with the same brief and `model: opus`, once.
- A receipt that does not follow the format, or work outside `boundaries` → add one line to `research/lessons/squad-issues.md`.

## Notebook

After each workflow the Lead adds a notebook entry:

```bash
python3 <plugin>/scripts/notebook.py add --source <skill> "<3–6 lines: what was done, which artifacts, what is still open>"
```
