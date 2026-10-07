---
name: run-exp
description: Run an approved (G3) experiment through the experimenter agent in the order smoke, baseline, ceiling, main runs, every run recorded in the ledger by runwrap.py. Spends compute, so it runs only when the user types the command. Also - chạy thí nghiệm; 运行实验; lancer l'expérience; 実験を実行.
argument-hint: "<exp-id> [smoke|baseline|main|all]"
disable-model-invocation: true
---

# /lab:run-exp

You are the Lead. `experimenter` does the work; you hold the gate, the budget and the report.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Rules that always hold:
- Run only when `PLAN.md` has `status: approved` or `running`. Otherwise stop and send the user to `/lab:design-exp`.
- Every run goes through `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/runwrap.py`. A runwrap refusal (exit 3) is a stop signal, not an obstacle to get around.
- At most 3 fix attempts; never change the eval, the metric or the test data.

Input: $ARGUMENTS (default scope `all`)

## Steps

1. Read `research/experiments/<exp_id>/PLAN.md`. Check `status`, `prediction`, `kill_criteria`. See the budget used: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py budget --exp <exp_id>`.
2. If `status: approved`: change it to `running`.
3. Call `lab:experimenter` with a TASK BRIEF:
   - `objective`: run scope <smoke|baseline|main|all> of <exp_id>
   - `inputs: research/experiments/<exp_id>/PLAN.md`, the relevant code
   - `playbook: ${CLAUDE_PLUGIN_ROOT}/playbooks/experiment.md`
   - `runwrap: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/runwrap.py --exp <exp_id> ...`
   - `budget`: runs left and compute minutes left according to `ledger.py budget`
   - `stop_when`: scope done; halt-and-report when runwrap refuses, after 3 failed fixes, or when a kill criterion is hit
4. Read the RECEIPT and `ledger.py list --exp <exp_id>`. Check: an `ok` smoke exists before real runs; the number of seeds per variant; failed runs are reported.
5. RECEIPT `blocked`: read `diagnosis.md` (if any) and present to the user: the symptom, what was tried, the options. Only when the user says to continue, call the experimenter again with a note "the user has read the diagnosis, --after-review is allowed".
   runwrap reports the budget used up: ask the user whether to raise `max_runs` / `budget_total_hours`; edit PLAN.md only if the user agrees, and record it in `decisions.md`.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source run-exp "<exp_id>: <run ids>, <ok/failed>, <compute minutes>"`.
7. Report to the user: run ids, status, budget left, and suggest `/lab:analyze <exp_id>`. **Do not** interpret results here; that is the `analyst`'s job.
