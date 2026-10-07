---
id: <paper-id>
title: <paper title>
year: <year>
venue: <venue>
link: <url>
pass: 2                   # 1 = scout, 2 = reader, 3 = --deep (reproduction)
relevance: <0-3>
tags: []
fulltext: <papers/raw/<id>/paper.tex or .pdf>
---

# <id>: <paper title> (<year>, <venue>)

## One sentence

<what the paper does and finds, in one sentence>

## The five Cs

- **Category:** <type of paper: new method, analysis, benchmark, survey, system...>
- **Context:** <which work it builds on; the 2–4 most related papers>
- **Correctness:** <are the assumptions reasonable?>
- **Contributions:** <the main contributions, at most 3>
- **Clarity:** <is it well written?>

## Main claims

> For each claim: a verbatim quote of at most 25 words, with its location (section, table, figure, page).

1. "<quote>" — §<section> / Table <n>

## Method

<enough to reproduce at the level of ideas: input, output, architecture or algorithm, loss, data, cost>

## Key experiment

<which experiment does the main claim rest on? which baselines? how many seeds? can it tell the authors' hypothesis from a more boring explanation?>

| setting | metric | number reported | location |
|---|---|---|---|

## Four skeptical questions (Lipton & Steinhardt)

- **Explanation or speculation?**
- **Has the source of the improvement been isolated by ablation? Is the baseline tuned equally?**
- **Does the math clarify, or just impress?**
- **Is the terminology stretched beyond its meaning?**

## Hidden assumptions and limits

## Which backlog problem does it unlock?

<point to a line in research/ideas/backlog.md, or "none">

## If you reproduce it

- data:
- estimated compute:
- where it is easy to go wrong:
- smallest result worth reproducing:

## Explain-back

> Three questions for the user to answer without looking at the card. The Lead compares the answers with the card.

1.
2.
3.
