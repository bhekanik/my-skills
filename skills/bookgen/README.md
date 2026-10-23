# Bookgen

`bookgen` makes a learning book around a real codebase and a language the learner wants to understand. The chapters ask for predictions, let the learner test them against running code, and build one concept at a time. The result is a project someone can work through across many sessions, with or without a live teaching agent.

Use it when the learner wants a sustained project. For a quick explanation or one lesson, use the [`teaching` skill](../teaching/SKILL.md) directly.

## What it needs

- A local repository or GitHub URL to study
- The target language and the learner's prior experience
- The learner's motivation and any examples they find compelling
- The sibling `teaching` skill, installed alongside `bookgen`

An optional `humanizer` skill can be supplied to the scaffold script. It is not required.

## What it creates

The scaffold includes a session plan, source map, dependency order, anchor table, chapter stubs, and the first completed chapter. It vendors a snapshot of `teaching` into the output repo so later sessions can use the same pedagogy. The bundled scripts can regenerate the concept index, detect drift in the anchor codebase, and export an mdBook site.

Invoke `/bookgen` with the repository and language. It will inspect the code, recommend whether to rebuild, tour, or extend it, then write the book with the learner's answers. The [`SKILL.md`](SKILL.md) holds the full workflow; [`references/workflow.md`](references/workflow.md) gives more detail.

## Optional parser dependencies

The Python scripts work with the standard library. Tree-sitter improves structural analysis for supported languages:

```sh
python3 -m pip install -r <bookgen-skill-dir>/scripts/requirements.txt
```

Without it, the scripts use a coarser regex parser. See [`docs/issues/0004-treesitter-nodeconfig-coverage.md`](docs/issues/0004-treesitter-nodeconfig-coverage.md) for current coverage.
