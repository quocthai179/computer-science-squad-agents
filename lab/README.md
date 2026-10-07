# Research Squad (`lab`)

**English** · [Tiếng Việt](README.vi.md) · [中文](README.zh.md) · [Français](README.fr.md) · [日本語](README.ja.md)

A Claude Code plugin for AI/ML research: a **Lead** (the main session, driven by the `/lab:*` skills) coordinates **7 subagents** and uses the `research/` folder in your repo as the shared lab notebook. Agents handle throughput (reading, running, checking, drafting); you keep taste and the decisions at five gates, G1–G5.

Three things the plugin adds compared with a one-off "deep research" run:

1. **A run ledger** and the rule "every number traces to a run", enforced by scripts and a hook rather than by prompts.
2. **`skeptic`**, an independent reviewer: it receives artifact paths only, never the author's reasoning.
3. **A learning loop** that measures calibration between predictions and results, and between time estimates and actual time.

It works in **five languages**: English (default), Vietnamese, Chinese, French and Japanese. See [Language](#language).

## Install

Requirements: Claude Code (v2.1.271 or later for the language picker; evals need v2.1.269+), `python3` ≥ 3.10 on `PATH`. The scripts use only the standard library; `pdftotext` (poppler) is optional for PDF text.

From GitHub:

```text
/plugin marketplace add quocthai179/computer-science-squad-agents
/plugin install lab@computer-science-squad-agents
```

Local development:

```bash
claude --plugin-dir ./lab        # edit files, then /reload-plugins
claude plugin validate ./lab
```

## Language

| Code | Language | Notes |
|---|---|---|
| `en` | English | default |
| `vi` | Tiếng Việt | English technical terms kept |
| `zh` | 中文 | Simplified characters |
| `fr` | Français | formal register (vous) |
| `ja` | 日本語 | polite form (です・ます) |

**What changes with the language:** everything written into `research/` (notes, cards, plans, reviews, reports) and the templates it starts from (`templates/<lang>/`), plus the agents' replies to you. **What never changes:** frontmatter keys and their fixed values (`status: approved`, `verdict: reject`), JSONL fields, file names, ids, and the `[@paper-id, loc]` / `[run:id]` anchors, so the scripts work in every language. Instructions, playbooks and script output are in English; the Lead relays them in your language.

**Choosing the language**, first match wins:

1. `language:` in `research/PROJECT.md`. `/lab:setup` writes it, using the language you write in. Change it later with `python3 <plugin>/scripts/lang.py set fr`.
2. The plugin option (your personal default for new projects):
   ```bash
   claude plugin configure lab@computer-science-squad-agents --values-stdin <<< '{"language":"fr"}'
   ```
   or `/plugin configure lab@computer-science-squad-agents` inside Claude Code. Until you save a value the option is unset and English applies.
3. English.

Chat replies follow the language you type in, whatever the project language is. Natural requests in all five languages trigger the right skill ("khảo sát…", "文献综述…", "revue de littérature…", "文献調査…").

## Commands

| You need | Command | Output |
|---|---|---|
| Start a project (G1) | `/lab:setup [title]` | `research/`, `PROJECT.md` (Heilmeier brief) |
| Get up to speed on a topic | `/lab:survey <topic> [--quick]` | a sourced survey, gaps, where papers contradict each other |
| Understand one paper | `/lab:read-paper <arXiv id \| URL \| file> [--deep]` | a paper card, explain-back |
| Critique any artifact | `/lab:critique <path>` | an independent review |
| Find ideas (G2) | `/lab:ideate [focus]` | idea cards that went through the novelty protocol |
| Design an experiment (G3) | `/lab:design-exp <idea-id \| question>` | `PLAN.md` |
| Run an experiment | `/lab:run-exp <exp-id>` (only when you type it) | the run ledger |
| Analyse | `/lab:analyze <exp-id>` | `FINDINGS.md`, tables, figures |
| Write up (G4, G5) | `/lab:write-up <kind> [slug]` | `claims.md` → `draft.md` → `final.md` |
| Weekly review | `/lab:retro [days]` | a retro, `LESSONS.md`, calibration |
| What to do next | `/lab:next` | exactly one thing, and why |

Every skill has a fallback: if subagents cannot be called, the Lead works sequentially with the same playbook and says so.

## The squad

| Agent | Role | Tools | Model | Writes to |
|---|---|---|---|---|
| `scout` | literature scout, pass 1 | Read, Glob, Grep, WebSearch, WebFetch, Write | sonnet | `surveys/<slug>/scout-*.jsonl` |
| `reader` | pass 2 on the full text | Read, Glob, Grep, Write | sonnet | `papers/cards/` |
| `writer` | the only writer | Read, Glob, Grep, Write, Edit | inherit | `surveys/`, `reports/` |
| `skeptic` | independent critic | Read, Glob, Grep, WebSearch, WebFetch, Write | opus | `reviews/` |
| `experimenter` | experiment engineer | Read, Glob, Grep, Edit, Write, Bash | sonnet | code, `experiments/<id>/` |
| `analyst` | results analyst | Read, Glob, Grep, Bash, Write | sonnet | `FINDINGS.md`, tables, figures |
| `ideator` | hypothesis generator | Read, Glob, Grep, Write | opus | `ideas/cards/` |

No agent has the `Agent` tool, so the call chain stays flat. `scout` and `reader` read untrusted content, so they have no `Bash` or `Edit`. `analyst` has no `Edit`, so it cannot change training code. All handoffs go through files with a `TASK BRIEF` / `RECEIPT` contract (`playbooks/handoff.md`).

## Workspace

```text
research/
├── PROJECT.md          # Heilmeier brief, stage, compute profile, language
├── notebook/           # YYYY-MM-DD.md, append-only (scripts/notebook.py)
├── decisions.md        # decisions at the gates
├── papers/             # index.jsonl, refs.bib, cards/, raw/ (gitignored)
├── surveys/<slug>/     # angles.md, scout-*.jsonl, evidence.jsonl, gaps.md, survey.md
├── ideas/              # backlog.md, cards/
├── experiments/<id>/   # PLAN.md, runs.jsonl, runs/ (gitignored), FINDINGS.md, tables/, figures/
├── reports/<slug>/     # claims.md, draft.md, final.md
├── reviews/
└── lessons/            # LESSONS.md (≤ 50 lines), calibration.jsonl, squad-issues.md, retros/
```

`/lab:setup` adds a block of shared rules to the repo's `CLAUDE.md` (between `<!-- lab:begin -->` and `<!-- lab:end -->`), because subagents load `CLAUDE.md`.

## Guardrails and how they are enforced

| Rule | Enforced by |
|---|---|
| No run when `PLAN.md` lacks `prediction` or `kill_criteria` | `runwrap.py` refuses (exit 3) |
| Only approved plans run (G3) | `runwrap.py` requires `status: approved` or `running` |
| Smoke before any real run | `runwrap.py` requires an `ok` smoke run |
| Run budget | `runwrap.py` checks `max_runs`; timeout from `budget_minutes_per_run` |
| At most 3 fix attempts | `runwrap.py` refuses after 3 failed runs in a row, unless you allow `--after-review` |
| No hand edits to the ledger, `tables/`, `figures/` | `PreToolUse` hook (`scripts/guard_generated.py`) |
| No changes to eval, metric or test data while running | the hook blocks the plan's `protected_files` while `approved`/`running` |
| Numbers in text must be in a table, ledger or card | `lint_report.py` |
| No placeholders in the final text | `lint_report.py` |
| No "novel", "first", "SOTA" without a checked `closest_prior_work` | `lint_report.py`, in all five languages |
| Citations must resolve | `cite_check.py` (arXiv, doi.org, Semantic Scholar; `--offline` checks locally only) |
| At most 2 review rounds, 1 extra survey round, 5 scouts | in the skills |

## How a training script reports metrics

Every run goes through `runwrap.py`:

```bash
python3 <plugin>/scripts/runwrap.py --exp e001-ls --name baseline --tag baseline --seed 0 -- python train.py
```

The training script reads its seed from `$LAB_SEED` and reports metrics either by printing a line `LAB_METRIC test_acc=0.8312` or by writing JSON to `$LAB_METRICS_FILE`. The ledger records the git SHA, a dirty flag, the config hash, seed, time, exit code and metrics.

## Scripts

| Script | Job |
|---|---|
| `init_workspace.py` | create `research/` (idempotent, `--lang`), add the rule block to `CLAUDE.md` |
| `lang.py` | show or set the workspace language |
| `paper_fetch.py` | arXiv id, URL or file → metadata, flattened LaTeX or PDF, `index.jsonl`, `refs.bib` |
| `paper_index.py` | merge and de-duplicate scout output; list; edit fields |
| `runwrap.py` | wrap a training command, hold the gates, write the ledger |
| `ledger.py` | list runs, generate Markdown tables and SVG figures, show the budget |
| `stats.py` | mean, std, 95% t-CI, seed-paired comparison with bootstrap CI |
| `cite_check.py` | check `[@id, loc]`, `\cite{}`, arXiv, DOI and `[run:id]` citations |
| `lint_report.py` | placeholders, unsourced numbers, unchecked novelty claims (en, vi, zh, fr, ja) |
| `calibration.py` | predictions vs outcomes; estimates vs actual time; Brier score |
| `retro_digest.py` | the weekly digest for `/lab:retro` and the status for `/lab:next` |
| `notebook.py` | append to the notebook |
| `guard_generated.py` | hook that blocks hand edits to generated and protected files |

## Demo

Screenshots from real runs in Claude Code (a Vietnamese-language session, so the replies are in Vietnamese). The inputs are eval fixtures, so you can rerun them ([how](../docs/screenshots/capture/README.md)).

**`/lab:critique`: independent review.** The Lead gives `lab:skeptic` paths only, no reasoning. This experiment report has five planted defects, and the skeptic names all five with line numbers.

![lab:skeptic reviewing FINDINGS.md](../docs/screenshots/critique-running.png)

![Verdict reject with five blocking issues](../docs/screenshots/critique-verdict.png)

**`/lab:read-paper`: deep reading and explain-back.** `lab:reader` reads the full text and writes a paper card; the Lead returns a summary and three questions so you can test your own understanding. The paper is synthetic, written for the evals, and the reader spots the weak evidence planted in it (unequal tuning, best of 3 seeds).

![lab:reader running in the background](../docs/screenshots/read-running.png)

![The paper card, summary and explain-back questions](../docs/screenshots/read-card.png)

**Guardrails in scripts, not prompts.** `runwrap.py` refuses to run an unapproved plan (G3) and refuses real runs before a smoke run; every run lands in the ledger with its git SHA.

![runwrap refusing, then a smoke run and 6 main runs](../docs/screenshots/guardrails.png)

**Seed-paired statistics.** On a toy experiment (logistic regression on synthetic data) label smoothing does nothing, and `stats.py compare` says so because the 95% CI of the difference contains 0.

![stats.py compare: CI contains 0](../docs/screenshots/stats.png)

## Testing

Unit tests for the scripts (from the repo root):

```bash
pip install pytest
pytest tests
```

They also check that all five languages have all 13 templates with identical frontmatter keys, headings and checklists, and that the linter works on English, Vietnamese, Chinese, French and Japanese text.

Plugin evals (`evals/`, 9 cases). Every run is a real model call billed to your usage. The cases build their fixtures with `scaffold.sh`, so they need `--scaffold`:

```bash
# quick iteration: one run, no baseline arm
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent --runs 1 --ablation none
# confirmation: three runs, with the no-plugin arm to see the delta
claude plugin eval ./lab --scaffold --allow-tools Bash Write Edit Agent
```

| Case | Checks |
|---|---|
| `read-paper-card` | English request → complete paper card with located quotes and explain-back |
| `critique-planted-bugs` | `skeptic` names all five planted defects |
| `design-exp-plan` | complete `PLAN.md`, prediction logged, plan not self-approved (G3) |
| `no-trigger-simple-question` | a single factual question does not invoke any skill |
| `next-step-analyze` | `/lab:next` recommends analysing the finished runs |
| `setup-fr` | French request → workspace in French, `language: fr`, French interview |
| `read-paper-ja` | Japanese request → card in Japanese, reply in Japanese |
| `critique-zh` | Chinese request → reply in Chinese naming all five defects |
| `read-paper-vi` | Vietnamese request → card and explain-back in Vietnamese |

A survey needs the web and is not deterministic, so it has no eval case; evaluate it with golden tasks.

## Defaults chosen

1. Main surface: Claude Code. Subagents and hooks in the Claude app are **unverified**.
2. Name and prefix: `lab`.
3. Workspace: `research/` in each repo.
4. Artifact language: English by default; `vi`, `zh`, `fr`, `ja` supported; a paper draft may be in another language than the project.
5. Compute profile: filled in during `/lab:setup`; plan budgets come from it.
6. `skeptic` uses `opus`; no second model family as reviewer yet.

## Limits

- Token cost: a full survey runs 4–5 scouts and 5–8 readers. Use `--quick` for narrow questions.
- `skeptic` is the same model family as the author and may share blind spots; you still have to read the final text.
- `cite_check.py` and `paper_fetch.py` need access to `export.arxiv.org`, `arxiv.org`, `doi.org` and `api.semanticscholar.org`.
- Hooks call `python3`; on Windows `python3` must be on `PATH`.
- Quality in non-English languages depends on the model; the structure, anchors and numbers are language-independent and checked by scripts.
- Speed up the mechanical parts, not the understanding: that is why `/lab:read-paper` has an explain-back and the write-up ends with G5.
