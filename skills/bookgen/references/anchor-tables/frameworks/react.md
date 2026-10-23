# Framework anchor addendum: React

Append to the TypeScript/JavaScript anchor table when the anchor repo is a React app (`scaffold.sh --framework react`). React's model is declarative-render-from-state; lead with the imperative-DOM pain it removes (rule 7).

## Pain-anchor table

| React construct | The pain it removes | Where the learner felt it |
|---|---|---|
| JSX + render-from-state | Manual `querySelector` + imperative DOM mutation that drifts from data | jQuery spaghetti; vanilla DOM |
| `useState` | Hand-syncing a variable and the DOM that displays it | manual `el.textContent = x` |
| `useEffect` | Lifecycle bookkeeping; listeners leaked on unmount | `addEventListener` with no matching `remove` |
| component props | Global mutable state threaded by hand | window globals |
| `key` on lists | DOM diffing bugs when rows reorder | manual list re-render |
| Context | Prop-drilling through many layers | passing a callback down six levels |

## Anti-anchors (where the analogy misleads)

- `useState` setters are **async-batched**, not immediate — reading the variable right after `setX(...)` gives the *old* value.
- `useEffect` runs *after* paint, not during render; it is not `componentWillMount`.
- Re-render ≠ re-mount. A component re-renders often; its state persists across renders unless its `key` changes.
- "The virtual DOM is fast" is a pitfall framing — it's *predictable*, not inherently fast. Unnecessary renders still cost.

## Defer-load note (rule 8)

Use `useState` / `useEffect` / props before explaining reconciliation, fiber, or memoisation (`useMemo` / `useCallback`). Introduce the rules-of-hooks constraint early (it bites immediately); defer *why* it exists until the render-model session.
