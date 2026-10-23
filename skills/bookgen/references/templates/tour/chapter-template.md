# Tour-mode chapter template

For chapters in books that *read* an existing codebase rather than rebuild one. The pedagogical structure stays the same as reproduce-mode (predict-before-X, surface-the-model, teach-back, pain anchors), but the *X* shifts from "before-run" to "before-read", and the artifact-at-close shifts from "a runnable thing" to "a paragraph of understanding."

The reproduce-mode counterpart lives at `~/.skills/teaching/references/chapter-template.md`. This file documents what's *different*; everything not mentioned here matches the reproduce template.

## Filename and frontmatter

Same as reproduce mode. `docs/book/<NN>-<kebab-title>.md`, sequential numbering across the entire book.

Frontmatter additions for tour mode:

```yaml
---
chapter: NN
session_id: <SID>
title: <Human title>
phase: <phase letter>
estimated_time_minutes: 60
artifact: A paragraph-shaped understanding of <subsystem>
status: stub | complete
related_codebase: <path-or-url to the file/crate the chapter tours>
---
```

The `artifact:` line phrasing is the visible difference. In reproduce mode it names a thing the learner runs. In tour mode it names something the learner *understands and can demonstrate*.

## Section-by-section delta from reproduce mode

### `## What you'll build` → `## What you'll be able to do`

Reproduce-mode chapters say "you'll build X." Tour-mode chapters say "you'll be able to read / predict / explain X."

Example:

> By the end of this chapter, opening any file under `crates/protocol/` and predicting its purpose from the filename will return the right answer 80%+ of the time.

That's a measurable artifact even though nothing gets built.

### `## Surface your model first`

Same as reproduce mode (🤔 Q: prompts), but the questions are about *the existing code*, not *what the learner would write*.

Reproduce-mode example:
> 🤔 Q: How would you spawn a child process and capture stderr in Node?

Tour-mode equivalent:
> 🤔 Q: Looking at `crates/protocol/`'s file list, what would you expect each file to contain? What's the *minimum* file set a length-prefixed JSON codec would need?

The tour-mode question is anchored against *what the learner will see in the codebase next*, not *what they'd hypothetically write*.

### `## Concept slices`

Identical pattern (narrative + 🔮 Predict pauses + `<details>` calibration), but the predicts are about *existing code*:

```markdown
> 🔮 **Predict:** open `crates/protocol/src/codec.rs`. What's the function signature of `read_message`? What does it return on EOF? What does it return on a malformed length prefix?

<details>
<summary>Click after you've predicted</summary>

(reveal the actual signature and behaviour)

</details>
```

The predict happens *before opening the file*, not before running code. Most chapters will have 3–6 such predicts spread across the chapter's concept slices.

### `## Try it yourself`

Reproduce mode has the learner write a function. Tour mode has them **read a sibling file and predict before opening**.

```markdown
> 🛠️ **Your turn:** You've now read `crates/protocol/src/codec.rs`. Open `crates/protocol/src/types.rs` (which you haven't read). Before reading: predict three types it defines, predict whether they're enums or structs, predict their serde tagging strategy. Then open and check.
```

The discipline is: prediction muscle, applied to a new file. Tour-mode learners who skip this section are skim-readers; the section is what makes them active readers.

### `## Compiler conversation` (rare in tour mode)

Mostly absent. Tour-mode chapters that have one usually involve having the learner make a small modification to an existing file (remove a `'a`, drop a trait bound) to see what the compiler says. This is the *deliberate-error* pattern from the teaching skill's rule 6, applied to tour mode.

If the chapter has no such modification, drop this section.

### `## What you can run now` → `## What you can now read / explain / predict`

Reproduce mode: "Run this command. See the output."
Tour mode: "Open this file. Read it. Notice you understand it. Now open this sibling file. Predict it. Verify."

Example:

```markdown
## What you can now read

```bash
$EDITOR <path>/crates/protocol/src/types.rs
```

You should be able to read this file end-to-end with no surprises. If anything reads as new, go back to Concept N.

**Ladder check:** Coming into this chapter, you knew `crates/protocol/` existed. Now you can navigate it, read its types, and predict what the next file in the chain probably contains.

Next chapter ([Chapter NN+1: <title>](NN+1-name.md)): we follow the IPC envelope through to where it gets dispatched in the daemon.
```

### `## Teach-back`

Identical to reproduce mode. Three or so 📣 questions that exercise the chapter's one concept.

### `## Pain anchors covered`

Identical to reproduce mode, but the "Where you've felt it" column may also list behaviour the learner knows from using the toured codebase.

### `## Altitude ladder` (optional navigation aid)

Borrowed from Understand-Anything's multi-altitude views: the same subsystem can be understood at three altitudes, and a tour chapter can let the reader pick which one to zoom to. Use this when a subsystem is large enough that one flat pass would overload (rule 3).

- **Structural** — what calls what (functions, types, the literal call graph).
- **Layer** — how the files group into roles (API / service / data / UI / util).
- **Domain** — what business purpose the subsystem serves.

Move from the altitude the learner is at to the one they want; don't dump all three at once. A typical chapter sits at one altitude and names the others as "we'll zoom in / out next chapter." This is a *navigation* aid, not a licence to break the one-concept cap. The `dep-skeleton.json` from `sequence.py` gives you the structural altitude for free; layer and domain are your read of the code.

## Voice notes specific to tour mode

- **Predict-before-read is the entire pedagogical bet.** Solo readers who skim through `<details>` blocks without predicting are getting a blog post, not a teaching chapter. The chapter prose should reinforce this every few sections, not just at the open.
- **Live agents reveal one stop at a time.** A tour chapter may contain several predict-before-read pauses, but an agent running it live should present only the current file/function prediction, wait, then continue. Do not paste the whole tour map before the first prediction.
- **Use second person consistently.** "You'll open `crates/protocol/`" — not "we'll open." The reader is alone with the book.
- **Don't summarise the codebase.** If the chapter would have the reader predict-then-read a real file, replacing it with a paragraph summary cheats the predict-pause. The book's value is the predict cycles, not the summarised content.
- Edit tour prose for clarity and a human voice. Use an installed `humanizer` skill when available.

## Anti-patterns specific to tour mode

- **Re-explaining instead of having the learner predict.** If the chapter says "the function does X" before the learner has tried to predict X, the predict pause is wasted.
  - **Bad:** "`read_message` returns `Option<IpcMessage>` — `None` on EOF. Now open the file and you'll see that."
  - **Good:** "🔮 Predict: what does `read_message` return on EOF? Open `codec.rs` and check."
- **Walls of code excerpts.** Tour-mode chapters include code, but pasting whole files inline defeats the purpose. The reader should open the actual file in their editor. Quote 5–15 lines max, then point at the file.
  - **Bad:** a 120-line paste of `codec.rs` inline in the chapter.
  - **Good:** "Open `codec.rs`. Look at lines 40–55 — the length-prefix read. Notice it reads exactly 4 bytes first."
- **Pretending tour mode is reproduce mode in disguise.** If the chapter says "now write your own version of this function," that's reproduce mode bleeding through. Tour mode means *understand the existing version*, not *re-implement it*. Save reproduce-style exercises for an explicitly-marked "exercise" sidebar if useful.
- **Forgetting that the learner may have written this code.** For "tour your own code" books (see `chapter-01-template.md` for the two sub-variants), the framing acknowledges this explicitly. Don't write as if the codebase is alien when it isn't.

## See also

- `~/.skills/teaching/references/chapter-template.md` — the reproduce-mode template (longer; this file documents only the deltas)
- `chapter-01-template.md` — the tour-mode first-chapter shape, with sub-variants for own-code vs someone-else's-code
- `build-philosophy.md` — the artifact-as-paragraph framing this template depends on
- `readme.md` — how the TOC differs in tour mode
