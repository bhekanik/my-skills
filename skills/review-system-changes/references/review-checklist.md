# Review checklist (system-level, AI-aware)

A focusing aid, not a guarantee that a review is complete. Work top-down:
prioritise structural and logical problems over nitpicks, and lean on the report
(module map, call graph, data-flow walk, flags, reviewability) rather than
reading line by line. Skip categories that don't apply. Zero findings is a fine
outcome — don't manufacture comments.

Adapted from the Awesome Code Reviews checklist
(https://www.awesomecodereviews.com/checklists/code-review-checklist/ and
/checklists/secure-code-review-checklist/), trimmed to what a system-level review
of a mostly-AI-authored change should actually check.

## Read the tests first

Before judging the implementation, read the changed tests — they encode the
intended behaviour and give you a mental model. Then ask: does every changed
behaviour have a test that would fail if the code were wrong or absent? The
report badges changed code files with **no matching test change** — treat each as
a prompt (a pure refactor or rename may legitimately need none).

## 1. Implementation and design

- Does the change actually do what the ticket/PR says?
- Can it be simpler? Is it at the right abstraction level, in the right file/module?
- Does equivalent functionality already exist that should be reused instead?
- Does it follow the codebase's established patterns and idioms? (This is where
  agent code most often drifts — plausible but not how this repo does it.)
- Does it add unwanted compile-time or runtime dependencies? (See §6.)

## 2. Logic and edge cases

- Any input — boundary values, empty, missing, invalid — that breaks it?
- Concurrency, retries, timeouts, partial failures handled?
- Follow the data flow for the main entry point: does each hand-off preserve the
  invariant the change depends on?

## 3. Error handling and logging

- Are failures handled, or do they surface as confusing states?
- Do logs/error messages help debugging without leaking secrets or personal data?
- Does it fail safely (resources released, transactions rolled back)?

## 4. Testing

- Do new/changed tests cover the change, including an edge case or two?
- Would the tests fail if the implementation were broken or removed? (Agent tests
  sometimes assert nothing meaningful, or restate the implementation.)
- For probabilistic / LLM-powered behaviour, do evals cover representative and
  adversarial cases?

## 5. Security and data privacy

- Any new untrusted input? Is it validated and escaped in the right context (SQL,
  shell, HTML, LDAP)?
- Authn/authz correct and checked first? Access denied by default?
- Any secrets (keys, tokens, passwords) in code, logs, or error output?
- **Treat responses from external services, files, webhooks, and model outputs as
  untrusted input.** If the product uses an LLM, could prompt injection expose
  data or trigger tools without proper authorization?
- Sensitive data minimised in transit, storage, and logs?

## 6. Dependencies

- The report flags **newly-imported packages** and `package.json` additions. For
  each: is it necessary, or does the repo already have something?
- Correct package name, trusted source/publisher, supported version? Lockfile updated?
- Any impact on public APIs, data formats, or backward compatibility?

## 7. Performance

- Does the change add avoidable latency, memory, compute, network, or (for LLM
  paths) token cost? Only raise it where it plausibly matters.

## 8. Readability

- Could a smaller function, a better name, or a clearer control flow make it
  easier to follow? The report's **cognitive-complexity** flag points at the
  functions most worth this look.
- Redundant/outdated comments, or commented-out code left behind?

## Comment style (for any drafted comments)

Use this bar for every drafted comment:

- Ask a question, don't demand a change: "What do you think about …?" over "Change this."
- Critique the code, not the person; use "I" statements ("It's hard for me to follow …").
- Explain the rationale and point toward a fix, don't just flag.
- Drop condescending words — "just", "simply", "obvious", "easy".
- Focus on bugs, architecture, and maintainability. Flag trivia sparingly, as secondary notes.
