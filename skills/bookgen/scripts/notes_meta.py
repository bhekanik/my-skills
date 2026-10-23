#!/usr/bin/env python3
"""
notes_meta.py — aggregate teaching-notes patterns across multiple sessions.

A teaching-notes file at `docs/teaching/notes/<NN>-<title>.md` accumulates
session-specific insights every time a chapter is taught: common wrong
predictions, sticky points, refinement ideas. After 3+ sessions, patterns
emerge that aren't visible from any single session.

This script reads all teaching-notes files in a book and aggregates:

  - Common wrong predictions that appear across multiple sessions
  - Sticky points that recurred (chapter sections that consistently
    needed a second pass)
  - Refinement ideas that are eligible for promotion (mentioned 3+
    times across sessions)
  - Chapters where the artifact didn't land

Output: a markdown report at `<book-repo>/docs/teaching/notes-meta-<DATE>.md`.

Usage:
  notes_meta.py --book-repo <path> [--chapter NN] [--threshold N]
                [--quiet]

  --chapter NN     Only analyse a specific chapter (default: all).
  --threshold N    Number of session occurrences before a pattern is
                   "recurring" (default: 2).

Exit codes:
  0  success
  1  bad arguments
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
TABLE_HEADER_RE = re.compile(
    r"\|\s*Predict question\s*\|\s*Common wrong answer\s*\|", re.IGNORECASE
)
SECTION_RE = re.compile(r"^##+ (.+?)$", re.MULTILINE)


@dataclass
class WrongPrediction:
    chapter: str
    predict_question: str
    wrong_answer: str
    why: str
    calibration: str
    raw_row: str


@dataclass
class StickyPoint:
    chapter: str
    text: str


@dataclass
class RefinementIdea:
    chapter: str
    text: str


@dataclass
class ArtifactStatus:
    chapter: str
    landed: bool
    note: str


@dataclass
class NotesMeta:
    book_repo: Path
    chapters_analysed: list[str] = field(default_factory=list)
    wrong_predictions: list[WrongPrediction] = field(default_factory=list)
    sticky_points: list[StickyPoint] = field(default_factory=list)
    refinement_ideas: list[RefinementIdea] = field(default_factory=list)
    artifacts: list[ArtifactStatus] = field(default_factory=list)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    body = m.group(1)
    result: dict = {}
    for raw in body.splitlines():
        line = raw.rstrip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        result[key.strip()] = value.strip().strip("\"'")
    return result


def split_sections(text: str) -> dict[str, str]:
    """Split markdown into a dict of {section-heading: body}."""
    sections: dict[str, str] = {}
    current_heading = "_preamble"
    current_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        m = re.match(r"^(##+)\s+(.+)$", line.rstrip())
        if m:
            sections[current_heading] = "".join(current_lines)
            current_heading = m.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)
    sections[current_heading] = "".join(current_lines)
    return sections


def extract_table_rows(section_body: str) -> list[list[str]]:
    """Extract rows from a markdown pipe-table. Returns list of cell lists."""
    rows: list[list[str]] = []
    in_table = False
    for raw in section_body.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            in_table = False
            continue
        # Skip alignment row
        if re.match(r"^\|[\s\-:|]+\|$", line):
            in_table = True
            continue
        if line.endswith("|"):
            cells = [c.strip() for c in line[1:-1].split("|")]
            if len(cells) >= 2 and not all(c == "" for c in cells):
                rows.append(cells)
    # First row is the header in pure-pipe tables; drop if it looks like one
    if rows and any(
        re.match(r"^[a-z]", c, re.IGNORECASE) for c in rows[0][:1]
    ) and "|" not in section_body.splitlines()[0]:
        # Heuristic: it's already a header. Skip first row if its first
        # cell matches "Predict question" etc.
        if rows and rows[0][0].lower().startswith(("predict", "question", "predict question")):
            rows = rows[1:]
    return rows


def analyse_notes_file(path: Path, meta: NotesMeta) -> None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    chapter = fm.get("chapter", path.stem.split("-", 1)[0])
    title = fm.get("title", path.stem)
    chapter_label = f"{chapter} ({title})"
    meta.chapters_analysed.append(chapter_label)

    sections = split_sections(text)

    # Common wrong predictions
    for heading, body in sections.items():
        if heading.lower().startswith("common wrong predictions"):
            rows = extract_table_rows(body)
            for row in rows:
                # Tolerate variable column counts.
                cells = row + [""] * (4 - len(row))
                if cells[0].lower().startswith(("predict question", "question")):
                    continue
                if cells[0] == "" or cells[0].startswith("(filled"):
                    continue
                meta.wrong_predictions.append(
                    WrongPrediction(
                        chapter=chapter_label,
                        predict_question=cells[0],
                        wrong_answer=cells[1] if len(cells) > 1 else "",
                        why=cells[2] if len(cells) > 2 else "",
                        calibration=cells[3] if len(cells) > 3 else "",
                        raw_row=" | ".join(cells),
                    )
                )

    # Sticky points
    for heading, body in sections.items():
        if heading.lower().startswith("sticky points"):
            for ln in body.splitlines():
                t = ln.strip()
                if t.startswith(("-", "*")) and len(t) > 5:
                    meta.sticky_points.append(
                        StickyPoint(chapter=chapter_label, text=t.lstrip("-* ").strip())
                    )

    # Refinement ideas
    for heading, body in sections.items():
        if heading.lower().startswith("refinement"):
            for ln in body.splitlines():
                t = ln.strip()
                if t.startswith("- [") and len(t) > 5:
                    meta.refinement_ideas.append(
                        RefinementIdea(chapter=chapter_label, text=t)
                    )

    # Did the artifact land?
    for heading, body in sections.items():
        if heading.lower().startswith("did the artifact land"):
            body_clean = body.strip()
            if body_clean and not body_clean.startswith("("):
                landed = "✅" in body_clean or "yes" in body_clean.lower()[:30]
                meta.artifacts.append(
                    ArtifactStatus(
                        chapter=chapter_label,
                        landed=landed,
                        note=body_clean[:300],
                    )
                )


def write_meta_report(meta: NotesMeta, threshold: int) -> Path:
    today = dt.date.today().isoformat()
    out_dir = meta.book_repo / "docs" / "teaching"
    out = out_dir / f"notes-meta-{today}.md"

    lines = [
        f"# Notes meta-pass — {today}",
        "",
        f"_Aggregating teaching-notes patterns across {len(meta.chapters_analysed)} chapters._",
        "",
    ]

    # ---- Cross-chapter wrong-prediction patterns ----
    # Group by predict question (rough match on first 60 chars to deduplicate
    # near-identical questions).
    by_question: dict[str, list[WrongPrediction]] = defaultdict(list)
    for wp in meta.wrong_predictions:
        key = wp.predict_question[:60].lower().strip()
        by_question[key].append(wp)

    recurring_qs = [
        (q, ws) for q, ws in by_question.items() if len({w.chapter for w in ws}) >= threshold
    ]
    lines.append(f"## Recurring wrong-prediction patterns (≥{threshold} chapters)")
    lines.append("")
    if recurring_qs:
        for q_prefix, group in sorted(recurring_qs, key=lambda x: -len(x[1])):
            lines.append(f"### Question: {group[0].predict_question}")
            lines.append("")
            lines.append(f"_Appears in {len({w.chapter for w in group})} chapters._")
            lines.append("")
            lines.append("| Chapter | Wrong answer | Why | How calibrated |")
            lines.append("|---|---|---|---|")
            for wp in group:
                lines.append(
                    f"| {wp.chapter} | {wp.wrong_answer} | {wp.why} | {wp.calibration} |"
                )
            lines.append("")
            lines.append("**Suggested action:** if the same wrong answer appears in 3+ chapters, the chapter that *first* introduces this concept could probably pre-empt the misunderstanding more strongly.")
            lines.append("")
    else:
        lines.append(f"_No predict question recurs across ≥{threshold} chapters yet (or not enough sessions taught)._")
        lines.append("")

    # ---- Sticky points by chapter ----
    lines.append("## Sticky points by chapter")
    lines.append("")
    by_chapter: dict[str, list[StickyPoint]] = defaultdict(list)
    for sp in meta.sticky_points:
        by_chapter[sp.chapter].append(sp)
    if by_chapter:
        for chapter, sps in sorted(by_chapter.items()):
            lines.append(f"### {chapter}")
            lines.append("")
            for sp in sps:
                lines.append(f"- {sp.text}")
            lines.append("")
    else:
        lines.append("_No sticky points logged yet._")
        lines.append("")

    # ---- Refinement ideas eligible for promotion ----
    lines.append(f"## Refinement ideas (across {len(meta.refinement_ideas)} ideas, all chapters)")
    lines.append("")
    if meta.refinement_ideas:
        for ri in meta.refinement_ideas:
            lines.append(f"- **{ri.chapter}**: {ri.text}")
        lines.append("")
        lines.append("**Suggested action:** any refinement idea that's been logged 3+ times (manual count) is eligible for promotion to a chapter revision.")
    else:
        lines.append("_No refinement ideas logged yet._")
    lines.append("")

    # ---- Artifact landing summary ----
    lines.append("## Artifact landing")
    lines.append("")
    if meta.artifacts:
        landed = sum(1 for a in meta.artifacts if a.landed)
        total = len(meta.artifacts)
        lines.append(f"_{landed}/{total} chapter artifacts landed cleanly._")
        lines.append("")
        for a in meta.artifacts:
            badge = "✅" if a.landed else "⚠️"
            lines.append(f"- {badge} **{a.chapter}**: {a.note[:160].splitlines()[0] if a.note else 'no note'}")
        lines.append("")
        non_landing = [a for a in meta.artifacts if not a.landed]
        if non_landing:
            lines.append("**Suggested action:** chapters where the artifact didn't land deserve a chapter revision before they're taught again. Common causes: too much new content, missing prerequisite, or environmental drift in the anchor codebase.")
    else:
        lines.append("_No artifact-landing notes logged yet._")
    lines.append("")

    # ---- Coverage summary ----
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Chapters analysed: {len(meta.chapters_analysed)}")
    lines.append(f"- Wrong predictions logged: {len(meta.wrong_predictions)}")
    lines.append(f"- Sticky points logged: {len(meta.sticky_points)}")
    lines.append(f"- Refinement ideas: {len(meta.refinement_ideas)}")
    lines.append(f"- Artifact-landing notes: {len(meta.artifacts)}")
    lines.append("")
    lines.append("(Most stub teaching-notes files won't have data yet. The meta-pass becomes useful after sessions have been taught and notes have accumulated.)")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Aggregate teaching-notes patterns across sessions.")
    p.add_argument("--book-repo", required=True, help="Path to a book repo (with docs/teaching/notes/).")
    p.add_argument("--chapter", help="Only analyse a specific chapter ID (e.g., 04).")
    p.add_argument("--threshold", type=int, default=2, help="Number of cross-chapter occurrences to flag a pattern as 'recurring'. Default 2.")
    p.add_argument("--quiet", action="store_true", help="Suppress stdout; just print report path.")
    args = p.parse_args()

    book_repo = Path(args.book_repo).expanduser().resolve()
    notes_dir = book_repo / "docs" / "teaching" / "notes"
    if not notes_dir.is_dir():
        sys.stderr.write(f"ERROR: {notes_dir} not found.\n")
        return 1

    meta = NotesMeta(book_repo=book_repo)

    candidates = sorted(notes_dir.glob("*.md"))
    if args.chapter:
        chapter_str = str(args.chapter).zfill(2)
        candidates = [c for c in candidates if c.name.startswith(chapter_str)]
        if not candidates:
            sys.stderr.write(f"ERROR: no notes file found for chapter {args.chapter}\n")
            return 1

    for path in candidates:
        analyse_notes_file(path, meta)

    out = write_meta_report(meta, args.threshold)

    if not args.quiet:
        print(f"==> Notes meta-pass: {out}")
        print(
            f"    Chapters analysed: {len(meta.chapters_analysed)}, "
            f"wrong predictions: {len(meta.wrong_predictions)}, "
            f"sticky points: {len(meta.sticky_points)}, "
            f"refinement ideas: {len(meta.refinement_ideas)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
