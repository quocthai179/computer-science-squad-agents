# Principles

The thirteen design principles of the Research Squad. Every skill and agent follows them; when two rules conflict, the earlier one wins.

1. **The human keeps taste, agents keep throughput.** The five gates G1–G5 belong to the user. Agents never choose the problem and never claim novelty.
2. **Every number traces to a run; every claim traces to a source.** Tables and figures are generated from the ledger. Citations must resolve. Quote with location: `[@paper-id, §3.2]`.
3. **Predict first, run second.** `runwrap.py` refuses to run when `PLAN.md` lacks `prediction` and `kill_criteria`.
4. **The most informative work per unit time goes first.** De-risk, then execute.
5. **Baseline and ceiling before the method. Change one thing at a time.**
6. **The critic does not see the author's reasoning.** `skeptic` receives artifact paths only, at most two rounds.
7. **Files are memory and the handoff protocol.** A subagent writes artifacts and returns a short `RECEIPT` with paths.
8. **Read in parallel, write sequentially.** One writer per artifact.
9. **Every loop has a cap:** scouts, tool calls, review rounds, fix attempts, compute minutes.
10. **A rule that must always hold goes into a script or a hook, not a prompt.**
11. **Write early; claims drive experiments.**
12. **Experience accumulates:** evidence-backed lesson → `LESSONS.md` → playbook → agent prompt.
13. **Speed up the mechanical parts, not the understanding.** The user must be able to explain everything that carries their name.

## Gates

| Gate | When | The user decides | Recorded in |
|---|---|---|---|
| G1 | after `/lab:setup` | the problem and the success criteria | `PROJECT.md`, `decisions.md` |
| G2 | after `/lab:ideate` | which idea deserves a pilot | idea card `status: selected`, `user_score` |
| G3 | before `/lab:run-exp` | approve `PLAN.md` = approve the compute spend | `PLAN.md` `status: approved`, `approved_at` |
| G4 | before any prose is written | approve `claims.md` | `claims.md` `status: approved` |
| G5 | before submitting or sharing | read the final text and do the explain-back | `decisions.md` |

Only the main session (the Lead) stops at a gate, because subagents cannot ask the user. The Lead never moves a gate status on the user's behalf: there must be a clear answer from the user in the conversation.

## Stages (Nanda)

| stage | north star | sign of being stuck |
|---|---|---|
| ideation | choose a problem worth doing | reading forever without choosing |
| exploration | gather information; many new bits per hour | thinking you are "proving" something before you have a hypothesis |
| understanding | convince yourself of one hypothesis | running more runs with no prediction |
| distillation | compress into rigorous truth and communicate it | writing while the claims have no evidence |

## Model routing and budgets

| tier | runs on | examples |
|---|---|---|
| mechanical | scripts | parse metadata, resolve citations, summarise logs |
| standard | `sonnet` | `scout`, `reader`, `experimenter`, `analyst` |
| judgment | `opus` or the main session's model | `skeptic`, `ideator`, `writer`, hard debugging |

When a `RECEIPT` says `escalate: model`, the Lead calls the same agent again with `model: opus`.

Starting budgets (tune from the logs):

- a single factual question: the Lead answers it, no squad;
- narrow topic: 2–3 `scout`, at most 12 tool calls each;
- broad survey: 4–5 `scout`, at most 15 tool calls each; deep-read 5–8 papers;
- fixing one failing run: at most 3 attempts; review: at most 2 rounds; survey: at most 1 extra search round.

## Fallback

If subagents cannot be called (for example on a surface that does not support them), the Lead works sequentially with the same playbooks, writes the same artifacts, and tells the user plainly that the critique is no longer independent.
