# Template: 00b-what-is-{{PROJECT}}.md

Use this as the seed for `<output-repo>/docs/book/00b-what-is-{{PROJECT}}.md`. The required-reading chapter that gives the technical context everyone needs.

Explain the domain, the architecture below the project, where the project sits, and the central question a newcomer needs answered.

---

```markdown
---
chapter: "0b"
title: What is {{PROJECT}}
status: complete
estimated_time_minutes: 8
---

# Chapter 00b — What is {{PROJECT}}

> Required reading. ~8 minutes. The technical context everyone needs before chapter 01.

## What you'll know by the end

- What {{DOMAIN_PROTOCOL_OR_CORE_CONCEPT}} is, and what it isn't
- {{IF_LAYER_CAKE_APPLIES: The architecture cake — the layers between you typing "{{ACTION}}" and {{KERNEL_OR_HARDWARE_OR_LOWEST}} actually doing the work}}
- Where {{PROJECT}} sits in that stack, and {{IF_WRAPPER_FRAMING_APPLIES: how the "wrapper" framing applies to it}}

## What is {{DOMAIN_PROTOCOL_OR_CORE_CONCEPT}}?

{{REPLACE: ~150 words. What is the protocol/concept the project depends on? Who created it, why, and who uses it now? Crucially: what is it NOT? (e.g., "DAP is communication, not debugging.") The framing here matters: distinguish the layer the project lives in from the layer below where the actual work happens.}}

## The {{DOMAIN}} {{architecture / layer cake / stack}}

{{IF_LAYER_CAKE_APPLIES: This is the sketch you'll come back to throughout the book.

```
{{REPLACE: ASCII layer diagram showing 4–6 stacked boxes. Top is the user/agent. Below is the project being built (with annotation: "← what we're building"). Below that is the layer the project talks to. Below that is the deeper machinery. Bottom is the foundational primitive (kernel / hardware / I/O / OS).}}
```

Layer by layer, briefly:

{{REPLACE: 4–6 bullet points, one per layer in the diagram. Each bullet: one sentence on what the layer does, one sentence on what it does NOT do, one sentence on which existing tool/protocol/library lives there.}}

For the long version with each layer explained and a worked example of "what happens when {{CANONICAL_OPERATION}}", read [`docs/reference/{{DEEP_DIVE_REF}}.md`]({{PATH}}). It's the most important reference doc in this project.

The short version, in one sentence: **{{PROJECT}} is the {{LAYER_NAME}} layer. Everything below it already exists and we're not rewriting it.**}}

## Where {{PROJECT}} sits

So {{PROJECT}} is a {{LAYER_NAME}}. It:

- {{REPLACE: bullet list of what the project DOES at its layer (3–5 bullets)}}

It does **not**:

- {{REPLACE: bullet list of what the project does NOT do (3–5 bullets, often the layers below the project)}}

This is the right slice to work at. The {{stack/layer cake}} below us is mature. {{IF_APPLICABLE: Anyone trying to write a {{X}} from scratch in {{YEAR}} is doing it for academic reasons, not practical ones.}}

## "But isn't {{PROJECT}} just a wrapper?"

{{IF_WRAPPER_FRAMING_APPLIES:

Yes. Every usable {{DOMAIN}} surface is a wrapper.

{{REPLACE: 4–5 bullet examples of well-known wrappers in the same domain — e.g., for debuggers: "VS Code wraps DAP. CLion wraps DAP. Xcode wraps LLDB. nvim-dap wraps DAP."}}

The question isn't whether {{PROJECT}} is a wrapper. **The question is what the wrapper is for.** {{PROJECT}}'s design constraints ({{LIST_3_KEY_DESIGN_CONSTRAINTS}}) exist because the wrapper has a specific job: {{ONE_LINE_PROJECT_THESIS}}. Not "expose {{LOWER_LAYER}}," but "expose {{HIGHER_LEVEL_VALUE}}."

If you want the long-form version of this argument with concrete comparisons (lazygit on git, kubectl on the K8s API, httpie on curl), {{LINK_TO_WRAPPER_ARTICLE_IF_EXISTS}} is a good read.}}

## What to take from this chapter

The required thing is the **{{KEY_MENTAL_MODEL}}**. Keep it in your head. {{IF_APPLICABLE: When chapter {{N}} has you {{DOING_X}}, you'll think: "right, {{PROJECT}} ({{LAYER}}) is talking to {{LOWER_LAYER}}, which will eventually talk to {{DEEPER_LAYER}}." That mental picture is what makes the design choices comprehensible.}}

{{IF_WRAPPER_FRAMING_APPLIES: Optional but useful: the wrapper framing. When someone asks "isn't this just a wrapper on {{PROTOCOL}}?" — yes, and here's why the question misses the point.}}

If you'd like the personal backstory behind the project (why I built this, what was the {{TANGENT_LANGUAGE_OR_PROBLEM}} journey doing, why {{TARGET_LANGUAGE}} specifically), [Chapter 00c](00c-why-i-built-this.md) has it. If you don't care, skip straight to [Chapter 01]({{PATH_TO_01}}). The book works either way.

## See also

{{REPLACE: 3–5 cross-references — internal docs, articles, external specs that go deeper on this chapter's topics.}}

Next up: [Chapter 00c — Why I built this](00c-why-i-built-this.md) (optional backstory) or [Chapter 01 — {{FIRST_CHAPTER_TITLE}}]({{PATH_TO_01}}) (where the book starts building).
```

## Notes for the bookgen agent

- The "what is X / where it sits / wrapper question" structure is the pattern. Even if the project isn't a *protocol wrapper* specifically, the structure usually applies — there's *some* domain context that needs explaining before the project's design choices make sense.
- The layer-cake diagram is high-value content. Adapt to the project's actual architecture; don't force a debugger-shaped stack onto an HTTP framework.
- If the project has an existing `docs/reference/<deep-dive>.md`, link to it as the long version and summarise its key points here.
- Edit for clear, human prose. Use an installed `humanizer` skill when available.
