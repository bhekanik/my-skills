# bookgen workflow — extended walkthrough

Step-by-step, with worked examples. The summary lives in the skill's `SKILL.md`; this is the depth.

## Step 1 — Confirm scope and intent

Ask the learner four things in order. Don't skip; the answers feed every subsequent step.

### 1a. Target language

> "Which language do you want to learn? Rust, Go, Swift, Zig, OCaml, Elixir — or something else?"

Pre-baked anchor tables exist for the six listed; for "something else," you'll need to construct an anchor table from the learner's prior-language pains in real time.

### 1b. The anchor repo

> "Which repo do you want to anchor the book against? GitHub URL or local path. Pick something you'd genuinely want to spend several months working through."

Probe for genuine interest, not arbitrary picking. If the learner names a repo they've never used, that's a yellow flag — engagement drops. Better fit: their own past projects, OSS they actively use, libraries they admire.

### 1c. Prior-language background and pains

> "What languages have you shipped real work in? And — this is the load-bearing question — what *pains* have you felt with those languages? Things like: NULL dereferences, manual memory, exception-throws-from-anywhere, switch fall-through, dependency hell."

The pains they list here populate the pain-anchor table (rule 7 of teaching skill). If they've felt the pain, the target language's solution lands as a *gift*. If they haven't, it lands as trivia.

### 1d. Motivation (the why)

> "Why this language, why this repo, why now? It's fine to say 'just curiosity' — that goes in the why chapter."

This populates `00c-why-i-built-this.md`. Capture the learner's actual reasons and words; do not supply a stock motivation.

## Step 2 — Analyse the anchor repo

Time-box this to ~15 minutes. You're getting a useful picture, not a comprehensive audit.

### 2a. Clone or read in place

If the user gave a GitHub URL, clone it into a disposable directory. If they gave a local path, fetch its default branch and read the fetched ref without changing their working tree. Record the SHA behind the chapter examples.

### 2b. Take measurements

```bash
cd <repo>
echo "Top-level structure:"
ls -la
echo
echo "Lines of code by language:"
tokei . 2>/dev/null || cloc . 2>/dev/null || (find . -name '*.rs' -o -name '*.go' -o -name '*.swift' | xargs wc -l)
echo
echo "Size:"
git log --oneline | head -20
echo
echo "Largest source files:"
find . -name '*.<primary-extension>' | xargs wc -l 2>/dev/null | sort -rn | head -10
```

Tokei is preferred. Cloc is the fallback. Bare `wc -l` works as last resort.

### 2c. Look for natural phase markers

In order of preference:

1. `docs/blueprint/`, `docs/roadmap/`, `RFCs/` directories — these often define explicit phases
2. `CHANGELOG.md` — major version bumps often correspond to teaching phases
3. `README.md` "Architecture" or "Design" sections
4. Top-level module structure (for example, protocol, service and UI modules may suggest three phases)
5. Git log searching for "milestone", "phase", "release" keywords

If none of these exist, the repo's natural shape will have to be inferred from module structure and dependency graph.

### 2d. Identify prerequisite knowledge

What does the learner need to know *before* they can productively work through this codebase? Examples:

- A debugger frontend may require understanding its protocol and where it sits in the stack before touring its code.
- A web framework (axum) requires knowing what HTTP is and what async means
- A database (TigerBeetle) requires knowing what consensus is and what direct I/O is

The prerequisites become the `00b-what-is-<X>.md` chapter.

### 2e. Run the deterministic facts pass (two-phase)

Don't reconstruct the dependency structure by reading files — run the script and reason over its output. This is the Understand-Anything pattern: a deterministic skeleton, with LLM judgment layered on top. The structure is reproducible; only the meaning is yours to add.

```bash
<bookgen-skill-dir>/scripts/sequence.py \
  --anchor-repo <repo> --book-repo <output-repo>
```

This writes `docs/teaching/dep-skeleton.json` (dependency graph, detected entry point, per-file fan-in/fan-out, key definitions) and `docs/teaching/suggested-order.md` (a BFS-from-entry ordering). Trust it for *what depends on what*; do not re-extract structure by hand. Tree-sitter is used when installed; otherwise it falls back to regex — coarser but still useful (see `scripts/requirements.txt`).

For a large tour-mode repo (10K+ LOC), also run `scripts/compute_batches.py --anchor-repo <repo> --book-repo <output-repo>` and analyse the batches it plans, writing each `docs/teaching/intermediate/batch-NN.json` to disk and reducing from there rather than holding the whole repo in context.

## Step 2.5 — Build the source map

Before mode selection and session planning, write the evidence preflight that keeps the book honest.

Target path:

```txt
<output-repo>/docs/teaching/source-map.md
```

If the project already has a `docs/research/` or `literature/` convention, use `docs/research/<subject>/<topic>-review.md` and link it from `docs/teaching/source-map.md`.

Use four depth levels:

| Level | Use when | Sources |
|---|---|---|
| 0 | Local code walkthrough | Anchor repo code only |
| 1 | Language/runtime/API behaviour | Official docs, specs, source code |
| 2 | Ecosystem practice or architecture | Docs plus expert commentary, postmortems, mature blog posts |
| 3 | Research-shaped claims | Papers, surveys, citations, competing empirical evidence |

The source map records:

- **Consensus** — stable claims the book can teach directly.
- **Real tensions** — trade-offs or active disagreements. Branches are not tensions; name the deeper question.
- **Common misunderstandings** — false models learners bring from slogans, outdated docs, or prior languages.
- **Pitfalls** — runtime/tooling/platform behaviours that surprise people.
- **Gaps** — thin evidence, version-specific caveats, or concepts deliberately deferred by the one-concept cap.
- **Sources kept** — title, URL, and why it matters.
- **Curriculum tree** — root → branches → real tensions → leaves → pitfalls. Branches are accepted subtopics; tensions are contested trade-offs under those branches.
- **Probe bank** — diagnostic questions for each major misunderstanding or pitfall.
- **Sources dropped** — title and exclusion reason, so future agents don't reintroduce weak material.

Keep it useful, not academic for its own sake. A Rust compiler chapter may need official docs and source code. A chapter on learning science may need actual papers. A pure tour of a local module may need no external sources at all.

Recommended shape:

```markdown
# Source map: <topic>

## Curriculum tree

- Root: <topic>
  - Branch: <accepted subtopic>
    - Real tension: <contested trade-off or active disagreement>
    - Pitfall: <known trap>
    - Leaf: <fine-grained question>

## Probe bank

| Misunderstanding / pitfall | Diagnostic probe | Expected wrong answer | Calibration |
|---|---|---|---|

## Consensus

## Tensions

## Common misunderstandings

## Pitfalls

## Gaps

## Sources kept

## Sources dropped
```


## Step 3 — Mode selection

Three modes; see `mode-selection.md` for full criteria. Brief summary:

- **Reproduce**: build a clone from zero. Best for repos under ~10K LOC where the learner has time and patience to rebuild. Each chapter rebuilds one slice.
- **Tour**: read existing code chapter-by-chapter. Best for large repos (10K+ LOC) where rebuilding isn't realistic. Each chapter explores one major subsystem with predict-pauses about what each function probably does before reading it.
- **Extend**: take the repo, add features as chapters. Best for medium-sized repos that are feature-extension-friendly. Good for fork-and-evolve learners.

Recommend one mode with one-line reasoning. Ask if the learner wants to override. If the source map reveals that the concept space is research-heavy or disputed, say how that affects the mode recommendation.

Examples:

> "Recommend: **reproduce mode** — the repo is 4K LOC, has clean module boundaries, and you said you enjoy rebuilding small tools. Override?"

> "Recommend: **tour mode** — the repo is 80K LOC and includes a full network stack. Rebuilding from zero in 6 months isn't realistic; we'd be building tutorial code, not the actual project. Override?"

## Step 4 — Generate the session plan

Write `<output-repo>/docs/teaching/sessions.md` as a table grouped by phase.

Constraints:

1. **One new concept per session** (rule 3). If a session would need two, split.
2. **Each session ships an artifact** (rule 13). If no artifact, name it as ceremony.
3. **Cumulative arc.** Chapter N's artifact builds on chapter N−1's. Skateboard → scooter → bike. Don't pile concepts toward a future arrival.
4. **Phase markers visible.** Group sessions into phases (Phase 0 / A / B / C / D / E or whatever maps to the repo's natural structure). Phase boundaries are good moments to *celebrate* in the book.
5. **Defer load multipliers** (rule 8). Async, generics with multiple trait bounds, macros — introduce shallowly first; deep-dive later. Order matters.
6. **Carry evidence posture forward** (rule 20). Each session row should note relevant consensus, tension, pitfall, misunderstanding, or gap from the source map. Avoid fake tensions; if the difference is just a branch, say so.
7. **Carry Socratic pressure forward** (rule 21). Each session row should identify likely fuzzy terms, at least one diagnostic probe for the key misunderstanding, and what Confused/Aware/Confident would look like.
8. **Start from `suggested-order.md`** (step 2e's `sequence.py` output). It is the dependency-derived BFS order: overview → core types → features → infrastructure. Re-shape it for pedagogy (one-concept cap, defer-load, pain anchors), but don't contradict the dependency graph without a reason.
9. **Prerequisite-integrity invariant.** Every `requires:` concept must be `teaches:` by an earlier chapter. After writing the plan, run `scripts/chain_index.py --book-repo <repo> --strict`; an unresolved `requires:` is a planning bug — fix it before scaffolding, don't let the learner hit it.

Length: aim for 25–50 sessions for a 6-month, daily-practice arc. A few more if the repo is dense.

## Step 5 — Scaffold the book skeleton

Use the bundled `scripts/scaffold.sh` helper. It handles the mechanical parts (directory tree, vendored skills, VERSION file, anchor table copy, build-philosophy copy, optional first commit) idempotently:

```bash
<bookgen-skill-dir>/scripts/scaffold.sh \
  --output-dir   <output-repo> \
  --target-language <rust|go|swift|zig|ocaml|elixir> \
  --anchor-repo  <path-or-url> \
  --mode         <reproduce|tour|extend>
```

The script does NOT write the seed chapters (00, 00b, 00c, 01) — those need the learner's stated motivation, source-map judgment, and the agent's chapter-writing judgment, so they stay manual. The script is for the *mechanical* setup: directories, vendoring, anchor table installation, mode-appropriate build-philosophy copy.

For the `<output-repo>` location, ask the learner. Default suggestion: `~/code/<owner>/<project>-book` (book repo separate from the source code repo).

After the script runs, the agent writes the seed chapters (step 6), then re-runs the script with `--commit` to land the first commit.

## Step 6 — Write the seed chapters

Three chapters get full content; the rest stay stubs.

**Branch on mode for templates.** The templates live under `references/templates/<mode>/`:

| Mode | Templates directory | Build-philosophy installed by scaffold script |
|---|---|---|
| reproduce | `references/templates/reproduce/` | `reproduce/build-philosophy.md` (artifact-as-binary) |
| tour | `references/templates/tour/` | `tour/build-philosophy.md` (artifact-as-paragraph) |
| extend | `references/templates/reproduce/` (closest fit; tweak inline) | reproduce variant for now |

**Compose each filled chapter in passes (Re3 / LongWriter).** Outline the sections with intent and a rough length budget, expand one section at a time, then run two *separate* editorial passes — a coherence pass (follows the outline, reuses prior chapters' terms) and a factual pass (every claim and code block verified, per "Verify before publishing"). Keep them separate; fusing them lets factual errors hide behind smooth prose.

### 6a. `00-introduction.md`

Adapt `references/templates/<mode>/introduction.md` (or fall back to `reproduce/introduction.md` if the mode-specific one isn't present). Three pedagogical ideas (surface-the-model, predict-before-run, compiler-as-teacher) are universal across modes. Project-specific bits get filled from step 1's answers and step 4's plan.

For tour-mode books, replace "build" / "you'll have X you can run" framings with "read" / "you'll be able to predict / explain X" framings.

### 6b. `00b-what-is-<X>.md`

The required technical context. Adapt `references/templates/<mode>/what-is.md`. The pattern: *what is the domain* + *where does this sit in the architecture* + *is this a wrapper and why does that miss the point*. Different per repo.

If the anchor project has existing reference or architecture docs, link to them and summarise the useful parts here.

### 6c. `00c-why-i-built-this.md`

Adapt `references/templates/<mode>/why.md` from the learner's actual answers in step 1d. Do not substitute a stock motivation.

For own-code tours, use the variant A template in `references/templates/tour/chapter-01-template.md`.

### 6d. `01-<title>.md`

Full first chapter. The shape depends on mode:

- **Reproduce mode**: use the sibling `teaching` skill's `references/chapter-template.md`. Chapter 01 is usually project setup (workspace, conventions). Often a light concept session.
- **Tour mode**: use `references/templates/tour/chapter-template.md` *and* `references/templates/tour/chapter-01-template.md`. The latter has two sub-variants depending on whether the learner wrote the anchor code (variant A — predict before re-read) or didn't (variant B — predict before first read). Detect via `git log --author="<user-email>"` against the anchor repo, or just ask.
- **Extend mode**: chapter 01 is "running the existing project successfully" — confirm the baseline before adding to it.

The first chapter is what the learner reads to decide whether the book is for them. It has to land.

### 6e. All other chapters

Stubs only: frontmatter, outline, see-also, and `status: stub`. Use the mode-specific templates in this skill.

## Step 7 — Companion artifacts

### 7a. `AGENTS.md`

Use `references/templates/reproduce/agents-md.md` as the starting point. Declare teaching mode, point at the vendored teaching skill, and describe the learner profile.

### 7b. `docs/teaching/<lang>-anchor-table.md`

Pull the starter table from `references/anchor-tables/<lang>.md`. Add rows for the learner's specific prior-language pains from step 1c.

### 7c. `docs/teaching/source-map.md`

Write or copy the source map from step 2.5. Link it from `sessions.md` and from any chapter frontmatter whose evidence depends on it. Include the curriculum tree, probe bank, kept sources, and dropped sources.

### 7d. `docs/teaching/build-philosophy.md`

Copy the mode-specific build-philosophy template from this skill and adapt its project-specific lines.

### 7e. Repository handoff

Initialize Git for a new output repository. Commit the generated files only when the user or repository policy authorizes it. Pushing and publishing are separate decisions.

## After step 7

The book is ready. The learner can either:

- Read solo from `docs/book/00-introduction.md` onward
- Open the repo in a coding agent and run live teaching sessions per the vendored `teaching` skill

The next time they want to teach a chapter live, they invoke the `teaching` skill (or it auto-loads via the project's `AGENTS.md`).

## Common pitfalls

1. **Skipping step 1d (motivation).** Without the learner's actual why, the `00c-why-i-built-this.md` chapter reads as filler. Either capture it or omit the chapter entirely; don't fake it.

2. **Generating all chapter content up front.** Don't. The pedagogy assumes one-concept-per-session, captured during the live session. Stubs are the right call.

3. **Forgetting to vendor the skills.** A learn-by-LLM book that requires the learner to have the original author's dotfiles isn't shareable. Vendor.

4. **Picking a repo the learner has no real interest in.** If the project doesn't compel them, no pedagogy will sustain a 6-month arc. Push back if the picked repo feels arbitrary.

5. **Making chapter 01 too dense.** First-chapter density determines whether the learner continues. Reproduce-mode chapter 01 should be light setup; tour-mode chapter 01 should be a clean entry into the highest-level abstraction. Resist the urge to teach two concepts on day one.

6. **Treating branches as tensions.** "React vs Vue" is often a branch. "Framework magic vs local reasoning" is a tension. If you can't name the deeper trade-off or active disagreement, don't label it as a tension.

7. **Dropping source rejections.** If you rejected an outdated blog post or shallow explainer, record that in the source map. Future agents will otherwise rediscover it and may trust it.

8. **Listing misunderstandings without probes.** A misunderstanding note is only half useful. Turn it into a diagnostic question the chapter can ask before explaining.

9. **Skipping fuzzy-term planning.** If the source map contains overloaded terms, list them. Future teachers need to know when to pause and stabilise vocabulary.

10. **Formulaic prose in seed chapters.** Write plainly in the learner's voice and remove filler. Use an installed `humanizer` skill when available; the book must work without it.
