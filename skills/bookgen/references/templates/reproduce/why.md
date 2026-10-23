# Template: 00c-why-i-built-this.md

Use this as the seed for `<output-repo>/docs/book/00c-why-i-built-this.md`. The optional personal-backstory chapter.

Use this template to write from the current learner's own reasons; do not copy a prior learner's backstory.

Possible motivations include learning slowly, building something useful, or understanding code the learner already uses. Use the learner's actual answers rather than supplying a stock story.

---

```markdown
---
chapter: "0c"
title: Why I built this
status: complete
estimated_time_minutes: 8
---

# Chapter 00c — Why I built this

> Optional. ~8 minutes. Skip to [Chapter 01]({{PATH_TO_01}}) if you just want to learn {{LANGUAGE}} by building a thing. The technical context you need is in [Chapter 00b](00b-what-is-{{PROJECT}}.md).

This is a longer answer than most book introductions need. If you read it, the design choices in {{PROJECT}} and the way this book teaches will make a different kind of sense. If you skip it, you'll still learn {{LANGUAGE}} just fine.

## The gym for the brain

{{IF_LEARNER_AGREES_WITH_FRAME: I have a theory that everyone needs a hobby that is *deliberately difficult*. Not a trade, not something you'll be paid for, not something with a deadline. Something that pushes your brain past what it can comfortably do, the way the gym pushes your body past what it can comfortably lift. Reading classical literature. Learning math. Learning a low-level programming language. Speaking a new natural language. Chess against humans. The category is wide.

Most of us want to *have done* the difficult thing. We just don't want to pay the tax. Modern life makes the avoidance easy. The principle: most people overestimate what they can achieve in a year and underestimate what they can achieve in ten. The only way to get the ten-year compound is to put in the daily reach when there's no deadline forcing you to.}}

{{REPLACE: 1–2 paragraphs of the learner's specific framing. If they don't connect to the gym-for-the-brain analogy, use whatever motivates them. Capture their actual words from step 1d as faithfully as possible.}}

## What AI {{did to that practice / fits into the practice}}

{{IF_LEARNER_HAS_AI_PLATEAU_FRAMING: There are two ways to use AI when you're learning.

The first is AI as a *solution provider*. Fast, productive, you produce more output, you understand less of it.

The second is AI as a *thinking companion*. You bring a half-formed thought; the AI plays it back and stress-tests it; you push back; you both refine; you walk away with a better thought *that you actually had*. The AI didn't give you the answer; it pulled it out of you. This is closer to a Socratic dialogue than to a Q&A. It's slower than the first mode, by a lot. But what you keep is yours.

This book is built around the second mode. The predict-before-run prompts, the surface-your-model prompts, the let-the-compiler-be-the-teacher discipline — those aren't pedagogy decoration. They're the operational difference between "the agent gives you {{LANGUAGE}}" and "you understand {{LANGUAGE}}, with the agent's help."}}

{{REPLACE: 1–2 paragraphs of the learner's specific take on AI in their learning.}}

## Why {{TARGET_LANGUAGE}}, why {{ANCHOR_REPO}}, why this project

{{REPLACE: 2–4 paragraphs from the learner's step-1 answers. Cover: why this language specifically (often: because it solves problems felt in another language). Why this project (often: because the existing tools didn't fit the learner's workflow). Why now (often: because the learner is rebuilding a learning practice).}}

## Why "build it instead of fixing/forking the existing thing"

{{IF_APPLICABLE: I asked myself this. {{ALTERNATIVE_NAMED}} would have been more practical.

Honest answer: I'm building this primarily as a learning project. {{ALT}} teaches me {{ALT_LANG_OR_THING}}. Building {{PROJECT}} from scratch teaches me {{TARGET_LANGUAGE}} and {{LIST_3_OTHER_THINGS_ENCOUNTERED}}. Every concept in modern {{TARGET_LANGUAGE}} shows up in this project somewhere.}}

{{REPLACE: learner's specific answer if relevant. If they didn't have an existing alternative they could have forked, omit this section entirely.}}

## Why {{TARGET_LANGUAGE}} specifically (closing the loop)

{{IF_LEARNER_HAS_PRIOR_PAIN_LANGUAGE: Because the {{PRIOR_PAIN_LANGUAGE}} journey was the setup. I was building up live experience of:

{{REPLACE: 4–6 specific pain examples the learner felt in their prior language(s).}}

…and so on. {{TARGET_LANGUAGE}} solves *most* of those at compile time / runtime / by design. {{LIST_2_3_KEY_FEATURE_TO_PAIN_MAPPINGS}}. The list goes on, and you'll meet each one in the book as it shows up in {{PROJECT}}'s code.

So when the chapters point at a {{TARGET_LANGUAGE}} feature and say "this exists because of *this specific pain in {{PRIOR_PAIN_LANGUAGE}}*," that's not pedagogy framing. It's literally the path I was walking when I decided to write {{PROJECT}}. The pain anchor is real.}}

## What you should take from this chapter

{{REPLACE: 1–3 short takeaways, optional, each one paragraph max. Use the learner's own words and priorities.}}

That's why this book exists, and why it teaches the way it does.

Next up: [Chapter 01 — {{FIRST_CHAPTER_TITLE}}]({{PATH_TO_01}}). The book's setup is done; we start building.
```

## Notes for the bookgen agent

- The bookgen agent should NOT fabricate the learner's motivation. If step 1d's answer is thin ("I just want to learn it"), keep this chapter short rather than padding with universal philosophy. The chapter is optional; thin is better than fake.
- The "do one difficult thing daily" / "AI as thinking companion" frame is universal-ish but not for everyone. If the learner's motivation is more pragmatic ("I need {{LANGUAGE}} for my job"), drop the philosophy framing entirely and just write a tight 2-paragraph "what brought me here" section.
- Keep the *voice* first-person throughout. This is the only chapter in the book that's first-person; all the others use second-person ("you'll write", "you'll see").
- Edit for the learner's own voice. Use an installed `humanizer` skill when available.
