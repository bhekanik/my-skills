# SwiftUI pain-anchor starter table

For books anchored against an iOS/macOS/watchOS app written in **SwiftUI**. Extends the generic `swift.md` table with SwiftUI-specific concepts that vanilla Swift books wouldn't need. If the anchor repo is mostly SwiftUI views and view models, use this table; if it's a Swift-on-the-server or command-line Swift project, use `swift.md` instead.

The Swift-language-level rows below are inherited verbatim from `swift.md`. The SwiftUI-specific rows are below them.

## Per-feature pain table — Swift language layer (inherited)

| Swift feature | Pain it solves | Where you've felt it |
|---|---|---|
| Optionals (`T?`) | Obj-C's `nil` pointer messaging silently no-ops. C's NULL deref crashes. Java's NPE. JS's "undefined is not a function". Swift's `T?` makes maybe-absent part of the type; you can't use a `T` until you've handled the `nil` branch. | Obj-C, C, Java, JS |
| Value types (`struct`/`enum`) | Obj-C's reference-everywhere model means every mutation is a hidden side effect. Java's pass-by-value-of-reference confuses. Swift makes copy-vs-share an explicit type-level decision (struct = copy; class = reference). | Obj-C, Java |
| Protocols with default implementations | Obj-C protocols are pure interfaces — no default behaviour. Swift protocols can carry default impls and conditional conformance, removing most of the inheritance-hierarchy boilerplate. | Obj-C, Java |
| `guard` / early-return clarity | Pyramid-of-doom nested `if`s ruin readability. Swift's `guard` flattens the happy path. | All curly-brace languages |
| Strong type inference | Java's verbose generics. Swift infers most types at function boundaries; explicit annotation only where it's load-bearing. | Java, C# |
| Automatic Reference Counting (ARC) | Obj-C's manual `retain/release/autorelease` (MRR). ARC inserts retain/release at compile time. | Obj-C |
| async/await (Swift 5.5+) | iOS's GCD with completion blocks turns deeply-nested logic into Christmas-tree closures. async/await flattens it. | Obj-C, JS pre-await |
| `Result<Success, Failure>` | NULL/exception pains the previous rows describe. `Result` is the typed, exhaustive alternative for sync error handling. | Obj-C, Java |
| `throws` and typed errors (Swift 6) | Pre-Swift-6 throws are untyped — caller can't know what to expect. Swift 6 typed throws make the error type visible. | Obj-C, Java |
| Modules + access control (`public`/`internal`/`private`/`fileprivate`) | C's header dance; Java's package-private confusion. Swift's access control is per-declaration with sensible defaults. | C, Java |

## For web-engineer learners: SwiftUI ↔ React/Vue mapping

Most senior engineers picking up SwiftUI in 2026 are coming from the web (React, Vue, Svelte, Solid) — not from UIKit. UIKit pain anchors land for the small population that shipped iOS before SwiftUI; for everyone else, web-framework analogies are the load-bearing ones. Use these as your primary anchors when the learner's background is web.

The mapping is unusually clean because SwiftUI was directly influenced by React's declarative-rendering model. Most patterns translate 1:1 with idiosyncratic naming.

| SwiftUI | React | Vue | Where the analogy breaks |
|---|---|---|---|
| `View` protocol with `body` computed property | Function component returning JSX | `<template>` block + `<script setup>` | SwiftUI views are *value types* (structs), not closures. Equivalent on the surface; very different on memory layout. |
| `@State` | `useState` | `ref` / `data()` | SwiftUI `@State` is owned by the view; React `useState` is owned by the component instance. Same lifecycle, different mental model for re-renders. |
| `@Binding` | Lifting state up + passing setter as prop | `v-model` two-way binding | `@Binding` is a typed two-way handle; React requires you to pass `value` and `onChange` separately. |
| `@StateObject` / `@ObservedObject` | `useReducer` + Context, or external state lib (Zustand, Redux) | Pinia store / Composition API ref | These are reference types; the view subscribes to changes via Combine. Closer to MobX than React's built-ins. |
| `@Environment` | React Context | `provide` / `inject` | Same idea, type-checked at compile time, value-type semantics. |
| `@ViewBuilder` (DSL) | JSX itself | `<template>` block | Same job: render-tree as composable expressions. SwiftUI's is type-checked all the way down; JSX type-checks at the boundary only (TS-aware editors help). |
| View modifiers (`.padding()`, `.foregroundColor()`) | Tailwind class chains, or CSS-in-JS prop spread | Scoped CSS or class binding | Modifiers compose top-down (each returns a new wrapped view); CSS classes compose at the leaf. Order matters in SwiftUI; usually doesn't in CSS. |
| `NavigationStack` with `.navigationDestination(for:)` | React Router `<Route path>` + URL state | Vue Router routes | SwiftUI's path is a typed value array (`@State var path: [Route]`); web routers are URL-bound. |
| `List` with `Identifiable` items | `array.map(item => <Component key={item.id} />)` | `v-for` with `:key` | The `Identifiable` protocol is functionally `key` from React; SwiftUI's diffing engine uses it the same way. |
| `Animation` modifiers | Framer Motion / Vue Transition | CSS transitions + animations | SwiftUI animations are implicit on state change; web frameworks usually require an explicit animation wrapper or class toggle. |
| `Task` + `.task(_:)` view modifier | `useEffect` with cleanup | `onMounted` / `onUnmounted` | `.task` ties async work to view lifecycle and auto-cancels on unmount; closer to React 18's auto-cleanup than to old useEffect. |
| `withAnimation { ... }` | `useTransition` / setTimeout-orchestrated | (no clean analog) | Synchronous block that triggers an implicit animation for any state change inside. No React equivalent. |
| `@AppStorage` | localStorage via custom hook (`useLocalStorage`) | `useStorage` from VueUse | Built into the framework; reactive without needing a wrapper. |
| `@FocusState` | `ref.current.focus()` + state to track | `v-focus` directive + ref | SwiftUI exposes focus as state, not as imperative method calls. |

**One specific framing to lead with for web engineers:**

> "SwiftUI is React for native. Same declarative-rendering bet, same component-as-function-of-state model, same hooks-flavoured state primitives. Different runtime — value types instead of references, Combine instead of fibers, async/await instead of Promises. If you've shipped React, you'll find your footing in days. The friction is the *value-type* mental model, not the rendering model."

Then introduce SwiftUI features as React-pattern + iOS-twist, in that order.

## Per-feature pain table — SwiftUI layer (specific to this table)

| SwiftUI feature | Pain it solves | Where you've felt it |
|---|---|---|
| The `View` protocol + `body` computed property | UIKit's "subclass `UIView`, override `init`/`layoutSubviews`/`drawRect`/`updateConstraints`" is a 4-method dance per view. SwiftUI's `View` is a single-property protocol: `var body: some View`. Declarative, compositional, no inheritance hierarchy. | UIKit, Android Views |
| Result-builder DSL (`@ViewBuilder`) | UIKit's `addSubview` + `NSLayoutConstraint.activate(...)` is imperative scaffolding. JSX is the closest analog. SwiftUI's `@ViewBuilder` lets you write nested view trees as natural Swift expressions. | UIKit, React-without-JSX |
| `@State` for owned, view-private state | UIKit's "where does this UI state live?" — usually a controller property with manual `setNeedsLayout` calls. SwiftUI's `@State` is "value type, view-owned, framework triggers redraw on change." | UIKit |
| `@Binding` for two-way state pass-through | UIKit's delegate-protocol-and-callback dance for child→parent communication. `@Binding` is a typed, compile-time-checked two-way handle that's syntactically a property. | UIKit |
| `@StateObject` and `@ObservedObject` for reference-typed state | UIKit's NotificationCenter for view-model→view updates is loose and untyped. ObservableObject + Combine publishers are typed at compile time. | UIKit, KVO |
| `@Environment` for ambient values | UIKit's "pass the AppDelegate everywhere" or singleton-pattern abuse. SwiftUI's `@Environment` is dependency injection with type-checked keys, scoped by the view tree. | UIKit |
| View modifiers (`.padding()`, `.foregroundColor()`, etc.) | UIKit's "set 5 properties on a label, hope you got the order right." SwiftUI's modifiers chain — each returns a new view with one property modified. Compose top-down, read top-down. | UIKit |
| `NavigationStack` + value-typed navigation | UIKit's `UINavigationController.pushViewController` requires manual VC instantiation, no type-checked navigation graph. NavigationStack with a path-bound `@State` array makes navigation routes type-safe values. | UIKit |
| `List` with built-in scroll, swipe, selection | UIKit's `UITableView` requires a delegate, a data source, a cell prototype, and `dequeueReusableCell` plumbing for the simplest list. SwiftUI's `List` is one declaration. | UIKit |
| `Identifiable` and `ForEach` | UIKit's "give me an index, give me a cell" model. SwiftUI's `ForEach(items) { item in ... }` works because each item is `Identifiable` — a protocol Swift's diffing engine relies on for animations. | UIKit |
| Animations as values (`.animation(.easeInOut)`) | UIKit's `UIView.animate(withDuration:animations:)` blocks. SwiftUI animations are implicit — declare the animatable property, the framework figures out the timing. | UIKit, CSS |
| `PreviewProvider` / `#Preview` macro | UIKit's "build, run, navigate to the screen, see the change, repeat." SwiftUI previews render in real-time as you type. The Xcode preview canvas is essential infrastructure, not a nice-to-have. | UIKit |
| Property wrappers in general | A meta-feature. iOS app developers write `@State`, `@Published`, `@AppStorage` daily. The mechanism behind them (custom property wrappers via `@propertyWrapper`) is mainstream Swift. | (no clean prior-language analog) |
| `ViewBuilder`-based DSLs that aren't UI | The same DSL machinery powers `Form`, `TableView`, `ToolbarBuilder`, custom non-UI DSLs. Once you've understood `@ViewBuilder`, you've understood half of modern Swift's DSL ecosystem. | (newer concept) |
| `Task` and `task(_:)` view modifier | UIKit's "kick off a background fetch in `viewDidAppear`, cancel it in `viewWillDisappear`" — manual lifecycle wiring. SwiftUI's `.task { await fetch() }` ties async work to the view's lifecycle automatically. | UIKit |
| `withAnimation { ... }` blocks | UIKit's `UIView.animate(withDuration:animations:completion:)` with the completion-block trap. `withAnimation` is a synchronous block that triggers an implicit animation for any state change inside it. | UIKit |

## Anti-anchors (concepts without obvious pain anchors in iOS-engineer prior knowledge)

These need extra time. Strategy: *create the pain experience first* by showing the pre-SwiftUI version, then introduce the SwiftUI feature as the fix.

- **`some View` opaque return types**. Returning `some View` (rather than a specific concrete type) is the language feature that makes `body` work. iOS engineers coming from UIKit don't have an analog — opaque return types arrived with Swift 5.1 specifically to support SwiftUI. Cliff topic.
- **The View identity contract**. SwiftUI relies on view identity (structural + explicit) to know which views to animate, which to discard, which to keep. UIKit had explicit object identity (every view is a class instance). SwiftUI's structural identity is subtler. Worth a dedicated chapter.
- **Actor isolation (Swift 6 strict mode)**. Cross-actor calls require `await`; `@MainActor` enforcement at compile time. UIKit had "main thread only for UI" as discipline; Swift 6 makes it a compile-time check. Disorienting at first.
- **Macros (Swift 5.9+)**. Compile-time code generation that's syntactic, not textual. Closest analog is Rust's procedural macros; many SwiftUI learners haven't seen those either. Use without explaining deeply early; deep-dive later.

## Voice for the chapter prose

When invoking a row from this table:

> **Pain anchor:** in UIKit, [pain]. SwiftUI handles this by [feature], which makes [the bad thing] either type-visible or impossible.

For learners coming from web (React, Vue), use the **"SwiftUI ↔ React/Vue mapping"** section above as the primary anchor. The web-framework analogies are usually load-bearing for senior engineers in 2026; UIKit anchors are the secondary track for the smaller population with prior iOS experience.

For learners coming from non-iOS native (Android Compose, Flutter), the analogies are even stronger — Jetpack Compose was directly inspired by SwiftUI; Flutter's widget tree is conceptually similar. Most patterns map 1:1, with idiosyncratic naming. Lean on those analogs heavily.

## Extending this table during a live session

If a SwiftUI pattern shows up in the anchor codebase that isn't in this table — log it in the project's local `docs/teaching/swiftui-anchor-table.md` (which gets seeded from this file on `/bookgen` invocation). Common candidates that may need adding when they appear:

- `Combine` publishers and operators (older codebases)
- `@Observable` macro (Swift 5.9+ replacement for `ObservableObject`)
- `AppStorage` / `SceneStorage` for persistence
- `EnvironmentValues` custom keys
- `ViewThatFits`, `Layout` protocol (iOS 16+)
- `Animation.spring(...)` parameter intuition
- `accessibilityLabel`, `accessibilityIdentifier` and the audit story
