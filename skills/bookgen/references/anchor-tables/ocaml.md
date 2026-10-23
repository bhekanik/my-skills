# OCaml pain-anchor starter table

The pains OCaml solves, indexed by prior-language. Seed for `<output-repo>/docs/teaching/ocaml-anchor-table.md`.

## Per-feature pain table

| OCaml feature | Pain it solves | Where you've felt it |
|---|---|---|
| Algebraic data types | TypeScript's discriminated unions are verbose. Java has none — you fake them with sealed classes and visitor patterns. C only has tagged-enum-by-hand. OCaml's `type` declares sum + product types natively in one line. | TS, Java, C |
| Pattern matching with exhaustiveness checks | C's `switch` doesn't enforce exhaustiveness; JS's `switch` falls through. Java's switch on enums got slightly better in recent versions but not pattern-matchy. OCaml's `match` warns on non-exhaustive patterns at compile time. | C, JS, Java |
| Hindley-Milner type inference | TypeScript needs annotations everywhere or types collapse to `any`. Java's verbose generics (`Map<String, List<Pair<Foo, Bar>>>`). OCaml infers nearly everything; you only annotate when it's load-bearing or for documentation. | TS, Java |
| Immutable-by-default | JS's "is this mutated by the function I just called?" Java's defensive-copy discipline. OCaml: data is immutable by default; mutation requires explicit `mutable` keyword on record fields or use of `ref`. | JS, Java |
| Modules + signatures + functors | Java's package + interface hierarchies don't compose. Python's import-but-also-class-but-also-static-method confusion. OCaml's module system is the cleanest version of "code organised into named, parameterisable units." Functors are modules-as-functions: take a module, produce a module. | Java, Python |
| Tail-call optimisation | Recursive code in JS or Python blows the stack at depth. Java doesn't TCO. OCaml TCOs aggressively; recursion is the natural loop construct. | JS, Python, Java |
| `option` and `result` types | NULL deref, exception-throw-from-anywhere — same pains as Rust's `Option`/`Result`. OCaml had these decades earlier. | C, Java, JS |
| Polymorphic variants | "I want a sum type that doesn't need to be declared up front" — useful for ad-hoc tags shared across modules. No analog in most languages; closest is TypeScript's structural string-literal unions. | TS (sort of) |
| First-class modules | Pass a module as a value, return one from a function. Useful for plugin systems and dependency injection. No clean analog in mainstream languages. | (no analog) |
| Records with field punning | C's struct-with-explicit-`name = name` repetition. OCaml's `{ name; age; email }` shorthand when the field name matches the variable. | C, Java |
| `let ... in` flow | C's "I introduce a temp variable; here's its scope" — implicit. OCaml's `let x = ... in <expr>` makes the scope of `x` explicit and small. | C, Java |
| `;;` REPL terminators (utop / ocaml top-level) | Java's lack of REPL (until JShell). Python and JS REPLs are single-expression. OCaml's REPL with `;;` lets you write multi-line declarations interactively. | Java |
| Effect handlers (OCaml 5.0+) | Async-without-monads-everywhere. Algebraic effects let you write code that *looks* synchronous and the runtime handles the effect (async I/O, exceptions, generators). Cutting-edge concept; few prior-language analogs. | (cutting-edge) |
| GC with low-pause guarantees | Java's GC pauses (historically painful for low-latency code). OCaml's GC is incremental and tunable; Jane Street uses OCaml in production trading systems. | Java |
| Compilation to native code or bytecode | "Do I want fast or do I want portable?" Java picks bytecode + JIT. OCaml lets you choose: `ocamlopt` for native speed, `ocamlc` for bytecode portability. | Java |

## Anti-anchors (OCaml features without prior-language analogs)

- **The syntax itself**. Different from C-family. Significant whitespace isn't quite a thing but newlines matter for some constructs. The `;` vs `;;` distinction (statement separator vs REPL terminator) confuses beginners. No analog; pure-immersion teaching.
- **`let ... in ...` chains.** Multiple bindings nest. Looks awkward at first; lands as "this is just structured `let` plus a body" once you see it.
- **The two stdlib factions**. The OCaml standard library is small. Real production OCaml uses either Jane Street's Core or batteries-included alternatives. Mention this explicitly so learners don't expect Java-stdlib-completeness from `Stdlib`.
- **Variance markers in module signatures**. `+'a` (covariant), `-'a` (contravariant), `'_'a` (weak/unbound). Edge case but appears in practice. Cliff topic.

## Voice for the chapter prose

> **Pain anchor:** in JS, [pain — usually a "is this mutated?" or "what does this throw?" question]. OCaml's [feature] makes [the bad thing] either type-visible or impossible.

OCaml's pitch to most learners is "everything you think languages should have but don't." Frame around what's been *missing* in their prior languages.
