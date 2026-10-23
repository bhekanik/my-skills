#!/usr/bin/env bash
#
# bookgen/scripts/update.sh
# -------------------------
# Update an existing book repo to the current bookgen world: re-vendor skills,
# refresh the anchor table and build philosophy, regenerate the chain index,
# run drift, and report what's changed in the anchor codebase since the last
# update.
#
# Does NOT touch chapter content. The book's chapters are the user's work;
# updates only refresh the *infrastructure* around them.
#
# What gets updated (idempotent — safe to run repeatedly):
#   1. .skills/teaching       (re-vendored from current source)
#   2. .skills/humanizer      (re-vendored only when supplied)
#   3. .skills/VERSION        (timestamp + skill versions refreshed)
#   4. docs/teaching/<lang>-anchor-table.md  (re-copied from current bookgen)
#   5. docs/teaching/build-philosophy.md     (re-copied from current bookgen)
#   6. docs/chain/                            (regenerated via chain_index.py)
#   7. docs/issues/NNNN-drift-<date>.md       (new drift report appended)
#   8. .bookgen/anchor-changes-<date>.md      (what changed in the anchor
#                                              codebase since last update)
#
# Usage:
#   update.sh --book-repo <path> [--skip-drift] [--skip-chain] [--skip-anchor-diff]
#             [--anchor-since <git-ref>] [--bootstrap-version]
#
# Reads:
#   <book-repo>/book-chain.toml      (for chain, anchor_repo)
#   <book-repo>/.skills/VERSION      (to find target language and the last
#                                     scaffold/update time for anchor diff)
#
# Flags:
#   --bootstrap-version     If .skills/VERSION is missing, infer target
#                           language and anchor from existing state
#                           (docs/teaching/<lang>-anchor-table.md and
#                           book-chain.toml's anchor_repo) and write a
#                           fresh VERSION. Use this on books that predate
#                           scaffold.sh.
#
# Exit codes:
#   0  success
#   1  bad arguments / missing book-chain.toml or VERSION

set -euo pipefail

BOOK_REPO=""
SKIP_DRIFT=false
SKIP_CHAIN=false
SKIP_ANCHOR_DIFF=false
ANCHOR_SINCE=""
BOOTSTRAP_VERSION=false

BOOKGEN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEACHING_DIR="${TEACHING_DIR:-$BOOKGEN_DIR/../teaching}"
HUMANIZER_DIR="${HUMANIZER_DIR:-}"

usage() {
  sed -n '3,28p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-1}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --book-repo) BOOK_REPO="$2"; shift 2 ;;
    --skip-drift) SKIP_DRIFT=true; shift ;;
    --skip-chain) SKIP_CHAIN=true; shift ;;
    --skip-anchor-diff) SKIP_ANCHOR_DIFF=true; shift ;;
    --anchor-since) ANCHOR_SINCE="$2"; shift 2 ;;
    --bootstrap-version) BOOTSTRAP_VERSION=true; shift ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown arg: $1" >&2; usage 1 ;;
  esac
done

[[ -z "$BOOK_REPO" ]] && { echo "ERROR: --book-repo is required" >&2; exit 1; }
BOOK_REPO="${BOOK_REPO/#\~/$HOME}"
BOOK_REPO="$(cd "$BOOK_REPO" && pwd)"

if [[ ! -f "$BOOK_REPO/.skills/VERSION" ]]; then
  if "$BOOTSTRAP_VERSION"; then
    echo "==> Bootstrapping .skills/VERSION (book predates scaffold.sh)"
    mkdir -p "$BOOK_REPO/.skills"

    BOOTSTRAP_LANG=""
    if [[ -d "$BOOK_REPO/docs/teaching" ]]; then
      for at in "$BOOK_REPO/docs/teaching/"*-anchor-table.md; do
        [[ -f "$at" ]] || continue
        base="$(basename "$at" -anchor-table.md)"
        if [[ -f "$BOOKGEN_DIR/references/anchor-tables/${base}.md" ]]; then
          BOOTSTRAP_LANG="$base"
          break
        fi
      done
    fi
    [[ -z "$BOOTSTRAP_LANG" ]] && {
      echo "ERROR: could not infer target language from docs/teaching/<lang>-anchor-table.md." >&2
      echo "       Write .skills/VERSION manually with at least 'Target language: <lang>'," >&2
      echo "       then re-run without --bootstrap-version." >&2
      exit 1
    }

    BOOTSTRAP_ANCHOR=""
    if [[ -f "$BOOK_REPO/book-chain.toml" ]]; then
      BOOTSTRAP_ANCHOR="$(awk '/^[[:space:]]*anchor_repo[[:space:]]*=/ { sub(/^[^=]*=[[:space:]]*/, ""); gsub(/["]/, ""); sub(/[[:space:]]*$/, ""); print; exit }' "$BOOK_REPO/book-chain.toml")"
    fi
    [[ -z "$BOOTSTRAP_ANCHOR" ]] && BOOTSTRAP_ANCHOR="(unspecified)"

    cat > "$BOOK_REPO/.skills/VERSION" <<EOF
Vendored: (bootstrapped on $(date -u +%Y-%m-%dT%H:%M:%SZ))
Mode: tour
Target language: $BOOTSTRAP_LANG
Anchor repo: $BOOTSTRAP_ANCHOR
Previous vendored: (none — bootstrap)

Source skill versions:
  teaching:  unknown (will be populated on next run)
  humanizer: not vendored (optional)

Note: This VERSION was bootstrapped retroactively for a book that predates
scaffold.sh. Mode defaulted to "tour" — edit it here if your book is
"reproduce" or "extend". The next normal update.sh run will fill the rest.
EOF
    echo "    Wrote $BOOK_REPO/.skills/VERSION"
    echo "    Inferred target language: $BOOTSTRAP_LANG"
    echo "    Inferred anchor repo:     $BOOTSTRAP_ANCHOR"
    echo "    Mode defaulted to:        tour (edit VERSION if different)"
    echo
  else
    echo "ERROR: $BOOK_REPO/.skills/VERSION not found." >&2
    echo "       (Was this book scaffolded with scaffold.sh? If you generated" >&2
    echo "       it manually, write a VERSION file with at least a 'Target" >&2
    echo "       language: <lang>' line, then re-run.)" >&2
    echo "       Or pass --bootstrap-version to infer it from existing state." >&2
    exit 1
  fi
fi

# Read existing metadata
TARGET_LANGUAGE="$(awk '/^Target language:/ { sub(/^Target language:[[:space:]]*/, ""); print; exit }' "$BOOK_REPO/.skills/VERSION")"
PREVIOUS_VENDORED="$(awk '/^Vendored:/ { sub(/^Vendored:[[:space:]]*/, ""); print; exit }' "$BOOK_REPO/.skills/VERSION")"
MODE="$(awk '/^Mode:/ { sub(/^Mode:[[:space:]]*/, ""); print; exit }' "$BOOK_REPO/.skills/VERSION")"
ANCHOR_REPO_DISPLAY="$(awk '/^Anchor repo:/ { sub(/^Anchor repo:[[:space:]]*/, ""); print; exit }' "$BOOK_REPO/.skills/VERSION")"

# Fallback: older scaffolds didn't write Target language / Mode / Anchor.
# Infer from the book repo's contents and book-chain.toml.
if [[ -z "$TARGET_LANGUAGE" ]]; then
  # Match docs/teaching/<lang>-anchor-table.md
  for at in "$BOOK_REPO/docs/teaching/"*-anchor-table.md; do
    [[ -f "$at" ]] || continue
    base="$(basename "$at" -anchor-table.md)"
    if [[ -f "$BOOKGEN_DIR/references/anchor-tables/${base}.md" ]]; then
      TARGET_LANGUAGE="$base"
      echo "    (inferred target language: $TARGET_LANGUAGE from existing anchor-table file)"
      break
    fi
  done
fi
[[ -z "$TARGET_LANGUAGE" ]] && {
  echo "ERROR: VERSION file does not record a target language and none could be inferred." >&2
  echo "       Add \`Target language: <lang>\` to .skills/VERSION manually." >&2
  exit 1
}
[[ -z "$MODE" ]] && MODE="tour"
if [[ ( -z "$ANCHOR_REPO_DISPLAY" || "$ANCHOR_REPO_DISPLAY" == "(unspecified)" ) && -f "$BOOK_REPO/book-chain.toml" ]]; then
  ANCHOR_REPO_DISPLAY="$(awk '/^[[:space:]]*anchor_repo[[:space:]]*=/ { sub(/^[^=]*=[[:space:]]*/, ""); gsub(/["]/, ""); sub(/[[:space:]]*$/, ""); print; exit }' "$BOOK_REPO/book-chain.toml")"
fi
[[ -z "$ANCHOR_REPO_DISPLAY" ]] && ANCHOR_REPO_DISPLAY="(unspecified)"

echo "==> bookgen update"
echo "    book repo:           $BOOK_REPO"
echo "    target language:     $TARGET_LANGUAGE"
echo "    mode:                $MODE"
echo "    last vendored:       $PREVIOUS_VENDORED"
echo "    anchor repo display: $ANCHOR_REPO_DISPLAY"
echo

# ---------------------------------------------------------- 1, 2, 3: skills + VERSION

copy_skill() {
  local src="$1" dst="$2"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$src/" "$dst/"
  else
    rm -rf "$dst"
    cp -R "$src" "$dst"
  fi
}

echo "==> Refreshing vendored skills"
[[ -d "$TEACHING_DIR" ]] || { echo "ERROR: teaching skill not found at $TEACHING_DIR" >&2; exit 1; }
copy_skill "$TEACHING_DIR" "$BOOK_REPO/.skills/teaching"
if [[ -n "$HUMANIZER_DIR" ]]; then
  [[ -d "$HUMANIZER_DIR" ]] || { echo "ERROR: humanizer skill not found at $HUMANIZER_DIR" >&2; exit 1; }
  copy_skill "$HUMANIZER_DIR" "$BOOK_REPO/.skills/humanizer"
fi

TEACHING_VERSION="$(grep -m1 '^version:' "$TEACHING_DIR/SKILL.md" 2>/dev/null | tr -d ' ' || echo 'version: unknown')"

cat > "$BOOK_REPO/.skills/VERSION" <<EOF
Vendored: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Mode: $MODE
Target language: $TARGET_LANGUAGE
Anchor repo: $ANCHOR_REPO_DISPLAY
Previous vendored: $PREVIOUS_VENDORED

Source skill versions:
  teaching:  $TEACHING_VERSION (from $TEACHING_DIR)
  humanizer: ${HUMANIZER_DIR:-not vendored (optional)}

To refresh: re-run bookgen/scripts/update.sh --book-repo <this-repo>
EOF

# ----------------------------------------------- 4, 5: anchor table + build philosophy

ANCHOR_TABLE_SRC="$BOOKGEN_DIR/references/anchor-tables/${TARGET_LANGUAGE}.md"
if [[ -f "$ANCHOR_TABLE_SRC" ]]; then
  echo "==> Refreshing anchor table for $TARGET_LANGUAGE"
  cp "$ANCHOR_TABLE_SRC" "$BOOK_REPO/docs/teaching/${TARGET_LANGUAGE}-anchor-table.md"
fi

BP_SRC="$BOOKGEN_DIR/references/templates/${MODE}/build-philosophy.md"
[[ ! -f "$BP_SRC" ]] && BP_SRC="$BOOKGEN_DIR/references/templates/build-philosophy.md"
if [[ -f "$BP_SRC" ]]; then
  echo "==> Refreshing build philosophy ($MODE)"
  cp "$BP_SRC" "$BOOK_REPO/docs/teaching/build-philosophy.md"
fi

# --------------------------------------------- 5.5: refresh dependency skeleton

if [[ -f "$BOOK_REPO/book-chain.toml" ]] && command -v python3 >/dev/null 2>&1; then
  SEQ_ANCHOR_RAW="$(awk '/^[[:space:]]*anchor_repo[[:space:]]*=/ { sub(/^[^=]*=[[:space:]]*/, ""); gsub(/["]/, ""); sub(/[[:space:]]*$/, ""); print; exit }' "$BOOK_REPO/book-chain.toml")"
  if [[ -n "$SEQ_ANCHOR_RAW" ]]; then
    if [[ "$SEQ_ANCHOR_RAW" != /* && "$SEQ_ANCHOR_RAW" != ~* ]]; then
      SEQ_ANCHOR="$BOOK_REPO/$SEQ_ANCHOR_RAW"
    else
      SEQ_ANCHOR="${SEQ_ANCHOR_RAW/#\~/$HOME}"
    fi
    SEQ_ANCHOR="$(cd "$SEQ_ANCHOR" 2>/dev/null && pwd)" || true
    if [[ -n "$SEQ_ANCHOR" && -d "$SEQ_ANCHOR" ]]; then
      echo "==> Refreshing dependency skeleton (sequence.py)"
      python3 "$BOOKGEN_DIR/scripts/sequence.py" --anchor-repo "$SEQ_ANCHOR" --book-repo "$BOOK_REPO" --quiet || \
        echo "    (sequence.py reported errors; non-fatal)"
    fi
  fi
fi

# ------------------------------------------------------ 6: chain index

if ! "$SKIP_CHAIN" && [[ -f "$BOOK_REPO/book-chain.toml" ]]; then
  echo "==> Regenerating chain index"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$BOOKGEN_DIR/scripts/chain_index.py" --book-repo "$BOOK_REPO" || \
      echo "    (chain_index reported errors; non-fatal)"
  else
    echo "    (skipping — python3 not on PATH)"
  fi
fi

# ----------------------------------------------------- 7: drift report

if ! "$SKIP_DRIFT" && [[ -f "$BOOK_REPO/book-chain.toml" ]]; then
  echo "==> Running drift detection"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$BOOKGEN_DIR/scripts/drift.py" --book-repo "$BOOK_REPO" --quiet || \
      echo "    (drift findings recorded under docs/issues/)"
  else
    echo "    (skipping — python3 not on PATH)"
  fi
fi

# --------------------------------- 8: anchor codebase changes since last update

if ! "$SKIP_ANCHOR_DIFF" && [[ -f "$BOOK_REPO/book-chain.toml" ]]; then
  ANCHOR_REPO_RAW="$(awk '/^[[:space:]]*anchor_repo[[:space:]]*=/ { sub(/^[^=]*=[[:space:]]*/, ""); gsub(/["]/, ""); sub(/[[:space:]]*$/, ""); print; exit }' "$BOOK_REPO/book-chain.toml")"
  if [[ -n "$ANCHOR_REPO_RAW" ]]; then
    if [[ "$ANCHOR_REPO_RAW" != /* && "$ANCHOR_REPO_RAW" != ~* ]]; then
      ANCHOR_REPO="$BOOK_REPO/$ANCHOR_REPO_RAW"
    else
      ANCHOR_REPO="${ANCHOR_REPO_RAW/#\~/$HOME}"
    fi
    ANCHOR_REPO="$(cd "$ANCHOR_REPO" 2>/dev/null && pwd)" || true

    if [[ -d "$ANCHOR_REPO/.git" ]]; then
      echo "==> Computing anchor-codebase changes since last update"
      mkdir -p "$BOOK_REPO/.bookgen"

      TODAY="$(date +%Y-%m-%d)"
      OUT="$BOOK_REPO/.bookgen/anchor-changes-$TODAY.md"

      # Decide a "since" reference. Priority:
      # 1. --anchor-since <ref> if passed
      # 2. SHA stored from a previous run
      # 3. PREVIOUS_VENDORED date as a git --since
      LAST_SHA_FILE="$BOOK_REPO/.bookgen/last-anchor-sha"
      if [[ -n "$ANCHOR_SINCE" ]]; then
        SINCE_OPT="$ANCHOR_SINCE..HEAD"
      elif [[ -f "$LAST_SHA_FILE" ]]; then
        LAST_SHA="$(cat "$LAST_SHA_FILE")"
        if git -C "$ANCHOR_REPO" cat-file -e "$LAST_SHA" 2>/dev/null; then
          SINCE_OPT="$LAST_SHA..HEAD"
        else
          SINCE_OPT="--since=$PREVIOUS_VENDORED"
        fi
      else
        SINCE_OPT="--since=$PREVIOUS_VENDORED"
      fi

      CURRENT_SHA="$(git -C "$ANCHOR_REPO" rev-parse HEAD 2>/dev/null || echo 'unknown')"

      {
        echo "# Anchor changes since last update — $TODAY"
        echo
        echo "**Anchor repo:** \`$ANCHOR_REPO\`"
        echo "**Range:** \`$SINCE_OPT\`"
        echo "**Anchor HEAD now:** \`$CURRENT_SHA\`"
        echo "**Book last vendored:** $PREVIOUS_VENDORED"
        echo
        echo "## Commits"
        echo
        echo '```'
        git -C "$ANCHOR_REPO" log --no-merges --pretty='format:%h  %s  (%an, %cr)' $SINCE_OPT 2>/dev/null | head -100 || echo "(no commits in range)"
        echo
        echo '```'
        echo
        echo "## Files touched"
        echo
        echo '```'
        git -C "$ANCHOR_REPO" log --name-only --pretty='format:' $SINCE_OPT 2>/dev/null \
          | sort -u | grep -v '^$' | head -100 || echo "(none)"
        echo
        echo '```'
        echo
        echo "## What to do with this"
        echo
        echo "Look at the file list. Any chapter in this book that toured one of those files might be drifting. Cross-reference with \`docs/issues/NNNN-drift-*.md\` (the latest drift report should also have flagged the high-severity ones)."
        echo
        echo "Once you've reviewed and updated the affected chapters, the next \`update.sh\` run will start fresh from \`$CURRENT_SHA\`."
      } > "$OUT"

      # Persist current SHA for next run
      echo "$CURRENT_SHA" > "$LAST_SHA_FILE"
      echo "    Anchor changes report: $OUT"
    else
      echo "==> Anchor repo is not a git repo; skipping anchor-changes report."
    fi
  fi
fi

# --------------------------------------------------------- summary

echo
echo "==> Update complete"
echo
echo "Refreshed:"
echo "  - .skills/teaching (vendored); humanizer refreshed only when supplied"
echo "  - .skills/VERSION (timestamp updated)"
echo "  - docs/teaching/${TARGET_LANGUAGE}-anchor-table.md"
echo "  - docs/teaching/build-philosophy.md ($MODE-mode)"
echo "  - docs/teaching/suggested-order.md + dep-skeleton.json (if anchor is local)"
"$SKIP_CHAIN" || echo "  - docs/chain/ (chain index regenerated)"
"$SKIP_DRIFT" || echo "  - docs/issues/NNNN-drift-<date>.md (drift report)"
"$SKIP_ANCHOR_DIFF" || echo "  - .bookgen/anchor-changes-<date>.md (anchor diff)"
echo
echo "What was NOT touched: chapter content, sessions plan, AGENTS.md, READMEs, teaching-notes."
echo "Those are your work; update.sh refreshes the infrastructure around them."
