---
name: one-by-one
description: Pull out only what you need from me, then ask it one question at a time in plain language.
disable-model-invocation: true
---

The user typed this because your recent messages buried what you need from them under status, findings and options, and they can't tell what to do. Work out what you actually need from them, then walk them through it one question at a time.

## 1. Sort

Go back over everything you've said since the user last gave you a clear answer, plus anything still pending from before. Put each item in one bucket:

- **Ask**: a decision only the user can make, or something only they can do (run a command, approve an action, log in, check something on their side).
- **Look up**: a fact you can find yourself. Find it now; it never becomes a question.
- **FYI**: status and findings. Hold these for the recap.

Order the asks so each comes after anything it depends on.

Done when every item sits in a bucket and the asks are in dependency order. If there are no asks, say so in one plain sentence ("I don't need anything from you; I'm carrying on with X") and continue the work.

## 2. Ask one question

Open the first question with the count: "I need 3 things from you. Here's the first."

Each question stands on its own, so the user can answer it without scrolling up:

- Plain words. Explain every term, file or tool name the user hasn't used themselves.
- Two or three sentences of background: what's going on and where this question comes from.
- What changes: what you'll do differently depending on the answer.
- The kind of ask. A choice lists the options, your recommendation and why. A task gives the exact command or steps and how to tell it worked.

Where the host has a question tool (Claude Code's `AskUserQuestion`), use it with exactly one question per call and the recommended option first. Otherwise ask in plain text and end the message on the question.

Done when the user has answered.

## 3. Adjust

Recompute the asks: drop the ones the answer settled, add any it raised, and give the new count ("2 left", or "that raised one more, so 3 left"). When an answer is unclear, follow up on that same question before moving on.

Repeat step 2 until no asks remain.

## 4. Recap and carry on

Give one short list: what the user decided or did, and the FYI items that still matter. Then continue the work with their answers.
