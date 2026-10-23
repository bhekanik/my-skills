# Exercise answer-key template

Each `<NN>-<title>-exercises.md` has a sibling `<NN>-<title>-answers.md` with reference solutions and commentary. Per **rule 19**.

The answer key is **not just code** — it's the *commentary* on the choices the reference solution made. The learner who peeks should learn from the peeking, not just copy.

## Filename convention

```
docs/book/exercises/<NN>-<kebab-case-title>-answers.md
```

Same NN and slug as the exercises file.

## Required frontmatter

```yaml
---
chapter: 7
session_id: M2-2
title: DAP transport and atomic seq — answer key
exercises_file: <NN>-<title>-exercises.md
---
```

## Suggested file structure

```markdown
# Chapter NN — Exercise answer key

> ⚠️ Try the exercises before reading this. Peeking too early kills the transfer benefit.

## How to read this file

Each exercise gets:
- **Reference solution** — one valid implementation
- **Why it works** — what each choice teaches
- **Other valid solutions** — when the contract permits multiple shapes, what those shapes look like
- **Common wrong attempts** — patterns the test catches as failing, with the diagnosis

If your solution doesn't match the reference but the test passes, you're fine — that's the Implementation Swap Test working as designed (see the project's `tdd` skill). If the test fails and you don't know why, the "common wrong attempts" section is where to look first.

---

## 🛠️ Exercise 1 — Wield: <one-line concept>

### Reference solution

```rust
// crates/<crate>/tests/chapter_NN_exercises/wield.rs
pub fn <function_name>(...) -> ... {
    // implementation
}
```

### Why it works

<Walk through the choices made. What each line teaches about the concept. Where the reference solution touches the sticky-point the exercise targets.>

### Other valid solutions

<If the contract is behavioural (Implementation Swap Test passes), list 1–2 alternative shapes that also pass the test. For each, note what trade-off the alternative makes vs the reference solution.>

### Common wrong attempts

| Pattern | What the test catches | Diagnosis |
|---|---|---|
| `<wrong code shape>` | `<test failure mode>` | `<root cause — usually a chapter sticky-point>` |

---

## 🚀 Exercise 2 — Stretch: <cross-domain concept>

### Reference solution

```<language>
<code>
```

### Why it works

<Same structure as exercise 1. For cross-language stretches: explicitly compare what's the same vs different across the languages. The cross-language structure is *itself* the teaching content.>

### What this drill reveals

<For stretch exercises specifically: spell out what the learner now knows that they didn't before. "After doing this in C, you've felt why Rust's `AtomicI64` is a *language-level guarantee* rather than a library opt-in.">

---

## 🔀 Exercise 3 — Synthesise: <combining concepts>

### Reference solution

```rust
<code>
```

### Why it works

<Same structure. Specifically call out *where* the two concepts meet — the line(s) where the chapter's concept and the prior chapter's concept have to interact, and what makes the interaction non-trivial.>

### Common wrong attempts

| Pattern | Diagnosis |
|---|---|
| `<wrong shape>` | `<root cause>` |

---

## ✍️ Exercise 4 — Prose: <decision question>

### Reference answer

<400–600 words of prose. Cover the criteria listed in the exercises file. Show *judgment*, not just facts — when, where, why, what's the trade-off.>

### What a good answer covers

- ✅ <criterion 1> — <how the reference answer addresses it>
- ✅ <criterion 2> — <…>
- ✅ <criterion 3> — <…>

### Common gaps in submitted answers

| Gap | Why learners miss it | What the chapter teaches that closes it |
|---|---|---|
| `<gap>` | `<root cause>` | `<chapter section that fills it>` |

---

## See also

- ← [Chapter NN — exercises](<NN>-<title>-exercises.md)
- [Underlying chapter](../<NN>-<title>.md)
- [Teaching notes companion](../../teaching/notes/<NN>-<title>.md) (teacher-facing, anonymized)
```

## Style notes

- **Lead with the reference solution; commentary is the meat.** A solution without commentary is just a cheat sheet — the learner reads it and learns nothing about *why*. The commentary is where transfer happens.
- **Common wrong attempts come from real data.** Populate this section from the teaching-notes companion's "exercises authoring notes" — the patterns multiple learners hit. If the section is empty on first publish, leave a placeholder; fill as evidence accumulates.
- **For stretch exercises, the cross-domain comparison IS the lesson.** Don't just give the C answer — give the C answer alongside the Rust one and call out what each language *forces* you to think about that the other hides.
- **Honour creativity.** When the contract permits multiple solution shapes (Implementation Swap Test passes), say so explicitly: "the test passes; you're fine." Don't gaslight a learner who solved it differently.

## Anti-patterns

- **Reference solution with no commentary.** Just code = cheat sheet. Show the *thinking*.
- **Single-solution chauvinism.** When the contract permits multiple shapes, calling out only one as "the answer" misleads learners about what's actually being tested.
- **Spoilers in the visible part.** The exercises file links to the answer key; don't put solution code in the exercises file itself. Spoiler protection is the entire reason for the sibling-file structure.
