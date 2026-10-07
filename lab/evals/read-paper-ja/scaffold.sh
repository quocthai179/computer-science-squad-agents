#!/usr/bin/env bash
set -euo pipefail
mkdir -p papers-inbox
cat > papers-inbox/toy-paper.md <<'PAPER'
# Gated Residual Mixing for Small-Data Text Classification

A. Author, B. Author (synthetic paper written for an eval fixture; not a real publication), 2025

## Abstract

We propose Gated Residual Mixing (GRM), a drop-in layer that mixes token features with a learned scalar gate. On three small text classification datasets GRM improves accuracy over a fine-tuned baseline by 1.8 points on average while adding 0.3% parameters.

## 1 Introduction

Small labelled datasets make fine-tuning unstable. Our contributions are: (1) the GRM layer; (2) an analysis showing the gate learns to suppress noisy tokens; (3) results on three datasets.

## 2 Method

GRM computes h' = h + g * MLP(LayerNorm(h)), where g = sigmoid(w) is a single learned scalar per layer initialised to -2. We insert GRM after every attention block of a frozen-embedding transformer and fine-tune all other weights.

## 3 Experiments

Datasets: TinySent (1k train), MiniTopic (2k train), SmallNLI (3k train). Baseline: the same transformer fine-tuned without GRM. Hyperparameters for GRM were tuned with 20 trials per dataset; the baseline uses the learning rate recommended in its original paper. We report the best of 3 seeds.

Table 1: Dataset statistics.

| dataset | train | test | classes |
|---|---|---|---|
| TinySent | 1000 | 500 | 2 |
| MiniTopic | 2000 | 1000 | 4 |
| SmallNLI | 3000 | 1000 | 3 |

Table 2: Test accuracy (best of 3 seeds).

| model | TinySent | MiniTopic | SmallNLI | mean |
|---|---|---|---|---|
| baseline | 81.2 | 74.5 | 61.0 | 72.2 |
| GRM | 83.5 | 76.1 | 62.4 | 74.0 |

## 4 Analysis

The learned gate g stays below 0.2 in early layers and rises to 0.6 in late layers. We interpret this as the model learning to suppress noisy tokens early, which explains the gains.

## 5 Limitations

We only evaluate on English and on datasets under 5k examples.
PAPER
