#!/usr/bin/env python3
"""
chain_index.py — generate a cross-book concept index for a BookChain.

Walks a book's `book-chain.toml` to find sibling books, harvests `teaches:`
and `requires:` tags from every chapter's frontmatter across all books in
the chain, and emits a concept graph at `<book-repo>/docs/chain/`:

  - `concepts/<concept>.md`        — one file per concept; lists all chapters
                                     across all books that teach or require it
  - `concept-index.md`             — flat list of all concepts with link counts
  - `prerequisites-graph.md`       — chapters with unresolved `requires:` flagged
  - `concept-dag.json`             — machine-readable prerequisite DAG (nodes,
                                     edges, unresolved), consumed by the teaching
                                     skill's rule 23 (recursive prerequisite descent)
  - `chain-summary.md`             — chain metadata + book ordering

Idempotent: regenerates from scratch each run.

Usage:
  chain_index.py --book-repo <path> [--also-list-concepts] [--strict]

Options:
  --book-repo <path>      Required. Path to a book repo (the one with
                          book-chain.toml; sibling books are discovered from there).
  --also-list-concepts    After generation, print the full concept namespace.
                          Useful when authoring a new chapter and you want to
                          reuse existing tag names rather than coining new ones.
  --strict                Exit non-zero if any chapter has an unresolved
                          `requires:` (a concept no chapter teaches). Useful in CI.

Exit codes:
  0  success (or, with --strict, success and no broken chains)
  1  bad arguments or missing book-chain.toml
  2  --strict failed (broken chain detected)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.stderr.write(
            "ERROR: this script needs Python 3.11+ (or `pip install tomli`).\n"
        )
        sys.exit(1)


# ----------------------------------------------------------------------------
# Frontmatter parsing — we don't pull in PyYAML; we do a strict subset parse.
# ----------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse the frontmatter block of a markdown file into a dict.

    We support: scalar key:value pairs, list values via `key:` followed by
    `  - item` lines. No nested objects, no flow-style lists. That's enough
    for chapter frontmatter as we use it.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    result: dict = {}
    current_list_key: str | None = None
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line or line.startswith("#"):
            continue
        # List item line
        if line.lstrip().startswith("- ") and current_list_key is not None:
            item = line.lstrip()[2:].strip().strip("\"'")
            result[current_list_key].append(item)
            continue
        # key: value or key: (start of list)
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Could be a block scalar or a list; assume list until we see
                # the next non-list line.
                result[key] = []
                current_list_key = key
            else:
                result[key] = value.strip("\"'")
                current_list_key = None
            continue
        # Otherwise: ignore (e.g., multiline block scalars we don't support)
    return result


# ----------------------------------------------------------------------------
# Book and chain data structures
# ----------------------------------------------------------------------------


@dataclass
class Chapter:
    book_name: str
    book_path: Path
    file_path: Path  # absolute path to the .md
    chapter_id: str  # "00", "00b", "04", etc.
    title: str
    teaches: list[str]
    requires: list[str]
    status: str  # "stub" or "complete"

    @property
    def relative_path(self) -> Path:
        return self.file_path.relative_to(self.book_path)


@dataclass
class Book:
    name: str
    path: Path
    chapters: list[Chapter] = field(default_factory=list)


@dataclass
class Chain:
    name: str
    description: str
    books: list[Book] = field(default_factory=list)


def discover_chapters(book_path: Path, book_name: str) -> Iterable[Chapter]:
    """Yield Chapter records for every .md file under <book>/docs/book/."""
    book_dir = book_path / "docs" / "book"
    if not book_dir.is_dir():
        return
    for md in sorted(book_dir.glob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        chapter_id = str(fm.get("chapter", md.stem.split("-", 1)[0]))
        title = fm.get("title", md.stem.split("-", 1)[-1].replace("-", " ").title())
        teaches = fm.get("teaches") if isinstance(fm.get("teaches"), list) else []
        requires = fm.get("requires") if isinstance(fm.get("requires"), list) else []
        status = fm.get("status", "complete")
        yield Chapter(
            book_name=book_name,
            book_path=book_path,
            file_path=md,
            chapter_id=chapter_id,
            title=title,
            teaches=teaches,
            requires=requires,
            status=status,
        )


def load_chain(root_book: Path) -> Chain:
    """Read root_book's book-chain.toml and walk siblings."""
    toml_path = root_book / "book-chain.toml"
    if not toml_path.is_file():
        sys.stderr.write(f"ERROR: no book-chain.toml at {toml_path}\n")
        sys.exit(1)

    cfg = tomllib.loads(toml_path.read_text(encoding="utf-8"))

    chain_name = cfg.get("chain") or cfg.get("name") or "unnamed"
    description = cfg.get("description", "")

    chain = Chain(name=chain_name, description=description)

    # Track seen paths so we don't add the root book twice if it's also
    # listed in its own siblings array (a common mistake when the same
    # book-chain.toml is shared across all books in the chain).
    seen_paths: set[Path] = set()

    # The root book itself is always a member.
    root_resolved = root_book.resolve()
    chain.books.append(Book(name=root_resolved.name, path=root_resolved))
    seen_paths.add(root_resolved)

    # Walk siblings.
    for sib in cfg.get("siblings", []):
        sib_name = sib.get("name", "unnamed-sibling")
        sib_path = sib.get("path")
        if sib_path:
            resolved = (root_book / sib_path).resolve()
            if resolved in seen_paths:
                continue  # dedupe — the root book is already in the chain
            if not resolved.is_dir():
                sys.stderr.write(
                    f"WARN: sibling '{sib_name}' path does not exist: {resolved}\n"
                )
                continue
            chain.books.append(Book(name=sib_name, path=resolved))
            seen_paths.add(resolved)
        elif sib.get("url"):
            sys.stderr.write(
                f"NOTE: sibling '{sib_name}' is URL-only ({sib['url']}); "
                "skipped (clone it locally to include).\n"
            )

    # Populate each book's chapters.
    for book in chain.books:
        book.chapters = list(discover_chapters(book.path, book.name))

    return chain


# ----------------------------------------------------------------------------
# Index generation
# ----------------------------------------------------------------------------


def generate_index(chain: Chain, output_dir: Path) -> dict:
    """Produce the chain index files. Returns stats for reporting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    concepts_dir = output_dir / "concepts"
    concepts_dir.mkdir(exist_ok=True)

    # Build the concept → (chapter, role) graph.
    teaches_map: dict[str, list[Chapter]] = defaultdict(list)
    requires_map: dict[str, list[Chapter]] = defaultdict(list)

    for book in chain.books:
        for chapter in book.chapters:
            for tag in chapter.teaches:
                teaches_map[tag].append(chapter)
            for tag in chapter.requires:
                requires_map[tag].append(chapter)

    all_concepts = sorted(set(teaches_map.keys()) | set(requires_map.keys()))

    # Per-concept files
    for concept in all_concepts:
        teach_chapters = teaches_map.get(concept, [])
        require_chapters = requires_map.get(concept, [])
        slug = concept.replace("/", "__")
        out = concepts_dir / f"{slug}.md"
        lines = [f"# Concept: `{concept}`", ""]
        if not teach_chapters:
            lines.append("> ⚠️ **Unresolved**: no chapter in this chain teaches this concept, but at least one chapter requires it.")
            lines.append("")
        if teach_chapters:
            lines.append("## Taught in")
            lines.append("")
            for ch in teach_chapters:
                lines.append(
                    f"- **{ch.book_name}** chapter {ch.chapter_id} — "
                    f"[{ch.title}](../../../{_relpath(ch, output_dir)}) "
                    f"_[{ch.status}]_"
                )
            lines.append("")
        if require_chapters:
            lines.append("## Required by")
            lines.append("")
            for ch in require_chapters:
                lines.append(
                    f"- **{ch.book_name}** chapter {ch.chapter_id} — "
                    f"[{ch.title}](../../../{_relpath(ch, output_dir)}) "
                    f"_[{ch.status}]_"
                )
            lines.append("")
        if not teach_chapters and not require_chapters:
            lines.append("(orphan concept — no references)")
        out.write_text("\n".join(lines), encoding="utf-8")

    # concept-index.md (flat list)
    flat = output_dir / "concept-index.md"
    lines = [
        f"# Concept index — {chain.name} chain",
        "",
        chain.description or "",
        "",
        f"_{len(all_concepts)} concepts across {len(chain.books)} books._",
        "",
        "| Concept | Taught in (count) | Required by (count) |",
        "|---|---|---|",
    ]
    for concept in all_concepts:
        slug = concept.replace("/", "__")
        t = len(teaches_map.get(concept, []))
        r = len(requires_map.get(concept, []))
        unresolved = " ⚠️" if t == 0 and r > 0 else ""
        lines.append(
            f"| [`{concept}`](concepts/{slug}.md){unresolved} | {t} | {r} |"
        )
    flat.write_text("\n".join(lines), encoding="utf-8")

    # prerequisites-graph.md (orphan + reverse-dep view)
    pg = output_dir / "prerequisites-graph.md"
    lines = [
        f"# Prerequisites graph — {chain.name} chain",
        "",
        "Chapters with unresolved prerequisites (a `requires:` concept that no chapter in the chain teaches).",
        "",
    ]
    unresolved_count = 0
    for book in chain.books:
        for chapter in book.chapters:
            unresolved = [t for t in chapter.requires if t not in teaches_map]
            if unresolved:
                unresolved_count += 1
                lines.append(
                    f"- **{book.name}** chapter {chapter.chapter_id} ({chapter.title}) requires:"
                )
                for tag in unresolved:
                    lines.append(f"  - `{tag}` — not taught anywhere in the chain")
    if unresolved_count == 0:
        lines.append("✅ No unresolved prerequisites. The chain is well-formed.")
    pg.write_text("\n".join(lines), encoding="utf-8")

    # chain-summary.md
    summary = output_dir / "chain-summary.md"
    lines = [
        f"# {chain.name} — chain summary",
        "",
        chain.description or "",
        "",
        f"_{len(chain.books)} books, {sum(len(b.chapters) for b in chain.books)} chapters, {len(all_concepts)} concepts._",
        "",
        "## Books in this chain",
        "",
    ]
    for book in chain.books:
        complete = sum(1 for c in book.chapters if c.status == "complete")
        total = len(book.chapters)
        lines.append(
            f"- **{book.name}** — {complete}/{total} chapters with full content. Path: `{book.path}`"
        )
    lines.append("")
    lines.append("## Generated")
    lines.append("")
    lines.append(
        "Run the installed bookgen skill's `scripts/chain_index.py --book-repo <this-book>` to regenerate."
    )
    summary.write_text("\n".join(lines), encoding="utf-8")

    # concept-dag.json — machine-readable prerequisite graph for the teaching
    # skill's rule 23 (recursive prerequisite descent) and any future tooling.
    chapters_json = [
        {
            "id": f"{book.name}:{ch.chapter_id}",
            "book": book.name,
            "chapter": ch.chapter_id,
            "title": ch.title,
            "status": ch.status,
            "teaches": ch.teaches,
            "requires": ch.requires,
            "path": str(ch.relative_path),
        }
        for book in chain.books
        for ch in book.chapters
    ]
    nodes = {
        concept: {
            "taught_by": [f"{c.book_name}:{c.chapter_id}" for c in teaches_map.get(concept, [])],
            "required_by": [f"{c.book_name}:{c.chapter_id}" for c in requires_map.get(concept, [])],
            "unresolved": not teaches_map.get(concept) and bool(requires_map.get(concept)),
        }
        for concept in all_concepts
    }
    edges = []
    unresolved_pairs = []
    for book in chain.books:
        for ch in book.chapters:
            for req in ch.requires:
                satisfied = [f"{c.book_name}:{c.chapter_id}" for c in teaches_map.get(req, [])]
                edges.append({"chapter": f"{book.name}:{ch.chapter_id}", "requires": req, "satisfied_by": satisfied})
                if not satisfied:
                    unresolved_pairs.append({"chapter": f"{book.name}:{ch.chapter_id}", "concept": req})
    dag = {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "chain": chain.name,
        "concept_count": len(all_concepts),
        "chapters": chapters_json,
        "nodes": nodes,
        "edges": edges,
        "unresolved": unresolved_pairs,
    }
    (output_dir / "concept-dag.json").write_text(json.dumps(dag, indent=2) + "\n", encoding="utf-8")

    return {
        "books": len(chain.books),
        "chapters": sum(len(b.chapters) for b in chain.books),
        "concepts": len(all_concepts),
        "unresolved_chapters": unresolved_count,
    }


def _relpath(chapter: Chapter, output_dir: Path) -> str:
    """Compute a relative path from the chain index back to a chapter file.

    The index lives at `<root_book>/docs/chain/`, the chapter at
    `<book>/docs/book/<file>.md`. We emit the chapter's path relative to
    the chain output dir so links work.
    """
    return str(
        Path("..") / chapter.book_path.name / chapter.relative_path
    )


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate cross-book concept index for a BookChain."
    )
    p.add_argument("--book-repo", required=True, help="Path to root book repo (must contain book-chain.toml).")
    p.add_argument("--also-list-concepts", action="store_true", help="Print the full concept namespace after generation.")
    p.add_argument("--strict", action="store_true", help="Exit non-zero if any chapter has unresolved requires.")
    args = p.parse_args()

    root = Path(args.book_repo).expanduser().resolve()
    if not root.is_dir():
        sys.stderr.write(f"ERROR: {root} is not a directory.\n")
        return 1

    chain = load_chain(root)
    output_dir = root / "docs" / "chain"
    stats = generate_index(chain, output_dir)

    print(f"==> Chain index generated at {output_dir}")
    print("    concept-dag.json (machine-readable prerequisite graph) written")
    print(
        f"    {stats['books']} books, {stats['chapters']} chapters, "
        f"{stats['concepts']} concepts, "
        f"{stats['unresolved_chapters']} chapters with unresolved requires."
    )

    if args.also_list_concepts:
        # Re-walk to list concepts.
        all_concepts = set()
        for book in chain.books:
            for ch in book.chapters:
                all_concepts.update(ch.teaches)
        print("\n==> Concept namespace:")
        for c in sorted(all_concepts):
            print(f"  - {c}")

    if args.strict and stats["unresolved_chapters"] > 0:
        sys.stderr.write(
            f"\n--strict failed: {stats['unresolved_chapters']} chapters have unresolved requires.\n"
            f"See {output_dir}/prerequisites-graph.md for details.\n"
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
