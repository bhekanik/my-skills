#!/usr/bin/env python3
"""Import-aware batching for large tour-mode anchor repos (bookgen port #5).

Mirrors Understand-Anything's analysis fan-out: split the anchor repo into
cohesive batches (~25 files), keep import-related files together, and compute a
`neighbor_map` of cross-batch exported symbols so each batch carries the context
it needs without re-reading the whole repo. The agent then analyses each batch
independently, writing `intermediate/batch-NN.json` to disk (disk-as-context-bus
— results never round-trip through the orchestrator's context), then reduces.

Use this only when an anchor repo is large enough that one linear read is wasteful
(tour mode, 10K+ LOC). Small repos don't need it.

    compute_batches.py --anchor-repo <path> [--book-repo <path>] [--batch-size 25] [--quiet]

Output: <book-repo>/docs/teaching/batch-plan.json  (+ ensures intermediate/ exists)
Exit 0 on success, 1 on bad args. Tree-sitter when available, regex fallback otherwise.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.treesit import has_treesitter  # noqa: E402
from sequence import build_graph  # noqa: E402  (reuse the dependency graph builder)


def _cohesive_order(nodes: dict) -> list[str]:
    """Order files so import-related and same-directory files sit adjacent.

    Sort by (top-level dir, full dir, fan-in desc, path). Keeping a directory
    contiguous keeps a module's files in the same batch most of the time, which
    is what makes a batch analysable in isolation.
    """
    def key(rel: str):
        node = nodes[rel]
        parts = rel.split("/")
        top = parts[0] if len(parts) > 1 else ""
        d = "/".join(parts[:-1])
        return (top, d, -node.fan_in, rel)

    return sorted(nodes, key=key)


def make_batches(nodes: dict, batch_size: int) -> list[list[str]]:
    ordered = _cohesive_order(nodes)
    batches: list[list[str]] = []
    cur: list[str] = []
    cur_dir: str | None = None
    for rel in ordered:
        d = rel.rsplit("/", 1)[0] if "/" in rel else ""
        # Start a new batch when full, but prefer to break at a directory boundary
        # to keep modules intact — unless the current batch is already oversized.
        if cur and (len(cur) >= batch_size and d != cur_dir or len(cur) >= batch_size + batch_size // 2):
            batches.append(cur)
            cur = []
        cur.append(rel)
        cur_dir = d
    if cur:
        batches.append(cur)
    return batches


def neighbor_map(batch: list[str], batch_of: dict[str, int], nodes: dict, my_index: int) -> dict:
    """For each file in the batch, the cross-batch symbols it depends on.

    Maps importer -> {imported_rel (in another batch): [exported symbols there]}.
    This is the minimal external context an analyser needs to resolve edges that
    leave the batch, without loading the other batch's full source.
    """
    out: dict[str, dict] = {}
    for rel in batch:
        node = nodes[rel]
        externals: dict[str, list[str]] = {}
        for tgt in sorted(node.out):
            if tgt in nodes and batch_of.get(tgt) != my_index:
                externals[tgt] = nodes[tgt].facts.exports[:20]
        if externals:
            out[rel] = externals
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Import-aware batching for large anchor repos.")
    ap.add_argument("--anchor-repo", required=True, type=Path)
    ap.add_argument("--book-repo", type=Path, default=Path.cwd())
    ap.add_argument("--batch-size", type=int, default=25)
    ap.add_argument("--max-files", type=int, default=5000)
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

    batches = make_batches(nodes, max(5, args.batch_size))
    batch_of: dict[str, int] = {}
    for i, b in enumerate(batches):
        for rel in b:
            batch_of[rel] = i

    plan = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "anchor_repo": str(root),
        "parser": "tree-sitter" if has_treesitter() else "regex-fallback",
        "file_count": len(nodes),
        "batch_size_target": args.batch_size,
        "batch_count": len(batches),
        "warnings": warnings,
        "intermediate_dir": "docs/teaching/intermediate/",
        "reduce_note": (
            "Analyse each batch independently and write docs/teaching/intermediate/batch-NN.json "
            "(NN = zero-padded index). Do not return batch results to the orchestrator — write to "
            "disk and reduce from there. Each output filename MUST match batch-NN.json exactly so a "
            "reducer can find it. After all batches are written, merge into the chapter/session plan."
        ),
        "batches": [
            {
                "index": i,
                "file_count": len(b),
                "files": b,
                "neighbor_map": neighbor_map(b, batch_of, nodes, i),
                "output": f"docs/teaching/intermediate/batch-{i:02d}.json",
            }
            for i, b in enumerate(batches)
        ],
    }

    out_dir = args.book_repo.expanduser().resolve() / "docs" / "teaching"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "intermediate").mkdir(exist_ok=True)
    (out_dir / "batch-plan.json").write_text(json.dumps(plan, indent=2) + "\n")

    if not args.quiet:
        print(f"==> {len(nodes)} files into {len(batches)} batches ({plan['parser']})")
        for b in plan["batches"]:
            print(f"    batch-{b['index']:02d}: {b['file_count']} files, {len(b['neighbor_map'])} with cross-batch deps")
        print(f"==> wrote {out_dir / 'batch-plan.json'}")
        print(f"==> analysers write to {out_dir / 'intermediate'}/batch-NN.json, then reduce")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
