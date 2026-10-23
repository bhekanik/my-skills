# Build philosophy for reproduce-mode chapters

This book runs in **reproduce mode**: each chapter rebuilds one slice of the anchor codebase from zero. Each chapter ends with **a runnable artifact** — a thing the learner can show. Skateboard → scooter → bike → motorbike → car (Henrik Kniberg's MVP framing).

The anchor repo is reference, not gospel. Where the original made a choice the chapter doesn't agree with, the chapter takes the better choice and explains why.

## What "artifact" means here

A *runnable thing* the learner can demonstrate at the end of every chapter:

- A CLI that prints something based on input.
- A test that passes.
- A function that returns the right value when called from a test or REPL.
- A binary that connects to an external thing and prints what it gets.
- A flag added to an existing CLI that changes behaviour visibly.

The bar is **demonstrable** + **incremental over the previous chapter**. Small is fine. Real is the requirement.

## The chapter-close ritual

**Open every chapter** by stating the artifact:
> "Today's concept is X. By the end of this chapter you'll have Y you can run."

**Close every chapter** by demonstrating the artifact:
> "Here's what you can do now that you couldn't an hour ago. Run it." [run it]

**Make the ladder visible** at chapter close:
> "Last chapter you had X. Now you have X + Y. Two chapters from now you'll have X + Y + Z."

Don't make the learner run the artifact themselves to feel motivated. That step is part of the chapter, not homework.

## The ceremony exception

Some chapters are unavoidable ceremony — workspace setup, license decisions, CI configuration. They produce no user-visible artifact. In these chapters:

- **Name the ceremony at chapter open**: "Today is workspace setup — there's nothing user-visible to show at the end. But here's what's now possible because of it..."
- **Close by stating what's now possible**, not what was demonstrated.
- **Pull a tiny artifact forward where possible**: even ceremony chapters can usually include "run `cargo fmt --check` and watch it pass" as a minimal demo.

## Reconciliation with rule #12 (slowness)

The teaching skill's rule #12 says slowness is the goal — resist racing. Rule #13 says every chapter ships an artifact. They're not in conflict:

- **Rule #12 governs pace within a chapter** — don't race through concepts.
- **Rule #13 governs deliverables across chapters** — don't pile concepts without artifacts.

A slow chapter can ship a small artifact. A 90-minute chapter might produce a 5-line CLI command. That's correct.

## Failure mode to watch for

When you finish three chapters in a row without an explicit demonstration at chapter close, the rule was violated. Pull the artifact forward in the next chapter — even a one-line behavior change is enough. Visibility matters more than size.

If the learner asks "where is this going?" — that's the signal that the cumulative narrative has gone fuzzy. Re-anchor by demonstrating what they can run today vs. last chapter.

## See also

- `~/.skills/teaching/SKILL.md` — rule 13 (artifact per chapter) and rule 15 (chapter-as-curriculum)
- `~/.skills/teaching/references/operating-rules.md` — the long-form rules
