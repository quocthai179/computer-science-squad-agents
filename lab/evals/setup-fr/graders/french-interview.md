---
type: llm
focus: last_message
---
PASS if the reply is written in French and asks the user between one and three questions about their project (for example what they want to do, how it is done today, what is new, compute available), without inventing answers for them.
FAIL if the reply is in another language, asks more than three questions in one turn, or states the project's goals, success criteria or compute as if the user had given them.
