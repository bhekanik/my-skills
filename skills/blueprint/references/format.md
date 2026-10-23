# Blueprint format

Use this as a starting format, then follow the target repository's conventions. Keep the decision history and enough detail for an agent that has not seen the planning conversation.

## File set and conventions

```
AGENTS.md                      repo root; new repos only
docs/blueprint/
  README.md                    index, summary, rules for coding agents
  KICKOFF.md                   paste-in prompt for the first build session
  00-overview.md
  01-architecture.md
  02-data-model.md
  03-design-concept.md         what it is, how it should feel, and the visual and interaction language (any app a person uses)
  04-… NN-…                    one domain doc per hard subsystem
  NN-reuse-map.md              only when the app borrows from the project owner's repos
  NN-roadmap.md
  NN-decision-log.md
  NN-open-questions.md
docs/research/<topic>.md       facts and prior-art reviews the decisions cite
docs/issues/README.md          only when the repository tracks issues in Markdown
```

- **Numbering.** Two digits, in reading order, kebab-case names. The tail is always reuse map, roadmap, decision log, open questions, in that order.
- **The design concept comes before the domain documents** because every user-facing domain document is written in its terms. Skip it only for an app no person looks at or touches (a library, a daemon with no CLI), and say so in the README.
- **Domain documents.** Name them after the subsystem, not after a generic category: `03-graph-provider`, `05-custom-features`, `06-natural-language`, `03-voice-agent`, `05-memory`, `06-post-call-pipeline`. The CLI and TUI each get their own document. Add `privacy-safety-compliance`, `cost-model` and `observability-and-evals` when the app holds other people's data, pays per use, or calls a model.
- **Titles.** `# NN: Title` (`# 11: Decision log`). There is no frontmatter and no status line in a first blueprint.
- **Cross-links.** Link documents by number, `[05](05-custom-features.md)`, with anchors where useful. Cite decisions inline by ID, as in `(D-014)`. Every document points back to the decisions it rests on.
- **Voice.** First person plural for the planning session ("we first proposed…"). Name the project owner in the third person ("the project owner's own app registration"). Prescriptive and calm: "must", "never", "If X, the app is broken". Nearly every rule carries its reason.
- **Dates.** Absolute and inline only: "as reviewed on 2026-09-24", "S5 result (2026-09-24)".

## README.md

```markdown
# <app>: technical blueprint

> <One sentence: what it is, its surfaces, and the core mechanism.>

The whole project was planned in one session on <date>, before any code existed. It is meant to be built by a coding agent that never saw that session, so this blueprint has to carry everything: what we're building, how, what we decided against, and why.

## Reading order

| # | Document | What it covers |
|---|---|---|
| 00 | [Overview](00-overview.md) | … |
| … |
| — | [Kickoff](KICKOFF.md) | The prompt to give the coding agent for the first build session |

Research behind these decisions:

- [../research/<topic>.md](../research/<topic>.md): <what it establishes>.

## Summary

- **Stack:** …
- **Runtime:** … (D-0NN)
- <5–10 bullets, each citing its decision IDs. Include what was dropped.>

## Rules for coding agents

1. **<The canonical-surface rule>.** …
2. **Run the spikes first.** …
3. **Update the decision log.** If you change a decision, add an entry to [NN-decision-log.md](NN-decision-log.md) with the reason. Don't silently change the design.
```

## KICKOFF.md

```markdown
# Kickoff prompt for the first build session

Paste this to the coding agent on the build machine, after `git clone <url>`:

---

You're building <app>, <one-line description>. It was fully planned in an earlier session you didn't see. Everything from that session is in this repo.

1. Read `AGENTS.md`, then `docs/blueprint/README.md` and every document it lists, in order. Then read `docs/research/`. Read `NN-decision-log.md` before proposing any change of direction; most alternatives were already considered and rejected there.
2. Clone <reuse repos> into `/tmp/<app>-refs/`. For each path in `NN-reuse-map.md`, check whether it changed since the SHA listed.
3. Phase 0: <the project owner's account actions: ask which are done; don't create accounts, keys or billing yourself>. Run the spikes that F1 and rung 1 depend on (<IDs>) and record them in `docs/research/spikes/` and `NN-open-questions.md`.
4. Before building any user-facing surface, read `03-design-concept.md` and make comps or a prototype of the rung's screens and key moments; show them to the project owner when the concept is new or a screen is central. Build to the approved comps, and brief any worker with the concept and the comp, not only the behaviour.
5. Build foundation turn F1, then climb `NN-roadmap.md` one rung at a time. A rung ends only when its completion check is observed on <the installed binary / the deployed system> and its demo has been run. Follow the repository's commit conventions.

Ask me about the product questions in `NN-open-questions.md` when they come up. Don't guess.

---
```

## AGENTS.md (repo root, new repos)

Use these headings: `# <app>: project context for AI agents`, a one-line pitch blockquote, then `## Status` ("**There's no code yet.** This repo holds a complete blueprint written in the planning session on <date>."), `## Start here` (blueprint README, decision log before any change of direction, research, KICKOFF), `## Rules` and `## Stack`.

The Rules section always includes:

- The blueprint is the spec, and the decision log is its history.
- Run the spikes before building on what they test.
- The canonical-surface rule, verified by driving the real binary or system.
- Reuse before rewriting, pointing to the reuse map.
- Follow the repository's issue-tracking convention.
- Commits follow the repository's conventions.

## 00-overview

1. `## What <app> is`. Its surfaces as bullets, and what stays the system of record.
2. `## Who it's for`. Name the first user explicitly, then any other audience.
3. The core loop, numbered, when the app has one (a product's daily loop).
4. `## What it should feel like`. Two or three sentences in plain words: the feeling the person should have using it, using the project owner's own words when available. The full concept is in the design-concept document; this is its summary.
5. `## Principles`. Five to ten numbered items, each a bold claim followed by its reason: "**Deterministic before clever.** Natural-language parsing is rule-based and testable. An LLM can be added later behind the same interface."
6. `## Scope`. What v1 covers, concretely: entities, operations, platforms.
7. A gap table when the app sits on someone else's platform: `| Feature | In the API? | <app>'s approach | Doc |`.
8. `## Non-goals`. Bullets, each with its decision ID or reason. Mark deferred items as "deferred, not rejected".
9. `## Glossary`, a `| Term | Meaning |` table, when the domain coins words.

## 01-architecture

- A box-drawing ASCII diagram of processes, clients, stores and external services.
- "Why <the key shape>" as a numbered list of the reasons and the alternatives rejected (D-IDs).
- What each process owns, its lifecycle, and the client/server split.
- A module, crate or package table (`| Crate | Job |`) with dependency rules, and the test that enforces them.
- Transport and protocol: the exact codec, message envelope and forward-compatibility rules.
- File and config paths.

## 02-data-model

- Conventions first: ID types, timestamp format, naming ("Instants are epoch milliseconds; names end in `At`").
- The actual schema, either as pseudo-DDL in a code block (`tasks(local_id PK, graph_id UNIQUE NULL, …)`), or as a `| Table | Fields | Indexes | Written by |` table, or as real type definitions. Use names that every other document reuses exactly.
- Indexes, idempotency keys, deletion and retention, and tenant isolation if there are multiple users.

## Design concept

The design concept decides what the product is to the person using it and how it should feel, before anyone specifies a screen. A spec that lists only behaviour can produce a correct but busy and lifeless interface. Write this document to give builders a coherent visual and interaction direction.

Sections, in order:

1. `## What this is to the person`. The role the product plays in their day, why they reach for it, and what they care about. Name the objects involved and what makes them special to the person.
2. `## The concept`. A short name and one paragraph: the metaphor, material, mood and light, and why it fits this product rather than any product (for example, an object in focus while secondary controls recede).
3. `## How the whole fits together`. The product as one thing, not a set of screens. Without this, each part gets designed alone and the whole feels assembled:
   - **The mental model.** The few nouns the person thinks in (the objects, actions and states the person actually names) and how they relate. Every surface uses these words and no others.
   - **The map.** Where things live and how you move between them: what is always present, what opens on top, what replaces what, and how you get back. Draw it.
   - **The journeys, end to end.** The three to five things the person comes to do, walked across every part they touch: a request through its review, application and visible result. Say what carries over at each hand-off (the selected key, the context, the undo) and where it must not break.
   - **Shared patterns.** One way to pick a thing, one way to confirm, one way to undo, one way to show "this changed", one place errors appear. A new feature reuses them; it doesn't invent its own.
   - **Across surfaces.** How the web app, the CLI, the agent and any device feedback stay consistent: the same names, the same states, the same sentences, so moving between them feels like one product.
   - **The system's own state.** What the person always knows without asking (what's saved, what's on the device, what's in progress), and where that lives.
4. `## Principles`. Five to eight, each a claim with its reason. They decide trade-offs later: "The hero is the board; every other element must earn its place", "Calm by default, detail on demand", "One click, one job".
5. `## Key moments`. A table: moment (first open, the core action, success, failure, waiting, empty), what the person should feel, and the interaction that makes it land (for example, a clear confirmation when a change takes effect). These are the things nobody asks for and a design team adds.
6. `## Visual language`. Type (families, a real size scale, weights), colour (neutral base, accents and what each means, light and dark both first-class), materials and depth (shadows, surfaces), iconography, density. Give tokens.
7. `## Motion`. What moves, why, durations and easing, and the reduced-motion version. Motion explains change; it never decorates.
8. `## Hierarchy and restraint`. What is primary, secondary and hidden until asked, on each main screen. List what is deliberately left off and why. "Busy" comes from giving every element equal weight; this section prevents it.
9. `## Taste references`. The products the project owner admires for this app and what specifically makes each good (not their feature lists), and what we take and what we don't.
10. `## Screens`. For each main screen: an ASCII or HTML mockup, and a paragraph on intent (what the eye lands on first, what it should feel like). Behaviour lives in the domain documents; this says how it should be experienced.
11. `## The design gate`. How a rung proves it looks and feels right: comps or a prototype approved before the UI is built; screenshots in every theme and width read against the concept; a design review against this document (not only "readable and not broken"); the key moments checked by using them; and the main journeys walked end to end across every part they touch, so a new piece is judged by how it fits the whole, not alone.

Where the project owner didn't state the concept, the blueprint proposes one and files "Q: blueprint assumes concept X". Prefer one strong concept to a hedged average of several.

For a CLI or TUI the same applies in its medium: the concept, the moments (a command's first output, progress, an error), the visual language (colour use, density, symbols) and the restraint.

## Domain documents

Each one specifies its subsystem to the level a builder needs:

- the exact API calls, limits and error handling
- algorithms and state machines
- edge cases and what happens on failure

A domain document that describes a user-facing surface says how it should feel and look in the concept's terms, beside what it does: what the eye lands on first, what recedes, and the micro-interactions of its key moments. A list of fields and buttons is not a design.

For a CLI document: a command tree in a code block, global flags, the output contract (`table|json|jsonl|ids`), an exit-code table, and the agent skill it ships. For a TUI document: ASCII screen mockups, keybinding blocks, and a latency budget ("under 16 ms per keypress"). Anything unverified points to its spike.

## Reuse map

```markdown
# NN: Reuse map

Policy: **"Do not rewrite architecture that <repo> already solved."** Copy first, adapt, and keep a `// Adapted from <repo> <path> @ <sha>` comment at the top of each copied file. Extract shared code only when three projects need it.

Source commits, as reviewed on <date>:

- <repo>: `<owner>/<repo>` @ `<full sha>`

Before copying, `git fetch` and diff these paths against these SHAs.

| <app> piece | Copy from | Size | Adapt |
|---|---|---|---|
| … | <repo> `<path>` (`<symbol>`, around :<line>) | <N> lines | … |

## References outside the source repositories (read them, don't copy)
## Not reused
```

## Roadmap

The roadmap is a ladder of usable releases, not a list of components. The ladder makes each release useful on its own.

`## Build philosophy` comes first:

- Skateboard → scooter → bicycle → motorbike → car.
- Each rung is a working, released product that lets its intended user do something new from start to finish, sized to one working session.
- Every rung ships through the real release channel.
- At most two new unknowns per rung. A rung that needs a third is split.
- Ceremony (CI, packaging, scaffolding) is named and pulled into the nearest useful turn. Only one foundation turn, F1, may be unusable on its own.
- Stop after any rung and there's a working product.
- A rung added later gets a letter (3b) so cited numbers keep their meaning.
- "Tests pass" is required, but it never counts as done on its own.
- "It behaves as specified" isn't done either for anything a person sees. A user-facing rung is done when it also feels the way the design concept says.

`## Phase 0: accounts and spikes (before product code)` holds a `| # | Action | Needed by |` table of A-items that only the project owner can do (accounts, billing, keys, legal identity), plus the spike IDs that gate F1 and rung 1.

Each rung follows this template:

```markdown
## Rung 1: Skateboard: <what the project owner can now do, in their words>

**Previously:** … **Now:** …

**Promise:** "<first-person sentence in the project owner's voice>"

**Build:** <bullets linking the documents and decisions>

**Design:** <for a rung with a user-facing surface: the screens and key moments it touches, where it sits on the map and which journeys it joins or changes, the shared patterns it reuses, and the comp or prototype to approve before building>

**New unknowns:** <at most two>

**Demo:** <the exact journey>

**Done when:**

- <observable checks against the real binary or deployed system>
- <for a user-facing rung: the design gate in the design-concept document passes, judged against the concept, not only "it works and is readable">

**Left out:** <what this rung deliberately doesn't do>
```

The roadmap ends with "After the car (not planned yet)".

## Decision log

```markdown
# NN: Decision log

Every decision from the planning session on <date>, **including the options we rejected and the reversals**, so a later agent understands how the design got here and doesn't argue its way back into an option we already rejected. The project owner is the decision-maker. Entries marked "Owner" are their calls. Change a decision only by adding a new entry that replaces the old one.

## The arc, briefly

1. <How the conversation moved, in about 10 numbered steps, reversals included: "We proposed no daemon, then reversed that when Owner asked what it was optimising for.">

## Decisions

### D-001: <The decision as a sentence.> (Owner)
- **Options rejected:** (a) …; (b) …
- **Why:** …
- **Principle (Owner):** "<verbatim quote>"
```

- **IDs.** Three digits: `D-001`.
- **Attribution.** In parentheses after the heading: `(Owner)`, `(Owner proposed; agreed)`, `(Agent, delegated by owner)`, `(Taken from <repo>.)`, or `(Replaces an earlier "<x>" proposal.)`.
- **Bullet labels.** Use what the entry needs: `Options rejected` or `Option rejected`, `Why`, `Earlier proposal`, `Owner asked`, `Risk`, `Way back`, `Revisit only if`, `Principle (Owner)`.
- **Short entries.** Small decisions can be a heading alone, as in "### D-009: The CLI is the canonical surface. (Taken from the existing app.)"
- **The project owner's words.** Quote them verbatim from the transcript. Never paraphrase them into a quote.

## Open questions

```markdown
# NN: Open questions and spikes

## Spikes (phase 0; run against <real account / real API>)

For each, record the request, the response (with private data removed), the date and the conclusion, then update the blueprint document it affects.

| # | Question | Why it matters | Affects |
|---|---|---|---|
| S1 | … | … | [04](04-sync-cache.md) |

## Product questions for the project owner

| # | Question | Status |
|---|---|---|
| Q1 | … | Open; blueprint assumes <X> |
```

Add a `Blocks` column (F1, rung N) when spikes gate specific rungs. Results are added in place later, under headings such as `### S5 result (<date>)`.

## Extending an existing blueprint

The original text is never rewritten away:

- New capabilities get new numbered chapters after the last one, or a section in the domain document they belong to.
- Decision IDs continue from the log's last ID. A changed decision gets a new entry with a `Replaces D-0NN` bullet. The old entry gets a `Replaced by D-0NN` bullet, or its text is struck through with a pointer.
- Add a row to the README index for each new chapter, and add new spikes and questions to open questions.
- Rungs inserted into the roadmap take letters.
- A later chapter may open with `Status: proposal, <date>. Source baseline: origin/main at <sha>.`

## Feature-scale blueprint

For a feature inside an existing app:

- Write `README.md` plus `00-overview`, then documents on the standards and current code state the feature touches, the libraries, the data model, the surfaces and security, and end with `NN-decisions`.
- Use a scoped decision prefix such as `D-FEATURE-001` with `Decision:` and `Rationale:` fields.
- Ground "current state" in code read at a named SHA.
- State the scope boundary explicitly: "Do not expand this into '<everything X>' without a separate validated problem."
