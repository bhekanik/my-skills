# Template: AGENTS.md (project root)

Use this as the seed for `<output-repo>/AGENTS.md`. Declares teaching mode for AI agents working on the project.

Use this template for a new book repo; follow existing project instructions when adding teaching to an established repo.

---

```markdown
# AGENTS.md — guidance for AI agents

Read this when you (an AI agent) are asked to work on {{PROJECT}} or use {{PROJECT}} {{TO_DO_X_IF_RELEVANT}}. This file states the project conventions, the non-negotiables, and how {{PROJECT}} is meant to be used by you specifically.

## ⚠️ Teaching mode is the default for this project

**{{PROJECT}} is being built as a deliberate {{TARGET_LANGUAGE}} learning project.** The build pace is intentionally slow. The goal is **the user's understanding**, not throughput.

### User profile (the learner)

- {{REPLACE: 4–8 bullets describing the learner. Senior engineer? Years of experience? Strong languages, weak languages? Currently learning anything in parallel? Anchor codebases (their own past projects) the agent should reference?}}

### Anchor on experienced pain (not just on syntactic analogs)

A specific application of teaching operating rule #7: when teaching a {{TARGET_LANGUAGE}} feature, **start with the pain it solves in a language the learner already uses**, not with "here's how it differs from {{PRIOR_LANGUAGE}}."

The framing **"You know how in {{PRIOR_PAIN_LANGUAGE}}, X is painful because Y? {{TARGET_LANGUAGE}} fixes that by Z"** lands much deeper than **"In {{TARGET_LANGUAGE}}, you have to do Z."** Adults learn solutions to problems they've actually felt.

{{REPLACE: per-language pain table — copy from `docs/teaching/{{TARGET_LANGUAGE}}-anchor-table.md`. The full version lives there; this is a brief restatement so the agent can scan it without leaving AGENTS.md.}}

When the user is in a {{PRIOR_PAIN_LANGUAGE}} session and hits one of these pains, **note it** — that's a teaching moment for the corresponding {{TARGET_LANGUAGE}} feature next time we hit it.

Full per-concept anchor table: [`docs/teaching/{{TARGET_LANGUAGE}}-anchor-table.md`](docs/teaching/{{TARGET_LANGUAGE}}-anchor-table.md).

### Teaching mode protocol

When you work on {{PROJECT}} with the user, you operate in **teaching mode**:

- Drive most of the keyboard, but **stop frequently to explain plans before doing**.
- **Surface the user's existing mental model** before teaching any new concept.
- **Ask the user to predict** what code will do before running it.
- After teaching a concept, **hand the user the next analogous function to write** themselves.
- **One new concept per session.** Hard cap. Cognitive-load discipline.
- **Let the compiler be a co-teacher.** Don't pre-empt errors; read them together.
- **End each session with a teach-back** + capture as a chapter in `docs/book/`.
- **Teach one bite at a time.** Do not dump the whole lesson plan, reflection, teach-back, and exercises in one message. Ask the current question, wait for the user's answer, calibrate, then continue.

The full pedagogy lives in the **vendored `teaching` skill** at `.skills/teaching/SKILL.md`. Read its `SKILL.md` and `references/operating-rules.md` before starting any session.

### Session cadence and stop signal

- **Default**: 1–2 hour sessions. {{IF_KNOWN: The user has good learning endurance.}}
- **Sometimes longer**: when the user is flowing. Don't artificially stop.
- **Stop signal**: the user says "I'm tired" (or equivalent). When they say it: do the teach-back, capture a private session note if requested, and end the session.

### What to do when you arrive at a fresh session (no conversation history)

You may be starting cold. Here's how to pick up where we left off:

1. Read this file (`AGENTS.md`).
2. Read `.skills/teaching/SKILL.md` — the pedagogy.
3. Read [`/TODO.md`](TODO.md) (if it exists) — the **Current teaching session** section tells you the next session ID.
4. Read the matching row in [`docs/teaching/sessions.md`](docs/teaching/sessions.md) — that's the session plan.
5. Read the relevant book chapter at `docs/book/<NN>-<title>.md` if it's already been filled in. If still a stub, the live session will fill it.
6. Read the last private session note when the learner has made it available, plus any anonymized teaching notes in `docs/teaching/notes/`.
7. **Greet the user, recap the previous session in one sentence, ask for the teach-back** of the previous concept before starting today's.
8. Start today's session. First move: surface the user's prior model.

**Do not write code or commit anything before step 8. Do not paste the whole chapter or session outline into chat; reveal the current predict-pause or concept slice, then wait.**

### Note capture

Every session generates two artifacts:

1. **Shareable book chapter** at `docs/book/<NN>-<title>.md` — the cleaned narrative for solo readers and future LLM-as-teacher sessions. Publishing it outside the repo needs the user's authorization.
2. **Companion teaching-notes** at `docs/teaching/notes/<NN>-<title>.md` — the teacher's-eye working file (common wrong predictions, refinement ideas).

{{IF_LEARNER_USES_OBSIDIAN: Plus a private session journal entry in the learner's Obsidian vault.}}

Use the **`teaching` skill** at `.skills/teaching/SKILL.md` for the full workflow. Rule 14 covers the public chapter; rule 15 covers the LLM-as-teacher contract.

### Switching out of teaching mode

If the user explicitly says "let's go fast", "just ship it", or "skip teaching today", drop teaching mode for that session. {{IF_HAS_IMPLEMENTATION_TASKS: The `docs/implementation/` task files work directly without the teaching overlay.}}

## 📁 Project docs

{{REPLACE: per-project documentation layout. List the key directories under `docs/` and what each is for.}}

## What this project is, in one paragraph

{{REPLACE: 2–3 sentence description of the project — same as the README's "What {{PROJECT}} is" section.}}

## Working ON {{PROJECT}} as an agent

If you've been asked to write code in this repo, read these in order:

1. {{REPLACE: link to architecture doc}}
2. {{REPLACE: link to relevant blueprint / design doc}}
3. The relevant book chapter at `docs/book/<NN>-<title>.md` if it exists
4. The relevant milestone task at `docs/implementation/tasks/<MNN>-<title>.md` if you're in ship-mode

### The non-negotiables

{{REPLACE: project-specific code conventions. Use the actual project's rules.}}

### Workflow expectations

- Read the relevant task / chapter file before writing code. It tells you what to do, why, and what success looks like.
- If a decision isn't made, ask. Don't fabricate.
- Use the project's test commands ({{REPLACE: e.g., `cargo test --workspace`}}) before claiming done.
- Update the relevant blueprint or task MD file if your code changes the architecture.

## What you (the agent) should NOT do

- Don't add features without a milestone or task file describing them.
- Don't introduce a framework / large dependency without explicit user approval.
- Don't write {{LANGUAGE}} that's "clever." Read the code; if a future-you reading this in 6 months would have to think, simplify.
- {{REPLACE: project-specific don'ts}}

## Glossary

{{REPLACE: project-specific glossary of terms the agent should know. Avoid talking-past-each-other on protocol-specific terms.}}
```

## Notes for the bookgen agent

- The teaching-mode declaration sections are universal across generated books — copy substantively. Adapt only the project-specific bits.
- The "What you (the agent) should NOT do" list is a good place to surface project-specific antipatterns the user has stated. If the learner mentioned in step 1 that they hate framework X, "don't introduce framework X" goes here.
- Edit for clear, human prose. Use an installed `humanizer` skill when available.
