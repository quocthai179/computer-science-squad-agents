# Ideation playbook

Frame: generate → reflect → rank → evolve → meta-review (AI co-scientist), with the user as the ranker.

## Diverse seeds

Sampling more from the same prompt only returns duplicates (Si et al. 2024: very few of thousands of generated ideas were unique). Diversify the *inputs*:

- `research/surveys/*/gaps.md` and the survey's open questions;
- anomalies and "why it did not run" in old `experiments/*/FINDINGS.md`;
- `research/ideas/backlog.md` (Hamming: 10–20 important problems);
- the "Unfair advantage" section of `PROJECT.md`;
- one concrete constraint, for example "the pilot must run in an hour on the current machine";
- "replicate then extend" a paper that already has a card: a legitimate starting point for beginners (Nanda, Silver).

Each idea card records `seeds:` so you can see where it came from.

## What makes a good idea card

- Goal-driven rather than idea-driven (Schulman): say which goal it serves.
- "10% or 10×?" The smaller the improvement, the simpler the method must be.
- A measurable `prediction` and a cheapest test of at most 1 day.
- Kill criteria.
- A `safe` or `ambitious` label; a batch should contain both.

## Novelty protocol (skeptic)

1. Assume someone has already done it.
2. Find the closest prior work: at least 3 different queries (the idea's own terminology, terminology of a neighbouring field, a plain-language description).
3. If the method mapping is nearly one-to-one, say so and write the mapping.
4. In the review write one line `closest_prior_work[<idea-id>]: ...` per card, even when the conclusion is "nothing close found" (give the queries). The Lead copies the line into the card's `closest_prior_work` frontmatter field; `lint_report.py` relies on that field.
5. State the strongest reason the idea could fail.

Gupta & Pruthi: a substantial share of LLM-generated research documents were judged by experts to be paraphrased or borrowed without credit, and automated tools did not catch it. The user owns every novelty claim.

## Ranking

LLM rankings of ideas agree with humans at close to chance level. Agents may give a suggested order with reasons, but **G2 is the user scoring 1–10** (`user_score`), ideally before seeing the suggested order.

Quick test (Olah): if another group published exactly this idea, would you be excited to read it?

## After G2

The selected idea goes straight into a pilot of at most one day (`/lab:design-exp`), because ideas that look good on paper often drop after execution (Si et al. 2025). Rejected ideas keep their card with `status: killed` and the reason.
