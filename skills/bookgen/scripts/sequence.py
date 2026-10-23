#!/usr/bin/env python3
"""Dependency-ordered chapter sequencer (bookgen port #1 — mirrors Understand-Anything).

Turns an anchor repo's import graph into a *suggested* reading order: detect the
entry point, BFS outward, and map BFS depth to chapter buckets (overview → core
types → features → infrastructure). This is the deterministic skeleton; the agent
then writes `sessions.md` over it, applying pedagogical judgment the graph can't
know (one-concept-per-session cap, defer-load-multipliers, pain anchors).

Two-phase by design: this script does all the graph math, the LLM reasons over
the JSON. The agent must NOT re-derive structure by eyeballing files — trust the
skeleton, override the *order* on pedagogical grounds only.

    sequence.py --anchor-repo <path> [--book-repo <path>] [--entry <relpath>] [--quiet]

Outputs (under <book-repo>/docs/teaching/):
    dep-skeleton.json   machine-readable graph + per-file depth/fan-in/fan-out
    suggested-order.md  human-readable bucketed order for writing sessions.md

Tree-sitter accelerates parsing when installed; regex fallback otherwise (so it
always produces output). Exit 0 on success, 1 on bad args.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.treesit import FileFacts, has_treesitter, iter_source_files, parse_file  # noqa: E402

ENTRY_NAME_HINTS = ("main", "index", "__main__", "app", "cli", "lib", "mod")
ENTRY_PATH_HINTS = ("src/main.", "src/index.", "src/lib.", "cmd/", "src/bin/", "bin/")
COMMON_EXTS = (".rs", ".go", ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".swift", ".zig", ".ml", ".ex")

BUCKETS = {
    0: "Overview & entry point",
    1: "Core types & configuration",
    2: "Feature modules & primary functionality",
}
DEEP_BUCKET = "Supporting infrastructure & utilities"


@dataclass
class Node:
    path: Path
    rel: str
    facts: FileFacts
    out: set[str] = field(default_factory=set)  # rel paths this file imports (local)
    fan_in: int = 0
    fan_out: int = 0
    depth: int | None = None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _build_index(nodes: dict[str, Node]) -> tuple[dict[str, list[str]], dict[str, str]]:
    """Index files for import resolution: stem -> rels, and path-without-ext -> rel."""
    by_stem: dict[str, list[str]] = defaultdict(list)
    by_relpath: dict[str, str] = {}
    for rel, node in nodes.items():
        stem = node.path.stem
        by_stem[stem].append(rel)
        no_ext = rel.rsplit(".", 1)[0]
        by_relpath[no_ext] = rel
        # Treat dir/index, dir/mod, dir/__init__ as the directory itself.
        if stem in ("index", "mod", "__init__", "lib"):
            parent = node.path.parent.as_posix()
            parent_rel = _strip_root_prefix(parent, rel, stem)
            if parent_rel:
                by_relpath.setdefault(parent_rel, rel)
    return by_stem, by_relpath


def _strip_root_prefix(parent: str, rel: str, stem: str) -> str | None:
    # rel is like "src/foo/mod.rs"; we want "src/foo" mapped to it.
    no_ext = rel.rsplit(".", 1)[0]
    if no_ext.endswith("/" + stem):
        return no_ext[: -(len(stem) + 1)]
    return None


def _resolve_import(spec: str, importer: Node, root: Path, by_stem, by_relpath) -> str | None:
    """Best-effort map an import specifier to a local file's rel path."""
    spec = spec.strip().strip("\"'`{}").split(" ")[0]
    if not spec:
        return None

    # Relative path imports (JS/TS, sometimes others).
    if spec.startswith((".", "/")):
        base = importer.path.parent
        target = (base / spec).resolve()
        for cand in _path_candidates(target, root):
            if cand in by_relpath:
                return by_relpath[cand]
        # also try by stem of the last segment
        seg = spec.rstrip("/").split("/")[-1]
        return _match_stem(seg, by_stem)

    # Module-ish specifiers: split on language separators, walk from most to least specific.
    segments = [s for s in _split_module(spec) if s]
    if not segments:
        return None

    # Try progressively shorter suffix joins as relative paths.
    for length in range(len(segments), 0, -1):
        joined = "/".join(segments[-length:])
        if joined in by_relpath:
            return by_relpath[joined]
        # also as src/<joined>
        if ("src/" + joined) in by_relpath:
            return by_relpath["src/" + joined]
    # Fall back to trailing-segment stem match.
    return _match_stem(segments[-1], by_stem, importer.rel)


def _split_module(spec: str) -> list[str]:
    for sep in ("::", "."):
        spec = spec.replace(sep, "/")
    return [s for s in spec.split("/") if s and s not in ("crate", "self", "super")]


def _path_candidates(target: Path, root: Path) -> list[str]:
    cands: list[str] = []
    base = target
    rels = []
    try:
        rels.append(base.relative_to(root).as_posix())
    except ValueError:
        rels.append(base.as_posix())
    stem_rel = rels[0]
    cands.append(stem_rel)  # exact (already without ext if spec had none)
    for ext in COMMON_EXTS:
        cands.append(stem_rel + ext.rstrip("."))  # not used directly; relpath index is ext-less
    # index/mod/__init__ under the directory
    for special in ("index", "mod", "__init__", "lib"):
        cands.append((stem_rel + "/" + special))
    # de-dupe, keep order, return ext-less forms for by_relpath lookups
    return _dedupe([c.rsplit(".", 1)[0] if c.rsplit(".", 1)[-1] in {e.strip(".") for e in COMMON_EXTS} else c for c in cands])


def _match_stem(seg: str, by_stem, importer_rel: str | None = None) -> str | None:
    cands = by_stem.get(seg)
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0]
    # Ambiguous: prefer one sharing the importer's top directory.
    if importer_rel:
        top = importer_rel.split("/", 1)[0]
        same = [c for c in cands if c.split("/", 1)[0] == top]
        if same:
            return same[0]
    return cands[0]


def _dedupe(items: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for i in items:
        seen.setdefault(i, None)
    return list(seen)


def _detect_entry(nodes: dict[str, Node], override: str | None) -> str | None:
    if override:
        if override in nodes:
            return override
        # try suffix match
        for rel in nodes:
            if rel.endswith(override):
                return rel
        return None
    scored: list[tuple[float, str]] = []
    for rel, node in nodes.items():
        score = 0.0
        low = rel.lower()
        if any(h in low for h in ENTRY_PATH_HINTS):
            score += 5
        if node.path.stem.lower() in ENTRY_NAME_HINTS:
            score += 3
        if "main" in node.facts.calls or "main" in node.facts.defs:
            score += 2
        # Entry points are imported by ~nobody but import a lot.
        if node.fan_in == 0:
            score += 1.5
        score += min(node.fan_out, 10) * 0.2
        if score:
            scored.append((score, rel))
    if not scored:
        # Highest fan-out as last resort.
        return max(nodes.values(), key=lambda n: n.fan_out).rel if nodes else None
    scored.sort(key=lambda t: (-t[0], t[1]))
    return scored[0][1]


def build_graph(root: Path, max_files: int) -> tuple[dict[str, Node], list[str]]:
    files = list(iter_source_files(root))
    warnings: list[str] = []
    if len(files) > max_files:
        warnings.append(f"{len(files)} source files exceed --max-files {max_files}; sequencing the first {max_files} by path. Consider scoping --anchor-repo to a subdir.")
        files = sorted(files)[:max_files]

    nodes: dict[str, Node] = {}
    for path in files:
        facts = parse_file(path)
        rel = _rel(path, root)
        nodes[rel] = Node(path=path, rel=rel, facts=facts)

    by_stem, by_relpath = _build_index(nodes)
    for node in nodes.values():
        for spec in node.facts.imports:
            target = _resolve_import(spec, node, root, by_stem, by_relpath)
            if target and target != node.rel:
                node.out.add(target)

    # fan-in / fan-out
    for node in nodes.values():
        node.fan_out = len(node.out)
    for node in nodes.values():
        for tgt in node.out:
            if tgt in nodes:
                nodes[tgt].fan_in += 1
    return nodes, warnings


def assign_depths(nodes: dict[str, Node], entry: str | None) -> None:
    if entry is None or entry not in nodes:
        return
    nodes[entry].depth = 0
    q = deque([entry])
    while q:
        cur = nodes[q.popleft()]
        for tgt in sorted(cur.out):
            if tgt in nodes and nodes[tgt].depth is None:
                nodes[tgt].depth = (cur.depth or 0) + 1
                q.append(tgt)


def bucket_for(depth: int | None) -> str:
    if depth is None:
        return "Unreached (no import path from entry) — order by fan-in"
    return BUCKETS.get(depth, DEEP_BUCKET)


def to_skeleton(root: Path, nodes: dict[str, Node], entry: str | None, warnings: list[str]) -> dict:
    files_out = []
    for rel, node in sorted(nodes.items(), key=lambda kv: (_sort_key(kv[1]))):
        files_out.append(
            {
                "path": rel,
                "lang": node.facts.lang,
                "parsed_with": node.facts.parsed_with,
                "depth": node.depth,
                "bucket": bucket_for(node.depth),
                "fan_in": node.fan_in,
                "fan_out": node.fan_out,
                "imports_resolved": sorted(node.out),
                "defs": node.facts.defs[:40],
                "exports": node.facts.exports[:40],
            }
        )
    edges = [[node.rel, tgt] for node in nodes.values() for tgt in sorted(node.out)]
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "anchor_repo": str(root),
        "parser": "tree-sitter" if has_treesitter() else "regex-fallback",
        "entry_point": entry,
        "file_count": len(nodes),
        "edge_count": len(edges),
        "warnings": warnings,
        "files": files_out,
        "edges": edges,
    }


def _sort_key(node: Node) -> tuple:
    # Reachable files first by depth; unreached last by descending fan-in.
    if node.depth is None:
        return (1, 0, -node.fan_in, node.rel)
    return (0, node.depth, -node.fan_in, node.rel)


def render_markdown(skel: dict) -> str:
    lines = [
        "# Suggested chapter order (dependency-derived)",
        "",
        f"_Generated {skel['generated']} from `{skel['anchor_repo']}` "
        f"({skel['parser']}). {skel['file_count']} files, {skel['edge_count']} import edges._",
        "",
        "This is a **starting order**, not a session plan. Derived by BFS from the entry "
        "point over the import graph (Understand-Anything's approach). Write `sessions.md` "
        "over it and **override the order on pedagogical grounds**: cap one new concept per "
        "session (rule 3), defer load multipliers (rule 8), and lead with pain anchors (rule 7). "
        "Trust the structure here; re-shape the *teaching* sequence.",
        "",
        f"**Entry point:** `{skel['entry_point'] or '(none detected — pass --entry)'}`",
        "",
    ]
    if skel["warnings"]:
        lines.append("> ⚠ " + " ".join(skel["warnings"]))
        lines.append("")

    # Group by bucket, preserving the sorted file order.
    groups: dict[str, list[dict]] = {}
    for f in skel["files"]:
        groups.setdefault(f["bucket"], []).append(f)

    bucket_order = list(BUCKETS.values()) + [DEEP_BUCKET, "Unreached (no import path from entry) — order by fan-in"]
    for bucket in bucket_order:
        items = groups.get(bucket)
        if not items:
            continue
        lines.append(f"## {bucket}")
        lines.append("")
        lines.append("| File | depth | fan-in | fan-out | key definitions |")
        lines.append("|---|---|---|---|---|")
        for f in items:
            defs = ", ".join(f["defs"][:5]) or "—"
            depth = "—" if f["depth"] is None else str(f["depth"])
            lines.append(f"| `{f['path']}` | {depth} | {f['fan_in']} | {f['fan_out']} | {defs} |")
        lines.append("")

    lines.append("## How to use this")
    lines.append("")
    lines.append(
        "1. README / overview first (\"what is this?\"), then the entry point (\"how does it start?\").\n"
        "2. Walk outward by depth — each chapter should build on the prior depth's concepts.\n"
        "3. Collapse or split buckets to honour the one-concept cap; a depth bucket is not a chapter.\n"
        "4. Unreached files are usually utilities/tests — fold them in where their concept is needed."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Dependency-ordered chapter sequencer.")
    ap.add_argument("--anchor-repo", required=True, type=Path)
    ap.add_argument("--book-repo", type=Path, default=Path.cwd(), help="Where to write outputs (docs/teaching/). Defaults to cwd.")
    ap.add_argument("--entry", default=None, help="Override entry point (rel path or suffix).")
    ap.add_argument("--max-files", type=int, default=2000)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = args.anchor_repo.expanduser().resolve()
    if not root.is_dir():
        print(f"error: --anchor-repo is not a directory: {root}", file=sys.stderr)
        return 1

    nodes, warnings = build_graph(root, args.max_files)
    if not nodes:
        print(f"error: no source files found under {root}", file=sys.stderr)
        return 1
    entry = _detect_entry(nodes, args.entry)
    assign_depths(nodes, entry)
    skel = to_skeleton(root, nodes, entry, warnings)

    out_dir = args.book_repo.expanduser().resolve() / "docs" / "teaching"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dep-skeleton.json").write_text(json.dumps(skel, indent=2) + "\n")
    (out_dir / "suggested-order.md").write_text(render_markdown(skel))

    if not args.quiet:
        print(f"==> parsed {skel['file_count']} files ({skel['parser']}), {skel['edge_count']} edges")
        print(f"==> entry point: {entry or '(none — pass --entry)'}")
        if warnings:
            for w in warnings:
                print(f"    ⚠ {w}")
        print(f"==> wrote {out_dir / 'dep-skeleton.json'}")
        print(f"==> wrote {out_dir / 'suggested-order.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
