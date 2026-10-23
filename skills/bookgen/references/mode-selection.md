# Mode selection — reproduce / tour / extend

Three teaching modes a generated book can take. Each shapes chapters differently.

## Reproduce

The learner builds a clone of the anchor repo from zero. The original is the reference; the learner re-creates it chapter-by-chapter, hitting the same design decisions and the same compiler errors.

**When this fits:**

- Repo is small (under ~10K LOC; ideally under 5K for a 6-month arc)
- Codebase has clean module boundaries (separate concerns sliceable into sessions)
- The anchor repo's complexity comes from *design*, not from *scale* (a clean implementation of a non-trivial idea, vs. an enormous battle-tested system)
- Learner has enjoyed rebuilding small tools from scratch and wants to do that here.

**Examples:**

- A toy compiler (Crafting Interpreters in your target language)
- A redis clone (small in-memory store)
- An HTTP server from `accept()` upward
- A debugger frontend with a small protocol surface
- A small Git-like tool that makes repository primitives visible

**Chapter shape (reproduce):**

```
1. Surface the model — what would you guess this slice does?
2. Predict the function signatures / module shape
3. Walk through the original's approach in concept (not code)
4. Have the learner write their version
5. Compare against the original
6. Compiler conversation if a deliberate-error session is in scope
7. Demo: their version runs, produces the same observable output as the original
8. Teach-back
```

## Tour

The learner reads the existing codebase chapter-by-chapter. Each chapter explores one major subsystem with predict-pauses about *what each function probably does before reading it*. No rebuilding.

**When this fits:**

- Repo is large (10K+ LOC, often 50K+)
- Reproducing in 6 months is unrealistic — would result in a tutorial-grade clone, not the actual project
- The learner wants to *deeply understand* an existing system (often: a system they use professionally)
- Architectural concepts (consensus, scheduling, GC, optimisation passes) are where the learning is

**Examples:**

- The Linux kernel's scheduler subsystem
- TigerBeetle's storage engine
- Postgres's planner
- The Go runtime
- Rustc's borrow checker pass
- Helix's text editor core

**Chapter shape (tour):**

```
1. Surface the model — given the subsystem's name, what would you guess it does?
2. Predict the entry points (function names, module structure)
3. Read the actual entry points together; calibrate predictions
4. Read one or two key functions in depth, predicting before each
5. Identify the pattern (e.g., "this is a worklist algorithm", "this is double-buffered")
6. Connect to the broader codebase (where else does this pattern appear?)
7. Demo: explain the subsystem to a junior engineer in one paragraph
8. Teach-back
```

Tour-mode chapters are *reading* chapters, not *writing* chapters. The artifact at chapter close is *understanding*, not running code. Make this explicit in the book's introduction so the reader doesn't expect "you'll have built X" promises.

## Extend

The learner takes the existing repo and adds one new feature or subsystem per chapter. Cumulative as in reproduce mode, but each chapter is a *contribution*, not a *re-implementation*.

**When this fits:**

- Repo is medium (5K – 50K LOC)
- Repo is *open to extension* — clean plugin API, well-defined extension points, or active issue tracker with feature requests
- The learner is willing to commit to features that *they* find useful (this matters; if the feature doesn't matter to them, motivation drops)
- The repo's maintainers welcome contributions (or the learner is forking and doesn't care)

**Examples:**

- Adding a new adapter to the anchor project (each adapter can be one chapter)
- Adding a new language to a multi-lang HTTP framework
- Adding a new optimisation pass to a JIT
- Adding a new visualization plugin to a charting library

**Chapter shape (extend):**

```
1. Surface the model — what should this feature do, from a user's perspective?
2. Survey the existing extension API — what does the codebase expect of new contributors here?
3. Predict the integration points (which files will you touch?)
4. Read the existing API contract
5. Implement the feature, with predicts before each design choice
6. Test against the existing test suite
7. Demo: feature works, didn't break anything
8. Teach-back
```

## How to recommend in step 3 of the workflow

Frame the recommendation as one line with reasoning, then invite override:

> "Recommend: **reproduce mode**. The repo is 4K LOC with clean boundaries, and you said you enjoy rebuilding small tools. Override if you'd rather tour or extend?"

> "Recommend: **tour mode**. TigerBeetle is 80K LOC of careful systems code. Rebuilding in 6 months would teach you about *tutorial systems*, not about *TigerBeetle*. Tour mode reads the actual code with you. Override?"

> "Recommend: **extend mode**. Helix is 30K LOC and has an active community plugin ecosystem. Adding a feature each chapter teaches you Rust idioms in context, in a codebase you actually use day-to-day. Override?"

## Templates by mode

The mode determines which template directory the agent pulls from in step 6 of the workflow:

| Mode | Template directory | Notes |
|---|---|---|
| reproduce | `references/templates/reproduce/` | Has: introduction.md, what-is.md, why.md, readme.md, agents-md.md, build-philosophy.md |
| tour | `references/templates/tour/` | Has: build-philosophy.md, chapter-template.md, chapter-01-template.md, readme.md (delta from reproduce) |
| extend | `references/templates/reproduce/` (closest fit; agent adapts inline) | A dedicated `extend/` directory may be added when extend-mode books accumulate |

The scaffold script `scripts/scaffold.sh` reads the mode and copies the right `build-philosophy.md` into the output repo's `docs/teaching/` automatically. The agent still picks the chapter-shape templates manually based on mode.

## Tour mode has two sub-variants

Tour-mode chapter 01 has a meaningful sub-variant choice:

- **Variant A (own-code tour)**: the learner wrote the anchor codebase. Framing: "predict before you re-read; don't be defensive about your past code."
- **Variant B (someone-else's-code tour)**: the learner is a user/admirer of the codebase but didn't write it. Framing: "predict before you read; the codebase has design rationale you'll discover as you go."

Detect via `git log --author="<learner-email>"` or ask. The two chapter-01 variants are in `references/templates/tour/chapter-01-template.md`.

## Hybrid modes (rare)

Most books pick one mode and stick with it. Occasionally a hybrid works:

- **Reproduce-then-extend**: build a small core from zero (chapters 1–10), then extend it with features (chapters 11+).
- **Tour-then-extend**: read the existing code first (chapters 1–10), then add a feature subsystem (chapters 11+).

Hybrids work but they're harder to design. If a learner asks for a hybrid, push back unless they have a specific reason. Single-mode books are easier to scope and easier to follow.

## Anti-patterns

**Picking reproduce for a repo that's too big.** A 50K-LOC reproduce would take 5+ years. Push the learner toward tour mode if the codebase is over ~10K LOC, even if they say they want to rebuild.

**Picking tour for a small repo.** A 1K-LOC tour book is just a code-reading session, which doesn't compound for 6 months. Push toward reproduce for small repos.

**Picking extend for a hostile codebase.** If the repo's contribution guidelines are unclear, the maintainers are unresponsive, or the architecture is hard to extend (god objects, no test suite, no public extension API), extend mode will frustrate the learner. Push toward reproduce or tour.
