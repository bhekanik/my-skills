"""Shared structural parser for bookgen scripts.

One place to turn a source file into structural facts — imports, exports,
definitions, calls — used by sequence.py (dependency graph + BFS ordering),
drift.py (structural fingerprints), and any other script that needs to reason
about code structure deterministically.

Design (mirrors Understand-Anything's hybrid approach): the *structure* comes
from a deterministic parser, never from an LLM, so re-running is reproducible.

Tree-sitter is the primary path when available; a regex fallback keeps every
function working with stdlib only, so vendored books never hard-fail if the
optional dependency is absent. Install the accelerator with:

    pip install -r scripts/requirements.txt   # tree-sitter + tree-sitter-language-pack

`parse_file` degrades per-file: if a grammar is missing or a parse throws, that
single file falls back to regex; everything else still uses tree-sitter.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

# --------------------------------------------------------------------------
# Language detection
# --------------------------------------------------------------------------

# Extension -> (canonical language name, tree-sitter-language-pack name).
# The pack name is what `tree_sitter_language_pack.get_parser(name)` expects.
LANG_BY_EXT: dict[str, tuple[str, str]] = {
    ".py": ("python", "python"),
    ".rs": ("rust", "rust"),
    ".go": ("go", "go"),
    ".js": ("javascript", "javascript"),
    ".jsx": ("javascript", "javascript"),
    ".mjs": ("javascript", "javascript"),
    ".cjs": ("javascript", "javascript"),
    ".ts": ("typescript", "typescript"),
    ".tsx": ("tsx", "tsx"),
    ".swift": ("swift", "swift"),
    ".zig": ("zig", "zig"),
    ".ml": ("ocaml", "ocaml"),
    ".mli": ("ocaml", "ocaml_interface"),
    ".ex": ("elixir", "elixir"),
    ".exs": ("elixir", "elixir"),
    ".c": ("c", "c"),
    ".h": ("c", "c"),
    ".cpp": ("cpp", "cpp"),
    ".cc": ("cpp", "cpp"),
    ".hpp": ("cpp", "cpp"),
    ".java": ("java", "java"),
    ".rb": ("ruby", "ruby"),
}

SOURCE_EXTS = frozenset(LANG_BY_EXT)


def detect_lang(path: Path) -> str | None:
    """Canonical language name for a path, or None if unrecognised."""
    entry = LANG_BY_EXT.get(path.suffix.lower())
    return entry[0] if entry else None


# --------------------------------------------------------------------------
# Facts
# --------------------------------------------------------------------------


@dataclass
class FileFacts:
    """Structural facts about one source file."""

    path: Path
    lang: str | None
    imports: list[str] = field(default_factory=list)  # raw module specifiers
    exports: list[str] = field(default_factory=list)  # publicly exposed names
    defs: list[str] = field(default_factory=list)  # top-level definitions
    calls: list[str] = field(default_factory=list)  # callee identifiers
    parsed_with: str = "none"  # "tree-sitter" | "regex" | "none"

    def signature(self) -> str:
        """Structural signature — order-independent, ignores comments/whitespace.

        Two files with the same exports + defs + import targets produce the same
        signature even after a pure rename of locals or a reflow. This is the
        basis for drift.py's cosmetic-vs-structural classification.
        """
        parts = [
            "exports:" + ",".join(sorted(set(self.exports))),
            "defs:" + ",".join(sorted(set(self.defs))),
            "imports:" + ",".join(sorted(set(self.imports))),
        ]
        return "\n".join(parts)

    def fingerprint(self) -> str:
        return hashlib.sha256(self.signature().encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# Tree-sitter availability
# --------------------------------------------------------------------------


@lru_cache(maxsize=1)
def has_treesitter() -> bool:
    try:
        import tree_sitter_language_pack  # noqa: F401

        return True
    except Exception:
        return False


@lru_cache(maxsize=64)
def _get_parser(pack_name: str):
    """Return a tree-sitter Parser for a language-pack name, or None."""
    try:
        from tree_sitter_language_pack import get_parser

        return get_parser(pack_name)
    except Exception:
        return None


# Per-language node-type configuration for the generic tree walk. Node type
# names vary by grammar; these cover the common cases. Anything missing simply
# yields fewer facts (the regex fallback and downstream resolvers tolerate it).
@dataclass(frozen=True)
class NodeConfig:
    import_nodes: frozenset[str]
    def_nodes: frozenset[str]
    call_nodes: frozenset[str]
    export_marker: frozenset[str] = frozenset()  # node types that mark `pub`/`export`


_NODE_CONFIG: dict[str, NodeConfig] = {
    "python": NodeConfig(
        import_nodes=frozenset({"import_statement", "import_from_statement"}),
        def_nodes=frozenset({"function_definition", "class_definition"}),
        call_nodes=frozenset({"call"}),
    ),
    "rust": NodeConfig(
        import_nodes=frozenset({"use_declaration"}),
        def_nodes=frozenset(
            {"function_item", "struct_item", "enum_item", "trait_item", "mod_item", "type_item", "const_item", "macro_definition"}
        ),
        call_nodes=frozenset({"call_expression", "macro_invocation"}),
        export_marker=frozenset({"visibility_modifier"}),
    ),
    "go": NodeConfig(
        import_nodes=frozenset({"import_declaration", "import_spec"}),
        def_nodes=frozenset({"function_declaration", "method_declaration", "type_declaration"}),
        call_nodes=frozenset({"call_expression"}),
    ),
    "javascript": NodeConfig(
        import_nodes=frozenset({"import_statement"}),
        def_nodes=frozenset({"function_declaration", "class_declaration", "method_definition", "generator_function_declaration"}),
        call_nodes=frozenset({"call_expression"}),
        export_marker=frozenset({"export_statement"}),
    ),
    "typescript": NodeConfig(
        import_nodes=frozenset({"import_statement"}),
        def_nodes=frozenset(
            {"function_declaration", "class_declaration", "method_definition", "interface_declaration", "type_alias_declaration", "enum_declaration"}
        ),
        call_nodes=frozenset({"call_expression"}),
        export_marker=frozenset({"export_statement"}),
    ),
}
_NODE_CONFIG["tsx"] = _NODE_CONFIG["typescript"]


def _node_text(node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", "replace")


def _named_child_text(node, source: bytes, field_name: str = "name") -> str | None:
    child = node.child_by_field_name(field_name)
    return _node_text(child, source) if child is not None else None


def _parse_treesitter(path: Path, lang: str, source: bytes) -> FileFacts | None:
    entry = LANG_BY_EXT.get(path.suffix.lower())
    if entry is None:
        return None
    parser = _get_parser(entry[1])
    if parser is None:
        return None
    config = _NODE_CONFIG.get(lang)
    if config is None:
        # Grammar exists but we have no node map; let regex handle it.
        return None
    try:
        tree = parser.parse(source)
    except Exception:
        return None

    facts = FileFacts(path=path, lang=lang, parsed_with="tree-sitter")
    root = tree.root_node

    # Iterative pre-order walk; cheaper and safer than recursion on big files.
    stack = [root]
    while stack:
        node = stack.pop()
        ntype = node.type
        if ntype in config.import_nodes:
            facts.imports.extend(_extract_import_targets(node, source))
        elif ntype in config.def_nodes:
            name = _named_child_text(node, source)
            if name:
                facts.defs.append(name)
                if _is_exported(node, source, config):
                    facts.exports.append(name)
        elif ntype in config.call_nodes:
            callee = node.child_by_field_name("function") or (node.children[0] if node.children else None)
            if callee is not None:
                facts.calls.append(_leaf_name(_node_text(callee, source)))
        stack.extend(reversed(node.children))

    facts.imports = _dedupe(facts.imports)
    facts.exports = _dedupe(facts.exports)
    facts.defs = _dedupe(facts.defs)
    facts.calls = _dedupe(facts.calls)
    return facts


def _is_exported(node, source: bytes, config: NodeConfig) -> bool:
    # Rust/Swift: a `visibility_modifier`/`pub` child. JS/TS: wrapped in export_statement.
    if not config.export_marker:
        # Python/Go: exported-by-default heuristics (Go: capitalized; Python: not _-prefixed).
        name = _named_child_text(node, source) or ""
        if node.type.startswith(("function", "method", "type")) and name:
            return name[0].isupper() or not name.startswith("_")
        return bool(name) and not name.startswith("_")
    for child in node.children:
        if child.type in config.export_marker:
            return True
    parent = node.parent
    return parent is not None and parent.type in config.export_marker


def _extract_import_targets(node, source: bytes) -> list[str]:
    """Pull module specifiers out of an import node (strings + dotted paths)."""
    targets: list[str] = []
    wanted = {
        "string",
        "string_literal",
        "interpreted_string_literal",
        "raw_string_literal",
        "dotted_name",
        "scoped_identifier",
        "crate",
        "identifier",
        "package_identifier",
    }
    stack = [node]
    while stack:
        n = stack.pop()
        if n is not node and n.type in wanted:
            text = _node_text(n, source).strip().strip("\"'`")
            if text:
                targets.append(text)
        stack.extend(n.children)
    if not targets:
        # Fall back to the first line of raw import text.
        targets.append(_node_text(node, source).splitlines()[0].strip())
    return targets


def _leaf_name(text: str) -> str:
    """Reduce `a.b.c(` / `a::b::c` / `obj.method` to the trailing identifier."""
    text = text.strip().split("(", 1)[0]
    for sep in ("::", "."):
        if sep in text:
            text = text.rsplit(sep, 1)[-1]
    return text.strip()


# --------------------------------------------------------------------------
# Regex fallback
# --------------------------------------------------------------------------

_IMPORT_PATTERNS: dict[str, list[re.Pattern]] = {
    "python": [
        re.compile(r"^\s*import\s+([a-zA-Z0-9_.]+)", re.M),
        re.compile(r"^\s*from\s+([a-zA-Z0-9_.]+)\s+import", re.M),
    ],
    "rust": [re.compile(r"^\s*(?:pub\s+)?use\s+([a-zA-Z0-9_:{}, *]+);", re.M)],
    "go": [re.compile(r'"([a-zA-Z0-9_./-]+)"')],
    "javascript": [
        re.compile(r"""import\s+.*?from\s+['"]([^'"]+)['"]""", re.S),
        re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)"""),
    ],
}
_IMPORT_PATTERNS["typescript"] = _IMPORT_PATTERNS["javascript"]
_IMPORT_PATTERNS["tsx"] = _IMPORT_PATTERNS["javascript"]

_DEF_PATTERNS: dict[str, list[re.Pattern]] = {
    "python": [re.compile(r"^\s*(?:async\s+)?def\s+([a-zA-Z0-9_]+)", re.M), re.compile(r"^\s*class\s+([a-zA-Z0-9_]+)", re.M)],
    "rust": [
        re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)", re.M),
        re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:struct|enum|trait|type|mod)\s+([a-zA-Z0-9_]+)", re.M),
    ],
    "go": [re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([a-zA-Z0-9_]+)", re.M), re.compile(r"^\s*type\s+([a-zA-Z0-9_]+)", re.M)],
    "javascript": [
        re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([a-zA-Z0-9_]+)", re.M),
        re.compile(r"^\s*(?:export\s+)?class\s+([a-zA-Z0-9_]+)", re.M),
        re.compile(r"^\s*(?:export\s+)?const\s+([a-zA-Z0-9_]+)\s*=", re.M),
    ],
}
_DEF_PATTERNS["typescript"] = _DEF_PATTERNS["javascript"] + [
    re.compile(r"^\s*(?:export\s+)?interface\s+([a-zA-Z0-9_]+)", re.M),
    re.compile(r"^\s*(?:export\s+)?type\s+([a-zA-Z0-9_]+)\s*=", re.M),
]
_DEF_PATTERNS["tsx"] = _DEF_PATTERNS["typescript"]

_EXPORT_HINT = re.compile(r"\b(?:pub|export|public)\b")


def _parse_regex(path: Path, lang: str | None, text: str) -> FileFacts:
    facts = FileFacts(path=path, lang=lang, parsed_with="regex" if lang else "none")
    if lang is None:
        return facts
    for pat in _IMPORT_PATTERNS.get(lang, []):
        facts.imports.extend(m.strip() for m in pat.findall(text))
    for pat in _DEF_PATTERNS.get(lang, []):
        for name in pat.findall(text):
            facts.defs.append(name)
    # Export heuristic: a def line that also carries an export marker, or
    # capitalised names in Go, or non-underscore names in Python.
    for line in text.splitlines():
        if _EXPORT_HINT.search(line):
            for pat in _DEF_PATTERNS.get(lang, []):
                m = pat.search(line)
                if m:
                    facts.exports.append(m.group(1))
    if lang == "go":
        facts.exports.extend(d for d in facts.defs if d[:1].isupper())
    elif lang == "python":
        facts.exports.extend(d for d in facts.defs if not d.startswith("_"))
    facts.imports = _dedupe(facts.imports)
    facts.defs = _dedupe(facts.defs)
    facts.exports = _dedupe(facts.exports)
    return facts


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def _dedupe(items: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for item in items:
        if item:
            seen.setdefault(item, None)
    return list(seen)


def parse_file(path: Path, source: str | bytes | None = None) -> FileFacts:
    """Structural facts for one file. Tree-sitter when possible, regex otherwise.

    `source` may be passed to avoid a disk read (useful when the caller already
    has the bytes). Errors never raise — an unreadable file yields empty facts.
    """
    lang = detect_lang(path)
    if source is None:
        try:
            raw = path.read_bytes()
        except OSError:
            return FileFacts(path=path, lang=lang, parsed_with="none")
    elif isinstance(source, str):
        raw = source.encode("utf-8")
    else:
        raw = source

    if lang is not None and has_treesitter():
        facts = _parse_treesitter(path, lang, raw)
        if facts is not None:
            return facts

    return _parse_regex(path, lang, raw.decode("utf-8", "replace"))


def iter_source_files(root: Path, ignore_dirs: frozenset[str] | None = None):
    """Yield source files under root, skipping noisy directories."""
    skip = ignore_dirs or frozenset(
        {".git", "node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__", "vendor", ".next", "zig-cache", "_build", "deps"}
    )
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SOURCE_EXTS:
            if any(part in skip for part in p.parts):
                continue
            yield p
