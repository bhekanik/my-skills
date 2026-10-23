# Go pain-anchor starter table

The pains Go solves, indexed by which prior-language a learner felt them in. Use as the seed for `<output-repo>/docs/teaching/<lang>-anchor-table.md` when scaffolding a Go book; extend with the learner's specific stated pains.

## Per-feature pain table

| Go feature | Pain it solves | Where you've felt it |
|---|---|---|
| `error` as a return value | Java's checked exceptions force a try/catch ladder that nobody actually reads. JS lets exceptions fly invisibly. C uses `errno` plus `return -1` and hopes you check. Go puts the error in the return tuple — visible at every call site. | Java, JS, C |
| Goroutines | Java's thread+lock model is verbose and easy to get wrong. Node's single thread can't use multiple cores without worker pools. Goroutines are cheap (KB of stack), the runtime schedules them, you write sequential code that runs concurrently. | Java, Node, Python (GIL) |
| Channels for coordination | Locks-and-shared-memory race conditions; "did I forget to acquire the mutex?". Go: share by communicating, not by sharing memory. Channels make data flow explicit. | Java, C, C++ |
| `defer` | C's "did I free / close / unlock on every exit path?" Go runs `defer` at function exit regardless of how you got there. | C, C++ |
| `context.Context` | Java's "how do I cancel a long-running call?" — nothing standard. Node's AbortSignal came late and isn't pervasive. Go threads `Context` through every function that does I/O; cancellation and deadlines are first-class. | Java, Node |
| Single static binary | Python's "which Python? which venv? which pip-installed-where?" hellscape. Java's classpath. Node's `node_modules` shipping problem. Go: one statically-linked binary, ship it. | Python, Java, JS |
| Standard library completeness | npm's left-pad situation. Java's standard lib is large but ergonomically rough. Go's stdlib covers HTTP, JSON, crypto, encoding, testing, profiling — most production work needs zero third-party deps. | JS, Java |
| Interface satisfaction (structural / duck-typed) | Java's nominal interfaces force inheritance hierarchies you didn't want. C++'s template-based duck typing produces unreadable error messages. Go interfaces are satisfied implicitly by any type with the right methods. | Java, C# |
| `gofmt` enforced | "Whose tab style won this PR?" — Go ships with one true formatter and the entire community uses it. | Every other language |
| Build tags | C's `#ifdef` macros for cross-platform builds. Go's `//go:build linux` comments are cleaner and integrated into the build system. | C, C++ |
| Garbage collection (low-pause) | C's manual `malloc/free` — leaks and double-frees. Java's GC pauses (historically). Go's GC targets sub-millisecond pauses, traded against throughput. | C, Java |
| `select` statement | Concurrency primitives without a `select` (Java's wait/notify; pthread condvars) require error-prone coordination. Go's `select` waits on multiple channels in one statement. | C (epoll) |
| Race detector built in | "I think I have a race condition somewhere" — in C/Java/Node you bolt on tools or pray. Go ships `go run -race` in the toolchain. | C, Java |
| Vendored / module-versioned dependencies | npm's transitive dependency hell. Maven's "version conflict resolved by which strategy?" Go modules pin transitive versions, support replace/exclude, and the `go.sum` ensures reproducible builds. | JS, Java |
| Test files alongside source | "Where do my tests live?" Go convention: `foo_test.go` next to `foo.go`. Same package; tests can read internals. No discovery configuration. | Java, JS |
| `go fmt` / `go vet` / `go test` as compiler-adjacent | "Did I install the linter? Is it the right version? Does CI run it?" Go: all of these ship in the toolchain. | All script-toolchain languages |

## Anti-anchors (Go features without obvious pain anchors)

- **Generics** (added in 1.18). Older Go code rarely uses them, and stylistic conventions are still settling. Idiomatic Go often prefers interfaces or copy-paste over generics. Frame as "modern Go optionally has these, but the older style is still valid."
- **No sum types**. Go has no `Result<T, E>` or `Option<T>` equivalent at the language level — it has `(T, error)` tuples and the zero-value convention. Frame as a deliberate absence; learners coming from Rust or OCaml will miss this and need to internalise the Go idiom.
- **Embedded structs / promoted methods**. Anonymous-field embedding looks like inheritance but isn't. Confuses Java/C# learners. Worth explicit teaching when it shows up.
- **Channels are not the answer to everything**. Newer Go style uses mutexes and atomics for state-sharing; channels for *signalling*. The "use channels for everything" advice from early Go talks is now considered anti-pattern. Worth flagging when teaching concurrency.

## Voice for the chapter prose

When invoking a row from this table:

> **Pain anchor:** in C, [pain]. In Java, [other-language pain]. Go handles this by [feature], which makes [the bad thing] either visible or impossible.

Lead with the pain, follow with the solution. Don't lead with "here's a Go feature" and tack on "and by the way it solves a problem you may have felt." The order matters.
