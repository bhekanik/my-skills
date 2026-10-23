# Template: 00-introduction.md

Use this as the seed for `<output-repo>/docs/book/00-introduction.md`. Replace `{{PLACEHOLDERS}}` during scaffold; keep the universal pedagogy sections intact.

Use this template to explain how this book's sessions work.

---

```markdown
# Chapter 00 — Introduction

> Read this first. ~10 minutes.

## What this book is, in one paragraph

A guided, multi-session walk through learning {{TARGET_LANGUAGE}} {{IF_DOMAIN: and {{DOMAIN}}}} while building {{PROJECT_DESCRIPTION}}. Each chapter is one teaching session: one new concept, one runnable artifact at the end. Read it solo (like a textbook with predict-pauses) or open it in an LLM-aware coding agent and have it taught to you live (the agent runs the chapter as a script, calibrating to your specific predictions). By chapter {{MILESTONE_CHAPTER_1}}, you'll have {{MILESTONE_DELIVERABLE_1}}. By chapter {{TOTAL_CHAPTERS}}, {{FINAL_OUTCOME}}.

## What this book is not

- **Not a {{LANGUAGE}} reference.** {{REPLACE: link to the official language docs}} covers the language exhaustively. Read those alongside; they're free, well-maintained, and complementary.
- **Not a {{DOMAIN}} specification.** {{REPLACE: link to the canonical spec}} is the source of truth. The book touches what's needed to make {{PROJECT}} work.
- **Not a tutorial.** Tutorials assume nothing about your prior knowledge and explain everything. This book assumes you've shipped real software in *something*, {{LIST_PRIOR_LANGUAGES}}, and uses that as your starting model. The chapters surface what you already know, then teach what's different.
- **Not interactive in the chat-bot sense.** "LLM-as-teacher" mode is a coding agent following the chapter as a script, not a chat about {{LANGUAGE}}.

## How learning works here

Three pedagogical ideas, paid for in pain:

### 1. Surface your model before teaching

Every chapter opens with a **🤔 Q:** prompt asking you to predict or describe how something works *in a language you already know*. You answer in your head (solo) or out loud (live). Then the chapter calibrates.

This isn't a quiz. It's a diagnostic. Your prediction tells the chapter (or agent) where you actually are, so it can teach what's *new* and skip what's familiar. If you've already mostly-known something, the chapter extends your model. If you've half-known it, the chapter flags where the analogy breaks.

> **Why it matters:** the hardest learners to teach are the ones who *think* they understand but actually don't. Surfacing the model up-front pulls the misalignment into view before you build code on top of it.

### 2. Predict before run

Every code block has a **🔮 Predict** prompt before you run it: "what will this print?" or "what will the compiler say?" Answer in your head, then expand the `<details>` block to calibrate.

Wrong predictions are the most teachable moments. They tell you exactly which part of your mental model is buggy. Right predictions move you forward fast.

If you skip the predicts, the chapter degrades into a flat tutorial. The pedagogy depends on you genuinely not knowing the answer when you guess.

### 3. The compiler is the teacher

{{LANGUAGE}}'s compiler {{IS / ISN'T}} famous for its error messages. Many chapters deliberately have you write code-that-doesn't-quite-work, hit a compiler error, read it together, and then fix.

Pre-empting compiler errors by writing "correct" code from the start would rob you of the conversation between you and the compiler that actually builds your mental model. Don't fight the chapter when it tells you to {{EXAMPLE_DELIBERATE_ERROR}}. The error is the curriculum.

## The cumulative project: {{PROJECT}}

This book is a long-arc project, not isolated examples. Each chapter's artifact is *cumulative*:

{{REPLACE: bulleted list of phases, each line "Chapters X–Y (Phase Z, name): you have <capability>"}}

By the time you finish chapter {{FINAL_CHAPTER}}, {{PROJECT}} {{IS DONE / IS MEANINGFULLY DEMONSTRABLE}}.

The frame to hold: **the goal isn't to ship {{PROJECT}}. The goal is to build a {{LANGUAGE}} engineer.** {{IF_PROJECT_IS_PUBLISHABLE: The {{PUBLISHED_FORM}} is a side effect. (A delicious one.)}}

## Pace and slowness

This book is slow on purpose. Senior-engineer learners have strong intrinsic motivation but high opportunity cost. The failure mode is "concepts piling up toward a future arrival point that never quite arrives." So:

- **Each chapter caps at one new concept.** Two new concepts in one session loads cognitive capacity past what schema-building can handle.
- **Each chapter ends with a runnable artifact.** Stop after any chapter and there's a working thing. Skateboard → scooter → bike → motorbike → car (Henrik Kniberg's MVP framing).
- **Each chapter ends with a teach-back.** If you can't articulate the concept in your own words, the chapter didn't land. Re-read before moving on.

Sessions that don't land aren't failures; they're data. The book says "go back" because going back is faster than fighting forward on a broken foundation.

## On {{PRIOR_PAIN_LANGUAGE}}

{{IF_RELEVANT: You will see references to **{{PRIOR_PAIN_LANGUAGE}} pain points** throughout the book: {{LIST_2_3_KEY_PAINS}}. This is deliberate.

Many of {{LANGUAGE}}'s hardest features ({{LIST_2_3_KEY_FEATURES}}) exist *to fix specific pains in {{PRIOR_PAIN_LANGUAGE}}*. If you've felt those pains, the {{LANGUAGE}} solutions land deeper. If you haven't, the {{LANGUAGE}} solutions feel like trivia.

If you're learning {{PRIOR_PAIN_LANGUAGE}} in parallel, the cross-pollination compounds. Every {{PRIOR_PAIN_LANGUAGE}} frustration becomes a sticky teaching moment for the {{LANGUAGE}} feature that fixes it. If you don't know {{PRIOR_PAIN_LANGUAGE}}: the book leans on {{ALTERNATIVE_ANCHOR_LANGUAGES}} more, and treats {{PRIOR_PAIN_LANGUAGE}} pains as "scenarios you'd hit in {{ROUGH_DESCRIPTION}}" — useful framing even if you don't run into them yourself.}}

## On predict-before-run for senior engineers

Senior engineers can fake confidence. You've probably done it; everyone has. Predict-before-run is a forcing function for honesty: when you write down (or think out loud) "I think this will print X", you commit. When the code prints Y, you can't pretend you knew. The misalignment is now visible, in your own head.

That visibility is what makes the learning stick. Trust the process; it gets less awkward by chapter 04.

## On the LLM-as-teacher mode

If you're reading this in an agent harness (Claude Code, Cursor, etc.), the agent will:

- Read the chapter and its companion teaching-notes file before starting
- Ask the chapter's **🤔 Q:** and **🔮 Predict:** questions to *you* in real time, not just inline
- Wait for your answer
- Calibrate (using the chapter's `<details>` blocks as a menu of common responses)
- Run the actual code in your environment, not a stale screenshot
- Read the actual compiler output with you, not a cached one
- Close with the chapter's teach-back questions

The agent should **not** paste the whole chapter, lesson plan, reflection, and exercise set into chat. The chapter is long-form because solo readers need it. Live teaching is progressive: one concept slice, one question, one answer, then the next slice.

The agent's contract: **the chapter is the curriculum.** It does not freestyle, skip ahead, or invent new concepts. If something genuinely new comes up, the agent flags it and stays in the chapter's lane.

If the chapter is wrong (a library version drifts, an OS quirk lands, your environment differs), the agent works around it AND files a follow-up to update the chapter. The book improves over time.

## Picking up where you left off

Each chapter's "Before you start" section lists *exact verification commands* you can run to confirm the previous chapter's artifact still works. Run them every time you re-open the book. If anything fails, go back to the chapter that introduced the broken thing.

If you're forking this repo to learn from someone else: `git log --oneline` shows you the cumulative commit history. Check out the commit at the end of any chapter to start from that point.

## Where to go next

[**Chapter 00b — What is {{PROJECT}} →**]({{PATH_TO_00B}}): the technical context everyone needs.

[**Chapter 00c — Why I built this →**]({{PATH_TO_00C}}): optional backstory, ~5–8 minutes.

[**Chapter 01 — {{FIRST_CHAPTER_TITLE}} →**]({{PATH_TO_01}}): where the book starts building.

If you'd like to skim the whole arc first: [Table of contents](README.md).
```

## Notes for the bookgen agent

- Keep the teaching method (surface the model, predict, run, explain, pause) but write for this learner and codebase.
- The project-specific sections (What this book is / The cumulative project / On {{PRIOR_PAIN_LANGUAGE}}) get populated from the learner's step-1 answers.
- Write plainly and edit for the learner. Use an installed `humanizer` skill when available.
