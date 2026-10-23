# Elixir pain-anchor starter table

The pains Elixir solves, indexed by prior-language. Seed for `<output-repo>/docs/teaching/elixir-anchor-table.md`.

## Per-feature pain table

| Elixir feature | Pain it solves | Where you've felt it |
|---|---|---|
| Pattern matching everywhere | JS destructuring is shallow; Java has nothing comparable; Python's pattern matching arrived in 3.10 and is rare in production. Elixir matches on argument shapes, return shapes, message contents — pattern matching is the language's primary control structure. | JS, Java, Python |
| Pipe operator (`\|>`) | Java's nested function calls read inside-out. JS the same. Python's `f(g(h(x)))` chain with no built-in pipe. Elixir's `\|>` linearises the data flow: `data \|> f \|> g \|> h`. | Java, JS, Python |
| Immutability everywhere | JS's "is this mutated?" — every function call is a question. Java's defensive-copy discipline. Elixir: data is fully immutable; transformation is the only model. No reference-vs-value confusion possible. | JS, Java |
| Actor model (GenServer) | Java's thread + lock + synchronized boilerplate. Python's GIL and multiprocess fork overhead. Node's single-thread main loop. Elixir's GenServer gives each actor its own mailbox; messaging is the only IPC. | Java, Python, Node |
| Supervision trees | "What happens when this service crashes?" — usually nothing automatic. Manual restart logic everywhere. Elixir's OTP supervisor restarts crashed processes per a declared strategy (one-for-one, one-for-all, etc.). The "let it crash" philosophy. | Java, Python, Node |
| Hot code reloading | Restart-the-process culture in Java/Node/Python. Elixir replaces modules in a running BEAM virtual machine. Production systems update without dropping connections. | Java, Node |
| `with` for happy-path chaining | Java's nested try-catch. JS's `if (!result) return null` ladder. Go's `if err != nil { return ... }` repetition. Elixir's `with` chains pattern matches; the first non-match becomes the result. Linear happy path. | Java, JS, Go |
| Macros (hygienic, syntactic) | C's preprocessor is textual substitution. Lisp's macros are unhygienic. Elixir's macros operate on the AST and respect variable scope by default. Most of the language's DSL ecosystem (Phoenix routes, Ecto schemas) is built on macros. | Lisp, C |
| Pattern matching in function heads | "How do I dispatch by argument shape?" — overload resolution in Java/C++ is type-based; runtime checks elsewhere. Elixir defines multiple clauses of the same function, dispatched by pattern. Cleaner than instanceof chains. | Java |
| Protocols (`defprotocol`) | "Open class hierarchy" — Java/C# closed classes vs Ruby/Python's monkey-patching. Elixir protocols let you implement an interface for a type you don't own. Rust traits with the orphan rule are a closer analog. | (Rust traits closest) |
| Phoenix LiveView | "I need realtime UI without writing both backend and frontend" — historically requires React + WebSocket + state-sync. LiveView keeps the state on the server, diffs HTML, sends patches. Single language end-to-end. | React+Node, Vue+Rails |
| Ecto for queries | Active Record's "what SQL did this generate?" mystery. Java JPA's annotations everywhere. Ecto's queries are explicit, composable, type-checked at compile time. | ActiveRecord, JPA |
| Guards (`when`) on function clauses | "I want this clause only when the argument is a positive integer" — Java needs an `if`-statement at the top of the function. Elixir lets you express it in the function head. | Java |
| Behaviours | "I want a contract that implementers must satisfy" — Java interfaces, Rust traits. Elixir behaviours declare callback signatures; modules implement them with `@behaviour`. | Java, Rust |
| Dialyzer (gradual typing) | "I want type checking on a dynamic language" — TypeScript layers types on JS. Dialyzer infers and checks types on Elixir/Erlang code without requiring annotations everywhere. | TS, Python (mypy) |

## Anti-anchors (Elixir features without prior-language analogs)

- **The BEAM execution model**. Preemptive scheduler, lightweight processes (not OS threads), per-process heaps, copying message passes, distributed-by-default cluster. None of this maps cleanly to Java/Node/Python's runtime. Cliff topic — spend extra time.
- **Erlang interop and the Erlang lineage**. Elixir runs on the BEAM; Erlang's stdlib is reachable via `:erlang.X` syntax. Worth flagging early so learners know the deeper ecosystem is there.
- **Process linking and monitors**. The fault-tolerance model relies on `link` and `monitor` calls forming process supervision graphs. Subtle; takes worked examples to internalise.
- **Hot reloading semantics**. State migration during code reload, version vectors on modules. Edge case for most learners but central to long-running OTP applications. Defer until the learner has a concrete use case.

## Voice for the chapter prose

> **Pain anchor:** in [Java/Node/etc.], [pain — usually a concurrency / fault-tolerance / state-mutation pain]. Elixir handles this by [feature], which makes [the brittle thing] structural rather than disciplined.

Elixir's pitch is "concurrency and fault tolerance that you don't have to remember to do." Frame around what discipline the prior language *required* and Elixir *replaces with structure*.
