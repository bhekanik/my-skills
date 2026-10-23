# Zig pain-anchor starter table

The pains Zig solves, indexed by prior-language. Seed for `<output-repo>/docs/teaching/zig-anchor-table.md`.

## Per-feature pain table

| Zig feature | Pain it solves | Where you've felt it |
|---|---|---|
| Explicit allocators everywhere | C's hidden default allocator (libc malloc, sometimes); over- and under-allocation invisible at call sites. Rust's global allocator is similarly hidden. Zig: every function that allocates takes an `Allocator` parameter. You see allocation in the API. | C, Rust |
| `comptime` | C's `#define` macros are textual substitution with no type checking. C++ templates are turing-complete but unreadable. Rust's macros work on token trees and require a separate language. Zig's `comptime` is *just Zig running at compile time*, with full type information. | C, C++, Rust |
| Error union types (`!T`) | Java's checked exceptions; C's errno; Go's `(T, error)` tuple. Zig: errors are values; the `!T` shorthand and `try` operator make propagation natural. Errors form a global enum that you compose, not a class hierarchy. | Java, C, Go |
| No hidden control flow | C++'s exceptions, RAII, virtual calls, and operator overloading all do work that doesn't appear in the source. Zig: no exceptions, no destructors, no overloading. You read code and it does what it says. | C++ |
| `defer` and `errdefer` | C's "did I clean up on every exit path?" Zig has unconditional `defer` (always runs) and `errdefer` (runs only on the error path). | C, C++ |
| Cross-compilation built in | Cross-compiling C/C++ via clang is configuration hell — sysroots, triples, libc choice. Rust supports it but requires `cargo install` of target packages. Zig ships with first-class cross-compilation targeting almost anything that can run a binary. | C, C++, Rust |
| `unreachable` and panic discipline | C's `assert` is runtime-only and disablable in release builds. Zig's `unreachable` is both an optimisation hint (compiler trusts it) and a safety check in safe build modes. | C |
| The build system (`zig build`) | Make, CMake, autotools, Bazel — pick your favourite C/C++ build poison. Zig ships with `zig build` using `build.zig` written in Zig itself. One tool. | C, C++ |
| Packed structs with bit-level layout | C's bitfield rules are implementation-defined; you can't rely on layout. Zig's packed structs let you specify layout exactly. Useful for protocols, hardware registers, file formats. | C |
| `usingnamespace` and the module system | C's header dance; C++'s namespaces with confusing visibility rules. Zig's modules are files; symbols imported with `@import` are first-class values; `usingnamespace` is the tool for re-exporting. | C, C++ |
| Slices as first-class types (`[]T`) | C's `T*` plus length passed separately and trusting the caller. Rust slices are similar but tied into the borrow checker. Zig's `[]T` is pointer + length together, no overhead. | C |
| Optionals (`?T`) and `orelse` | C's NULL + hope-you-checked. Same pain as in every C-like language. Zig's `?T` makes maybe-null part of the type; `orelse` provides defaults inline. | C, Java, JS |
| Tagged unions with exhaustive switch | C's `union` + tag is manual and error-prone. Zig's tagged unions are first-class with compiler-checked exhaustive `switch`. | C |
| `inline for` and `inline while` | Loop-unrolling-at-compile-time in C requires macros or template metaprogramming. Zig's `inline for` happens at comptime and the loop body sees concrete types per iteration. | C, C++ |
| Asynchronous frame-based concurrency (older Zig) | Note: pre-0.11 Zig had `async` / `await` based on stackless coroutines and frame allocation. Removed in 0.11+, status currently in flux. Watch the language announcements. | (changing) |

## Anti-anchors (Zig features without prior-language analogs)

- **The lack of GC and the lack of metaprogramming-via-macros**. These are deliberate absences. Frame them as "what Zig chose not to have, and why."
- **Explicit allocator passing** in *every* function that allocates. Even Rust hides this at the global level. Zig's discipline takes some adjustment for learners coming from any GC'd language.
- **`@import` semantics**. Files are values; `const x = @import("foo.zig")` returns the file's namespace. Different from C's `#include` (textual) and from Rust's `use` (path-based). No clean analog.
- **The current state of Zig itself**. Pre-1.0 language. Breaking changes between minor versions. Mention this explicitly to learners; they should pin to a specific Zig version when starting.

## Voice for the chapter prose

> **Pain anchor:** in C, [pain]. Zig handles this by [feature], which makes [the implicit/hidden/unsafe thing] explicit or impossible.

The "explicit" framing matters for Zig specifically. Most of Zig's value over C is making invisible-but-painful things visible.
