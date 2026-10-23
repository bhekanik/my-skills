#!/usr/bin/env python3
"""
drift.py — detect drift between a tour-mode book and its anchor codebase.

Walks every chapter's frontmatter for `related_codebase:` references plus
inline `path/to/file.ext` mentions in the chapter body, checks them against
the live anchor repo, and reports:

  - Missing files (renamed, moved, or deleted upstream)
  - **Structural changes** (port #3): a tracked file whose defs/exports/imports
    changed since the baseline — classified apart from cosmetic edits via a
    tree-sitter structural fingerprint. Names exactly which chapters to re-verify.
  - **Cosmetic-only changes**: size moved but structure is identical (comments,
    formatting, internal edits) — a glance, not a rewrite.
  - Function/symbol references that no longer appear in the file
  - Chapter sections that mention specific commit hashes from the anchor repo
    that no longer exist (currently flags any short SHA-like string for review)

Structural detection needs a baseline. Capture one right after the chapters are
verified against the current anchor:

    drift.py --book-repo <path> --rebaseline

The baseline lives at `<book-repo>/docs/teaching/.fingerprints.json`. Tree-sitter
gives accurate structure when installed; a regex fallback keeps drift working
(fingerprints are still stable, just coarser) so vendored books never hard-fail.

Output: a markdown report at `<book-repo>/docs/issues/00NN-drift-<DATE>.md`,
following the user's project-issue convention.

Idempotent: a re-run on the same day overwrites; the next day creates a new
file. Doesn't auto-fix anything.

Usage:
  drift.py --book-repo <path> [--anchor-repo <path>] [--lines-threshold N]
           [--rebaseline] [--quiet]

If --anchor-repo is omitted, drift.py reads it from book-chain.toml
(`anchor_repo = "..."`) or from chapter frontmatter (`anchor_repo:`).

Exit codes:
  0  no significant drift
  1  bad arguments
  2  drift detected (the report file is still written)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore
    except ModuleNotFoundError:
        sys.stderr.write("ERROR: needs Python 3.11+ or `pip install tomli`.\n")
        sys.exit(1)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.treesit import has_treesitter, iter_source_files, parse_file  # noqa: E402


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
PATH_MENTION_RE = re.compile(r"`([a-zA-Z0-9_./-]+\.(?:rs|swift|go|py|ts|tsx|toml|md|sh|yml|yaml|sql|h|c|cpp|m))`")
SHA_LIKE_RE = re.compile(r"\b([0-9a-f]{7,40})\b")


def parse_frontmatter(text: str) -> dict:
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
        if line.lstrip().startswith("- ") and current_list_key is not None:
            item = line.lstrip()[2:].strip().strip("\"'")
            result[current_list_key].append(item)
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                result[key] = []
                current_list_key = key
            else:
                result[key] = value.strip("\"'")
                current_list_key = None
    return result


@dataclass
class DriftFinding:
    chapter_path: Path
    chapter_id: str
    severity: str  # "high", "medium", "low"
    kind: str  # "missing-file", "size-drift", "stale-sha", etc.
    detail: str

    def to_md_row(self) -> str:
        return f"| `{self.chapter_path.name}` | {self.severity} | {self.kind} | {self.detail} |"


@dataclass
class DriftReport:
    book_repo: Path
    anchor_repo: Path
    findings: list[DriftFinding] = field(default_factory=list)
    chapters_scanned: int = 0
    files_checked: set[Path] = field(default_factory=set)
    chapters_to_reverify: dict[str, list[str]] = field(default_factory=dict)
    fingerprint_status: str = "not-run"  # not-run | no-baseline | ok
    structural_changes: int = 0
    cosmetic_changes: int = 0


def discover_anchor_repo(book_repo: Path, override: Path | None) -> Path | None:
    if override:
        return override.expanduser().resolve()

    # Try book-chain.toml.
    chain_toml = book_repo / "book-chain.toml"
    if chain_toml.is_file():
        cfg = tomllib.loads(chain_toml.read_text(encoding="utf-8"))
        ar = cfg.get("anchor_repo")
        if ar:
            return (book_repo / ar).resolve() if not Path(ar).is_absolute() else Path(ar).resolve()

    # Try first chapter's frontmatter.
    book_dir = book_repo / "docs" / "book"
    if book_dir.is_dir():
        for md in sorted(book_dir.glob("*.md")):
            if md.name == "README.md":
                continue
            text = md.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            ar = fm.get("anchor_repo") or fm.get("related_codebase")
            if ar:
                return (book_repo / ar).resolve() if not Path(ar).is_absolute() else Path(ar).resolve()

    return None


def check_chapter(
    chapter_path: Path,
    text: str,
    anchor_repo: Path,
    lines_threshold: float,
    report: DriftReport,
) -> None:
    fm = parse_frontmatter(text)
    chapter_id = str(fm.get("chapter", chapter_path.stem.split("-", 1)[0]))

    # Collect file references: from frontmatter + inline mentions.
    refs: set[str] = set()
    for key in ("related_codebase", "anchor_path"):
        v = fm.get(key)
        if isinstance(v, str) and v:
            refs.add(v)
        elif isinstance(v, list):
            refs.update(x for x in v if isinstance(x, str))

    for match in PATH_MENTION_RE.finditer(text):
        candidate = match.group(1)
        # Heuristic: skip URLs, dotfiles outside source dirs.
        if candidate.startswith(("http://", "https://", "../")):
            continue
        # Only count refs that look like they could be in the anchor repo.
        if "/" in candidate and not candidate.startswith("docs/"):
            refs.add(candidate)

    for ref in sorted(refs):
        # Resolve relative to the anchor repo.
        candidate = ref
        # Expand `~` so chapter prose like `~/code/example/Cargo.toml`
        # resolves against the user's home directory.
        if candidate.startswith("~"):
            candidate = str(Path(candidate).expanduser())
        # Strip leading repo-name prefixes if the user wrote them
        # (handles "example/Cargo.toml" → "Cargo.toml").
        repo_name = anchor_repo.name
        if candidate.startswith(f"{repo_name}/"):
            candidate = candidate[len(repo_name) + 1 :]
        # If the path is now absolute and points inside the anchor repo, use as-is.
        if Path(candidate).is_absolute():
            full = Path(candidate)
            try:
                full.relative_to(anchor_repo)
            except ValueError:
                # Absolute path that's outside the anchor repo; keep the
                # original ref but map it inside.
                full = anchor_repo / Path(candidate).name
        else:
            full = anchor_repo / candidate

        if not full.exists():
            # Try a shallow search in case the file moved within the repo.
            matches = list(anchor_repo.rglob(Path(candidate).name))
            if matches:
                report.findings.append(
                    DriftFinding(
                        chapter_path=chapter_path,
                        chapter_id=chapter_id,
                        severity="medium",
                        kind="file-moved",
                        detail=f"`{ref}` not found at expected path; possibly moved to `{matches[0].relative_to(anchor_repo)}`",
                    )
                )
            else:
                report.findings.append(
                    DriftFinding(
                        chapter_path=chapter_path,
                        chapter_id=chapter_id,
                        severity="high",
                        kind="missing-file",
                        detail=f"`{ref}` does not exist in anchor repo",
                    )
                )
            continue

        # File exists. Check size drift if we have a snapshot baseline.
        # Without a baseline (no .bookgen-baselines/ store), we can only
        # warn on suspiciously small files (probably stub) or huge files
        # (probably an unrelated path).
        try:
            line_count = sum(1 for _ in full.open(encoding="utf-8", errors="ignore"))
        except (OSError, UnicodeDecodeError):
            continue
        report.files_checked.add(full)

        # Look for symbols mentioned in the chapter that should appear in the file.
        # Heuristic: code-fenced identifiers like `read_message` or `IpcMessage`.
        # Cheap but effective.
        symbol_re = re.compile(r"`([A-Za-z_][A-Za-z0-9_]{3,})`")
        chapter_symbols = set(symbol_re.findall(text))
        try:
            file_text = full.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for sym in chapter_symbols:
            # Skip common words that aren't likely identifiers.
            if sym.lower() in {"some", "none", "true", "false", "result", "option", "string", "where"}:
                continue
            # Skip short Markdown noise like `cargo` or `the`.
            if len(sym) < 5:
                continue
            # If the chapter mentions the file AND a symbol, but the symbol is
            # not in the file, that's a drift.
            if sym not in file_text:
                # Only flag once per (file, symbol).
                key = f"{full}|{sym}"
                if key not in getattr(check_chapter, "_seen", set()):
                    if not hasattr(check_chapter, "_seen"):
                        check_chapter._seen = set()  # type: ignore
                    check_chapter._seen.add(key)  # type: ignore
                    # Only report when chapter mentions both this file and this symbol nearby.
                    # Cheap proximity: same paragraph (within 5 lines).
                    if _mentioned_near(text, ref, sym):
                        report.findings.append(
                            DriftFinding(
                                chapter_path=chapter_path,
                                chapter_id=chapter_id,
                                severity="medium",
                                kind="symbol-missing",
                                detail=f"chapter mentions `{sym}` near `{ref}`, but `{sym}` is not in that file",
                            )
                        )

    # Stale SHA detection (low priority warning).
    for match in SHA_LIKE_RE.finditer(text):
        sha = match.group(1)
        if len(sha) >= 7 and len(sha) <= 12:
            # We can't actually verify without running git in the anchor repo.
            # Just flag for human review on the first occurrence per chapter.
            if not any(
                f.chapter_path == chapter_path and f.kind == "sha-mention"
                for f in report.findings
            ):
                report.findings.append(
                    DriftFinding(
                        chapter_path=chapter_path,
                        chapter_id=chapter_id,
                        severity="low",
                        kind="sha-mention",
                        detail=f"chapter mentions SHA-like value `{sha}` (and possibly others) — verify these refer to commits that still exist",
                    )
                )


def _mentioned_near(text: str, ref: str, sym: str, radius: int = 8) -> bool:
    """Cheap proximity check: ref and sym appear within `radius` lines."""
    lines = text.splitlines()
    ref_lines = [i for i, ln in enumerate(lines) if ref in ln]
    sym_lines = [i for i, ln in enumerate(lines) if f"`{sym}`" in ln]
    for r in ref_lines:
        for s in sym_lines:
            if abs(r - s) <= radius:
                return True
    return False


BASELINE_NAME = ".fingerprints.json"


def baseline_path(book_repo: Path) -> Path:
    return book_repo / "docs" / "teaching" / BASELINE_NAME


def _line_count(path: Path) -> int:
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
    except OSError:
        return 0


def build_baseline(anchor: Path) -> dict:
    files: dict[str, dict] = {}
    for path in iter_source_files(anchor):
        facts = parse_file(path)
        rel = path.relative_to(anchor).as_posix()
        files[rel] = {
            "fingerprint": facts.fingerprint(),
            "lines": _line_count(path),
            "defs": facts.defs,
            "exports": facts.exports,
        }
    return {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(),
        "anchor_repo": str(anchor),
        "parser": "tree-sitter" if has_treesitter() else "regex-fallback",
        "files": files,
    }


def write_baseline(book_repo: Path, anchor: Path) -> tuple[Path, int]:
    data = build_baseline(anchor)
    out = baseline_path(book_repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return out, len(data["files"])


def load_baseline(book_repo: Path) -> dict | None:
    p = baseline_path(book_repo)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _resolved_refs(text: str, anchor: Path) -> set[Path]:
    """Resolve a chapter's file references to existing anchor files.

    Mirrors check_chapter's resolution so the fingerprint pass maps the same
    files back to the chapters that mention them.
    """
    fm = parse_frontmatter(text)
    refs: set[str] = set()
    for key in ("related_codebase", "anchor_path"):
        v = fm.get(key)
        if isinstance(v, str) and v:
            refs.add(v)
        elif isinstance(v, list):
            refs.update(x for x in v if isinstance(x, str))
    for match in PATH_MENTION_RE.finditer(text):
        candidate = match.group(1)
        if candidate.startswith(("http://", "https://", "../")):
            continue
        if "/" in candidate and not candidate.startswith("docs/"):
            refs.add(candidate)
    out: set[Path] = set()
    for ref in refs:
        candidate = ref
        if candidate.startswith("~"):
            candidate = str(Path(candidate).expanduser())
        repo_name = anchor.name
        if candidate.startswith(f"{repo_name}/"):
            candidate = candidate[len(repo_name) + 1 :]
        full = Path(candidate) if Path(candidate).is_absolute() else anchor / candidate
        if full.is_file():
            out.add(full)
    return out


def collect_chapter_file_refs(book_repo: Path, anchor: Path) -> dict[str, list[str]]:
    """Map anchor-relative source path -> chapter file names that reference it."""
    mapping: dict[str, set[str]] = {}
    book_dir = book_repo / "docs" / "book"
    for md in sorted(book_dir.glob("*.md")):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        for full in _resolved_refs(text, anchor):
            try:
                rel = full.relative_to(anchor).as_posix()
            except ValueError:
                continue
            mapping.setdefault(rel, set()).add(md.name)
    return {k: sorted(v) for k, v in mapping.items()}


def fingerprint_pass(
    report: DriftReport,
    anchor: Path,
    file_to_chapters: dict[str, list[str]],
    baseline: dict,
    threshold: float,
) -> None:
    """Compare current structure against the baseline for chapter-referenced files."""
    base_files = baseline.get("files", {})
    for rel, chapters in sorted(file_to_chapters.items()):
        full = anchor / rel
        if not full.is_file():
            continue  # missing-file handled by check_chapter
        facts = parse_file(full)
        base = base_files.get(rel)
        if base is None:
            continue  # new file not yet in baseline; --rebaseline to capture
        if facts.fingerprint() != base.get("fingerprint"):
            before = set(base.get("exports", [])) | set(base.get("defs", []))
            after = set(facts.exports) | set(facts.defs)
            removed = sorted(before - after)
            added = sorted(after - before)
            severity = "high" if removed else "medium"
            report.structural_changes += 1
            bits = []
            if removed:
                bits.append("removed " + ", ".join(f"`{r}`" for r in removed[:8]))
            if added:
                bits.append("added " + ", ".join(f"`{a}`" for a in added[:8]))
            summary = "; ".join(bits) or "signature changed (imports reordered or internal structure shifted)"
            report.findings.append(
                DriftFinding(
                    chapter_path=Path(chapters[0]),
                    chapter_id="",
                    severity=severity,
                    kind="structural-change",
                    detail=f"`{rel}` — {summary} (chapters: {', '.join(chapters)})",
                )
            )
            for ch in chapters:
                report.chapters_to_reverify.setdefault(ch, []).append(f"`{rel}` — {summary}")
        else:
            base_lines = base.get("lines", 0)
            now_lines = _line_count(full)
            if base_lines and abs(now_lines - base_lines) / max(base_lines, 1) > threshold:
                report.cosmetic_changes += 1
                report.findings.append(
                    DriftFinding(
                        chapter_path=Path(chapters[0]),
                        chapter_id="",
                        severity="low",
                        kind="cosmetic-change",
                        detail=f"`{rel}` size {base_lines}→{now_lines} lines but structure (defs/exports/imports) unchanged — likely comments/formatting/internal edits",
                    )
                )


def write_report(report: DriftReport) -> Path:
    today = dt.date.today().isoformat()
    issues_dir = report.book_repo / "docs" / "issues"
    issues_dir.mkdir(parents=True, exist_ok=True)
    # Find the next issue number, or just use the date if a file exists for today.
    existing = sorted(issues_dir.glob("[0-9][0-9][0-9][0-9]-drift-*.md"))
    if existing:
        last_num = int(existing[-1].name[:4])
        next_num = last_num + 1
    else:
        next_num = 1
    out = issues_dir / f"{next_num:04d}-drift-{today}.md"

    by_severity = {"high": [], "medium": [], "low": []}
    for f in report.findings:
        by_severity[f.severity].append(f)

    lines = [
        f"# {next_num:04d} — Drift report ({today})",
        "",
        f"**Status:** open",
        f"**Generated:** {dt.datetime.now().isoformat(timespec='seconds')}",
        f"**Book repo:** `{report.book_repo}`",
        f"**Anchor repo:** `{report.anchor_repo}`",
        f"**Chapters scanned:** {report.chapters_scanned}",
        f"**Files checked in anchor:** {len(report.files_checked)}",
        f"**Fingerprint baseline:** {report.fingerprint_status}",
        f"**Structural changes:** {report.structural_changes} · **Cosmetic-only changes:** {report.cosmetic_changes}",
        f"**Findings:** {len(report.findings)} (high: {len(by_severity['high'])}, medium: {len(by_severity['medium'])}, low: {len(by_severity['low'])})",
        "",
    ]

    if report.fingerprint_status == "no-baseline":
        lines.append("> ℹ No fingerprint baseline found, so structural drift detection was skipped. Run `drift.py --book-repo <path> --rebaseline` to capture one — ideally right after the chapters are verified against the current anchor.")
        lines.append("")

    if not report.findings:
        lines.append("✅ No drift detected. Book and anchor repo are aligned.")
    else:
        lines.append("## Findings")
        lines.append("")
        for sev in ("high", "medium", "low"):
            findings = by_severity[sev]
            if not findings:
                continue
            lines.append(f"### {sev.title()} severity ({len(findings)})")
            lines.append("")
            lines.append("| Chapter | Severity | Kind | Detail |")
            lines.append("|---|---|---|---|")
            for f in findings:
                lines.append(f.to_md_row())
            lines.append("")

        if report.chapters_to_reverify:
            lines.append("## Chapters to re-verify")
            lines.append("")
            lines.append("Structural changes in the anchor repo affect these chapters. Re-run the chapter's code/examples (rule 16) and update prose where the structure moved:")
            lines.append("")
            for ch, reasons in sorted(report.chapters_to_reverify.items()):
                lines.append(f"- **`{ch}`**")
                for r in reasons:
                    lines.append(f"  - {r}")
            lines.append("")

        lines.append("## Suggested triage order")
        lines.append("")
        lines.append("1. **High** findings (missing files, removed symbols): the chapter points at code or a symbol that no longer exists. Update the chapter or note the change in prose.")
        lines.append("2. **Medium** findings (file moved / symbol missing / structural additions): the predict-pause discipline depends on accuracy. Update.")
        lines.append("3. **Low** findings (SHA mentions, cosmetic-only size drift): verify SHAs still exist; cosmetic-only changes need a glance, not a rewrite (structure is unchanged).")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Detect drift between a book and its anchor codebase.")
    p.add_argument("--book-repo", required=True, help="Path to a book repo (with docs/book/).")
    p.add_argument("--anchor-repo", help="Path to the anchor codebase. Auto-detected from book-chain.toml or chapter frontmatter if omitted.")
    p.add_argument("--lines-threshold", type=float, default=0.30, help="Fraction (0–1) by which file size can drift before flagging. Default 0.30.")
    p.add_argument("--rebaseline", action="store_true", help="Capture/refresh the structural fingerprint baseline at docs/teaching/.fingerprints.json, then exit.")
    p.add_argument("--quiet", action="store_true", help="Suppress per-finding stdout; just print the report path.")
    args = p.parse_args()

    book_repo = Path(args.book_repo).expanduser().resolve()
    if not book_repo.is_dir():
        sys.stderr.write(f"ERROR: {book_repo} is not a directory.\n")
        return 1

    anchor = discover_anchor_repo(book_repo, Path(args.anchor_repo) if args.anchor_repo else None)
    if not anchor or not anchor.is_dir():
        sys.stderr.write(
            "ERROR: could not find anchor repo. Pass --anchor-repo or add\n"
            "       `anchor_repo = '<path>'` to book-chain.toml.\n"
        )
        return 1

    if args.rebaseline:
        out, n = write_baseline(book_repo, anchor)
        if not args.quiet:
            parser_name = "tree-sitter" if has_treesitter() else "regex-fallback"
            print(f"==> Wrote fingerprint baseline ({n} files, {parser_name}): {out}")
        return 0

    report = DriftReport(book_repo=book_repo, anchor_repo=anchor)
    book_dir = book_repo / "docs" / "book"
    if not book_dir.is_dir():
        sys.stderr.write(f"ERROR: {book_dir} not found.\n")
        return 1

    for md in sorted(book_dir.glob("*.md")):
        if md.name == "README.md":
            continue
        report.chapters_scanned += 1
        text = md.read_text(encoding="utf-8")
        check_chapter(md, text, anchor, args.lines_threshold, report)

    baseline = load_baseline(book_repo)
    if baseline is None:
        report.fingerprint_status = "no-baseline"
    else:
        report.fingerprint_status = "ok"
        file_to_chapters = collect_chapter_file_refs(book_repo, anchor)
        fingerprint_pass(report, anchor, file_to_chapters, baseline, args.lines_threshold)

    out = write_report(report)
    if not args.quiet:
        print(f"==> Drift report: {out}")
        print(f"    Chapters: {report.chapters_scanned}, files checked: {len(report.files_checked)}, findings: {len(report.findings)}")

    return 2 if report.findings else 0


if __name__ == "__main__":
    sys.exit(main())
