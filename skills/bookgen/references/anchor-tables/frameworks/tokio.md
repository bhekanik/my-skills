# Framework anchor addendum: Tokio (Rust async runtime)

Append to the Rust anchor table when the anchor repo uses Tokio (`scaffold.sh --framework tokio`). Tokio concepts sit on top of Rust's ownership/borrow foundations; defer the deep async semantics (rule 8) and lead with the pain each construct removes (rule 7).

## Pain-anchor table

| Tokio construct | The pain it removes | Where the learner felt it |
|---|---|---|
| `#[tokio::main]` | Hand-rolling an event loop / reactor | C `poll`/`epoll` loops; JS nested callbacks |
| `async fn` / `.await` | Manual state machines for non-blocking I/O | C `epoll` state structs; JS promise chains |
| `tokio::spawn` | `pthread_create` + join bookkeeping; unstructured background work | C threads; JS fire-and-forget |
| `tokio::sync::mpsc` | Hand-built lock + condvar queues; shared-memory races | C producer/consumer; Go channels (closest analog) |
| `tokio::select!` | Nested readiness loops; `Promise.race` with no cancellation | C `poll` fan-in; JS race |
| `Arc<Mutex<T>>` across tasks | "is this actually thread-safe?" guesswork | C shared globals |

## Anti-anchors (where the analogy misleads)

- Tokio tasks are **not** OS threads — `spawn` is cheap, but blocking a task blocks its worker thread. Use `spawn_blocking` for CPU-bound or blocking work.
- `.await` is a **suspension point**, not a thread yield. Holding a `std::sync::Mutex` guard across `.await` can deadlock; use `tokio::sync::Mutex`, or drop the guard before awaiting.
- Go channels look like `mpsc`, but Go's runtime preempts goroutines; Tokio does **not** preempt a task that never `.await`s.

## Defer-load note (rule 8)

Use `#[tokio::main]`, `.await`, and `spawn` long before explaining `Future`, `Pin`, `Send`/`Sync` bounds, or the executor. "Trust these for now; we'll dig into the state machine later." The first deep-dive session is where the deferred load gets paid back.
