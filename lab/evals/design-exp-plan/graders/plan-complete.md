---
type: regex
target: { source: file, path: research/experiments/e001-ls/PLAN.md }
pattern: '(?=[\s\S]*\nprediction:[ \t]*[^<\s])(?=[\s\S]*\nkill_criteria:[ \t]*[^<\s])(?=[\s\S]*\nseeds:[ \t]*([3-9]|\d\d))(?=[\s\S]*\nprotected_files:[ \t]*\[[^\]\s])(?=[\s\S]*[Cc]eiling)(?=[\s\S]*[Bb]aseline)'
weight: 3
---
