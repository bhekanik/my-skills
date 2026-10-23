---
name: blueprint
description: Turn a product-design conversation into a numbered docs/blueprint/ set that a coding agent can build from without seeing the chat, including decisions, rejected options, a release ladder, and a design concept for how the product should feel.
argument-hint: "[target repo path] [conversation reference]"
disable-model-invocation: true
---

# Blueprint

Write a numbered `docs/blueprint/` set for a coding agent that did not see the planning conversation. Carry forward what the product should do and feel like, the decisions and their reasons, rejected options, open questions, and a sequence of usable releases. Read [`references/format.md`](references/format.md) before choosing the file set.

The conversation is the source for decisions. Do not turn an unmade decision into an apparent fact. When a document needs to proceed, state the assumption and add it to open questions for the user to confirm.

A behavioural specification alone can yield a working but incoherent interface. For a product people use, define a design concept, the whole-product mental model, and the feel of important moments. If the conversation did not settle that concept, propose one explicitly as an assumption.

## Steps

1. **Recover the source.** Read the full available conversation, including earlier turns when a summary omitted decisions or reversals. If the user names an external conversation and an export is available, read it. If part of the source is inaccessible, say what is missing and do not invent its decisions.

2. **Build a ledger.** In a scratch file, record each decision and who made it; rejected options and reversals; stated principles, constraints and non-goals; facts and their sources; reusable work in other repositories; unanswered product questions and testable spikes; and what the user said about the product's audience, role, look and feel. Preserve a user's words verbatim only when quoting them accurately. Every substantive turn should map to an entry or be marked as chatter.

3. **Choose the target and outline.** Use the supplied repository path, or the current app repository when unambiguous. For an existing blueprint, extend it rather than replacing its decision history. For a feature in an existing app, use `docs/<feature>/blueprint/`. For a new app without a repository, ask where it should live before creating files. Outline the fixed head, one document per hard domain, and the fixed tail described in the format reference. Assign each ledger entry to a document.

4. **Find the design concept.** For a human-facing product, answer: what is this to the person using it; why do they open it; what is the primary object or action; how do the screens and other surfaces form one product; and how should first use, the core action, success, failure and waiting feel? Name what stays out of sight so the experience has a hierarchy. Ground the concept in the user's words and taste references. Mark any proposed part as an assumption. For a product without a human-facing surface, state why a design concept is unnecessary.

5. **Verify facts and pin reuse.** Check consequential factual claims against primary sources. Turn unresolved claims into spikes. For reused code, fetch its repository and record the current remote SHA, relevant paths, and what may be copied or adapted. Keep useful research in `docs/research/` and link it from the blueprint.

6. **Write from the ledger.** Start with the decision log and open questions, then the overview, architecture and domain documents, then the roadmap, README and kickoff prompt. Cite decision IDs where they support a rule. Describe how each user-facing surface should feel beside what it does. Use the repository's writing and commit conventions. A decision gap becomes a named assumption in the documents and an open question.

7. **Check the result.** Run `python3 -I <this skill>/scripts/check_blueprint.py <blueprint dir>`. Fix broken links, undefined decision IDs and missing index entries; examine warnings for uncited spike or question definitions. Compare the blueprint against the ledger entry by entry. Walk each main journey across documents and check that names, states and handoffs agree. For each user-facing surface, check that a builder could make the intended experience, not merely the specified controls.

8. **Hand over.** Report the blueprint location and file list, the design concept and whether it was agreed or assumed, the number of recorded decisions, open product questions, and all assumptions that affect the first release. Follow the user's or repository's commit policy.
