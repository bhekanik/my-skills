# Teaching notes template

Each book chapter has a companion **teaching-notes file** at `docs/teaching/notes/<NN>-<title>.md`. This is the *teacher's* working file, not the chapter itself. It may live in a shared repository, so keep it free of learner identity and private session details. It accumulates reusable refinements over multiple live sessions.

## Frontmatter

```yaml
---
chapter: 4
session_id: M0-1
title: Hello, adapter
sessions_run: 0           # aggregate count; no learner identity or private answers
---
```

## Body structure

```markdown
# Teaching notes — Chapter NN: <Title>

## Concept anchor

(One paragraph: the **one** new concept this chapter teaches. State it precisely. Everything else in the chapter is in service of this. If a session expanded the scope past one concept, that's a flag — refactor the chapter and update the session plan.)

## Common wrong predictions

For each predict-pause in the chapter, what real learners answer wrong, why they go there, and how the chapter calibrates.

| Predict question | Common wrong answer | Why learners go there | How the chapter currently calibrates |
|---|---|---|---|
| `<question>` | `<answer>` | `<root cause — usually a JS/TS/Python prior model>` | `<the discussion in the <details> block>` |

## Common misunderstandings

Common false models that may or may not have appeared in one learner's prediction. Capture the reusable pattern, why it is tempting, and how the chapter should correct it.

| Misunderstanding | Why it is tempting | Corrected model | Chapter location |
|---|---|---|---|
| `<false model>` | `<prior language / slogan / docs ambiguity>` | `<better model>` | `<section or TODO>` |

## Probe bank

Every important misunderstanding or pitfall should have a diagnostic question. Do not merely warn future learners; give the next teacher a way to test whether the false model is present.

| Misunderstanding / pitfall | Diagnostic probe | Expected wrong answer | Calibration if wrong | Mastery signal |
|---|---|---|---|---|
| `<false model>` | `<question or predict prompt>` | `<likely answer>` | `<follow-up explanation or experiment>` | `<what Aware/Confident sounds like>` |

## Expectations and graduated hints

For each predict-pause or exercise, hold the *expectations* (what a correct answer must contain) and a *hint ladder* (escalate specificity only after a real attempt fails — rule 21). The next teacher diagnoses "which expectation is missing / which misconception is active," then gives the smallest hint that closes the gap.

| Concept / task | Expectations (must contain) | L1 — nudge | L2 — structure | L3 — near-spoiler |
|---|---|---|---|---|
| `<concept or exercise>` | `<the points a correct answer needs>` | `<point at the area, sharper question>` | `<name the shape / relevant rule, no code>` | `<the missing piece, then learner restates why>` |

Start at L1 every time. Record which level learners actually needed — if most reach the answer from L1, the predict-pause is well-calibrated; if most need L3, the prior explanation is too thin.

## Fuzzy terms to sharpen

Terms that commonly get overloaded or used inconsistently. Pause on these live; vocabulary instability is often the model gap.

| Term | Common collapse | Canonical distinction | When to interrupt |
|---|---|---|---|
| `<term>` | `<what learners merge>` | `<precise distinction>` | `<signal in learner wording>` |

## Signals to check mastery

Use rule 21's rubric to prepare probes for the next teacher. Record general signals, not an individual learner's level.

| Topic / branch | Confused signal | Aware signal | Confident signal | Probe |
|---|---|---|---|---|
| `<topic>` | `<common wrong model>` | `<partial explanation>` | `<unaided transfer>` | `<prediction or edge case>` |

## Learner state stays private

Keep an individual learner's mastered concepts, shaky concepts, exact wrong predictions, and prior models in their private session note. The companion file records only reusable, anonymized patterns. This matters when the book repository is shared or public.

## Evidence posture

Record how confident the chapter should be about its claims. Use rule 20's vocabulary: consensus, tension, pitfall, misunderstanding, gap.

### Consensus

- <Stable claims grounded in code, primary docs, specs, or verified behaviour>

### Real tensions

- <Trade-offs or active disagreements. If a supposed tension dissolved under scrutiny, say that too.>

### Pitfalls

- <Operational behaviours that surprise learners in practice>

### Gaps and deferred questions

- <Weakly supported areas, version-specific caveats, or concepts deferred by the one-concept cap>

### Sources considered

**Kept**

- <Source title> (<url>) — <why it matters>

**Dropped**

- <Source title> — <why it was not used: outdated, shallow, contradicted primary docs, wrong scope, etc.>

## What surprised the learner

(Things the learner found unexpected that the chapter could pre-empt. If 3+ learners are surprised by the same thing, lift it from "surprise" to "explicit explanation" in the chapter.)

## Sticky points (concepts that needed a second pass)

(Sections of the chapter where the learner asked clarifying questions, paused longer than expected, or where the teach-back was rough. These are candidates for chapter revision.)

## Refinement ideas

- [ ] (idea) — (rationale) — (when to apply: next session / next refresh / wait for N more data points)

## Notes for future sessions on this chapter

(Things to do *differently* next time you teach this. Examples: "open with a specific anchor"; "skip section X if the learner already nailed it elsewhere"; "spend extra time on Y because two learners in a row stalled there".)

## Pressure-mode notes

(How to adapt Socratic pressure next time.)

- **Default mode:** Socratic | Curious Guide | Devil's Advocate — <why>
- **When to soften:** <signals the learner is lost; one reframe to try>
- **When to challenge:** <signals of overconfidence; edge case or counterargument to use>
- **Learner priors / biases to remember:** <opinionated prior models that help or mislead>

## Did the artifact land?

(Per session: did the learner end the session with the runnable artifact working? If no, what blocked? Rule 13 violation, or environment issue, or genuine learning gap?)

## Exercises authoring notes

(Per rule 19. Notes for the *teacher* about the chapter's exercise set — what each exercise targets, how learners interact with them, which prove high-yield over time.)

| Exercise | Grade | Sticky-point targeted | Yield observed |
|---|---|---|---|
| 1 | wield | <which sticky-point from above> | <high / medium / low / not-yet-data> + brief note |
| 2 | stretch | <which sticky-point> | <yield observation> |
| ... | ... | ... | ... |

**Authoring decisions:**
- Why these exercises were chosen (vs others considered)
- Any contract / test trade-offs made (e.g., "exercise 2 tests implementation directly because the implementation IS the lesson")
- Cross-language exercises: setup notes that aren't obvious from the exercise file

**Learner-data feedback to the chapter:**
- Patterns multiple learners hit when failing an exercise (lift to the answer key's "common wrong attempts" once 2+ data points)
- Exercises that turn out to be too easy / too hard — refinement candidates
- Exercises that turn out to drill the *wrong* sticky-point — refactor or replace

## Reuse log

(When this chapter has been used to teach this concept *outside* the project's main session sequence — e.g., a refresher for a returning learner — note it. Helps spot when the chapter has earned promotion to a "stable" status vs needing more refinement.)
```

## When to update

- **After every live session** that uses the chapter — even if no new wrong predictions came up, log it under "sessions run" and "did the artifact land".
- **Before re-teaching the chapter** — read the existing notes; pre-empt past sticky points.
- **When a refinement idea has 3+ data points** — lift it from "ideas" into a chapter revision.

## What NOT to put here

- The learner's *full* predictions verbatim — anonymise to the *pattern*, not the specific person. The chapter readership over time will grow; protect privacy.
- Anything that should be in the chapter itself — if a clarification helps the public reader, edit the chapter. The teaching notes are for *teacher-only* meta.
- Critique of the learner — write for the *next teacher*, not as a personal assessment. The frame is always "what could the chapter do better."
