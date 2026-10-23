# Skills I use with coding agents

I build and learn with coding agents. These skills capture the parts of that work that are easy to lose between sessions: decisions, evidence, a human review path, and a way to keep learning while agents write code. I've mostly used them on my own projects.

## The skills

- [blueprint](skills/blueprint/SKILL.md) turns a design conversation into documents another coding agent can build from, including decisions, open questions, a release ladder, and the intended experience.
- [orchestrate](skills/orchestrate/SKILL.md) coordinates substantial implementation in useful releases, routes bounded tasks to worker models, and keeps changes reviewable through focused PRs or a stack.
- [archaeology](skills/archaeology/SKILL.md) finds why code or a process exists, checks whether that reason still holds, and maps what depends on it.
- [review-system-changes](skills/review-system-changes/SKILL.md) makes an interactive map of a TypeScript or JavaScript change so a reviewer can follow modules, calls, data flow, and the diff.
- [writing-docs](skills/writing-docs/SKILL.md) writes software documentation around what readers need to do and what verified output they should see.
- [teaching](skills/teaching/SKILL.md) turns a coding session into a lesson: predict, run, examine the result, and explain the concept back.
- [bookgen](skills/bookgen/SKILL.md) builds a multi-session learning book around a real repository. Install `teaching` alongside it; the generated book vendors a snapshot of that skill.
- [one-by-one](skills/one-by-one/SKILL.md) gathers the decisions an agent needs from you and asks for them one at a time in plain language.

## Install

```sh
npx skills add bhekanik/my-skills
```

Choose the skills you want and the agent you use. To install just one, add `--skill <name>`. Add `-g` to install it globally instead of in the current project. For `bookgen`, choose `teaching` too.

Each skill lives under [`skills/`](skills/), where you can read its instructions and supporting files before using it.
