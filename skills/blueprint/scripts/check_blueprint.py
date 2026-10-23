#!/usr/bin/env python3
"""Check a blueprint directory for broken links, undefined IDs and index drift.

Usage: check_blueprint.py <blueprint dir>

Errors (exit 1): a relative link or anchor that doesn't resolve, a cited
decision ID with no heading, a numbered document missing from the README.
Warnings (exit 0): a cited S/Q spike or question ID with no table row. These
are warnings because prose like "AWS S3" or "Q1 revenue" matches the pattern.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
DECISION_DEF = re.compile(r"^#{2,6}\s+(D-?(?:[A-Z]+-)?\d{3})\b")
DECISION_REF = re.compile(r"\bD-(?:[A-Z]+-)?\d{3}\b")
# A table row ("| S1 |") or a bullet ("- **Q3. Open.**") defines a spike or question.
ROW_ID_DEF = re.compile(r"^(?:\|\s*|\s*[-*]\s+\**)([SQ]\d+[a-z]?)\b")
RESULT_DEF = re.compile(r"^#{2,6}\s+([SQ]\d+[a-z]?)\b")
ROW_ID_REF = re.compile(r"\b([SQ]\d+[a-z]?)\b")
NUMBERED_DOC = re.compile(r"^\d{2}[a-z]?-.+\.md$")


def slugify(heading: str) -> str:
    """GitHub's anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"[`*_~]|\[([^\]]*)\]\([^)]*\)", r"\1", heading).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def prose_lines(text: str, keep_code_spans: bool = False):
    """Yield (line number, line) outside fenced code blocks, by default with code spans removed."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line if keep_code_spans else re.sub(r"`[^`]*`", "", line)


def anchors(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path not in cache:
        found: set[str] = set()
        counts: dict[str, int] = {}
        for _, line in prose_lines(path.read_text(encoding="utf-8"), keep_code_spans=True):
            match = HEADING.match(line)
            if match:
                slug = slugify(match.group(1))
                # GitHub suffixes repeated headings with -1, -2, ...
                seen = counts.get(slug, 0)
                found.add(slug if seen == 0 else f"{slug}-{seen}")
                counts[slug] = seen + 1
        cache[path] = found
    return cache[path]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    docs = sorted(root.glob("*.md"))
    texts = {doc: doc.read_text(encoding="utf-8") for doc in docs}
    errors: list[str] = []
    warnings: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}

    decisions_defined: set[str] = set()
    rows_defined: set[str] = set()
    for text in texts.values():
        for line in text.splitlines():
            for pattern, bucket in ((DECISION_DEF, decisions_defined), (ROW_ID_DEF, rows_defined), (RESULT_DEF, rows_defined)):
                match = pattern.match(line)
                if match:
                    bucket.add(match.group(1))
    has_rows = bool(rows_defined)

    for doc, text in texts.items():
        name = doc.name
        for number, line in prose_lines(text):
            where = f"{name}:{number}"
            for target in LINK.findall(line):
                # Skip URLs and placeholders such as "(…)" in quoted UI copy.
                if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or not re.search(r"\w", target):
                    continue
                file_part, _, anchor = target.partition("#")
                linked = (doc.parent / file_part).resolve() if file_part else doc
                if not linked.exists():
                    errors.append(f"{where}: link target not found: {target}")
                elif anchor and linked.suffix == ".md" and anchor.lower() not in anchors(linked, anchor_cache):
                    errors.append(f"{where}: anchor not found: {target}")
            if not DECISION_DEF.match(line):
                for ref in DECISION_REF.findall(line):
                    if ref not in decisions_defined:
                        errors.append(f"{where}: {ref} is cited but has no decision heading")
            if has_rows and not ROW_ID_DEF.match(line) and not RESULT_DEF.match(line):
                for ref in ROW_ID_REF.findall(line):
                    if ref not in rows_defined:
                        warnings.append(f"{where}: {ref} is cited but no spike or question row defines it")

    readme = root / "README.md"
    if not readme.exists():
        errors.append("README.md is missing")
    else:
        indexed = {Path(t.partition("#")[0]).name for t in LINK.findall(texts[readme])}
        for doc in docs:
            if (NUMBERED_DOC.match(doc.name) or doc.name == "KICKOFF.md") and doc.name not in indexed:
                errors.append(f"README.md: {doc.name} is not linked from the index")

    for line in errors:
        print(f"error: {line}")
    for line in warnings:
        print(f"warning: {line}")
    print(f"{len(docs)} documents, {len(decisions_defined)} decisions, {len(rows_defined)} spikes/questions: "
          f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
