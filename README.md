# Skills I use with coding agents

I like doing the hard thinking with a strong model: deciding what to build, finding the right boundaries, and checking whether the result works. Once the plan is clear, I want agents to carry the implementation without turning it into one enormous diff or spending frontier-model tokens on every task.

This is where I share the skills I've built for that way of working. I mostly use them on my own projects. They're plain files you can inspect before using them.

## Start with `orchestrate`

[`orchestrate`](skills/orchestrate/SKILL.md) is for substantial work that needs more than one implementation pass. I invoke it after working through the plan in my main session. It coordinates the rest:

- Break the outcome into useful, deployable slices, then give workers bounded tasks.
- Start workers on cheaper, faster models when the task allows it. Raise reasoning effort and model tier only when the evidence shows the current choice is struggling.
- Keep changes small enough to review. When a slice still makes a large diff, use focused, stacked PRs with a clear reading order.
- Verify, review, and ship each increment, then carry what was learned into the next one.

It isn't a shortcut for a one-agent fix. The point is to keep the human in control of the plan and make the implementation easier to inspect.

## Install

```sh
npx skills add bhekanik/my-skills --skill orchestrate
```

Run the command in your project to install the skill there. Add `-g` if you want it available globally. Then invoke `/orchestrate` with your goal and the checks that would prove it works.

More skills can live alongside it in [`skills/`](skills/).
