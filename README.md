# Skills I use with coding agents

I spend time talking through what I want to build with an agent: the problem, the experience, the architecture, and the tradeoffs. Once we've made the important decisions, I use [blueprint](skills/blueprint/SKILL.md) to turn that conversation into a comprehensive build plan. Other people might call it a spec; I call it a blueprint. It gives the next agent the decisions, open questions, implementation sequence, and intended experience in one place.

For substantial implementation, I use [orchestrate](skills/orchestrate/SKILL.md). It breaks the work into useful releases and bounded tasks, picks worker models according to cost and capability, checks their output, and keeps changes small enough to review. It can use a stack of PRs when that makes the solution easier to follow. I've mostly tested this workflow on my own projects, so I don't have a reliable measurement of its cost impact at work.

## When the agent needs a decision from me

Agents sometimes bury several questions in a wall of text. I use [one-by-one](skills/one-by-one/SKILL.md) to have the agent work out what it actually needs from me, then ask one question at a time with enough context to answer without hunting through the previous response.

## When I need to understand or explain the work

- [archaeology](skills/archaeology/SKILL.md) traces why code or a process exists, whether that reason still holds, and what depends on it.
- [review-system-changes](skills/review-system-changes/SKILL.md) maps a TypeScript or JavaScript change so I can follow its modules, calls, data flow, and diff during review.
- [teaching](skills/teaching/SKILL.md) makes a coding session an active lesson: predict what will happen, run it, examine the result, and explain it back.
- [bookgen](skills/bookgen/SKILL.md) builds a learning book around a real repository for a longer course of study. Install `teaching` alongside it; generated books include a snapshot of that skill.

## When the writing needs work

- [writing-docs](skills/writing-docs/SKILL.md) writes software documentation around what the reader needs to do and what verified result they should see.
- [humanizer](skills/humanizer/SKILL.md) edits prose to remove common AI writing patterns while preserving the facts and the author's voice. This is my adapted copy of [Siqi Chen's Humanizer](https://github.com/blader/humanizer), distributed under its [MIT license](skills/humanizer/LICENSE).

## Install

```sh
npx skills add bhekanik/my-skills
```

Choose the skills you want and the agent you use. Add `--skill <name>` to install just one, or `-g` to install globally. For `bookgen`, choose `teaching` too. Every skill's instructions and supporting files are under [`skills/`](skills/).
