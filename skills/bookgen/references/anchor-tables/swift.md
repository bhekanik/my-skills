# Swift pain-anchor starter table

The pains Swift solves, indexed by prior-language. Seed for `<output-repo>/docs/teaching/swift-anchor-table.md`.

## Per-feature pain table

| Swift feature | Pain it solves | Where you've felt it |
|---|---|---|
| Optionals (`T?`) | Obj-C's `nil` pointer messaging silently no-ops. C's NULL deref crashes. Java's NPE. JS's "undefined is not a function". Swift's `T?` makes maybe-absent part of the type; you can't use a `T` until you've handled the `nil` branch. | Obj-C, C, Java, JS |
| Value types (`struct`/`enum`) | Obj-C's reference-everywhere model means every mutation is a hidden side effect. Java's pass-by-value-of-reference confuses. Swift makes copy-vs-share an explicit type-level decision (struct = copy; class = reference). | Obj-C, Java |
| Protocols with default implementations | Obj-C protocols are pure interfaces — no default behaviour. Java pre-8 same. Swift protocols can carry default impls and conditional conformance, removing most of the inheritance-hierarchy boilerplate. | Obj-C, Java |
| Protocol-oriented programming | Java's deep inheritance trees become brittle. Obj-C's category system is loose and global. Swift composes behaviour through protocols + extensions — small interfaces, mixed and matched. | Obj-C, Java |
| `guard` / early-return clarity | Pyramid-of-doom nested `if`s ruin readability. Swift's `guard` flattens the happy path by demanding that the unhappy branch leave the scope. | All curly-brace languages |
| Strong type inference | Java's verbose generics (`Map<String, List<Pair<Foo, Bar>>>`). C#'s `var` is opt-in. Swift infers most types at function boundaries; explicit annotation only where it adds clarity or load-bearing constraints. | Java, C# |
| Automatic Reference Counting (ARC) | Obj-C's manual `retain/release/autorelease` (MRR) was a constant footgun. ARC inserts retain/release at compile time. Closer to Rust's deterministic destruction than to Java's GC. | Obj-C |
| Async/await (Swift 5.5+) | Obj-C/iOS's GCD with completion blocks turns deeply-nested logic into Christmas-tree closures. Swift's async/await flattens it. | Obj-C, JS pre-await |
| Actors (Swift 5.5+) and isolation | "Is this object thread-safe?" — Java relies on discipline + synchronized; Obj-C/iOS uses serial dispatch queues by hand. Swift's `actor` keyword guarantees mutually exclusive access at the type level. | Obj-C, Java |
| `Result<Success, Failure>` | Same NULL/exception pains the previous rows describe. `Result` is the typed, exhaustive alternative for sync error handling. | Obj-C, Java |
| Throwing functions + typed errors (Swift 6) | Pre-Swift-6: throws are untyped — caller can't know what to expect. Swift 6 typed throws make the error type visible, eliminating the "what does this throw?" guess. | Obj-C, Java |
| Result builders / DSLs | Building UI/HTML/SQL DSLs by hand is repetitive. Swift's `@resultBuilder` powers SwiftUI and similar DSLs without macros. JSX is the closest analog from JS-land. | (no clean analog) |
| Property wrappers (`@State`, `@Binding`, etc.) | "I want this property to behave specially (publish, persist, observe) without the call sites knowing." Property wrappers do this declaratively. | (no clean analog) |
| KeyPath / keypath member lookup | Obj-C `[obj valueForKeyPath:]` was untyped string-based reflection. Swift KeyPaths are statically typed and refactor-safe. | Obj-C |
| Copy-on-write collections | "Did this `Array` actually copy when I passed it?" Swift's stdlib types use COW so mutation is cheap when the only owner mutates. | C++ (manual COW) |
| Modules + access control (`public`/`internal`/`private`/`fileprivate`) | C's header dance; Java's package-private confusion. Swift's access control is per-declaration with sensible default. | C, Java |

## Anti-anchors (Swift features without prior-language analogs)

- **Existential types and `any P` vs `some P`**. The `any`/`some` distinction (introduced gradually across Swift 5.6–5.9) has no clean analog. Frame as "two ways to use a protocol as a type — `any P` is dynamic dispatch; `some P` is monomorphised. Use `some` unless you specifically need heterogeneous collections."
- **Actor isolation in Swift 6 strict mode**. Cross-actor calls require `await`; non-Sendable values can't cross actor boundaries. No analog in any common language. Cliff topic — spend extra time.
- **Macros (Swift 5.9+)**. Compile-time code generation that's syntactic, not textual. Closest analog is Rust's procedural macros; many Swift learners haven't seen those either.
- **`@MainActor` and main-thread enforcement**. iOS/macOS culture has always had "must be on main thread for UI" but it was discipline-based. Swift 6 makes it a compile-time check.

## Voice for the chapter prose

> **Pain anchor:** in Obj-C, [pain]. Swift handles this by [feature], which makes [the bad thing] either type-visible or impossible.

For learners coming from non-Apple-platform languages (Java, JS, etc.), substitute the relevant prior-language pain. The Obj-C anchor is most resonant for learners with iOS history.
