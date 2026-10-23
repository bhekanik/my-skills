# Template: docs/book/README.md

Use this as the seed for `<output-repo>/docs/book/README.md`. The TOC and how-to-read-this-book.

Use the current book's chapters and project facts to fill this template.

---

```markdown
# Learn {{TARGET_LANGUAGE}} {{IF_DOMAIN_RELEVANT: and {{DOMAIN}}}} by building {{PROJECT}}

A book that teaches you {{TARGET_LANGUAGE}} {{IF_DOMAIN_RELEVANT: and {{DOMAIN}}}} while you build {{PROJECT_DESCRIPTION}}. Read it solo, or open it in an LLM-aware coding agent and have it taught to you live.

## Two ways to read this book

### 🚶 Solo

Open chapter 01, work through it under your own steam. Each chapter:

- Opens by stating the **artifact** you'll have at the end (a thing you can run, not a concept).
- Surfaces your existing mental model with a **🤔 Q:** prompt before teaching anything new.
- Has **🔮 Predict** prompts before every code run. Answer in your head, then expand the `<details>` block to calibrate.
- Lets compiler errors land deliberately so you read them with the agent, instead of avoiding them.
- Closes with **📣 Teach-back** questions and a literal *run the artifact* moment.

Skip the predicts and this is just a tutorial. Do them and it's a teaching book.

### 🤖 LLM-as-teacher

Clone this repo, open it in an agent harness (Claude Code, Cursor, etc.), and ask:

> Start the next chapter

The agent will pick up where you left off, run the chapter live and responsively (calibrating to your specific predictions, running the real code, hitting the real compiler errors), and close with the same teach-back. The chapter is the canonical curriculum. The agent's job is to add live responsiveness inside that script, not to invent its own way.

See [`AGENTS.md`](../../AGENTS.md) for the teaching-mode contract.

## Who this is for

You're a senior software engineer (or close to it) with strong skills in something *other* than {{TARGET_LANGUAGE}}: {{LIST_PROBABLE_PRIOR_LANGUAGES}}. You want to learn {{TARGET_LANGUAGE}} for real, on a real project, without slogging through {{NUMBER}} pages of language-feature reference. You learn fastest when you write code and hit compiler errors, not when you read about them.

{{IF_DOMAIN_RELEVANT: You're also someone who will benefit from learning {{DOMAIN}} along the way: because {{REASON_1}}, or because {{REASON_2}}, or because you want to see how {{INDUSTRY_USE_CASE}} actually works.}}

## What {{PROJECT}} is

{{REPLACE: 2–3 sentence description of the project. What it is, what it does, what makes it specifically interesting.}}

For the full project vision, see [{{LINK_TO_VISION_DOC}}]. For the underlying engineering tasks (ship-mode, no teaching), see [{{LINK_TO_IMPLEMENTATION_DOCS}}].

## Table of contents

{{REPLACE: a phase-grouped table of contents.

Per phase, a markdown table:

| Ch. | Title | Concept | Artifact |
|---|---|---|---|
| 01 | [Title](01-slug.md) | The one new concept | The runnable artifact at chapter close |
...

Generate from the session plan in step 4 of the bookgen workflow.}}

## How to read it

1. Start at chapter 01. The ladder is cumulative. Chapter 04 assumes you ran chapter 03's artifact.
2. Read in order. Each chapter caps at one new concept (cognitive load discipline). Skipping ahead is allowed but you'll feel it.
3. Type the code yourself. Don't paste. The compiler conversation is the curriculum.
4. Pause at every **🔮 Predict** before expanding the `<details>`. Wrong predictions are the most teachable moments. Your mental model needs that data.
5. Demonstrate the artifact at chapter close. Run the thing. See it work. The visibility is the fuel.

## Prerequisites

- {{REPLACE: Required toolchain installation, e.g., "A working Rust toolchain. Install via rustup."}}
- {{REPLACE: OS support, e.g., "macOS or Linux. Windows isn't currently a target."}}
- **Comfort with one mainstream language.** The book uses {{PRIMARY_ANCHOR_LANGUAGE_1}} and {{PRIMARY_ANCHOR_LANGUAGE_2}} as primary anchors{{IF_DEEP_PAIN: , with {{PRIOR_PAIN_LANGUAGE}} as a deeper pain anchor for {{TYPE_OF_CONCEPTS}}-related concepts}}. You don't need {{PRIOR_PAIN_LANGUAGE}}; you do need *some* mainstream language to anchor against.

## Picking up mid-book

If you skipped chapters: each chapter's "Before you start" section lists exact verification commands. Run them; if they fail, go back and follow the linked predecessor.

If you got the repo from someone else and want to start from the current state: `git log --oneline` shows the canonical commits. Check out the commit that lands the chapter you want to start from, then go forward.

## Companion artifacts

- [`docs/teaching/notes/`](../teaching/notes/): *teacher's* working files. One per chapter. Captures common wrong predictions, sticky points, refinement ideas. Read these if you're an LLM teaching a learner; they tell you what to pre-empt.

## See also

- [`AGENTS.md`](../../AGENTS.md): teaching-mode contract for AI agents working on {{PROJECT}}
- {{REPLACE_IF_EXISTS: link to project blueprint / vision docs}}
- [`docs/teaching/sessions.md`](../teaching/sessions.md): the per-session syllabus that produced this book
- The portable [teaching skill](../../.skills/teaching/SKILL.md): the pedagogy this book is built on
- {{IF_HUMANIZER_VENDORED: Link the optional writing-quality skill at `../../.skills/humanizer/SKILL.md`.}}
```

## Notes for the bookgen agent

- The TOC table is the most labour-intensive section to fill. Generate it from the session plan in step 4 of the bookgen workflow.
- "Who this is for" should match the learner profile from step 1c. If the learner is a junior engineer (rare for this skill but possible), soften the "senior software engineer" framing.
- Edit for clear, human prose. Use an installed `humanizer` skill when available.
