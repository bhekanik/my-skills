#!/usr/bin/env bash
#
# bookgen/scripts/scaffold.sh
# ---------------------------
# Scaffold the mechanical parts of a learn-by-LLM book repo.
# Idempotent: re-running with same args is a no-op.
#
# Resolves issue 0001 in the bookgen skill: the directory tree, vendored
# skills, VERSION file, anchor table, build philosophy, and the optional
# first commit.
#
# Does NOT write seed chapters (00-introduction, 00b-what-is-X, 00c-why,
# 01-X). Those still get written by the agent because they need the
# learner's specific motivation, prior-language pains, and architecture.
#
# Usage:
#   scaffold.sh \
#     --output-dir <path> \
#     --target-language <rust|go|swift|swiftui|zig|ocaml|elixir> \
#     --anchor-repo <path-or-url> \
#     --mode <reproduce|tour|extend> \
#     [--framework <name>] \
#     [--commit] \
#     [--bookgen-skill-dir <path>] \
#     [--teaching-skill-dir <path>] \
#     [--humanizer-skill-dir <path>]
#
# Exits non-zero on bad args; idempotent on success.

set -euo pipefail

# ---------------------------------------------------------------- defaults

OUTPUT_DIR=""
TARGET_LANGUAGE=""
ANCHOR_REPO=""
MODE=""
FRAMEWORK=""
COMMIT=false

BOOKGEN_DIR="${BOOKGEN_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
TEACHING_DIR="${TEACHING_DIR:-$BOOKGEN_DIR/../teaching}"
HUMANIZER_DIR="${HUMANIZER_DIR:-}"

# ----------------------------------------------------------------- parse args

usage() {
  sed -n '3,30p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --output-dir)            OUTPUT_DIR="$2"; shift 2 ;;
    --target-language)       TARGET_LANGUAGE="$2"; shift 2 ;;
    --anchor-repo)           ANCHOR_REPO="$2"; shift 2 ;;
    --mode)                  MODE="$2"; shift 2 ;;
    --framework)             FRAMEWORK="$2"; shift 2 ;;
    --commit)                COMMIT=true; shift ;;
    --bookgen-skill-dir)     BOOKGEN_DIR="$2"; shift 2 ;;
    --teaching-skill-dir)    TEACHING_DIR="$2"; shift 2 ;;
    --humanizer-skill-dir)   HUMANIZER_DIR="$2"; shift 2 ;;
    -h|--help)               usage 0 ;;
    *)                       echo "Unknown arg: $1" >&2; usage 1 ;;
  esac
done

# --------------------------------------------------------------- validate args

[[ -z "$OUTPUT_DIR" ]]      && { echo "ERROR: --output-dir is required" >&2; exit 1; }
[[ -z "$TARGET_LANGUAGE" ]] && { echo "ERROR: --target-language is required" >&2; exit 1; }
[[ -z "$ANCHOR_REPO" ]]     && { echo "ERROR: --anchor-repo is required" >&2; exit 1; }
[[ -z "$MODE" ]]            && { echo "ERROR: --mode is required" >&2; exit 1; }

case "$MODE" in
  reproduce|tour|extend) ;;
  *) echo "ERROR: --mode must be one of: reproduce, tour, extend" >&2; exit 1 ;;
esac

# Anchor table for the language must exist
ANCHOR_TABLE_SRC="$BOOKGEN_DIR/references/anchor-tables/${TARGET_LANGUAGE}.md"
if [[ ! -f "$ANCHOR_TABLE_SRC" ]]; then
  echo "ERROR: no anchor table for '$TARGET_LANGUAGE' at $ANCHOR_TABLE_SRC" >&2
  echo "       supported: $(ls "$BOOKGEN_DIR/references/anchor-tables/" | sed 's/\.md$//' | tr '\n' ' ')" >&2
  exit 1
fi

# Vendored skills must exist
[[ ! -d "$TEACHING_DIR" ]]  && { echo "ERROR: teaching skill not found at $TEACHING_DIR" >&2; exit 1; }
[[ -n "$HUMANIZER_DIR" && ! -d "$HUMANIZER_DIR" ]] && { echo "ERROR: humanizer skill not found at $HUMANIZER_DIR" >&2; exit 1; }

# ------------------------------------------------------------------ resolve

# Expand ~ in OUTPUT_DIR
OUTPUT_DIR="${OUTPUT_DIR/#\~/$HOME}"
ANCHOR_REPO_DISPLAY="$ANCHOR_REPO"
if [[ "$ANCHOR_REPO" =~ ^~ ]]; then
  ANCHOR_REPO="${ANCHOR_REPO/#\~/$HOME}"
fi

mkdir -p "$OUTPUT_DIR"
cd "$OUTPUT_DIR"

echo "==> bookgen scaffold"
echo "    output:    $OUTPUT_DIR"
echo "    language:  $TARGET_LANGUAGE"
echo "    anchor:    $ANCHOR_REPO_DISPLAY"
echo "    mode:      $MODE"
echo "    commit:    $COMMIT"
echo

# -------------------------------------------------------- directory tree

mkdir -p "$OUTPUT_DIR"/{docs/book,docs/teaching/notes,.skills}

# --------------------------------------------------------- vendor skills

# Use rsync for idempotent re-copy without re-creating dirs unnecessarily.
# Falls back to cp -R if rsync isn't available.
copy_skill() {
  local src="$1" dst="$2"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$src/" "$dst/"
  else
    rm -rf "$dst"
    cp -R "$src" "$dst"
  fi
}

echo "==> Vendoring teaching skill"
copy_skill "$TEACHING_DIR" "$OUTPUT_DIR/.skills/teaching"

if [[ -n "$HUMANIZER_DIR" ]]; then
  echo "==> Vendoring optional humanizer skill"
  copy_skill "$HUMANIZER_DIR" "$OUTPUT_DIR/.skills/humanizer"
fi

# Read source skill versions if present
TEACHING_VERSION="$(grep -m1 '^version:' "$TEACHING_DIR/SKILL.md" 2>/dev/null | tr -d ' ' || echo 'version: unknown')"

# Idempotency: only rewrite VERSION if mode/language/anchor differ from existing.
# (The timestamp always changes per-run, so unconditional rewrite would dirty the
# tree on every re-run. Match against the args-bearing lines instead.)
VERSION_FILE="$OUTPUT_DIR/.skills/VERSION"
SHOULD_WRITE_VERSION=true
if [[ -f "$VERSION_FILE" ]]; then
  if grep -qF "Mode: $MODE" "$VERSION_FILE" 2>/dev/null \
  && grep -qF "Target language: $TARGET_LANGUAGE" "$VERSION_FILE" 2>/dev/null \
  && grep -qF "Anchor repo: $ANCHOR_REPO_DISPLAY" "$VERSION_FILE" 2>/dev/null; then
    SHOULD_WRITE_VERSION=false
  fi
fi

if "$SHOULD_WRITE_VERSION"; then
  cat > "$VERSION_FILE" <<EOF
Vendored: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Mode: $MODE
Target language: $TARGET_LANGUAGE
Anchor repo: $ANCHOR_REPO_DISPLAY

Source skill versions:
  teaching:  $TEACHING_VERSION (from $TEACHING_DIR)
  humanizer: ${HUMANIZER_DIR:-not vendored (optional)}

To refresh: re-run bookgen/scripts/scaffold.sh with the same args.
EOF
fi

# ------------------------------------------------------- copy anchor table

echo "==> Installing anchor table for $TARGET_LANGUAGE"
cp "$ANCHOR_TABLE_SRC" "$OUTPUT_DIR/docs/teaching/${TARGET_LANGUAGE}-anchor-table.md"

# Compose an optional framework addendum onto the base language anchor table.
if [[ -n "$FRAMEWORK" ]]; then
  FW_SRC="$BOOKGEN_DIR/references/anchor-tables/frameworks/${FRAMEWORK}.md"
  if [[ -f "$FW_SRC" ]]; then
    echo "==> Appending framework anchor addendum: $FRAMEWORK"
    {
      echo
      echo "<!-- framework addendum: $FRAMEWORK -->"
      echo
      cat "$FW_SRC"
    } >> "$OUTPUT_DIR/docs/teaching/${TARGET_LANGUAGE}-anchor-table.md"
  else
    echo "==> WARN: no framework addendum for '$FRAMEWORK' at $FW_SRC (skipping)"
    echo "    available: $(ls "$BOOKGEN_DIR/references/anchor-tables/frameworks/" 2>/dev/null | sed 's/\.md$//' | tr '\n' ' ')"
  fi
fi

# ------------------------------------------------------ copy build philosophy

# Pick mode-specific build philosophy if it exists, otherwise the generic
BP_SRC="$BOOKGEN_DIR/references/templates/${MODE}/build-philosophy.md"
if [[ ! -f "$BP_SRC" ]]; then
  BP_SRC="$BOOKGEN_DIR/references/templates/build-philosophy.md"
fi
if [[ -f "$BP_SRC" ]]; then
  echo "==> Installing build philosophy ($MODE-mode)"
  cp "$BP_SRC" "$OUTPUT_DIR/docs/teaching/build-philosophy.md"
else
  echo "==> No build-philosophy template found; agent will write inline"
fi

# ---------------------------------------------- dependency skeleton + baseline

# When the anchor is available locally, run the deterministic facts pass so the
# session plan can be written over a real dependency order, and capture an
# initial structural-fingerprint baseline for drift detection. Both degrade to
# a regex fallback when tree-sitter isn't installed (see scripts/requirements.txt).
if [[ -d "$ANCHOR_REPO" ]] && command -v python3 >/dev/null 2>&1; then
  echo "==> Computing dependency skeleton (sequence.py)"
  python3 "$BOOKGEN_DIR/scripts/sequence.py" --anchor-repo "$ANCHOR_REPO" --book-repo "$OUTPUT_DIR" --quiet || \
    echo "    (sequence.py reported errors; non-fatal)"
  echo "==> Capturing initial fingerprint baseline (drift.py --rebaseline)"
  python3 "$BOOKGEN_DIR/scripts/drift.py" --book-repo "$OUTPUT_DIR" --anchor-repo "$ANCHOR_REPO" --rebaseline --quiet || \
    echo "    (drift baseline reported errors; non-fatal)"
  echo "    NOTE: refresh the baseline (drift.py --rebaseline) after the seed chapters are verified."
else
  echo "==> Anchor not local or python3 unavailable; skipping sequence.py + baseline"
  echo "    (run scripts/sequence.py once you have a local clone of the anchor)"
fi

# ----------------------------------------------------------------- git init

if [[ ! -d "$OUTPUT_DIR/.git" ]]; then
  echo "==> git init"
  git init -q -b main
fi

# Commit if requested AND the agent has populated seed chapters
if "$COMMIT"; then
  if [[ ! -f "$OUTPUT_DIR/docs/book/01-"*.md ]] 2>/dev/null && \
     ! ls "$OUTPUT_DIR/docs/book/01-"*.md >/dev/null 2>&1; then
    echo "==> --commit requested but no chapter 01 yet; skipping commit"
    echo "    (the agent should write seed chapters first, then re-run with --commit)"
  else
    git add -A
    if git diff --cached --quiet 2>/dev/null; then
      echo "==> Nothing to commit (idempotent)"
    else
      git commit -q -m "docs: scaffold learn-by-llm book ($MODE mode, $TARGET_LANGUAGE)"
      echo "==> First commit landed"
    fi
  fi
fi

# -------------------------------------------------------------- summary

echo
echo "==> Scaffold complete"
echo
echo "Tree:"
find "$OUTPUT_DIR" -maxdepth 3 \
  -not -path '*/.git/*' \
  -not -path '*/.skills/*/references/*' \
  -not -path '*/.skills/*/scripts/*' \
  -not -name '.DS_Store' | sort | head -40
echo
echo "Next: review docs/teaching/suggested-order.md (dependency-derived), then write the session plan and seed chapters."
echo "  - docs/book/00-introduction.md"
echo "  - docs/book/00b-what-is-<X>.md"
echo "  - docs/book/00c-why-i-built-this.md  (optional)"
echo "  - docs/book/01-<title>.md"
echo
echo "Then: re-run with --commit to land the first commit."
