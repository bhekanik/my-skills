# Skills I use with coding agents

I build a lot with agents. The best results come when the agent knows which decisions are settled, which claims need evidence, what a person will have to review, and when to stop and ask me something. These skills are instructions I've written for those moments. I've mostly used them on my own projects.

## The skills

- **[blueprint](skills/blueprint/SKILL.md)** turns a long design conversation into a set of documents another coding agent can build from, including the decisions, rejected ideas, open questions, release ladder, and the experience the product should create.
- **[orchestrate](skills/orchestrate/SKILL.md)** takes a substantial implementation after planning. It breaks the outcome into useful releases, gives bounded tasks to worker models, checks the result, and uses smaller PRs or a stack when that makes the change easier to review.
- **[archaeology](skills/archaeology/SKILL.md)** finds out why a piece of code or a process exists, checks whether that reason still holds, and maps what would break if it changed.
- **[one-by-one](skills/one-by-one/SKILL.md)** gathers the decisions an agent needs from you and asks for them one at a time, in plain language.

I use `blueprint` when a planning conversation has become too large to carry into implementation by memory. I use `orchestrate` when the work needs several passes or people to review a large change. `archaeology` is for the moment a dependency has no clear reason, and `one-by-one` is for when an agent has buried a question under status and options.

## Install

```sh
npx skills add bhekanik/my-skills
```

Choose the skills you want and the agent you use. To install just one, add `--skill blueprint`, `--skill orchestrate`, `--skill archaeology`, or `--skill one-by-one`. Add `-g` to install it globally instead of in the current project.

Each skill is a folder under [`skills/`](skills/), so you can inspect its instructions and any supporting files before using it.
