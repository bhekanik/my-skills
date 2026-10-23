---
name: writing-docs
description: Write operational software documentation for developer tools, apps, packages, CLIs, APIs, config, runbooks, docs sites, and maintainer guides. Use when drafting a new docs page, README section, quickstart, how-to, reference page, recipe, architecture note, package README, or reviewing a draft for docs-writing quality. If the task is mainly stale-doc cleanup or drift auditing, prefer documentation-refiner.
---

# Writing docs

Write docs that leave the reader able to do the thing, not merely understand the thing.

Source principle: no reader should finish a doc and think, "I get what this is, but I don't know how to make it useful."

## Workflow

1. Read local instructions first: `AGENTS.md`, repo docs conventions, docs config, package scripts, and existing nearby docs.
2. Identify the reader and page mode. Pick one Diataxis quadrant per page: tutorial, how-to, reference, or explanation.
3. Verify the source of truth before writing. Use code, CLI help, schemas, route tables, config, tests, workflows, screenshots, and generated output over stale docs or tickets.
4. Draft around the reader's next action. First paragraph names the verb the reader will perform.
5. End every major section with something usable: a command, code block, output shape, exact UI step, screenshot reference, or verification step.
6. Run examples before publishing. Paste real output when the reader needs to compare results. If a failure is deliberate, label it clearly.
7. Check nav and links. If the repo uses `mkdocs.yml`, TechDocs, VitePress, Docusaurus, Storybook, or generated refs, make sure the page is reachable and links resolve.
8. Apply a clarity pass, then a humanizer pass. Check substance and register first: who the reader is, what they should be able to do afterward, and whether each section has a mechanism, exact step, or example beside its claim. Keep headings, lists, caveats, and required structure intact. Then remove formulaic phrasing. Use installed `clarity` and `humanizer` skills when available.

## Page rules

- Use second person and imperative voice.
- Show before tell. Command first, explanation second.
- Use inline code for commands, paths, flags, config keys, APIs, UI labels, and identifiers.
- Use real placeholders beside real values, for example `--space-id <space-id>` after showing `--space-id abc123`.
- Do not say "click here" or "see above." Name the target.
- Do not invent product claims, performance claims, supported platforms, or guarantees.
- Prefer links over duplicated explanation.
- Do not patch generated docs by hand. Update the source and regenerate.

## Surface coverage

If it ships, document it:

- CLI commands, flags, env vars, config keys, exit codes, output formats
- API routes, request bodies, response bodies, errors, auth, rate limits
- UI panels, settings, destructive actions, notifications, URL schemes
- Webhook events, background jobs, queues, metrics, logs, alerts
- Package exports, public types, examples, conformance tests

For broad surfaces, generate reference from source truth and fail CI on drift where the repo supports it.

## Recipes

Recipes solve goals. Do not restate reference.

A useful recipe has:

- the reader's problem
- the smallest working path
- exact inputs
- exact command or UI flow
- expected output shape
- what to check when it fails

## Mutations

Document mutating operations dry-run first.

Show the safe command before the destructive one:

```sh
tool migrate --dry-run
tool migrate --yes
```

For UI docs, show the confirmation flow before the irreversible action. Copy-paste habits should absorb the safety model.

## Maintainer docs

For maintainer or contributor docs, add these sections when useful:

- Locked decisions: choices reviewers should not relitigate without new constraints.
- Out of scope: tempting work the team has decided not to implement.
- Regeneration: commands that rebuild generated docs.
- Verification: commands that prove the page still matches the system.

Keep these sections short and specific.

## Public package docs

A package README should explain the trust story:

- why the package exists
- what spec, product behavior, or external contract it follows
- what it refuses to do
- how users can verify the claims
- how examples are tested

Runnable examples and a conformance corpus beat broad claims.

## Review checklist

- Title leads with a verb when the page is task-oriented.
- Description is short and promises an action.
- First paragraph names what the reader will do.
- Each major section has a runnable example, exact UI step, output shape, or verification step.
- Mutations show dry-run or confirmation first.
- The page stays in one Diataxis quadrant.
- Generated surfaces come from source truth.
- Links and docs nav resolve.
- The prose sounds like a person who has used the system.
- Structure follows the reader's task; no gap was filled with an invented detail instead of a `[TK]` question.
- Check final prose for invisible AI marks. If `remove-ai-marks` is installed, run its Layer A cleaner on prose while leaving code blocks and frontmatter untouched.
