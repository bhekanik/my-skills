# Architecture & interface review

Interrogate the structure the change produced. Two layers: module architecture
and function interfaces. Report concrete, rankable findings.

## Module architecture

Use the Modules view + the model's `moduleEdges`, `cycles`, and each file's
`importsTo` / `importedBy`.

Check for:

- **Import cycles** — listed in `cycles` and clickable in the left rail. Cycles
  couple modules and block clean reasoning/testing. Flag every cycle touching a
  changed file.
- **Layering violations** — data/domain modules importing UI/HTTP/framework
  code; utilities importing services; low-level modules depending on high-level
  ones. Dependencies should point inward/downward, not up.
- **New coupling** — did the change add an import edge that connects two areas
  that were previously independent? Ask whether that coupling is warranted.
- **Fan-in / fan-out** — a changed module imported by many others (high fan-in)
  is high-risk: verify its interface stayed stable. A module importing many
  others (high fan-out) may be doing too much.
- **Misplaced modules** — a file whose dependencies suggest it belongs in a
  different layer or package.

## Function interfaces (rapid spot-check)

Scroll the call graph and the `flags` list. Do NOT read bodies line-by-line —
check the *shape*. The model pre-computes metrics; thresholds:

| Metric | Threshold | Smell |
|---|---|---|
| arguments | > 4 | too many params — likely missing an object/param type or doing too much |
| lines | > 60 | long function — probably >1 responsibility |
| cyclomatic complexity | > 10 | too many branches — hard to test, likely needs splitting |
| cognitive complexity | > 15 | deeply nested flow, hard to read; the headline signal in `analyze.mjs` |

Also judge by eye (no threshold):

- **Names** — does the function name state what it does? Vague names
  (`process`, `handle`, `doStuff`, `manager`) or names that lie about behavior.
- **Cohesion** — do a class's methods belong together, or is it a grab-bag?
- **Anything outlandish** — a 300-line function, a function with 9 booleans, a
  "God" class with 40 methods, duplicated logic across new functions.

## How to present findings

Rank by impact. For each finding give: the module/function (with `file:line`),
what's wrong in one line, and the fix direction. Example:

```
1. Import cycle: pricing.ts ⇄ checkout.ts — extract shared Order type into a
   types module to break it.
2. handleCheckout (checkout.ts:4) — 5 args, complexity 9. Pass an Order object;
   move branch logic into PricingService.
3. New coupling: utils/format.ts now imported by 6 modules — fine, but keep it
   dependency-free (it currently imports nothing — good).
```

Keep it actionable so the reviewer can point at a flaw and tell the agent to
fix it. Don't comment on formatting, comment wording, or import ordering.
