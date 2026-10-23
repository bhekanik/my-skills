# Data-flow tracing

Goal: understand a change by following data through the system, not by reading
files top-to-bottom. Code is data being routed through a flow that transforms
and uses it. Find where the data enters, then follow it.

In the HTML report this is the **▶ Follow data** mode: a guided step-by-step
walk. Your job as reviewer is to make that walk *explain itself* — author the
`explanations.json` (SKILL.md step 3.5) so each step and hop carries a
plain-language description. The method below is how you derive those
explanations and the narrative you report back.

## 1. Pick entry points

Entry points are where data originates or enters the changed subsystem. The
model's `entryPoints` list is a starting hint (changed, exported, no in-scope
caller, or entry-like names). Also consider:

- HTTP/route handlers, controllers, middleware, CLI commands.
- Event handlers, subscribers, queue/message consumers.
- Exported functions the change adds or modifies that other modules will call.
- UI: component props / user actions / form submissions.

If several exist, start with the one most central to the change.

## 2. Follow the flow

From an entry point, walk **downstream** (its callees) in the call-graph view
using **Uses ▾**. At each hop ask:

- What data comes in (parameters, their types/shape)?
- How is it transformed here? What new value comes out?
- Where does it go next — which function, which module boundary?
- Does it cross a boundary it shouldn't (e.g. a domain module reaching into
  HTTP, a util importing a service)?

Follow branches. A conditional or a switch splits the flow — note each branch
and where it leads. Loops mean the data is a collection; note the per-item
transform. Trace until data reaches a **sink**: a return to the caller, a DB
write, a network call, a render, a log, or state mutation.

## 3. Describe the flow (the deliverable)

Write the flow as a short narrative or arrow chain, e.g.:

```
handleCheckout(qty, unit, discount)
  → PricingService.compute(order)        // raw = qty*unit; clamp(discount,0,100)
  → formatCurrency(cents)                // -> "$12.34"
  → returns label string (sink: HTTP response)
```

Then judge it:
- Is the path direct, or does data bounce through unnecessary hops?
- Are transformations in sensible places, or scattered?
- Is anything passed a long distance just to reach one deep function (prop/arg
  drilling)? That's a "clunky data flow" worth flagging.
- Is the same data re-fetched or re-derived at multiple points?
- Are there dead branches the data can never reach?

## 4. Upstream tracing

To assess blast radius of a changed function, use **Used by ▴** (callers). Everything
upstream is potentially affected by the change. Use this to answer "what breaks
if this is wrong?"

## Output

For each significant entry point, give the user: the flow chain, one or two
sentences on whether it's clean, and any specific clunky spots to fix (naming
the function and module). Keep it in plain language a reviewer can act on.
