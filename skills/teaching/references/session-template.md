# Session note template

For a private Obsidian session note. Adapt the structure if the learner uses another note system; never place this raw session record in a shareable book chapter.

## Filename

```
<Project> Session <YYYY-MM-DD>.md
```

## Location

Use the location the learner chose for private session notes.

## Frontmatter

```yaml
---
tags:
  - projects
  - projects/<project-slug>/sessions
  - resources/programming/<language>
  - resources/learning/teaching-sessions
type: "[[Teaching Session Note]]"
date: <YYYY-MM-DD>
project: "[[<Project>]]"
related:
  - "[[<Project> Teaching Sessions]]"           # the session hub
  - "[[<Atomic concept note created or referenced>]]"
session_concept: "<one-line description of today's concept>"
duration_minutes: <NN>
---
```

## Body sections

```markdown
# <Project> Session <YYYY-MM-DD> — <Concept of the session>

## Concept of the session

<One paragraph stating the one new concept we worked on. Should match `session_concept` in frontmatter.>

## Learner's prior model

> Question: "How do you think Rust handles X?"

<What the learner said before any teaching happened. Quote them where possible. This is the diagnostic — record exactly what they thought going in.>

## Where the model needed adjustment

<The analogy break. What did the learner expect that turned out to be different in the new language? Where did the JS/TS or Python intuition fail?>

## Worked examples we covered

<Code snippets we wrote together, with the explanations attached. Use code blocks. Include the compiler errors we hit and what they revealed. Apply gradual release labelling: which round was each example?>

### I do — <function name>

```rust
// Code I wrote, fully narrated.
```

Explanation: <what I said while writing>

### We do — <function name>

```rust
// Code we wrote together, with the conceptually meaty bit left for the learner.
```

The piece the learner filled: <which lines>

### You do — <function name>

```rust
// Code the learner wrote alone.
```

What I noticed in review: <observations>

## Compiler conversations

<Interesting compiler errors we hit. Format: error message + what it taught us.>

```
error[E0382]: borrow of moved value: `s`
  --> src/main.rs:5:20
   |
3  |     let s = String::from("hello");
   |         - move occurs because `s` has type `String`...
```

What this revealed: <the conceptual insight>

## Teach-back capture

> Question: "Explain <concept> to me as if I'm a colleague who knows JS but not Rust."

<The learner's actual words. Don't polish. The roughness is data — it shows what's solid and what's still hand-wavy.>

## Learner level

<Use the rule 21 rubric. Trust diagnostic/tension tests more than self-rating.>

- **Start:** Unknown | Confused | Aware | Confident — <evidence>
- **End:** Unknown | Confused | Aware | Confident — <evidence>
- **Tension / edge-case test used:** <question asked and what it revealed>

### Learner-state carry (rule 22)

<The four-field snapshot to reconcile into the teaching-notes `learner_state:` at session end. Capture start and end so the delta is visible.>

- **Mastered (added this session):** <concepts now demonstrated unaided>
- **Shaky (still / newly):** <met but not solid>
- **Recent errors:** <specific wrong predictions / compiler conversations this session>
- **Priors surfaced:** <opinionated prior-language models that shaped predictions>

## Socratic pressure notes

- **Mode shifts:** <Socratic / Curious Guide / Devil's Advocate, why, and how the learner responded>
- **Fuzzy terms sharpened:** <overloaded terms paused on, canonical terms chosen, why it mattered>
- **Probe questions used:** <diagnostic questions for misunderstandings or pitfalls>
- **Learner priors / biases surfaced:** <useful but opinionated prior models that shaped predictions>
- **One-reframe moments:** <when the learner was stuck, what single reframe was given, what they did next>

## Open questions

- <Anything the learner asked that we didn't fully answer>
- <Anything I noticed they're still shaky on>
- <Concepts we touched briefly but deferred>

## Evidence posture

<Consensus, tensions, pitfalls, misunderstandings, and gaps surfaced in this session. Keep this lightweight; the point is to calibrate future teaching, not to turn every session note into a paper.>

- **Consensus:** <claims that are stable, source-backed, or verified against code/docs>
- **Tensions:** <real trade-offs or active disagreements; do not list mere branches>
- **Common misunderstandings:** <false models the learner had or that people commonly bring>
- **Pitfalls:** <runtime/compiler/tooling behaviours that surprise people>
- **Gaps / deferred questions:** <what the one-concept cap intentionally left out>
- **Sources consulted:** <only sources that materially shaped the explanation>

## Working map (for Socratic concept sessions)

<Use when the artifact is an understanding map rather than code. Keep this as a map, not a transcript.>

- **Root:** <topic/question>
- **Current branch:** <active branch>
- **Real tension:** <if any>
- **Leaves explored:** <fine-grained questions covered>
- **Unexplored siblings:** <what remains>
- **Current state:** INCOMPLETE | COMPLETE

## Atomic concept notes touched this session

<Wikilinks to any concept notes created or extended. The Obsidian linking protocol applies — these should be bidirectional.>

- [[Rust Ownership]] — created
- [[Rust Borrowing]] — extended with the move-vs-copy section
- [[Result vs try-catch]] — referenced

## Next session

<What we agreed to cover next. One concept maximum per the cognitive-load discipline. If we deferred something, name it explicitly so it doesn't get lost.>

## Notes for self (the teacher)

<Private notes — what worked, what didn't, where the learner struggled, where the pace was wrong. Used to improve subsequent sessions.>
```

## Hub note pattern

Use a `<Project> Teaching Sessions.md` hub if the learner wants one.

```markdown
---
tags:
  - projects
  - projects/<project-slug>
  - resources/learning/teaching-sessions
type: "[[Synthesis Note]]"
date: <YYYY-MM-DD>
project: "[[<Project>]]"
---

# <Project> Teaching Sessions

Hub for the pair-teaching sessions on [[<Project>]]. Each session captured as a child note. Atomic concept notes accumulated here as cross-references.

## Sessions

| Date | Concept | Duration | Notes |
|---|---|---|---|
| 2026-05-15 | <Concept> | 90 min | [[<Project> Session 2026-05-15]] |
| 2026-05-22 | <Concept> | 120 min | [[<Project> Session 2026-05-22]] |

## Concepts learned (Rust cluster, growing)

- [[Rust Ownership]]
- [[Rust Borrowing]]
- [[Rust Lifetimes]]
- [[Result vs try-catch]]
- ...

(When 3+ accumulate around a sub-topic, propose a synthesis like [[Rust Memory Model]] per the Obsidian emergent-synthesis principle.)

## Teaching pedagogy reference

Link to the teaching skill or local teaching notes.
```

## Notes on usage

- **Capture the session at the end**, not in the middle. Mid-session capture interrupts flow. Mid-session, drop one-line stubs into a scratchpad if you must; expand to the full template at session end.
- **Don't over-format the worked examples**. The transcript-quality is fine. Don't waste teach-back-time formatting code that already lives in the project repo.
- **The teach-back capture is the most important section.** If you're short on time, prioritise it. The other sections can be filled later from memory or git diff; the teach-back has to be captured live or it's lost.
