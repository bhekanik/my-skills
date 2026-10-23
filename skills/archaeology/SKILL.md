---
name: archaeology
description: Recover the lost provenance of anything whose reason for existing nobody remembers (a service, a cross-repo pattern, a pipeline, a data flow, a team process, an abstraction, a flag, a workaround), test whether that reason still holds, and recommend keep, simplify, migrate or delete with the dependents mapped. Works across repos, systems and organisational history. Use for "why do we still do this", "why does this exist", "is this still needed", "can we get rid of X", legacy systems and compatibility layers, and anything with no remaining institutional knowledge.
---

# Archaeology

Things survive because understanding them used to be expensive. Nobody knew why
they existed, so nobody dared touch them. An agent can now traverse years of
history, tickets, docs, code across repos and runtime behaviour cheaply, so the
question "why do we still do this?" is finally worth asking. This skill recovers the
original rationale, checks it against today, and ends in a decision the user can act
on.

The subject can be anything that outlived its explanation: one line of config, a
function, a service, a pattern repeated across twenty repos, a queue, a data
pipeline, a deploy step, a scheduled job, a team process or approval. The output is
a verdict, not a history lesson.

Other skills call this one from a subagent when their task hits something whose
reason isn't clear. Called that way, answer only the question you were given,
return the verdict and evidence, and leave any removal to the caller.

For open-ended "how does X work" questions, use a general investigation workflow instead.

## 1. Pin the subject and its footprint

State exactly what is being excavated and find everywhere it lives. A service or
pattern usually spans repos, infrastructure, dashboards, runbooks and docs, so map
the footprint before digging:

- code search across the available repositories (for example, `gh search code`) for
  its names, identifiers, config keys, queue or topic names, env vars and URLs;
- service catalogs, ownership files (`CODEOWNERS`, catalog metadata), infrastructure
  and deploy config;
- where it shows up at runtime: metrics, logs, traces, alerts and dashboards, and
  for CI or scheduled work, run history.

Classify each hit as a **caller** of one shared thing, a **fork** that copied its
logic, or a mere **reference** (docs, comments). One shared job with ten callers and
ten diverged copies are different problems with different fixes.

Code search indexes only default branches and forgets deleted files, so absence from
search is weak evidence; confirm removals in history. Org-wide searches burn API
quota fast: check `gh api rate_limit` before a wide sweep, batch queries, and clone
a repo once instead of fetching many files from it.

Read code from fresh remote state: fetch, then read `origin/<default>` in disposable
clones under `/tmp/archaeology-clones/<repo>`, never the user's working trees.

Match the effort to the subject. A one-line config entry needs its introducing
commit, a check of whether anything still matches it, and a verdict. A service or an
organisation-wide pattern needs every step below and often parallel digging per repo
or per source; use subagents for that when the footprint is wide. Skip sources that
can't apply: a local config may have no tracking ticket.

## 2. Recover the origin

Find when and why it appeared, which is often earlier and elsewhere than where it
lives now. Stop when a primary source states the reason, or when every lead from the
oldest evidence has been read without one.

- **Git history:** `git log --follow`, `git log -S` / `-G` and `git blame -w -C -C`
  for the introducing commit, not the latest touch. Follow renames, moves, repo
  splits, monorepo merges and copies between repos: the first occurrence across the
  footprint is the origin, the rest are propagation.
- **Review:** the PR that introduced it and its discussion
  (`gh api repos/<o>/<r>/commits/<sha>/pulls`), which often holds the real reason.
- **Decisions:** RFCs, ADRs, design docs, incident and postmortem reports, issue-tracker epics
  and tickets, and team discussions where accessible. Incidents are a common
  origin for workarounds and guard rails.
- **People:** commit authors, PR reviewers and doc owners show who knew. Check whether
  they are still available to ask. When the evidence runs out, a named person
  to ask is a valid finding.
- **Tests:** tests added alongside it encode the case it was built for; a test named
  after a bug is a rationale in disguise.
- **Upstream:** if it works around a library, vendor, service or platform, find the
  bug, limitation or version it was avoiding.

Separate stated reasons from inferred ones. "Fix" with no context is not a
rationale; say the reason is unknown rather than inventing one.

## 3. Test whether the reason still holds

A rationale is a claim about the world at a point in time. Check it against the world
now:

- the upstream bug is fixed, the missing capability exists, and since which version;
- the client, customer, team, platform or regulation it served still exists;
- the constraint it guarded (load, ordering, compliance, cost, a rate limit, a
  failure mode from an incident) still applies, measured rather than assumed;
- the tests or checks that justified it still pass without it, where that can be
  tried safely in a disposable environment.

Prefer runtime evidence: whether the path still runs, how often and for whom (logs, metrics and traces). Traffic that stopped years ago is
strong evidence. Traffic from one unexpected caller is a finding.

## 4. Map what depends on it

Find every consumer across the footprint: callers and importers in every repo,
services calling its API, readers of its data, subscribers to its events, jobs and
pipelines, dashboards and alerts, runbooks and the teams whose process assumes it.
For declarative rules (ignore patterns, lint rules, routing, feature flags), the
dependents are whatever they match; check whether anything still matches and whether
another rule already covers the case.

For each dependent, name the owner and say whether it could migrate trivially, needs
work, or relies on something undocumented: an ordering guarantee, a side effect, a
default value, a swallowed error, a data shape. The undocumented dependencies are the
ones that break removals, so look for them deliberately.

## 5. Verdict

Lead with the answer, in this shape:

> This was introduced in `<date>` (`<commit, PR, ticket or RFC>`) because `<reason>`.
> `<What changed since>`. `<N>` dependents remain across `<repos or teams>`:
> `<which>` can migrate trivially, `<which>` relies on `<undocumented guarantee>`.
> **Recommendation:** keep | simplify | migrate then delete | delete, because `<why>`.

Then give the evidence behind each claim (commit SHAs, PR, ticket and doc links,
file-and-line references, runtime queries), marking each verified, inferred or
unknown. Name the people who could confirm what the evidence can't.

End with the concrete next step: the removal or migration plan in order with each
dependent's owner, or the reason it must stay, recorded where the next person will
look (a code comment, an ADR, or the owning team's docs) so nobody has to dig again.

## Boundaries

This skill investigates and recommends. Removing or changing the subject is separate
work the user asks for; offer a scoped follow-up. Anything outside the user's
own files, such as team pages, tickets or other teams' repos, gets a draft rather
than a write, and each write needs the user's say-so. When the rationale still holds
and was undocumented, offer to record it, since that is the cheapest way to stop the
next excavation.
