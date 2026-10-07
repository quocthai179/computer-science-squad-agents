# computer-science-squad-agents

Claude Code plugins that help with research and engineering work in computer science.

## Plugins

| Plugin | What it does |
|---|---|
| [`lab`](lab/README.md) (Research Squad) | A Lead plus 7 subagents (`scout`, `reader`, `writer`, `skeptic`, `experimenter`, `analyst`, `ideator`) and 11 `/lab:*` skills for AI/ML literature surveys, deep paper reading, experiments with a run ledger, write-ups and weekly retros. Works in English (default), Vietnamese, Chinese, French and Japanese. |

## Languages

English (default) · [Tiếng Việt](lab/README.vi.md) · [中文](lab/README.zh.md) · [Français](lab/README.fr.md) · [日本語](lab/README.ja.md)

The plugin's instructions are English; everything it writes into your workspace (notes, cards, plans, reviews, reports) follows the project language, and its replies follow the language you type in. Set a personal default with `claude plugin configure lab@computer-science-squad-agents --values-stdin <<< '{"language":"fr"}'`, or per project with `python3 lab/scripts/lang.py set fr`. Details in [lab/README.md](lab/README.md#language).

## Demo

`/lab:critique` (screenshot from a Vietnamese-language session) on an experiment report with five planted defects. The `skeptic` subagent reviews it in its own context and names every one of them: a number not in the run ledger, a missing baseline, model selection on the test set, scaler leakage, and a cherry-picked seed.

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
