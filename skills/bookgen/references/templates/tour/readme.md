# Tour-mode book README template

For tour-mode books. The reproduce-mode counterpart lives at `references/templates/reproduce/readme.md`; this file documents the tour-mode-specific differences. Most of the README structure is identical — what changes is the framing of "what is this book" and the TOC column structure.

## Title and intro paragraph

Reproduce-mode books open with: "A book that teaches you {{LANGUAGE}} while you build {{PROJECT}}."

Tour-mode books open with: "A book that takes you on a {{N}}-chapter tour of {{PROJECT}} — {{ONE_LINE_DESCRIPTION_OF_PROJECT}} — for the purpose of *deeply* learning {{LANGUAGE}} by reading a real {{LANGUAGE}} codebase with structured pedagogy."

The framing emphasis: **reading**, not building. The book is a syllabus; the codebase is the textbook.

## "Two ways to read this book"

Identical to reproduce mode (Solo / LLM-as-teacher), with one phrasing tweak. Reproduce mode says "Skip the predicts and this is just a tutorial. Do them and it's a teaching book." Tour mode says "Skip the predicts and this is just a code-walking exercise. Do them and it's a learning book."

Same idea, different vocabulary fits.

## "Who this is for"

Reproduce-mode books target learners building from zero. Tour-mode books target learners who want **deep understanding of an existing system** — that's a different audience and worth naming.

For tour-your-own-code books (variant A from `chapter-01-template.md`), the audience description is specifically the version-of-you-who-wrote-it.

For tour-someone-else's-code books (variant B), the audience is users/admirers/contributors of the anchor project.

The README should make the variant clear in the first sentence of "Who this is for."

## "What {{PROJECT}} is"

Identical structure to reproduce mode (2–3 sentences describing the project, link to canonical project docs). The text is the same; this section doesn't depend on mode.

## TOC column structure — the visible difference

Reproduce-mode TOCs have these columns:

| Ch. | Title | Concept | Artifact |

Tour-mode TOCs have:

| Ch. | Title | One-line goal |

The "Concept" and "Artifact" columns merge into a single "One-line goal" because in tour mode the artifact *is* the concept (a paragraph-shaped understanding) and they'd be redundant.

Example tour-mode TOC row:

```markdown
| 11 | [SQLite as source of truth](11-sqlite-as-source-of-truth.md) | sqlx compile-time checked queries; the .sqlx cache; schema migrations |
```

Compare to reproduce-mode equivalent:

```markdown
| 11 | [Set up storage](11-storage-setup.md) | Schema design, sqlx migrations | `cargo sqlx migrate run` produces the schema |
```

## "How to read it"

Reproduce mode: "Type the code yourself. Don't paste. The compiler conversation is the curriculum."
Tour mode: "Don't skim. You're touring code that exists; the instinct to skim is strong. Predict-before-read is the antidote."

The instructions list otherwise matches.

## "Prerequisites"

Tour mode adds one prerequisite: the anchor codebase must be cloned or accessible. For "tour your own code" books, this is the learner's own repo. For "tour someone else's code" books, instructions for cloning go here.

## "Companion artifacts"

Same as reproduce mode (`docs/teaching/notes/`, `sessions.md`, anchor table, build-philosophy). The build-philosophy file linked here is the *tour-mode* variant (`docs/teaching/build-philosophy.md`, generated from `references/templates/tour/build-philosophy.md`).

## See also

The "See also" section ends with a pointer to the anchor codebase as **the textbook**:

```markdown
- {{ANCHOR_REPO}} — the textbook
```

This single line is the most important framing in the entire README. The book is the syllabus; the anchor codebase is the textbook. Tour mode is reading the textbook with the syllabus as your guide.

## See also (this template)

- `chapter-template.md` — tour-mode chapter shape
- `chapter-01-template.md` — first-chapter sub-variants (own-code vs someone-else's)
- `build-philosophy.md` — the artifact-as-paragraph contract
- `references/templates/reproduce/readme.md` — the reproduce-mode counterpart
