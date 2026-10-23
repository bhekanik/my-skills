# 0004 — tree-sitter node-config coverage is partial

**Status:** open (known limitation, documented)
**Opened:** 2026-05-25
**Area:** `scripts/lib/treesit.py`

## What

`scripts/lib/treesit.py` extracts structure (imports / exports / defs / calls) two ways:

1. **Tree-sitter** — accurate, but only for languages that have an entry in `_NODE_CONFIG` (the per-grammar node-type map). Currently: **python, rust, go, javascript, typescript, tsx**.
2. **Regex fallback** — coarser, used when tree-sitter isn't installed *or* when a language has a grammar but no `_NODE_CONFIG` entry.

So Swift, Zig, OCaml, Elixir, C, C++, Java, Ruby (all of which have anchor tables and/or `LANG_BY_EXT` entries) fall back to **regex even when `tree-sitter-language-pack` is installed**, because there's no node-config for them yet.

## Impact

- `sequence.py` (dependency ordering) and `drift.py` (structural fingerprints) still work for these languages, but with regex-level accuracy: import resolution and def/export detection are coarser, so a few edges may be missed and some structural changes may read as cosmetic (or vice-versa).
- No hard failure. The graceful fallback path is the intended degradation (see `README.md` → Optional dependencies).

## Fix (when it earns priority)

Add `_NODE_CONFIG` entries for the remaining anchor-table languages. Each needs the grammar's node-type names for imports, definitions, calls, and the export marker. Verify against the actual grammar in `tree-sitter-language-pack` (node type names differ per grammar; don't guess). Swift and Zig are the highest-value next additions since they have first-class anchor tables.

## Related

- `references/concept-namespaces/` was added in the same change set, closing the older "starter concept lists don't exist" TODO referenced in `references/templates/chain/concept-tags-spec.md`.
