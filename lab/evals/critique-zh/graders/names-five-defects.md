---
type: llm
focus: last_message
weight: 3
---
The reply must be in Chinese and name these five defects of the report (in any wording): (1) data leakage, such as normalisation fitted on all the data; (2) model or checkpoint selection on the test set; (3) cherry-picking, such as reporting only the best of five seeds; (4) a missing baseline or a baseline number taken from the paper without a run; (5) a number in the text (0.913) that does not match the run ledger (0.871).
PASS if all five are named. FAIL if the reply is not in Chinese or any of the five is missing.
