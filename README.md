# Skills I use with coding agents

I've mostly used these on my own projects.

## The skills

- [blueprint](skills/blueprint/SKILL.md) writes a detailed build plan after I've talked through what I want to build and its architecture with an agent. Other people might call this a spec; I call it a blueprint.
- [orchestrate](skills/orchestrate/SKILL.md) breaks substantial implementation into smaller tasks and reviewable PRs, then routes each task to the cheapest model that can handle it. It checks the brief and task split before raising reasoning effort or switching models.
- [one-by-one](skills/one-by-one/SKILL.md) pulls questions out of an agent's wall of text and asks them one at a time, with enough context for me to answer each one.
- [archaeology](skills/archaeology/SKILL.md) finds why code or a process exists, checks whether that reason still holds, and maps what depends on it.
- [review-system-changes](skills/review-system-changes/SKILL.md) makes an interactive map of a TypeScript or JavaScript change so I can follow modules, calls, data flow, and the diff.
- [writing-docs](skills/writing-docs/SKILL.md) writes software documentation around what readers need to do and what verified result they should see.
- [teaching](skills/teaching/SKILL.md) turns a coding session into a lesson: predict, run, examine the result, and explain it back.
- [bookgen](skills/bookgen/SKILL.md) builds a learning book around a real repository. Install `teaching` alongside it; the generated book includes a snapshot of that skill.
- [humanizer](skills/humanizer/SKILL.md) removes common AI writing patterns without changing the facts or flattening the author's voice. This is my adapted copy of [Siqi Chen's Humanizer](https://github.com/blader/humanizer), under its [MIT license](skills/humanizer/LICENSE).

## Install

```sh
npx skills add bhekanik/my-skills
```

Choose the skills you want and the agent you use. To install just one, add `--skill <name>`. Add `-g` to install it globally. For `bookgen`, choose `teaching` too.

Each skill lives under [`skills/`](skills/), where you can read its instructions and supporting files before using it.
