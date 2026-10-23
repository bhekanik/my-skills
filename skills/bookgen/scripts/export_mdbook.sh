#!/usr/bin/env bash
#
# bookgen/scripts/export_mdbook.sh
# --------------------------------
# Export a BookChain book as an mdBook static-site source tree, ready to
# `mdbook build` or `mdbook serve`.
#
# Reads:
#   <book-repo>/docs/book/*.md             (chapters + introduction)
#   <book-repo>/docs/book/README.md        (TOC; optional, used as preface)
#   <book-repo>/docs/chain/concepts/*.md   (optional chain concept pages)
#   <book-repo>/book-chain.toml            (optional chain metadata)
#
# Writes to:
#   <output-dir>/book.toml          (mdBook config)
#   <output-dir>/src/SUMMARY.md     (mdBook TOC)
#   <output-dir>/src/<chapter>.md   (each chapter, copied)
#   <output-dir>/src/concepts/*.md  (chain concept pages, if present)
#
# Then you can:
#   cd <output-dir>
#   mdbook serve --open    # local preview
#   mdbook build           # static site under <output-dir>/book/
#
# Idempotent: rebuilds from scratch each run (deletes <output-dir>/src/ and
# recreates).
#
# Usage:
#   export_mdbook.sh --book-repo <path> [--output-dir <path>] [--title <text>]
#
# Defaults:
#   --output-dir defaults to <book-repo>/build/mdbook
#   --title      defaults to <book-repo>/docs/book/README.md's H1, or the
#                book repo's directory name.

set -euo pipefail

BOOK_REPO=""
OUTPUT_DIR=""
TITLE=""

usage() {
  sed -n '3,30p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --book-repo) BOOK_REPO="$2"; shift 2 ;;
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    --title) TITLE="$2"; shift 2 ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown arg: $1" >&2; usage 1 ;;
  esac
done

[[ -z "$BOOK_REPO" ]] && { echo "ERROR: --book-repo is required" >&2; exit 1; }
BOOK_REPO="${BOOK_REPO/#\~/$HOME}"
BOOK_REPO="$(cd "$BOOK_REPO" && pwd)"

[[ ! -d "$BOOK_REPO/docs/book" ]] && {
  echo "ERROR: $BOOK_REPO/docs/book not found." >&2
  exit 1
}

if [[ -z "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR="$BOOK_REPO/build/mdbook"
fi
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"

# Resolve title
if [[ -z "$TITLE" ]]; then
  if [[ -f "$BOOK_REPO/docs/book/README.md" ]]; then
    TITLE="$(awk '/^# / { sub(/^# */, ""); print; exit }' "$BOOK_REPO/docs/book/README.md")"
  fi
  if [[ -z "$TITLE" ]]; then
    TITLE="$(basename "$BOOK_REPO")"
  fi
fi

echo "==> mdBook export"
echo "    book repo:  $BOOK_REPO"
echo "    output:     $OUTPUT_DIR"
echo "    title:      $TITLE"

# Wipe and recreate src/
rm -rf "$OUTPUT_DIR/src"
mkdir -p "$OUTPUT_DIR/src"
mkdir -p "$OUTPUT_DIR/src/concepts"

# ---------- book.toml ----------
AUTHOR="$(git -C "$BOOK_REPO" config user.name 2>/dev/null || echo 'BookChain author')"
DESC=""
if [[ -f "$BOOK_REPO/book-chain.toml" ]]; then
  DESC="$(awk -F'=' '/^description\b/ { gsub(/[" ]/, "", $2); print $2; exit }' "$BOOK_REPO/book-chain.toml")"
fi

cat > "$OUTPUT_DIR/book.toml" <<TOML
[book]
title = "$TITLE"
authors = ["$AUTHOR"]
language = "en"
multilingual = false
src = "src"
description = "$DESC"

[output.html]
default-theme = "dark"
preferred-dark-theme = "navy"
git-repository-url = ""
edit-url-template = ""
playground = { editable = false }

[output.html.fold]
enable = true
level = 1

[output.html.search]
enable = true
limit-results = 30
use-boolean-and = true
boost-title = 2

[preprocessor.links]
TOML

# ---------- Copy chapters and build SUMMARY.md ----------
SUMMARY="$OUTPUT_DIR/src/SUMMARY.md"
echo "# Summary" > "$SUMMARY"
echo "" >> "$SUMMARY"

# Copy intro chapters first (00, 00b, 00c) if present, in that order.
for prefix in "00-introduction" "00b-" "00c-"; do
  for src in "$BOOK_REPO/docs/book/${prefix}"*.md; do
    [[ -f "$src" ]] || continue
    name="$(basename "$src")"
    cp "$src" "$OUTPUT_DIR/src/$name"
    title="$(awk '/^# / { sub(/^# */, ""); print; exit }' "$src")"
    echo "- [$title]($name)" >> "$SUMMARY"
  done
done

# Numbered chapters (01-, 02-, ...).
echo "" >> "$SUMMARY"
echo "# Chapters" >> "$SUMMARY"
echo "" >> "$SUMMARY"

for src in "$BOOK_REPO"/docs/book/[0-9][0-9]-*.md; do
  [[ -f "$src" ]] || continue
  name="$(basename "$src")"
  cp "$src" "$OUTPUT_DIR/src/$name"
  title="$(awk '/^# / { sub(/^# */, ""); print; exit }' "$src")"
  num="$(echo "$name" | grep -o '^[0-9]\+')"
  echo "- [$title]($name)" >> "$SUMMARY"
done

# Optional: chain concept pages
if [[ -d "$BOOK_REPO/docs/chain/concepts" ]]; then
  echo "" >> "$SUMMARY"
  echo "# Chain concepts" >> "$SUMMARY"
  echo "" >> "$SUMMARY"
  for src in "$BOOK_REPO"/docs/chain/concepts/*.md; do
    [[ -f "$src" ]] || continue
    name="$(basename "$src")"
    cp "$src" "$OUTPUT_DIR/src/concepts/$name"
    title="$(awk '/^# / { sub(/^# */, ""); print; exit }' "$src")"
    [[ -z "$title" ]] && title="${name%.md}"
    echo "- [$title](concepts/$name)" >> "$SUMMARY"
  done
fi

# ---------- Rewrite relative links so they work in mdBook ----------
# Chapter files reference each other by basename ('next chapter'), which
# already works. We only need to fix:
#   - links to ../implementation/foo.md (point outside; convert to abs URL stub)
#   - links to ../reference/foo.md (same)
#   - wikilinks like [[Foo Bar]] (rare in book chapters; ignore for now)
#
# For now we do the simplest thing: leave the links alone. mdBook will produce
# warnings on broken links, but that's a follow-up issue rather than a blocker.

# ---------- Final report ----------
chapter_count=$(ls "$OUTPUT_DIR/src"/*.md 2>/dev/null | wc -l | tr -d ' ')
concept_count=$(ls "$OUTPUT_DIR/src/concepts"/*.md 2>/dev/null | wc -l | tr -d ' ')

echo
echo "==> Export complete"
echo "    Chapters: $chapter_count"
echo "    Concepts: $concept_count"
echo
echo "Build & preview:"
echo "    cd $OUTPUT_DIR"
echo "    mdbook serve --open"
echo
echo "If mdBook isn't installed: cargo install mdbook"
