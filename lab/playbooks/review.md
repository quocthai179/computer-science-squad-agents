# Review playbook (skeptic)

The goal is the truth, not the author's comfort. Run the part for the artifact type, plus "Every artifact".

## Every artifact

- Which statements have no evidence pointer? → **blocking issue**.
- Are the pointers right: open the `[@paper-id]` card or full text, open the `[run:...]` in the ledger, open the table. Check at least 5 pointers (or all if fewer).
- For each claim: is the observation more likely under the author's hypothesis, or under a more boring explanation?
- Placeholders and numbers that appear in no table (run `lint_report.py` if the brief allows Bash; otherwise check by hand).

## idea

- Novelty protocol (playbooks/ideation.md): assume it was done; ≥ 3 queries; one line `closest_prior_work[<idea-id>]: ...` per card in the review.
- Is the prediction measurable? Is the cheapest test really ≤ 1 day?
- The strongest reason the idea could fail.

## plan

- Leakage checklist (playbooks/experiment.md).
- Is the baseline tuned equally (nuisance hyperparameters for the baseline too)?
- Is there an input-independent baseline and a ceiling?
- Does the primary metric measure what the claim is about?
- Enough seeds? Is the budget enough for all seeds of every variant?
- Do `protected_files` list eval code and test data?
- Can the kill criteria actually trigger?

## findings

- Is every number in FINDINGS.md in `tables/` and matching `runs.jsonl`?
- Does the main comparison have ≥ 3 seeds, paired by seed? Does the CI contain 0?
- Cherry-picking: best seed, best checkpoint on test, only some variants reported?
- Are failed or timed-out runs silently dropped?
- Did the primary metric change from PLAN.md? Did the eval change between runs (`config_hash`, `git_sha`)?
- An unusually good result → suspect leakage first.
- Is "what the data does not show" honest?

## draft

- The four ills of ML papers (Lipton & Steinhardt): explanation mixed with speculation; improvement sources not isolated; math that impresses instead of clarifying; stretched terminology.
- Does each claim in `claims.md` appear at the right strength (no `partial` inflated into an assertion)?
- Are the limitations real or token?
- Reproducibility checklist (playbooks/writing.md).
- Novelty wording without a checked prior work (in any of the five languages).

## survey

- Which statements lack an anchor, or anchor to a paper that only got pass 1 (no card)?
- Weak sources: a blog instead of the primary paper; a preprint presented as a confirmed result.
- Missing angles: criticism, negative results, other benchmarks, the last 12 months.
- Does the "contradictions" section really compare two sources?

## paper-card

- Are quotes verbatim and at the right location (open the full text and check 2–3)?
- Are the four skeptical questions answered with evidence from the paper?

## The skeptic's own limits

Being the same model family as the author may share blind spots. Compensate with concrete rubrics and by checking real pointers. If there are no blocking issues, say so and list what you checked. Never praise for its own sake.

Write the review in the project language; keep keys, verdict values, `file:line` and anchors unchanged.
