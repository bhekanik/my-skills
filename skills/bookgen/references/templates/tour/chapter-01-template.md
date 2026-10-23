# Tour-mode chapter 01 — first-chapter framing

The first chapter sets the tone for the whole tour. It has to do two things at once:

1. **Land a useful artifact** (concept slice complete; learner can predict their first file).
2. **Establish the pedagogy norm** (predict-before-read is real; the learner has to do the work).

There are two sub-variants depending on whether the learner *wrote* the anchor codebase or not.

## Sub-variant A — Tour your own code

The learner wrote or co-wrote the anchor repo. For example, they may tour a project they shipped years ago.

The framing is: **predict before you re-read; don't be defensive about your past code.**

Specific moves the chapter should make:

- Open with: "You wrote this. The exercise is to predict the code before you re-read it. The version of you reading it now knows more Rust than the version that wrote it."
- The first 🤔 Q: prompt is anchored against the learner's own memory: "Without looking, how many crates does the project have? Name as many as you can."
- The first 🔮 Predict prompt is "I think this function does X" against a function the learner wrote.
- The 🛠️ Your turn section is "open a sibling file you don't recall as clearly. Predict it. Verify."
- The teach-back asks the learner to articulate the design choice, *and* to articulate one thing they got wrong. The wrong-prediction is gold; surfacing it is the chapter's success metric.

Use the variant A template below to ask the learner what they remember before showing the code.

## Sub-variant B — Tour someone else's code

The learner is a user, admirer, or new contributor of the anchor codebase but didn't write it. Examples: someone touring TigerBeetle to learn Zig; a Rust learner touring rustc; a database engineer touring Postgres.

The framing is: **predict before you read; the codebase has design rationale you'll discover as you go.**

Specific moves the chapter should make:

- Open with: "You've used this project. You've read parts of it. The exercise is to *predict before you read*, even on parts you've encountered before — predicting forces active reading instead of skimming."
- The first 🤔 Q: prompt is anchored against the project's *external behaviour*: "What does this project do, in three sentences? What user-facing surfaces does it expose?"
- The first 🔮 Predict prompt is structural: "Open the project's `Cargo.toml`. Predict three crates from the README description. Verify."
- The 🛠️ Your turn section is "pick a crate name you don't recognise. Predict its purpose from the name. Open it. Calibrate."
- The teach-back asks the learner to articulate the project's *design* — what it chose to do and what it chose not to do.

There's no canonical worked example yet. The first time `/bookgen` is invoked against a foreign repo with `--mode tour`, capture the resulting chapter 01 here.

## Detecting which sub-variant applies

When `/bookgen` runs in tour mode, ask the learner:

> "Did you write this codebase, or are you touring someone else's?"

If they say they wrote (or co-wrote) it: variant A.
If they say they didn't: variant B.

A reasonable default check (when the user doesn't answer): scan the anchor repo's `git log --author="<user-email>"` for commits. If they have substantive commits (e.g., 10+ non-trivial), variant A is the better default.

## What's the same across both variants

- Sequential numbering (chapter 01).
- One new concept (whatever the chapter teaches — workspace structure, the central abstraction, the architecture entry point).
- Predict-before-read pauses with `<details>` blocks for calibration.
- A teach-back at chapter close.
- Pain anchors where applicable.
- The compiler-conversation pattern is *rare* in tour-mode chapter 01s; usually no deliberate-error walkthrough until later chapters.

## Anti-patterns

- **Variant A pretending to be Variant B.** If the learner wrote the code, don't pretend they're discovering it from scratch — they aren't. The pedagogy needs to acknowledge the prior knowledge and use it.
- **Variant B pretending to be Variant A.** If the learner didn't write the code, don't write "you wrote this" framings — they'll feel false and disorient the learner.
- **Skipping the framing entirely.** Both variants depend on the framing because it sets the contract for the rest of the book. Without it, the predict-pauses feel arbitrary.
- **Treating the sub-variant as cosmetic.** The actual *prompts* differ between variants — variant-A prompts assume memory recall, variant-B prompts assume external/structural knowledge. Don't paste a variant-A prompt into a variant-B chapter.

## See also

- `chapter-template.md` — the general tour-mode chapter shape both variants share
- `build-philosophy.md` — the artifact-as-paragraph contract
- Adapt the variant A prompts to the learner's actual code and memory of writing it.
