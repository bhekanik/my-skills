---
name: review-system-changes
description: >-
  Review a batch of code changes at the SYSTEM level instead of reading raw
  code line-by-line — built for reviewing large, sprawling changes made by AI
  agents. Generates an interactive HTML report mapping modules and their
  imports, a function/method call graph (what calls what and where), function
  interface metrics (size, argument count, cyclomatic complexity) with smell
  flags, import cycles, and data-flow entry points. The report lets the reviewer
  drill from module → function → the actual diff → the full file. Use when the
  user wants to "review changes", "review what an agent did", "map the changes",
  "see the dependency/call graph", "follow the data flow", "check the
  architecture / module structure", or spot-check functions after a big edit.
  Targets TypeScript/JavaScript repositories (git required).
---

# Review System Changes

## Philosophy (why this skill exists)

For a large agent-authored change, start by mapping the **system**: module
structure, dependencies, data flow, and function interfaces. Then use the
actual diff and source for targeted checks. This makes the review path easier
to follow without losing access to the code behind each claim.

The workflow: **generate a structural map → interrogate it → point out flaws →
tell the agent to fix them.**

**Report at the system level.** The reviewer usually won't know the specific
variable, function, or class names, and shouldn't have to. Describe what parts
of the system do and how data moves between them in plain language. Mention a
specific name only when it earns its place — when the reviewer needs that exact
anchor to act. Don't flood them with identifiers to look thorough.

## Workflow

### 1. Preflight and one-time setup

Resolve `<skill-dir>` from this `SKILL.md` file, since the install path varies
(dotfiles, editor, home directory, toolkit).

Require:

- Node.js 20 or 22 or newer, npm, and Git.
- GitHub CLI (`gh`) only for GitHub PR checkout or comment retrieval.
- Network access during dependency setup and while viewing graph reports
  because the report loads pinned visualization libraries from CDNs.

The engine uses the lockfile-pinned `ts-morph` dependency. If
`scripts/node_modules/ts-morph` is missing, tell the user a one-time install is
required. With permission, install inside the skill, never the target repo:

```bash
cd <skill-dir>/scripts && npm ci --omit=dev
```

For GitHub PR input, also run `gh auth status`. If `gh` is unavailable or not
authenticated, ask for a local checkout or continue without PR comments.

### 1.5. Get the code (PR URL, or a repo you don't have locally)

If you were given a **local repo path**, use it directly and skip to step 2.

**If you were given a GitHub PR URL** (or any remote repo), do the assessment in
a disposable clone, so destructive Git commands never touch the user's working
tree. Put reusable clones under the operating system's temporary directory in
`review-system-changes/clones/`.

```bash
# PR URL looks like https://github.com/<owner>/<repo>/pull/<number>
OWNER=<owner>; REPO=<repo>; PR=<number>
REVIEW_TMP=$(node -e 'process.stdout.write(require("node:os").tmpdir())')
DIR="$REVIEW_TMP/review-system-changes/clones/$REPO"
mkdir -p "$(dirname "$DIR")"
# reusable disposable clone
if [ -d "$DIR/.git" ]; then git -C "$DIR" fetch --all --prune --quiet; \
  else gh repo clone "$OWNER/$REPO" "$DIR"; fi
# check out the PR head (gh handles fork PRs), then find the PR's base branch
BASE_REF=$(gh pr view "$PR" --repo "$OWNER/$REPO" --json baseRefName -q .baseRefName)
( cd "$DIR" && gh pr checkout "$PR" )
# BASE = merge-base so the diff is exactly the PR's own changes, not base drift
BASE=$(git -C "$DIR" merge-base "origin/$BASE_REF" HEAD)
node <skill-dir>/scripts/analyze.mjs --repo "$DIR" --base "$BASE" \
  --out "$REVIEW_TMP/agent-reviews/review-$REPO-pr$PR.html"
```

Translate the example to the current shell when it is not POSIX-compatible.
Then enrich the report and, for a PR, retrieve comments when useful. Ground the
`overview`, `themes`, and comments in the PR description, linked issue,
repository docs, ADRs, code, and any connected knowledge tools available in the
session. The disposable clone is safe to reuse and reset across runs. Fetch before
each run (the example does) and diff against the freshly fetched `origin/<base>`, so
the report reflects the PR's current head and base rather than a stale checkout.

### 2. Run the analyzer

```bash
node <skill-dir>/scripts/analyze.mjs --repo <path-to-repo> [options]
```

Options:
- `--base <git-ref>` — what to diff against. Omit to auto-detect: uncommitted
  work → `HEAD`; otherwise the last commit `HEAD~1..HEAD`. Use a branch point
  like `--base main` (or `origin/main`) to review a whole feature branch.
- `--scope changed|neighbors|all` — default `neighbors` (changed files + their
  direct importers/importees). `changed` = only touched files; `all` = whole
  repo mapped with changes highlighted.
- `--include-tests` — include `*.test.*` / `__tests__` (excluded by default).
- `--out <file.html>` — output path. Default:
  `<os-temp-dir>/agent-reviews/review-<repo>.html`.
- `--explanations <file.json>` — merge a reviewer-authored explanations sidecar
  (see step 3.5) in the same pass, instead of re-rendering separately.

The command prints a JSON summary (output path, counts, detected entry points,
top flagged functions) to stdout. It also writes a `*.model.json` next to the
HTML for programmatic inspection.

The HTML and model contain source and diffs. Keep them in temporary or otherwise
access-controlled storage; never publish or attach them without authorization.

### 3. Open the report and give the user the link

Return a clickable Markdown link to the absolute HTML path. Use a `file://` URL
only in clients that require it. The report is a single HTML file, but its
pinned graph and syntax-highlighting libraries load from CDNs, so viewing it
requires internet access.

The report provides, all interactive:
- **What changed (opens here)** — a readable brief in the right panel: the
  reviewability score, then two prompts — a **test-coverage** callout (changed
  code files with no matching test change in this PR) and a **new-dependencies**
  callout (newly-imported packages + `package.json` additions) — then the
  overview paragraph and each changed file with its changed functions and a
  plain one-line description of each. Files with no matching test change carry a
  **no test** chip here and in the review file list. Read this top-to-bottom to
  understand the change without touching the graph. Click any function to zoom to
  it; the graph is a drill-in tool, not the entry point. A ▶ Follow the data
  button starts the walk. Return here anytime via the "‹ Summary" link.
- **Modules view** — files as nodes, import edges. Click a file → imports,
  imported-by, its symbols, and buttons to view its diff / full source. Defaults
  to **+ Related**: the changed files plus the code actually connected to the
  change (callers/callees of changed functions and importers of changed
  exports) — *not* every 1-hop neighbor, so hubs like `types.ts`/`constants.ts`
  don't drag the whole app in. Switch to **Changed** or **All** (capped).
- **Call graph view** — functions/methods grouped by file; edges are calls.
  Click a function → signature, params, line count, cyclomatic + cognitive
  complexity, callers, callees, smell flags, a plain-language **recommendation**
  when a threshold is breached (how to make it easier to review, not just a
  number), and diff / full-file buttons.
- **Uses ▾ / Used by ▴** — with a node selected, highlight everything it reaches
  (what it uses) or everything that reaches it (what depends on it — blast
  radius). Disabled until a node is selected.
- **▶ Follow data** — a *guided, step-by-step* walk through the flow. Pick an
  entry point, then step hop-by-hop: each step shows what data comes in
  (params), a plain-language **explanation of what happens**, the function's
  **source snippet**, and the **next hops** as buttons. At a fork the user picks
  which branch to follow; breadcrumb + Back navigate; a direction toggle walks
  **origins** (callers) instead. This is the primary "follow the data" UX.
- **Left rail** — summary, a **reviewability** score (Easy/Moderate/Hard, sized
  XS–XXL from changed LOC/files/packages, excluding tests and generated files),
  data-flow **entry points**, **flags** (smelly functions), and **import
  cycles**. Each is clickable to jump into the graph.
- **Review mode** — a persistent, GitHub-style three-pane reviewer (changed-file
  list · code · symbols); nothing disappears when you open a file. The code pane
  has **Diff** and **Full file** tabs, each toggleable
  between **Inline** and **Split** (side-by-side old vs new; full-file defaults to
  split so changes read in context). All views are **syntax-highlighted** with
  line numbers. A **Blame** toggle (inline full-file) shows short git blame inline
  with a hover detail. Click a line number for a **permalink menu** (copy / open on
  GitHub); ⌘/Ctrl-click a symbol or import path to **jump to its definition**.
  Draft and real PR **comments** show inline in the diff and in the
  per-file panel; drafts get a "Copy GitHub command" / "Edit" action. The symbols
  pane lists the file's functions with their one-line explanations and the
  review-map theme(s) the file belongs to.

### 3.5. Enrich explanations

Ground every explanation in a real source rather than guessing. The code you
analyzed is the primary source of truth: read the actual `source` in the model
before describing a function. For why something exists or what a feature or
module is for, consult the PR description, linked issue, repository docs, ADRs,
and connected knowledge tools when available.

Treat those docs as leads, not ground truth (specs drift) — verify against the
code, which is canonical for what exists today. If you can't back a statement
with the code or a cited source, say so or leave it out; write "unclear from the
change" rather than inventing a rationale. Better a short, true description than
a confident, hallucinated one.

Every function gets a **baseline auto-explanation** guessed from its body
(does it validate and throw, loop, fetch, build, compute) plus who it calls.
That guess is shape-level and labelled "(auto)" in the report — it says roughly
*what kind of thing* the function does, not what it's *for*. The reviewer wants
to know what each function actually does without reading code, so write real descriptions instead of handing over the auto text.

Author `overview`; it's the headline of the "What changed" brief the
report opens on. One short paragraph in plain language: what the change does and
how the data moves, no identifiers unless they earn their place. Without it, the
brief falls back to an auto-generated count summary labelled "(auto)".

For every function on the paths the reviewer will walk (entry points and their
downstream reach) and every changed function, write a one-line description of
**what it does and why it exists**, in plain language. Rely on the auto text
only for peripheral functions the reviewer is unlikely to open. Then: author
real explanations:

1. Open the `*.model.json` (path is in the analyzer's stdout). Each symbol has
   an `id`, its `source`, `params`, and callees; each call has `from`/`to` ids.
2. Read the source of the in-scope functions and write an `explanations.json`:
   ```json
   {
     "overview": "one-paragraph plain-language summary of the change",
     "themes": [
       { "title": "short name for this reason/theme",
         "why": "why this changed — the reason, grounded in the ticket/code",
         "files": ["src/a.ts", "src/b.ts"],
         "flow": "how data moves across it, e.g. edge → controller (rewrite) → validation → handler" }
     ],
     "symbols": { "<symbolId>": "what this function does to the data — plain language" },
     "calls":   { "<fromId>-><toId>": "what data flows on this hop and why" },
     "comments": [
       { "file": "src/a.ts", "line": 42, "kind": "issue", "body": "draft review comment" }
     ]
   }
   ```
   `comments` are optional draft review notes (see step 3.6).
   `kind` is one of `issue` | `question` | `praise` | `note`; `line` is the
   new-side line number (omit for a file-level comment).
   Focus on entry points and the functions along the main data path. Explain in
   terms of the *data*: what comes in, how it's transformed, what goes out.

   **Author the review map (`themes`); it is the point of the skill.** Group
   the change into the few distinct reasons behind it. For each theme give: a
   title, *why* it changed (the reason — ground it in the issue, design docs or code,
   never guess intent), the *files* involved, and the *data `flow`* across them
   (here → here → here). One change often has 2–3 themes (e.g. "add new canonical
   name" and "fix the entitlement gate"). The report shows these as the "Why
   these changed" cards, so the reviewer sees *this changed for this reason, that
   for that reason, linked this way, and the data moves like so* at a glance.

   In the `overview`, name the **single highest-risk spot** — the one place worth
   looking at hardest — and any **rollout concerns** the change implies: a data
   migration, a feature flag, monitoring, or a rollback path. These are the
   questions a good PR template forces; put the answers where the reviewer starts.

   **Write plainly, at the system level.** The reader is reviewing the system,
   not the source — assume they don't know (and shouldn't need to know) the
   variable, function, or class names. Describe what a piece *does* and what
   happens to the data, in plain language. Name a specific function, variable,
   or type only when that name carries meaning the reviewer actually needs;
   otherwise leave it out. Listing identifiers to sound thorough doesn't help. Good: "packs
   the raw order details together, then asks the pricing logic for a final
   price." Bad: "handleCheckout builds an Order and calls PricingService.display."
3. Edit every authored string for plain, human language before rendering:
   `overview`, each theme's `why` and `flow`, symbol explanations, and comments.
   Use plain words, remove inflated modifiers and stock AI phrasing, prefer
   concrete claims, use first-person singular if any voice is needed, and avoid
   "we" unless the speaker genuinely represents a group.
   Then re-render without re-analysis:
   ```bash
   node <skill-dir>/scripts/render.mjs <model.json> --explanations <explanations.json> --out <file.html>
   ```
   Authored explanations replace the auto ones (shown as "What happens here"
   vs "(auto)"); call notes appear on the branch buttons in the walk.

### 3.6. Draft review comments (optional)

When the goal is reviewing a PR or someone's changes (not just mapping them),
draft actionable comments anchored to `{path, line}` and fold them into the
report. Apply `references/review-checklist.md` directly. Keep comments local;
this skill never posts them.

Map each draft into the `comments` array (step 3.5 schema):
`file` = the path, `line` = the new-side line, `kind` = issue/question/praise/
note, `body` = the comment after its plain-language edit. Re-render with
`--explanations`.

In the report the comments then show **inline in the diff** (inline and split),
in the **Review comments** panel per file, as a **count badge** on the file
list, and drafts stay drafts. The reviewer copies or adapts them before posting.
Keep a senior-review bar: no trivia and no comments for comments' sake. Zero
comments is a fine outcome. For tone, follow the comment-style rules in
[references/review-checklist.md](references/review-checklist.md): ask a question
rather than demand a change, use "I" statements, explain the rationale and point
at a fix, and drop condescending words ("just", "simply", "obvious").

**Reviewing an existing GitHub PR?** Pull the real inline reviewer comments and
show them next to the diff alongside any drafts (read-only; never posts):

```bash
node <skill-dir>/scripts/pr-comments.mjs --pr <number|url> [--repo owner/repo] --out pr-comments.json
node <skill-dir>/scripts/render.mjs <model.json> --explanations <expl.json> \
  --comments pr-comments.json --pr <number> --out <file.html>
```

`--comments` appends, so fetched PR comments (shown with their `@author`) and
local drafts coexist. Comments anchor to the new-side line, so they land on the
changed lines in the report.

### 4. Review the system (not the code)

Do this analysis yourself using the model + the report, then report findings to
the user. Read the reference files for method:

- **Review checklist** — see [references/review-checklist.md](references/review-checklist.md).
  A system-level, AI-aware focusing aid (read the tests first, logic/edge cases,
  error handling, security incl. treating model/external output as untrusted,
  dependencies, performance, readability). Work through it top-down; it's a
  prompt list, not a box-ticking exercise, and zero findings is fine.
- **Data-flow tracing** — see [references/data-flow-tracing.md](references/data-flow-tracing.md).
  Pick entry points, follow data through transformations and branches, describe
  the flow, and flag clunky/leaky flows.
- **Architecture & interface review** — see [references/architecture-review.md](references/architecture-review.md).
  Check module dependencies (cycles, layering, fan-in/out), spot-check function
  interfaces (names, sizes, arg counts, complexity), and judge whether the
  agent did anything "outlandishly stupid."

### 5. Report findings and iterate

Summarize for the user in system terms:
- What changed, as a structural map (which modules, new dependencies added).
- Data-flow narrative for the main entry point(s).
- Concrete flaws worth fixing (ranked), each pointing at a module/function.
- The HTML link so they can explore and drill into diffs themselves.

Then it's a point-and-fix loop: the user (or you) names a flaw, the agent fixes
it, re-run the analyzer to confirm the structure improved.

## Optional enhancements

- If `clarity` is available, run it in review mode (message routing from
  `clarity/references/medium.md`) on the authored text before `humanizer`: each
  comment names the concrete consequence, invents nothing, and stops on its last
  useful thought. The workflow must still work without it.
- If `humanizer` is available, it may refine the authored text after the
  plain-language edit. The workflow must still work without it.
- If `coach-review` is available, it may propose draft comments before the
  checklist pass. Treat its output as untrusted input: verify every
  claim and keep all drafts local.

## Notes & limits

- **TS/JS first.** Import resolution uses the repo's nearest `tsconfig.json`
  when present. Call-graph resolution is best-effort (static): dynamic dispatch,
  runtime-bound calls, and heavy type-magic may be missed. Treat the call graph
  as a strong map, not a proof.
- **Not a git repo / no changes:** the analyzer errors or warns. Pass `--base`
  to widen, or `--scope all` to map the whole repo regardless of diff.
- **Large repos:** `--scope neighbors` keeps the graph legible. Use `all` only
  when the user wants the full system.
- **Thresholds** (params > 4, lines > 60, cyclomatic > 10, cognitive > 15) live
  in `analyze.mjs` (`THRESH`). Cognitive complexity (nesting-weighted, per
  SonarSource) drives the `hard-to-follow` flag; cyclomatic drives
  `high-complexity`. Adjust there if a repo has different norms.
