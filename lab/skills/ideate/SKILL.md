---
name: ideate
description: Find and screen research ideas - the ideator writes Heilmeier idea cards from diverse seeds (gaps, anomalies, backlog, unfair advantage), the skeptic runs the novelty protocol looking for prior work, the user scores and chooses (G2). Use for "find ideas", "brainstorm research directions", "what should I work on". Also - tìm ý tưởng, brainstorm hướng nghiên cứu; 寻找研究想法, 头脑风暴研究方向; trouver des idées de recherche, brainstorming; アイデア出し, 研究テーマの案.
argument-hint: "[focus]"
---

# /lab:ideate

You are the Lead. Frame: generate → reflect → evolve → the user ranks.

Language: the project language is `language:` in `research/PROJECT.md`; if it is blank, the plugin default `${user_config.language}` (if that still shows as the literal text `${user_config.language}`, the option is unset: use English) (rules in ${CLAUDE_PLUGIN_ROOT}/playbooks/language.md). Reply to the user in the language they write in. Put `language: <code>` in every TASK BRIEF.

Rules that always hold:
- The user scores and chooses (G2). The agents' ranking is advisory only; LLM rankings of ideas are close to chance.
- Diversify the **inputs**; do not sample more from the same prompt.
- Nobody in the squad claims novelty. The user owns every such claim.

Focus: $ARGUMENTS

## Steps

1. Read `research/PROJECT.md` ("Unfair advantage", constraints, compute), `research/lessons/LESSONS.md`, ${CLAUDE_PLUGIN_ROOT}/playbooks/ideation.md. No workspace: tell the user to run `/lab:setup` and stop.
2. Collect seeds and list their paths: `research/surveys/*/gaps.md`, `research/experiments/*/FINDINGS.md` (anomalies, "why it did not run"), `research/ideas/backlog.md`, paper cards with "Which backlog problem does it unlock". Add one concrete constraint, for example "the pilot must run in an hour on the current machine". Too few seeds (< 3 sources): say so and suggest `/lab:survey` first, or ask the user for 2–3 problems they care about.
3. Call `lab:ideator` in mode `generate`: 6–10 cards in `research/ideas/cards/`, template `${CLAUDE_PLUGIN_ROOT}/templates/<language>/idea-card.md`.
4. Call `lab:skeptic` with type `idea` and the paths of the new cards (one skeptic for the whole batch, `budget: 40 tool calls`). Review at `research/reviews/ideas-<YYYY-MM-DD>.md`.
5. For each line `closest_prior_work[<id>]: ...` in the review: copy it into the `closest_prior_work` frontmatter field of that card and into its "Critique" section. A card without such a line stays empty.
6. Call `lab:ideator` in mode `evolve` with the review path: one round of merging, simplifying and dropping.
7. **G2.** Show the user a table: id, title, safe/ambitious label, prediction, cheapest test, closest prior work, the strongest reason it could fail. **Do not** show the agent's suggested scores before the user has scored. Invite the user to score each card 1–10 and choose 1–2. Quick test: "If another group published exactly this idea, would you be excited to read it?"
8. Write `user_score` in each card; chosen cards get `status: selected`; rejected ones `status: parked` or `killed` with the reason. Record in `research/decisions.md`.
9. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/notebook.py add --source ideate "<number of cards>, chose <ids>"`. Suggest: `/lab:design-exp <idea-id>` for a pilot of at most one day.
