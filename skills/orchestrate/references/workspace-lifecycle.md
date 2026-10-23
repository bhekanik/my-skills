# Workspace lifecycle

Treat a workspace as a leased resource: keep it while its worker needs it, release it when its stage closes, and account for it when work stops unexpectedly. Separate durable source and evidence from rebuildable output so a finished run does not leave hundreds of gigabytes behind.

## Register resources before creating them

In the existing run ledger, maintain one resource table with these fields:

| Field | Record |
|---|---|
| Identity | Exact canonical path, repository/common Git directory, branch, base/head SHA, and resource kind |
| Ownership | Run/stage/worker that created it; owned process IDs, ports, and build-queue job IDs when applicable |
| Storage | Measured size, run-wide/per-resource budget, and build/cache paths, including any target outside the worktree |
| Retention | Release condition, durable evidence destination, and next cleanup action if retained |
| Authorization | User approval covering these exact run-created paths and their routine cleanup, or `pending` |
| Disposition | `active`, `eligible`, `removed`, or `retained` with the reason and last check |

Obtain one scope-bound cleanup approval for the run's declared disposable resources. If it is missing, request it before deletion; an implementation request alone is not blanket deletion authority. Approval for this run does not cover inherited worktrees, user data, shared caches, branch deletion, or other runs. On resume, reconcile the existing table before allocating replacements. Unexpected or unowned resources remain untouched.

Create durable workspaces under the code directory, separate from generated output. Keep source checkouts, ledgers, and evidence out of `target`, `DerivedData`, `.turbo`, dependency stores, and other cache directories: a cache may later need deletion without taking source or evidence with it. Use throwaway `/tmp` clones only for restart-disposable read-only work.

## Bound storage while work is active

- Set a run-wide generated-data budget before the first build; default to **100 GiB** unless a different budget is agreed and recorded. Include workers, review clones, eval copies, dependency installs, and run-local caches. Check sizes and free disk space at stage boundaries and when a path exceeds its allocation. Retire eligible owned resources or ask before increasing the budget; do not silently allocate another build directory.
- Use one build target/cache directory per active worker worktree. Keep it separate from other workers' mutable targets, reuse it through retries, and use shared `sccache` rather than multiplying targets for each command, review round, or model escalation.
- Reuse a review checkout or eval snapshot only after its prior processes finish and its state is verified. Allocate another only when concurrent isolation actually requires it, then register its owner and release condition.
- Keep only the workspaces the current stage and its real dependencies need. A merged stage's old workers are not a standing pool of future worktrees. After preserving the knowledge packet, release them before allocating the next stage's workers.
- Measure Turbo caches, native DerivedData, Rust targets, and dependency installs as well as Git checkouts. Shared global caches, simulator runtimes, VMs, and unrelated application data are outside routine run cleanup.

## Close out on success, pause, failure, cancellation, and handover

1. Reconcile the resource table with the filesystem and the repository's worktree registry. Account for every owned path, including partial attempts, review clones, eval snapshots, and external target directories. Record already-absent paths rather than recreating them.
2. Preserve the final source SHA, review/deploy facts, compact knowledge packet, and evidence cited by durable records outside disposable workspaces. Keep required release artifacts and rollback material. Generated output and durable evidence are different retention classes even when an earlier run mixed them in one directory.
3. Inspect active processes, current working directories, open files, and queued/running build jobs. Await or stop only this run's recorded processes; cancel only its owned queue jobs through the queue's cancellation command. Do not kill other sessions' processes. Move attached sessions and the coordinator out of a worktree before removing it. If ownership or idleness cannot be established, retain the resource with a blocker.
4. Recheck authorization and the exact canonical path immediately before each deletion. Reject unexpected paths, symlinks, shared stores, nested source worktrees, and Git common directories used by other checkouts. A broad parent folder, cache label, `CACHEDIR.TAG`, or old creation time is not proof that all its contents are disposable.
5. For **generated-data cleanup**, verify the exact subtree is rebuildable and has no tracked source, nested checkout, evidence, credentials, local database, user attachment, or active/queued consumer. Inspect nonstandard entries before deleting a whole target/cache directory. When evidence and compiler output are mixed, preserve the evidence and remove only verified generated subdirectories. Preserve unfinished source even when its caches can be released.
6. For **whole-worktree removal**, recheck tracked changes, staged changes, untracked files, and ignored files; `git status --porcelain` alone misses ignored `.env`, databases, backups, and evidence. Classify ignored entries individually: exclude only verified generated paths from the preservation check. Fetch relevant refs and prove the current HEAD is reachable from a currently advertised remote ref; a stale local `origin/*` ref is insufficient. Preserve unpushed/detached-only commits, dirty files, unknown ignored data, locked worktrees, active dependencies, and repositories that hold another worktree's common Git directory. A squashed merge alone does not prove that a local candidate SHA was saved; if proof is unavailable, retain it and report why.
7. Remove only approved, eligible paths. Use `git worktree remove <exact-path>` or the host's worktree-removal API for linked worktrees, without force. Preserve branches. If normal removal refuses, record the blocker and retain the path; do not follow with recursive deletion or broad prune/reset commands. A standalone clone needs the same checks plus confirmation that no other checkout depends on its Git objects.
8. Verify the approved paths are absent and remaining source worktrees/branches are intact. Measure free disk space before and after cleanup; report the observed delta separately from folder-size estimates, since APFS sharing and concurrent work can make them differ. Record failures or recreated paths rather than claiming cleanup succeeded.

## Retained resources stay visible

At each stage close or interruption, report cleanup separately from product status:

```text
Removed: exact owned paths and observed free-space change.
Retained: path | measured size | owner | preservation reason | next action/release condition.
Cleanup: complete, or pending with the exact blocker/approval needed.
```

Keep the compact ledger and required evidence, not every raw build tree. Carry retained-resource rows into the next stage or session, including when the run is blocked or abandoned. A handover is not a release condition for unfinished work, and a successful deployment is not permission to delete someone else's checkout.
