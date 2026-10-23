# Book chapter template

Every learning-book session produces a **shareable chapter** under the project's `docs/book/` directory, alongside any private session note the learner requested. The chapter is a *cleaned narrative* designed for two consumption modes. Publishing it outside the repository requires the user's authorization:

1. **Solo reader** — works through the chapter under their own steam, pausing at the predict-points, typing the code, hitting the same compiler errors. Like Vim Tutor in book form.
2. **LLM-as-teacher** — an agent loads the chapter as a script, runs the session live and responsively (surfaces the learner's prior model, calibrates, lets compiler errors land).

## Filename convention

```
docs/book/<NN>-<kebab-case-title>.md
```

- `NN` is sequential across the entire book (zero-padded, 01–99). NOT the session ID.
- The session ID (e.g. `WS-1`, `M0-1`) goes in the chapter's frontmatter, not the filename. This keeps the book's reading order linear regardless of how the underlying milestone plan evolves.

Example: `docs/book/04-hello-adapter.md` for session `M0-1`.

## Required frontmatter

```yaml
---
chapter: 4
session_id: M0-1
title: Hello, adapter
phase: A
estimated_time_minutes: 60
artifact: A binary that spawns codelldb and prints its first chunk of output
prerequisites:
  - chapter 03 (conventions-as-code)
  - cargo workspace exists from chapter 01
new_concepts:
  - tokio::process::Command and async process spawning
  - kill_on_drop and the Drop trait (gloss only)
  - Option::take and mutability propagation through fields
related_milestone: docs/implementation/tasks/M00-hello-adapter.md
evidence:
  status: consensus                         # consensus | tension | pitfall-heavy | disputed | exploratory
  sources:
    - title: <source title>
      url: <url>
      role: <why this source shaped the chapter>
  common_misunderstandings:
    - <false model this chapter corrects>
  gaps:
    - <what this chapter deliberately does not cover yet>
---
```

## Suggested chapter structure

The structure is *suggested, not strict*. Some chapters are ceremony-heavy and need different shapes. Use judgment.

```markdown
# Chapter NN — <Title>

> Session ID: `<WS-1 | M0-1 | ...>` · Phase <0|A|B|C|D|E> · ~<N> min · [Underlying milestone](../implementation/tasks/MNN-name.md)

## What you'll learn

(2–3 sentence preview. State the *one* new concept. Mention what's deferred to later chapters.)

## What you'll build

(1–2 sentence description of the artifact. End with a concrete promise:)

> By the end of this chapter, running `<command>` will print `<expected output>`. That's something you couldn't do before chapter NN.

## Before you start

Prior knowledge assumed:
- (bullet)
- (bullet)

Setup state required (run these to confirm you're ready):
- `<verification command>` — should output `<expected>`
- (etc.)

If you skipped chapters, read [the setup recovery section](../book/00-introduction.md#picking-up-mid-book) first.

---

## Surface your model first

> 🤔 **Q:** <a question that surfaces the reader's prior model — JS / TS / Python / C analog>

Pause and answer in your head before continuing. (For LLM mode: the agent will wait for your answer.) If you use a term loosely here, your teacher may pause to sharpen it. That pause is part of the lesson, not a tangent.

<details>
<summary>Click after you've answered</summary>

(Discussion of common answers. *Don't* preserve any one specific learner's wrong prediction — write for the population. "Many readers say X — that's a partial truth. Here's where it diverges.")

</details>

---

## <Concept slice 1>

(Narrative explanation. Pain anchor where applicable — "in C, this is painful because Y; in JS it's invisible until production." Then how the new construct handles it.)

```rust
// code
```

> 🔮 **Predict:** <prediction question>

<details>
<summary>Click after you've predicted</summary>

(What actually happens, plus the *why*. If many readers will predict wrong here, surface the partial truth and the gap.)

</details>

## <Concept slice 2>
...

---

## Try it yourself

### Single-stage shape (default)

> 🛠️ **Your turn:** <task — concrete, single-step, builds on what was just shown>

After you've written it, run:

```bash
<command>
```

Expected output:

```
<output>
```

If you got something different, common causes are:
- (likely cause 1) — fix is `<fix>`
- (likely cause 2) — fix is `<fix>`

**Graduated hints (rules 5–6, 21).** If you stall, don't reach for the answer. Escalate one level at a time, only after a real attempt: **L1 nudge** (point at the area, sharper question) → **L2 structure** (name the shape of the answer, no code) → **L3 near-spoiler** (the missing piece, then restate why). Solo readers get this as nested `<details>` blocks; an LLM-as-teacher applies it live and drops a level only when an attempt genuinely fails.

### Multi-stage shape (use when the exercise has cleanup, restore, or distinct verifiable states)

Per rule 4's checkpoint discipline, multi-stage exercises must pause for verification *between* stages, never collapse into "do everything then tell me." The cleanup or restore step destroys the prior state's evidence; without a checkpoint the agent can't verify the build worked.

> 🛠️ **Your turn — Stage A (build):** <construction task>
>
> Run `<verify command>` and confirm `<expected outcome>`. **Stop here and tell me you're at this point** so we can verify the build state together before you tear it down.

(Agent verifies stage A.)

> 🛠️ **Your turn — Stage B (cleanup / next state):** <cleanup or transition task>
>
> Run `<verify command>` again. **Stop and tell me** so we can verify the cleanup state.

(Agent verifies stage B.)

The same shape applies to *modify-then-restore* sequences (compiler-conversation pattern), *add-then-test-then-refactor* sequences, and any other "you do" with multiple verifiable states. **Each state with a distinct teaching target gets its own observable checkpoint.**

---

## Compiler conversation

(Where applicable: a deliberate-error walkthrough. Have the reader remove a keyword, run the build, read the compiler's response together, **stop for the agent to verify the error landed**, then restore. The mid-pause is non-negotiable — once the file is restored, the error message is gone and the agent can't verify the learner saw the right error. Use the multi-stage shape from "Try it yourself" above.)

---

## What you can run now

```bash
<final demo command>
```

Output:

```
<final output>
```

**Ladder check** — connect this to the previous chapter's artifact:

> Last chapter (`<title>`) you had `<previous capability>`. Now you have `<new capability>` on top. <One-line forward look.>

---

## Teach-back

Before moving on, answer these in your own words. If you can't, re-read the relevant section.

> 📣 **Q1:** <teach-back question on the core concept>
> 📣 **Q2:** <teach-back question on a subtle/surprising point>

---

## What people usually get wrong

(Use when the concept has predictable false models. Be sympathetic: most misunderstandings are reasonable transfers from another language, framework, or simplified slogan. Each important misunderstanding should also have a diagnostic probe in the teaching-notes companion.)

- <misunderstanding> — <why it is tempting> — <the corrected model>

> 🧪 **Probe:** <short question or prediction that reveals whether this false model is present>

## What this chapter does not cover yet

(Use this to preserve the one-concept cap without pretending the simplified model is the whole truth.)

- <deferred concept or weakly supported area> — <where it will be handled, or why skepticism is warranted>

---

## Pain anchors covered

| New construct | The pain it solves | In which language |
|---|---|---|
| `<construct>` | `<pain>` | C / JS / Python |

---

## Exercises

> Per rule 19. Skip this section only if the chapter is ceremony with nothing to reinforce.

See [`exercises/<NN>-<title>-exercises.md`](exercises/<NN>-<title>-exercises.md) for the full set; quick preview:

- 🛠️ **Wield:** <one-line description of the near-context exercise>
- 🚀 **Stretch:** <one-line description of the cross-domain exercise>
- 🔀 **Synthesise:** <one-line description combining a prior chapter's concept>
- ✍️ **Prose:** <one-line question for the decision-flavoured exercise>

Pick one or all; live in-session if your agent is running you through this chapter, async otherwise. Reference solutions and commentary at [`exercises/<NN>-<title>-answers.md`](exercises/<NN>-<title>-answers.md) — peek only after you've taken your own swing.

---

## Sources

(Only include sources that materially affected the chapter. Prefer primary docs/specs/code for operational claims; use papers or expert commentary when the concept is genuinely research-shaped. Record rejected sources in teaching notes, not the public chapter, unless the rejection itself is educational.)

- [<Source title>](<url>) — <role in this chapter>

## See also

- ← [Chapter NN-1: <previous title>](NN-1-name.md)
- → [Chapter NN+1: <next title>](NN+1-name.md)
- [Underlying milestone](../implementation/tasks/MNN-name.md)
- (optional) Atomic concept references in the learner's KMS
```

## Style notes

- **Voice:** second person ("you'll write", "you'll see"). No first-person plural ("we"). The reader is alone with the book; *they* are the doer.
- **Code blocks:** always include language tag (`rust`, `bash`, `toml`). Always include the *full output* as a separate block, never inlined as a comment.
- **Don't preserve the original learner's mistakes.** Common-wrong-prediction info goes in the *teaching notes* file (see below), not the chapter. The chapter writes for the *population* of readers.
- **Predict-pauses use `<details>` tags** so reading flows when collapsed and reveals the calibration when expanded. Works on GitHub, mdBook, and most renderers.
- **Honour the cumulative narrative.** Every chapter ends with a "ladder check" connecting back to the prior artifact. Every chapter starts with a setup-verification step.
- **One concept per chapter** is the cap (rule 3). If you find yourself writing two new concepts, split into two chapters and update the project's session plan.
- **Evidence posture matters** (rule 20). Mark consensus, real tensions, pitfalls, misunderstandings, and gaps in frontmatter when external knowledge shapes the chapter. Do not manufacture tension where there is only branching.
- **Socratic pressure matters** (rule 21). Common misunderstandings should become probes. Fuzzy terms should be sharpened live. If the learner claims confidence, test an edge case or real tension before moving on.
- **Graduated hints, never giveaways** (rules 5–6, 21). When a reader stalls on a "Try it yourself" or a predict-pause, escalate L1 nudge → L2 structure → L3 near-spoiler; drop a level only after a real attempt. Withhold the finished solution; offer the smallest hint that closes the specific gap.

## Companion: teaching notes

Each chapter has a *companion teaching-notes file* under `docs/teaching/notes/<NN>-<title>.md`. This is **not for the public reader** — it's where the agent (or a human teacher) records:

- Common wrong predictions actual learners gave (and why they made sense)
- What surprised the learner that the chapter could pre-empt
- Refinement ideas for the chapter
- Sticky points that needed a second pass

See `references/teaching-notes-template.md` for the structure. Update the teaching notes after every live session that uses the chapter.

## The chapter is the script for LLM-as-teacher mode

When an agent runs a session live (LLM-as-teacher mode), the chapter is the **canonical curriculum**, not a suggestion. The agent must:

- **Reveal the chapter progressively** — do not paste the whole chapter, full lesson outline, reflection, teach-back, and exercises into chat. Ask the current question, wait, calibrate, then move to the next slice.
- **Follow the predict-pauses in order** — surface the same prior model, ask the same predict questions, hit the same compiler conversations, demonstrate the same artifact. Don't substitute "your favourite way to teach this" for what the chapter says.
- **Use the chapter's pain anchors** — they were chosen for a reason (the project's anchor table + the learner profile). Don't substitute random analogies.
- **Calibrate dynamically inside the script.** The learner's specific prediction is the data point; the chapter's `<details>` block is the *menu of common responses* you're calibrating against. If the learner predicts something the chapter didn't anticipate, address it AND log it in the teaching-notes file for future chapter revision.
- **Don't skip ahead** even if the learner seems to know it. The chapter's order is deliberate (cognitive load discipline). If the learner's clearly past a section, mark a teach-back pass and move to the next predict.
- **Don't invent new concepts in-session.** The chapter caps at one new concept (rule 3). If something genuinely new comes up that the chapter doesn't cover, capture it as a follow-up and stay on the chapter's concept.

The contract: **the book is the ground truth; live mode adds responsiveness, not curriculum invention.** When the agent improvises curriculum, the book's value (consistent shareable learning) collapses.

If the chapter is wrong or missing something, **fix the chapter** (and its teaching-notes), don't route around it.

## Anti-patterns

- **Dialog transcripts.** Chapters are cleaned narrative, not literal dialog. Predict-pauses preserve interactivity without preserving the original conversation.
  - **Bad:** "Then I asked you about ownership, and you said it would still be usable…" — reproducing the live session turn by turn.
  - **Good:** "Many readers expect the value to still be usable here. It isn't — here's why," written for the population.
- **Linking to private notes.** Keep private session notes out of the chapter. Cross-link only to other chapters and to content intended for the book's readers.
- **Skipping the predict-before-run pauses.** They're the core of the pedagogy. A chapter without `<details>`-wrapped predicts is a flat tutorial, not a teaching chapter.
- **Stating the answer in the predict question itself.** The question must be genuinely answerable wrong.
  - **Bad:** "What does `Command::new` return — a `Command` builder?" (the answer is in the question)
  - **Good:** "After `Command::new("ls")`, has the process started yet? What do you have in your hand?"
- **Fake tensions.** Branches dressed up as trade-offs.
  - **Bad:** "REST vs GraphQL" or "supervised vs self-supervised" presented as a deep tension.
  - **Good:** the real trade-off underneath — "stable coarse-grained contracts vs client-shaped data access" — or say plainly the choice is contextual.
- **Uncited confidence on external claims.** If the chapter leans on runtime, language, framework, or research facts outside the repo, cite the source of truth or mark the gap.
- **Live-mode improv that abandons the chapter.** If the agent finds itself teaching things the chapter doesn't cover, *in the chapter's order*, the chapter has been abandoned — that's a regression to "teaching skill without book." Route surprises into teaching-notes instead.
- **Live-mode chapter dumping.** If the agent pastes the whole lesson or all exercises before the learner has answered the first predict-pause, the chapter has stopped being interactive. Keep the long-form chapter in the file; keep the chat bite-sized.
