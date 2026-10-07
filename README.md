# computer-science-squad-agents

Claude Code plugins that help with research and engineering work in computer science.

## Plugins

| Plugin | What it does |
|---|---|
| [`lab`](lab/README.md) (Research Squad) | A Lead plus 7 subagents (`scout`, `reader`, `writer`, `skeptic`, `experimenter`, `analyst`, `ideator`) and 11 `/lab:*` skills for AI/ML literature surveys, deep paper reading, experiments with a run ledger, write-ups and weekly retros. Docs are in Vietnamese with English technical terms. |

## Demo

`/lab:critique` on an experiment report with five planted defects. The `skeptic` subagent reviews it in its own context and names every one of them: a number not in the run ledger, a missing baseline, model selection on the test set, scaler leakage, and a cherry-picked seed.

![Skeptic verdict: reject, five blocking issues](docs/screenshots/critique-verdict.png)

More screenshots (paper reading, run guardrails, paired-seed statistics) are in the [lab README](lab/README.md#demo). All of them come from real runs; [docs/screenshots/capture](docs/screenshots/capture/README.md) explains how they were made.

## Install

```text
/plugin marketplace add quocthai179/computer-science-squad-agents
/plugin install lab@computer-science-squad-agents
```

Local development: `claude --plugin-dir ./lab`, then `claude plugin validate ./lab`.

## Tests

```bash
pip install pytest
pytest tests                       # unit tests for lab/scripts (stdlib only)
claude plugin validate --strict ./lab
```

Plugin evals live in `lab/evals/`; see [lab/README.md](lab/README.md#kiểm-thử) for how to run them.
