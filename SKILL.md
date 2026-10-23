---
name: orchestrate
description: Orchestrate substantial multi-phase implementation work with host-specific model routing, isolated worktrees, vertical deployable capability slices, iterative adversarial review, cross-model verification, knowledge transfer, exact-SHA merge gates, deployment after every increment, and run-owned workspace cleanup. Use when the user invokes /orchestrate or asks one thread to coordinate multiple agents or phases. Not for small one-agent tasks.
---

# Orchestrate

Run the current thread as the control plane for a multi-agent delivery program. Workers implement. This thread owns the product sequence, shared context, adversarial review, integration, documentation, deployment, workspace cleanup, and truthful completion status.

This skill stands alone. Routing or domain skills may add their own gates when invoked; those gates supplement these rather than replacing them.

## Select the model topology first

This is the model routing policy for an orchestration run. It encodes how to choose, never which models: names and versions change faster than this file.

### Look up the models before every choice

Before planning a run, list the models the host offers right now, with what each is for. Never route from memory or from an earlier run.

- **Claude Code:** the model aliases the subagent `model` parameter accepts and those listed in `claude --help`. Aliases roll forward to the newest model of their family; pass the alias, not a pinned version.
- **Codex:** the listed (not hidden) models in `~/.codex/models_cache.json`, or the host's model picker, with their descriptions and supported reasoning levels.

Keep only the newest version of each family and drop every older one before sorting. An older generation is never a candidate, not even as a cheaper step or a tier between current models. A family whose newest version is a generation behind the others stays in, at its own family's place.

Sort what you find into four capability tiers using the host's own descriptions, and write the mapping into the ledger:

| Tier | What the host says about it |
|---|---|
| Fast | fast, affordable, for easier tasks |
| Balanced | balanced, for straightforward work |
| Strong | the workhorse for coding and everyday complex work |
| Frontier | the most capable, for the most demanding work |

A host may not offer all four. If two models are hard to tell apart, say which you picked and why. If the user names models for a run, use those instead and record it.

| Role | Tier | Reasoning effort |
|---|---|---|
| Orchestrator (this thread): planning, routing, review, integration | Frontier | User's selected setting |
| Implementation workers | Chosen per task (see below) | High, raised before any tier change |
| Independent verifier | Frontier from a different provider, looked up the same way | Highest |
| Review subagents (read-mostly cleanup or type reviews that need their own agent) | Fast, passed explicitly | High |

Preserve the user's selected reasoning effort for the orchestrator, including when switching its model. Do not raise it to the highest setting or ask the user to raise it. The worker and verifier effort rules apply only to those roles.

### Route each worker to the intelligence its task needs

The orchestrator runs on frontier because routing is judgement: it sizes each task and picks the cheapest worker that can do it. Choose workers by the reasoning the task requires, not by a general belief that the strongest model can handle anything.

Fast models are quick, cheap and capable enough for a large share of implementation. A miss there is cheap: review catches it and the retry often lands before a slower model would have finished its first attempt. Strong models handle almost everything else when they get the right brief, context and environment. So:

- **Start every task on fast** unless you can name the specific reasoning it demands that fast can't supply. Size, unfamiliarity, importance and a full verification tier don't qualify on their own; risk is handled by the review gates, not by a bigger worker.
- **Start on balanced or strong only for a named reasoning demand,** for example subtle concurrency or ordering, a design decision with non-obvious trade-offs, debugging across many interacting parts, or logic where a plausible but wrong answer would survive review. Write the demand in the brief and the ledger.
- **Escalate slowly, and only when intelligence is what's missing.** A task escalates when it has failed review or its acceptance checks at least twice on the same problem at its current tier, and at least one of those failures came after you ruled out the other causes:
  - an unclear or incomplete brief;
  - missing context: files, conventions, contracts or ledger facts;
  - a broken environment, flaky tests or tooling;
  - a task too big for one attempt that should be split.

  If one of these is the cause, fix the brief, the context, the environment or the split, and retry on the same tier. Escalate only when the worker had everything it needed and still couldn't reason its way to a solution. Name that reasoning gap in the ledger.
- **Raise effort before changing model.** The first escalation keeps the model and raises the worker to its highest reasoning effort, from the levels you looked up. Skip any level that delegates to other agents on its own (Codex's `ultra` does). More thinking on a fast model is cheaper than a bigger model. Only when the task meets the escalation trigger again at that effort does it move up one tier, starting back at high effort. A model that offers no higher effort goes straight to the next tier.
- **Frontier workers are very rare.** No task starts there. A task reaches frontier only when strong has been confounded: it failed repeatedly at its highest effort after the brief, context, environment and split were all fixed. Before that, the orchestrator, already on frontier, works the problem itself and puts the missing insight into a new brief for a strong worker. Escalate to a frontier worker only when even that fails, and tell the user when you do.
- **A task that changes tier gets a new worker** on the next tier, continuing in the same worktree, briefed with the failed attempts and what each one got wrong.
- **Escalation stays with the task.** The next task is sized fresh. If fast keeps failing the same kind of task across a run, record that in the ledger and start later tasks of that kind one tier up.

Record each worker's tier, model, effort, the reason for them and every escalation with its diagnosis in the ledger and the stage report, so the user can challenge the routing.

If this thread is not running the orchestrator tier and the host cannot switch in place, tell the user which model to select before delegating. Don't silently run the plan on a lower tier. Check the active model through runtime metadata or a host command; if the host exposes none, say so and ask the user to confirm once. Absent metadata is not a mismatch.

Use a native cross-provider agent or tool for the verifier when one exists. Otherwise use the installed provider CLI in a non-interactive, read-only review session. Before trusting that review, check that it reports the model you asked for, runs in a fresh session, can read the exact review clone, receives no secrets, and cannot change the candidate or deployment. A same-provider substitute is not an independent second opinion: report the gate as blocked instead. A tier that doesn't require the verifier skips the gate; that isn't a waiver. Only the user can waive it for a stage; record the waiver and never infer one.

## Start with the product outcome, not the component list

Before spawning implementation workers:

1. Fetch the relevant remote refs and pin the current base SHA (`origin/<default>`, not local main).
2. Recover current work, open PRs, plans, deploy state, and external blockers.
3. State the underlying user outcome in one sentence.
4. Search the current codebase for established patterns and already-built capabilities before proposing architecture.
5. Challenge unvalidated features. A requested subsystem does not earn a stage until it supports a real user outcome; flag speculative features for the user instead of inventing demand.
6. Map dependencies as a DAG: what blocks what, what can run in parallel, and which shared seams need one integration owner.
7. Convert the DAG into **vertical deployable capability slices**.
8. Audit any inherited plan against the ladder before executing it. A roadmap, kickoff prompt or phase list from an earlier session isn't exempt. If its phases are components ("foundation", "full API surface", "TUI", "ship at the end"), restructure them into rungs, or show the user the restructured ladder first, rather than carrying out a component-phased plan because it was handed over.

### Vertical slice rule

Use the skateboard → scooter → bicycle → motorbike → car model. Every stage is a smaller but useful version of the whole outcome.

- A stage must let a user do something they could not do before.
- Pull every required layer into that stage: UI, domain logic, storage/backend, error handling, tests, documentation, deployment, and the release-defining smoke.
- Components are enablers, not milestones. “Database,” “editor engine,” “API,” “app shell,” and “rate limiter” are not stages by themselves.
- If a slice is too large, narrow the user promise. Do not split it into horizontal parts that become useful only when recombined later.
- Preserve useful behavior from the previous stage. Make the ladder explicit: “previously X; now X + Y.”
- Foundation-only work is ceremony. Keep it inside the nearest user-facing slice where possible. If unavoidable, name it as ceremony and do not call it shipped product progress.
- A hidden feature flag can make integration safe, but hidden partial work is not a completed stage.
- One working session per rung. The user should end every turn with something usable, never after days of building toward "the end". If a rung won't fit in a session, narrow its promise.
- Every rung ships through the real release channel. The release chain (CI, versioning, the install path) is ceremony pulled into rung 1, so rung 1 is already installable and each later rung is a release the user can install and use.
- Close each turn by demoing the rung and stating the ladder: "previously X; now X + Y; next Z".
- Accept small rework, such as a temporary handler that a later rung replaces, to keep rungs usable. Record the trade-off in the plan.
- Foundation turns are allowed when there's no sensible usable artifact yet. Some projects can't be useful after turn one: a new runtime, a protocol, a hardware bring-up, heavy platform setup. Follow the philosophy broadly, not rigidly. A plan may open with a few foundation turns, up to about three, before the first usable rung.
  - Name each one as foundation, with what it makes possible.
  - End each one with something runnable or checkable where possible: a passing smoke, a signed-in `status`, a probe that talks to the real service.
  - State in the plan which turn delivers the first usable rung.
  - Once usable rungs start, go back to one usable release per turn. Don't mix foundation turns in between unless a new subsystem truly has no usable form.
  - If the foundation keeps growing, stop and look for a thinner first rung.

Apply this rejection test mechanically: can the promised demo run from a released client using only artifacts deployed in this stage or an earlier one? If not, the stage is a horizontal component or ceremony, regardless of its label.

### Plan the human review path

Product stages and PRs answer different questions. Keep the stage's user promise intact, then consider whether its candidate diff is too large or tangled for a human to review confidently. Split it into a small number of cohesive PRs with a clear reading order when that makes the design and behavior easier to follow. Each PR should have a focused diff, its own validation, and a short route through the change for the reviewer. Do not create extra PRs for a size target when they would obscure the logic.

Use independent PRs when the slices can be reviewed and merged independently. Consider a [GitHub stack](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-stacked-pull-requests) when later slices build on earlier ones, or when an ordered chain makes a substantial change easier to review. A stack can be useful for review even when the code has no strict dependency. Base each PR on the branch below it so GitHub shows only that layer's diff; show the order and what each PR contributes. Keep lower layers safe to merge on their own, and merge from the bottom up. A PR slice is not a completed product stage: the stage remains open until its full user journey is deployed and passes.

Record the proposed PR shape in the stage plan before implementation. Preserve the same exact-SHA review, documentation, authorization, and deploy gates for every affected candidate; stacking does not grant permission to push, open, or merge PRs.

For every planned stage, write:

- User promise: “After this stage, a user can …”
- Demo: the exact journey that proves the promise.
- Acceptance: tests and observable behavior.
- Deploy target: production, staging, TestFlight, device, package registry, or another real target.
- Dependencies and non-goals.
- Verification tier and the trigger that set it (see "Size verification to the stage's risk").
- Documentation scope and owner from the documentation gate below.

Do not implement a dependent stage until the prerequisite stage is deployed and its user journey passes. Read-only research and risk discovery may proceed, but must not freeze an undeployed contract into code.

### Size verification to the stage's risk

Every stage gets a verification tier, set at plan time from what the stage touches, not from how simple it feels. Diffs that look simple are where the self-check bug classes hide, so the triggers decide, not judgement.

| Tier | Triggers | Gates |
|---|---|---|
| **Full** | Persistence or data migration, auth/tenant/privacy, schema/protocol/public API, concurrency or shared mutable state, money, or anything hard to roll back | Every gate in this skill |
| **Standard** | Real logic or new behaviour with no full trigger | Worker gate, the self-check classes that apply, orchestrator review. Cross-model verification only when the orchestrator review found a blocker |
| **Light** | No full trigger, small diff, follows an existing pattern (copy, styling, a field on an existing form, config, docs) | Worker runs targeted tests, a typecheck of the changed package and one scoped simplification pass. The orchestrator reads the diff once. No self-check list and no cross-model verification |

Every tier keeps exact-SHA provenance, the merge gate and the deploy smoke: they're cheap, and they prove the user promise.

Escalation runs one way. When the diff picks up a higher tier's trigger, or a light or standard review finds a blocker, raise the tier and run its missing gates on the current head. Never lower a tier mid-stage. Record the tier, its trigger and any escalation in the ledger and the stage report so the user can challenge what was skipped.

## Documentation gate

Run this gate for every stage and verification tier, including light changes. Documentation is part of the delivered capability: correct code with stale instructions can still leave the user unable to use or operate it.

1. Before implementation, discover and read the documentation relevant to the stage: repository instructions, README, applicable `docs/` pages, architecture/ADRs, API or CLI references, configuration examples, and operating/release runbooks. Follow relevant links and record the paths reviewed, missing coverage, and the owner of any likely updates in the stage plan and worker brief. Verify documented assumptions against the current code rather than treating docs as ground truth.
2. Reassess documentation impact against the actual candidate diff, including review fixes. When changes affect documented behavior, interfaces, setup, configuration, architecture, usage, or operations, update the authoritative documentation in the same stage and PR as the implementation, even if the user did not explicitly ask for docs. Add missing coverage where the change needs it, following the existing documentation structure; keep unrelated cleanup out of scope. Update executable examples and generated references through their source or generator where applicable.
3. Reconcile affected docs with the candidate, using `/documentation-refiner` when available. Check changed claims and examples against the implementation, run applicable documentation builds, link checks, and example commands, and report any checks that could not run. If no update is needed, record which docs were inspected and a concrete reason the change leaves them accurate; a bare N/A is insufficient.
4. The orchestrator verifies the documentation result before merge and rechecks it at stage close against what actually shipped. Required repository updates belong in the reviewed candidate; a ledger entry, handover, or promise to write docs at the end of the program does not replace them. Required documentation left stale or missing prevents stage completion.
5. Stay within the authority boundary: in-scope repository documentation accompanies implementation, but external documentation writes or publishing still require explicit authorization for that exact action. If approval or access is missing, report the affected page and exact blocker, carry it into the handover, and keep the required documentation work pending rather than claiming the stage is done.

## Parallelism

Parallelize only when it shortens delivery without hiding integration risk.

Good parallel work:

- independent vertical capabilities that can each deploy safely;
- platform work after a shared contract is stable and deployed;
- read-only research or review that does not mutate the same candidate;
- work inside one release wave with an explicit integration owner and non-overlapping seams.

Do not parallelize:

- multiple workers editing the same integration seam without one owner;
- dependent stages whose prerequisite has not deployed;
- native UI suites against the same simulator/device session;
- horizontal components merely because they can be built separately.

Respect the host's concurrency limit. Keep one slot free when an independent review or urgent integration task will need it.

## Worktree isolation and provenance

- Before allocating a worktree, clone, build target, or eval snapshot, read [Workspace lifecycle](references/workspace-lifecycle.md). Register its exact path, owner, purpose, storage budget, cleanup authorization, and release condition in the ledger. Reuse a worker's workspace and build target across review rounds; a new attempt is not a reason for a new checkout or target directory.
- Implement in worktrees, not the user's active checkout, and preserve uncommitted and untracked user files.
- Fetch before making code claims. Prefer explicit HTTPS remotes when SSH is not configured.
- Give each implementation worker its own branch and disposable worktree/clone, created from the freshly fetched `origin/<default>` (or the prerequisite stage's merged result), never local main.
- Keep anything that must survive the run out of `/tmp`: worker worktrees, eval snapshots, long-running servers the user restarts, and any clone with unpushed commits. Some hosts clear `/tmp` on restart. Put durable workspaces under the user's code directory, for example `~/code/<org>/.worktrees/`. `/tmp` is only for throwaway read-only clones and logs.
- Keep worker branches current: workers fetch and rebase onto `origin/<base>` after long phases and before each candidate report, and the orchestrator re-fetches before every review round, so conflicts surface early instead of as one large rebase at the end.
- Record base SHA, head SHA, tree SHA, merge base, worktree path, and dirty/clean status.
- Declare likely file ownership and shared integration seams before parallel work begins.
- Review and deploy exact commits. A branch name or stale local ref is not provenance.

When a stage changes a schema, protocol, file format, or public API, define compatibility with every still-deployed client before implementation. Include migration, mixed-version behavior, rollback/forward-fix posture, and destructive-change safety in acceptance.

### Close owned workspaces at stage boundaries

Run the [Workspace lifecycle](references/workspace-lifecycle.md) closeout after a stage's deploy smoke, before handing off to a fresh orchestrator, and whenever work pauses, fails, or is cancelled. Keep scaffolding during an active review loop, not indefinitely after it ends.

1. Reconcile every registered path and process, including reviewers' clones, eval snapshots, dependency installs, and build caches.
2. Preserve durable evidence and unfinished source work; stop or await only this run's processes and queued jobs before releasing their resources.
3. With the recorded scope-bound approval, remove eligible generated data and completed worktrees using the reference's safety checks. Retain active, dirty, local-only, locked, foreign-owned, or unverified resources and name the blocker instead of forcing removal.
4. Report removed paths, measured free-space change, and every retained path with its size, reason, owner, and next cleanup action. An unresolved entry stays in the next handover; it does not disappear when the orchestrator starts fresh.

A stage report is incomplete until every registered resource is removed or explicitly retained. Product deployment status and cleanup status are reported separately.

## Authority boundary

The skill selects a workflow; it does not broaden the user's requested scope.

- When the user asks the orchestrator to carry implementation through merge and deployment, ordinary in-scope branches, PRs, merges, and declared deploy targets are authorized.
- When the user asks only for mapping, planning, review, or diagnosis, stop at that boundary.
- Do not infer authority for billing changes, credential creation, account configuration, destructive data operations, public announcements, or a different production target.
- Resolve an ambiguous or high-risk deploy target before mutation. Prefer the repository's established release channel.

## Shared knowledge ledger

Create one shared ledger outside any repository and outside `/tmp`, for example `~/code/<org>/.orchestrate/<run>/`, and give every worker its path. A host that clears `/tmp` on restart would also lose briefs, triage and cited evidence stored there. Keep run scaffolding out of the repository; maintain project documentation through the documentation gate. Evidence a durable record cites (screenshots, review output) goes in the project's own working folder, not only the ledger. The orchestrator is the sole writer; workers return knowledge packets instead of editing the ledger. Keep secrets and raw credentials out. Record a cleanup path and retain the ledger through the final deployment report.

After every worker or reviewer report, add only durable facts you have verified or that carry their source:

- what was learned;
- assumptions that proved false;
- attempts that failed and why;
- new constraints or invariants;
- decisions and their evidence;
- deployment facts and blockers;
- residual risks.

The orchestrator owns context propagation. Before a worker starts or resumes, send the relevant ledger delta, upstream contracts, current base, and product promise. Do not make workers rediscover facts another worker already paid to learn. Do not flood them with unrelated history.

## Verify claims before reporting them

Anti-pattern: noticing something (a search hit, a file name, an enum value, a log line), turning it into a claim, and reporting it with "likely" or "I haven't checked that yet". The reader can't tell an observation from a guess, and decisions get made on the guess. A search hit alone does not establish what a live code path does.

- When a claim is relevant to the decision, the user's question or the next step, check it before reporting it: read the code at a named SHA, query the data or run the command. It's usually one or two tool calls.
- Report what you observed, with its source: a SHA plus `path#Lx-Ly`, a query plus its window, or a command plus its output.
- If a claim can't be checked (no access, rate limits, another team's system), say what you tried and what would settle it. Leave unchecked claims out of tickets, PR text and other durable writes.
- Don't hedge with "likely" or "probably" when one more read would settle it. Hedge only what genuinely can't be checked.
- Re-check numbers and causal claims before they go into anything someone else will read.

## Worker brief

Every implementation worker receives:

1. the vertical user promise and exact demo;
2. scope and non-goals;
3. pinned base SHA and isolated worktree requirement;
4. relevant knowledge-ledger facts, dependency contracts, and exact file pointers (paths and line ranges) in the brief itself, so the worker doesn't spend round trips re-reading design docs;
5. acceptance checks, deploy target and the stage's verification tier. A light-tier worker runs the light verification gates and the documentation gate, and reports N/A, with the tier, for skipped review gates;
6. instruction to review changed TypeScript/JavaScript types and simplify the touched implementation before reporting back; use `/typescript-reviewer` and `/code-simplifier` when available. Run the scoped simplification pass inline in the worker's context; avoid a built-in simplify command that starts multiple reviewers for this pass. Any review that still needs its own subagent runs on the review tier;
7. the integration owner and owned/shared file seams;
8. instruction not to push, merge, or deploy outside the explicitly assigned environment.
9. the "Work efficiently" rules below, including the adversarial self-check, plus the worker's own eval port and a snapshot or restart script it reuses across rounds;
10. the "Verify claims before reporting them" rule above, verbatim.
11. its registered workspace/build-cache paths, storage budget, process and queue ownership, evidence destination, and cleanup release condition from [Workspace lifecycle](references/workspace-lifecycle.md).
12. the documentation gate, relevant documentation paths, and ownership of the required updates.

### Work efficiently

Repeated full-suite runs, idle waits for evals, and one-file-at-a-time reads can dominate worker time. Brief every worker on these:

- **Test what you touched while iterating:** run the spec files you changed, or a related-tests command such as `vitest related <files>` when the project uses it. Run the full suite once, before reporting.
- **Batch reads:** read several files or ranges in one command. The brief already carries the contract, the file pointers and the ledger facts, so don't send workers to re-read whole design docs. For "where is X" questions, use a fast read-only search agent when available instead of many separate greps.
- **Never block on an eval run:** run evals against a built copy of the committed SHA (its own worktree and port), not your hot-reloading dev server. Keep working while they run. A dev server that reloads on edits mixes commits into a run.
- **Keep the scaffolding during review:** reuse your worktree, dependency install, and build target across rounds. Use one restart script that records process IDs and stops only its own process tree. If the project uses Nx, set `NX_DAEMON=false` for controlled runs. Return paths and process ownership for the stage-boundary cleanup gate; keeping scaffolding is not permanent retention.
- **Typecheck incrementally:** only the changed package while iterating. Run the full typecheck before reporting.
- **Run the adversarial self-check before reporting** (standard and full tiers). Check these bug classes where they apply:
  - parallel tool calls racing a gate (a read approving an edit already queued; state changing while an await runs)
  - polarity: a check that ignores `not`
  - agent-provided values of the wrong type reaching UI or checks (objects where strings are expected; prototype keys like `constructor`)
  - results that depend on storage order
  - stale state across turns, retries, Stop and unmount
  - a lock released before the last write lands, and save racing other writers
  - checks that reject a valid input on a common path

  Write a test for each one that applies, or state why it doesn't.
- **Start the orchestrator fresh per stage:** a long orchestrating session re-reads its own context every turn. At each stage close, write the handover into the ledger and continue in a fresh session.

Workers do not push by default. If an assigned preview environment requires a remote branch, explicitly authorize that worker to push only its named branch, or have the orchestrator push the reviewed candidate. Keep “deploy preview” and “do not push” consistent.

Review changed TypeScript/JavaScript for type and API issues. If none changed, the worker reports a concrete N/A. Inspect the touched implementation for avoidable complexity without widening scope. Use `/typescript-reviewer` and `/code-simplifier` for those passes when available; otherwise do them inline and report that the companions were unavailable.

Every worker report must contain:

- final SHA and tree SHA;
- base and merge base;
- changed files and user-visible behavior;
- exact checks and results;
- documentation result: paths inspected, updates made and validation results, or the concrete no-update reason or exact blocker from the documentation gate;
- deploy result and smoke evidence, or the exact blocker;
- `/typescript-reviewer` result;
- `/code-simplifier` result;
- learnings;
- false assumptions;
- failed attempts and why;
- new constraints/invariants;
- residual risks;
- resource packet: owned workspace/cache paths and sizes, running process/queue IDs, durable evidence paths, and what can be released versus what must survive;
- a concise knowledge packet for downstream workers.

Every claim in the report, including learnings, false assumptions, constraints and risks, is either observed with its source or marked unverified with the reason it couldn't be checked. A "likely" claim the worker could have checked with one more read is a reason to send the report back.

## Profile anything slow without being asked

Development speed is the orchestrator's job, not the user's. Notice when a step is slow, measure it, and fix it or report the fix. Don't wait to be asked.

Do this:
- **Set a budget for every long step when you start it, and write it in the plan.** Unless the project says otherwise:

  | Step | Budget |
  |---|---|
  | Checkpoint eval | 5 min |
  | Release gate | 15 min |
  | Snapshot or build | 3 min |
  | Cross-model review | 20 min |
  | Worker round | 45 min |

- **Measure as soon as a step runs over, or the user is waiting on it.** Use evidence, not guesses:
  - run timestamps and per-attempt durations
  - the concurrency settings actually used
  - workers' slowest tool calls, read from their transcripts

  Then fix the cause in the same stage, or report the cause, the fix and the expected saving with numbers.
- **Run independent work at full parallelism.** Eval cases and attempts, reviews and builds that share no state start as high as they can go. Step down only when throttling or errors are measured. Record the sweet spot as the default.
- **Start the longest step as soon as its inputs are final.** The release gate starts when the agent's code is final. Reviews, cross-model checks and changes outside that code run beside it, and a scorer or harness fix re-scores the stored runs offline.
- **Give each worker its budgets in the brief.** A worker blocked in its own poll loop is the smell: it should keep working while evals run, or report the wait.
- **Close every stage with a timing table:** wall clock per phase and the biggest time sink, plus what changes next time.

## Review loop

Run this loop for each vertical stage.

### 1. Worker gate

The worker implements the full slice, runs proportionate local checks, and reports the exact candidate. It may deploy only to the assigned development/preview environment when that is part of the brief. Review iterations do not each require a deployment; redeploy a preview only when runtime evidence is needed or the change affects deployment behavior.

### 2. Orchestrator adversarial review

This thread reviews the exact candidate in a separate clean worktree or clone. Review the complete diff from the pinned base and attack the promised user journey, not only the worker's chosen unit tests.

Look for:

- data loss, stale state, retries, reentrancy, cancellation, and idempotency;
- tenant/auth/privacy boundaries;
- deployment and configuration assumptions;
- upgrade, rollback, relaunch, offline, and failure recovery;
- platform-specific runtime behavior;
- gaps between “tests pass” and “the user promise works.”
- worker claims stated as fact or "likely" without a source. Check the ones the review relies on yourself before accepting them.
- the documentation gate result, including whether the actual diff requires updates the worker missed.

Prefer runnable repros or attack tests. Give one consolidated feedback packet with severity, evidence, affected files, and the invariant the fix must preserve.

### 3. Worker iteration

The same worker fixes the findings, reruns its tier's gates, including whichever of `/typescript-reviewer` and `/code-simplifier` the tier uses, and returns a new exact candidate plus knowledge delta.

Repeat orchestrator review and worker iteration until this thread is green. Do not create noisy review rounds for style nits. Material correctness, safety, maintainability, and deployability block green.

### Severity and stopping

Reviews stop at diminishing returns. Don't be pedantic, but don't let real bugs through.

- A blocker is only a concrete contradiction, data loss or duplication, a user journey or check that can't pass, or a security or privacy leak.
- Everything else is should-fix or nit: edge-case hardening, a gap a builder would settle while implementing, a rare case already routed to the user, or wording. Fix it in the same pass if it's trivial; otherwise log it in the repo's issue tracker. It never justifies another review round.
- Put this definition in every worker and verifier prompt.
- The orchestrator sorts every finding by substance before sending it to a worker. A verifier's BLOCKED label alone doesn't extend the loop. When a round's only blockers are edge cases already routed to the user, record the triage in the ledger, fix the trivial items, log the rest, and treat the stage as green. Tell the user plainly that this happened.
- When successive rounds keep finding narrower edge cases, that's the signal to stop. Say so and move on.

### 4. Independent cross-model verification

Run this gate on full-tier stages, and on standard-tier stages whose orchestrator review found a blocker. Only after orchestrator green, give the second-opinion verifier:

- exact base/head/tree;
- the full user promise and acceptance journey;
- complete diff, not only the latest fix;
- relevant ledger constraints;
- read-only instructions: no candidate edits, push, merge, or deploy.

The verifier performs a fresh whole-diff adversarial review, using the blocker definition in "Severity and stopping". If it finds a real blocker, return the finding to the worker, then rerun the orchestrator review and independent verification on the new exact head. Green does not carry across changed commits. The one exception is trivial triaged fixes applied after a triaged round: record their diff against the last verified head in the ledger instead of running another round.

## Merge gate

Merge only when every review the stage's tier requires is green on the same exact candidate. Green means no blockers left after triage, per "Severity and stopping". Trivial fixes made after that triage are covered by the ledger record.

Before merge:

- fetch the remote base again;
- verify PR head/base and file list;
- confirm no unreviewed commits or generated drift appeared;
- verify the documentation gate on the exact candidate;
- compute or fetch the merge result and verify its tree;
- rerun any check invalidated by a moved base or changed merge tree.

After merge, fetch remote `main` and record its SHA/tree. Do not claim the reviewed commit itself is on `main` after a squash merge; prove tree equivalence instead.

## Deploy-as-you-go gate

A feature is not finished when it builds, passes CI, is reviewed, or merges. It is finished only when the merged result deploys successfully and its release-defining user journey passes on the target. “Deploy after every increment” means once per merged vertical stage, plus additional preview deploys only when they produce useful evidence; it does not mean deploy every review commit.

For each stage:

1. Deploy from a clean checkout of the merged `main` SHA.
2. Verify the target identity before trusting the deploy command.
3. Record the last known-good deployment and the rollback or forward-fix path before changing the target.
4. Record deployment ID/version/build and the exact source SHA/tree.
5. Exercise the user-visible promise at the layer where users encounter it.
   - Web: browser journey, not only HTTP 200.
   - Native: Xcode build, install, launch, Simulator/device interaction, screenshot/AX evidence, and TestFlight when that is the release channel.
   - Backend: call through the consuming client or public contract, not only function registration.
6. Check the target's available crash/error/health signal for a risk-proportionate observation window. A smoke is necessary, not always sufficient.
7. Fix deployment/runtime failures before any dependent stage starts.
8. Run the workspace cleanup gate before starting a dependent stage or handing over. Carry explicit retained-resource entries forward when cleanup is blocked.

Do not retry the same unchanged infrastructure failure more than twice. Diagnose runner availability, billing, credentials, provisioning, target linkage, and platform constraints first.

If deployment needs external credentials or user action, report the smallest exact blocker. The stage remains integrated or review-green, never “done.”

## Status vocabulary

Use these terms precisely:

- **planned:** promise and dependencies mapped;
- **building:** worker owns a candidate;
- **reviewed:** orchestrator adversarial review green;
- **verified:** independent cross-model review green on the same head, or not required by the stage's tier (say which);
- **integrated:** exact reviewed tree is merged into remote `main`;
- **deployed:** merged tree is live/installable on the target;
- **done:** deployed, the release-defining user journey passes, and the documentation gate is satisfied;
- **blocked:** an exact external dependency prevents progress.

Do not compress these into a generic “green.”

## Orchestrator communication

- Lead with the current product outcome and stage status.
- Keep progress updates brief and evidence-based. Apply "Verify claims before reporting them" to every message to the user: check a relevant claim before stating it, rather than reporting it with "I haven't checked".
- Tell the user when a skill or external gate changes the course of work.
- Share one consolidated review packet per iteration.
- Surface external blockers early.
- Report how each stage advanced the usable product: “Previously …; now …”.
- Keep the roadmap and any human-readable plan artifact current when dependencies or acceptance change.
