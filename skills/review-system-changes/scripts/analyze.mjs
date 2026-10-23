#!/usr/bin/env node
// review-system-changes analysis engine.
// Extracts a system-level model of a set of code changes (module graph, call
// graph, function metrics, per-file diff/source) and renders a single-file
// interactive HTML report.
//
// Usage:
//   node analyze.mjs --repo <path> [--base <git-ref>] [--scope changed|neighbors|all]
//                    [--out <file.html>] [--include-tests]
//
// Defaults: --repo = cwd, --scope = neighbors, base auto-detected.

import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { renderModel, mergeExplanations } from "./render.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const nodeMajor = Number.parseInt(process.versions.node.split(".")[0], 10);
if (nodeMajor !== 20 && nodeMajor < 22) {
  console.error(
    `[error] Node.js 20 or 22 or newer is required; found ${process.version}.`
  );
  process.exit(1);
}

const nullDevice = process.platform === "win32" ? "NUL" : "/dev/null";

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------
function parseArgs(argv) {
  const args = { scope: "neighbors", includeTests: false };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const next = () => argv[++i];
    if (a === "--repo") args.repo = next();
    else if (a === "--base") args.base = next();
    else if (a === "--scope") args.scope = next();
    else if (a === "--out") args.out = next();
    else if (a === "--explanations") args.explanations = next();
    else if (a === "--include-tests") args.includeTests = true;
    else if (a === "--help" || a === "-h") args.help = true;
  }
  return args;
}

const args = parseArgs(process.argv);
if (args.help) {
  console.log(
    "Usage: node analyze.mjs --repo <path> [--base <ref>] [--scope changed|neighbors|all] [--out <file.html>] [--include-tests] [--explanations <file.json>]"
  );
  process.exit(0);
}

let Project;
let Node;
let SyntaxKind;
try {
  ({ Project, Node, SyntaxKind } = await import("ts-morph"));
} catch (error) {
  console.error(
    `[error] analyzer dependencies are missing. Run "npm ci --omit=dev" in ${__dirname}.`
  );
  if (error && error.code !== "ERR_MODULE_NOT_FOUND") {
    console.error(`[error] ${error.message}`);
  }
  process.exit(1);
}

const repo = resolve(args.repo || process.cwd());
if (!existsSync(repo)) {
  console.error(`[error] repo path does not exist: ${repo}`);
  process.exit(1);
}

const CODE_EXT = /\.(m|c)?[jt]sx?$/;
const TEST_RE = /(\.(test|spec)\.[jt]sx?$)|(^|\/)(__tests__|__mocks__|tests?)\//;

function git(gitArgs) {
  try {
    return execFileSync("git", ["-C", repo, ...gitArgs], {
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
      stdio: ["ignore", "pipe", "pipe"],
    });
  } catch (e) {
    return e.stdout ? String(e.stdout) : "";
  }
}

function isGitRepo() {
  try {
    execFileSync("git", ["-C", repo, "rev-parse", "--is-inside-work-tree"], {
      stdio: "ignore",
    });
    return true;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Determine changed files + how the diff was scoped
// ---------------------------------------------------------------------------
function collectChanges() {
  if (!isGitRepo()) {
    console.error(
      `[error] ${repo} is not a git repository. This skill diffs changes with git.`
    );
    process.exit(1);
  }

  let base = args.base;
  let source;
  const files = new Set();
  const diffFor = new Map();

  const porcelain = git(["status", "--porcelain"]).trim();
  const hasWorkingChanges = porcelain.length > 0;

  if (!base) {
    if (hasWorkingChanges) {
      base = "HEAD";
      source = "working tree vs HEAD (uncommitted changes)";
    } else {
      base = "HEAD~1";
      source = "HEAD~1..HEAD (last commit)";
    }
  } else {
    source = `${base}..working tree`;
  }

  // name-status across the diff range (includes staged + unstaged when base=HEAD).
  const nameStatus = git(["diff", "--name-status", base]).trim();
  const statusOf = new Map();
  for (const line of nameStatus.split("\n").filter(Boolean)) {
    const parts = line.split("\t");
    const code = parts[0][0]; // A/M/D/R...
    const path = parts[parts.length - 1];
    statusOf.set(path, code);
    files.add(path);
  }
  // Untracked files show only in status --porcelain.
  for (const line of porcelain.split("\n").filter(Boolean)) {
    const code = line.slice(0, 2);
    const path = line.slice(3).trim();
    if (code.includes("?")) {
      statusOf.set(path, "A");
      files.add(path);
    }
  }

  // Capture unified diff per changed file (best effort).
  for (const path of files) {
    let d = git(["diff", base, "--", path]);
    if (!d.trim() && statusOf.get(path) === "A") {
      // Untracked/new file: synthesize a diff against the platform null device.
      d = git(["diff", "--no-index", "--", nullDevice, path]);
    }
    diffFor.set(path, d);
  }

  // New-side line numbers touched (added or adjacent to deletions) per file.
  const changedLinesFor = new Map();
  for (const [path, diff] of diffFor) {
    changedLinesFor.set(path, parseChangedLines(diff));
  }

  return { base, source, statusOf, files, diffFor, changedLinesFor, hasWorkingChanges };
}

// Parse a unified diff into the set of new-side line numbers that were touched.
function parseChangedLines(diff) {
  const lines = new Set();
  if (!diff) return lines;
  let newNo = 0;
  for (const line of diff.split("\n")) {
    const m = /^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/.exec(line);
    if (m) {
      newNo = parseInt(m[1], 10);
      continue;
    }
    if (line.startsWith("+++") || line.startsWith("---")) continue;
    if (line.startsWith("+")) {
      lines.add(newNo++);
    } else if (line.startsWith("-")) {
      lines.add(newNo); // mark the boundary where content was removed
    } else if (line.startsWith(" ")) {
      newNo++;
    }
  }
  return lines;
}

const changes = collectChanges();

// symbol is "changed" if its line range intersects touched lines, or the file is new.
function symbolChanged(path, startLine, endLine) {
  if (!changedCode.has(path)) return false;
  if (changes.statusOf.get(path) === "A") return true;
  const touched = changes.changedLinesFor.get(path);
  if (!touched || touched.size === 0) return true; // changed file, unknown hunks -> assume changed
  for (let ln = startLine; ln <= endLine; ln++) if (touched.has(ln)) return true;
  return false;
}

// Set of changed code files (repo-relative, posix-ish), filtered to code.
function isCode(p) {
  if (!CODE_EXT.test(p)) return false;
  if (!args.includeTests && TEST_RE.test(p)) return false;
  return true;
}
const changedCode = new Set([...changes.files].filter(isCode));

if (changedCode.size === 0) {
  console.error(
    `[warn] No changed TypeScript/JavaScript files detected via ${changes.source}.\n` +
      `       Pass --base <ref> to widen the diff, or --include-tests to include test files.`
  );
}

// ---------------------------------------------------------------------------
// Build the ts-morph project
// ---------------------------------------------------------------------------
function findTsconfig() {
  // Prefer the tsconfig nearest a changed file, else repo root.
  const candidates = new Set();
  for (const f of changedCode) {
    let dir = dirname(join(repo, f));
    while (dir.startsWith(repo)) {
      candidates.add(join(dir, "tsconfig.json"));
      if (dir === repo) break;
      dir = dirname(dir);
    }
  }
  candidates.add(join(repo, "tsconfig.json"));
  for (const c of candidates) if (existsSync(c)) return c;
  return null;
}

const tsconfig = findTsconfig();
let project;
if (tsconfig) {
  project = new Project({
    tsConfigFilePath: tsconfig,
    skipAddingFilesFromTsConfig: false,
    compilerOptions: { allowJs: true, checkJs: false, noEmit: true },
  });
} else {
  project = new Project({
    compilerOptions: { allowJs: true, checkJs: false, noEmit: true },
  });
}

// Ensure changed files are in the project even if tsconfig excludes them.
for (const f of changedCode) {
  const abs = join(repo, f);
  if (existsSync(abs) && !project.getSourceFile(abs)) {
    try {
      project.addSourceFileAtPath(abs);
    } catch {
      /* ignore unparseable */
    }
  }
}
if (!tsconfig) {
  // No tsconfig: pull in the tree so imports can resolve.
  project.addSourceFilesAtPaths([
    join(repo, "**/*.{ts,tsx,js,jsx,mjs,cjs,mts,cts}"),
    "!" + join(repo, "**/node_modules/**"),
    "!" + join(repo, "**/dist/**"),
    "!" + join(repo, "**/build/**"),
  ]);
}

const rel = (abs) => relative(repo, abs).split(sep).join("/");

// Map of repo-relative path -> source file, for files under the repo & not in node_modules.
const sourceFiles = new Map();
for (const sf of project.getSourceFiles()) {
  const p = sf.getFilePath();
  if (!p.startsWith(repo + sep) && p !== repo) continue;
  const r = rel(p);
  if (r.includes("node_modules/")) continue;
  sourceFiles.set(r, sf);
}

// ---------------------------------------------------------------------------
// Module graph (import edges)
// ---------------------------------------------------------------------------
const moduleEdges = []; // {from, to}
const importsTo = new Map(); // path -> Set(path)
const importedBy = new Map(); // path -> Set(path)
const add = (map, k, v) => {
  if (!map.has(k)) map.set(k, new Set());
  map.get(k).add(v);
};

for (const [path, sf] of sourceFiles) {
  const targets = new Set();
  const collect = (spec) => {
    if (!spec) return;
    const t = spec.getModuleSpecifierSourceFile?.();
    if (t) {
      const tp = rel(t.getFilePath());
      if (sourceFiles.has(tp) && tp !== path) targets.add(tp);
    }
  };
  sf.getImportDeclarations().forEach(collect);
  sf.getExportDeclarations().forEach(collect);
  // Dynamic import("...") calls.
  sf.getDescendantsOfKind(SyntaxKind.CallExpression).forEach((call) => {
    if (call.getExpression().getKind() === SyntaxKind.ImportKeyword) {
      const arg = call.getArguments()[0];
      if (arg && Node.isStringLiteral(arg)) {
        const resolved = sf
          .getImportDeclarations()
          .find((d) => d.getModuleSpecifierValue() === arg.getLiteralValue());
        collect(resolved);
      }
    }
  });
  for (const t of targets) {
    moduleEdges.push({ from: path, to: t });
    add(importsTo, path, t);
    add(importedBy, t, path);
  }
}

// ---------------------------------------------------------------------------
// Scope: changed files + 1-hop neighbors
// ---------------------------------------------------------------------------
const changedInProject = new Set(
  [...changedCode].filter((p) => sourceFiles.has(p))
);

let scopeFiles;
if (args.scope === "all") {
  scopeFiles = new Set(sourceFiles.keys());
} else if (args.scope === "changed") {
  scopeFiles = new Set(changedInProject);
} else {
  scopeFiles = new Set(changedInProject);
  for (const p of changedInProject) {
    for (const t of importsTo.get(p) || []) scopeFiles.add(t);
    for (const s of importedBy.get(p) || []) scopeFiles.add(s);
  }
}
// Always keep changed files even if not resolvable in project (e.g. deleted).
for (const p of changedCode) scopeFiles.add(p);

// ---------------------------------------------------------------------------
// Symbols + call graph within scope
// ---------------------------------------------------------------------------
const DECISION_KINDS = new Set([
  SyntaxKind.IfStatement,
  SyntaxKind.ForStatement,
  SyntaxKind.ForInStatement,
  SyntaxKind.ForOfStatement,
  SyntaxKind.WhileStatement,
  SyntaxKind.DoStatement,
  SyntaxKind.CaseClause,
  SyntaxKind.CatchClause,
  SyntaxKind.ConditionalExpression,
]);

function complexityOf(fn) {
  let c = 1;
  fn.forEachDescendant((d) => {
    const k = d.getKind();
    if (DECISION_KINDS.has(k)) c++;
    else if (k === SyntaxKind.BinaryExpression) {
      const op = d.getOperatorToken().getKind();
      if (
        op === SyntaxKind.AmpersandAmpersandToken ||
        op === SyntaxKind.BarBarToken ||
        op === SyntaxKind.QuestionQuestionToken
      )
        c++;
    }
  });
  return c;
}

// Cognitive complexity (nesting-weighted), after SonarSource's model: flow-break
// structures cost +1, and each extra nesting level they sit inside adds +1 more.
// This penalizes deep nesting (hard to read) while barely charging flat switches
// or guard clauses — a far more actionable signal than cyclomatic complexity.
const NEST_KINDS = new Set([
  SyntaxKind.IfStatement,
  SyntaxKind.ForStatement,
  SyntaxKind.ForInStatement,
  SyntaxKind.ForOfStatement,
  SyntaxKind.WhileStatement,
  SyntaxKind.DoStatement,
  SyntaxKind.CatchClause,
  SyntaxKind.SwitchStatement,
  SyntaxKind.ConditionalExpression,
]);
function cognitiveOf(fn) {
  let total = 0;
  const body = fn.getBody ? fn.getBody() : null;
  const walk = (node, depth) => {
    node.forEachChild((child) => {
      const k = child.getKind();
      let nests = false;
      if (NEST_KINDS.has(k)) {
        // `else if` shouldn't stack nesting; ts-morph models else-if as a nested
        // IfStatement, but charging it full nesting over-counts — cap the bump.
        total += 1 + depth;
        nests = true;
      } else if (k === SyntaxKind.BinaryExpression) {
        const op = child.getOperatorToken && child.getOperatorToken().getKind();
        if (op === SyntaxKind.AmpersandAmpersandToken || op === SyntaxKind.BarBarToken) total += 1;
      }
      walk(child, depth + (nests ? 1 : 0));
    });
  };
  walk(body || fn, 0);
  return total;
}

const symbols = []; // flat list
const symbolById = new Map();
const declStartToId = new Map(); // `${path}:${startPos}` -> id
const behaviorById = new Map(); // id -> behavior tags for a richer auto-explanation

// Read the body for behavioral signals so the auto-explanation can say what a
// function does (validate, loop, fetch, build, compute) rather than just its shape.
const IO_RE = /\b(fetch|axios|request|http|query|find(One|Many)?|save|create|update|delete|insert|upsert|exec|select|send|emit|dispatch|publish|subscribe|read|write|load|persist|store|get|post|put|patch)\b/i;
const ITER_RE = /\.(forEach|map|filter|reduce|some|every|flatMap|find)\b/;
function computeBehavior(fn) {
  const b = { throws: false, loop: false, awaits: false, returnsVal: false, io: false, builds: false, throwMsg: "" };
  fn.forEachDescendant((d) => {
    const k = d.getKind();
    if (k === SyntaxKind.ThrowStatement) {
      b.throws = true;
      if (!b.throwMsg) {
        const lit =
          d.getFirstDescendantByKind(SyntaxKind.StringLiteral) ||
          d.getFirstDescendantByKind(SyntaxKind.NoSubstitutionTemplateLiteral) ||
          d.getFirstDescendantByKind(SyntaxKind.TemplateExpression);
        if (lit) {
          let t = lit.getLiteralText ? lit.getLiteralText() : lit.getText().replace(/[`'"]/g, "");
          t = (t || "").replace(/\$\{[^}]*\}/g, "…").replace(/\s+/g, " ").trim();
          if (t) b.throwMsg = t.slice(0, 60);
        }
      }
    } else if (
      k === SyntaxKind.ForStatement || k === SyntaxKind.ForOfStatement ||
      k === SyntaxKind.ForInStatement || k === SyntaxKind.WhileStatement || k === SyntaxKind.DoStatement
    ) {
      b.loop = true;
    } else if (k === SyntaxKind.AwaitExpression) {
      b.awaits = true;
    } else if (k === SyntaxKind.ReturnStatement) {
      if (d.getExpression && d.getExpression()) b.returnsVal = true;
    } else if (k === SyntaxKind.CallExpression) {
      const t = d.getExpression().getText();
      if (ITER_RE.test(t)) b.loop = true;
      if (IO_RE.test(t)) b.io = true;
    } else if (k === SyntaxKind.ObjectLiteralExpression || k === SyntaxKind.NewExpression) {
      b.builds = true;
    }
  });
  return b;
}

let idSeq = 0;
function symbolId(path, startPos) {
  return `s${idSeq++}:${path}:${startPos}`;
}

function paramInfo(fn) {
  if (!fn.getParameters) return [];
  return fn.getParameters().map((p) => ({
    name: p.getName(),
    type: safeTypeText(p),
    optional: p.isOptional?.() || p.hasQuestionToken?.() || false,
    rest: p.isRestParameter?.() || false,
  }));
}
function safeTypeText(node) {
  try {
    const tn = node.getTypeNode?.();
    if (tn) return tn.getText();
    const t = node.getType?.();
    const txt = t?.getText?.();
    return txt && txt.length < 80 ? txt : "";
  } catch {
    return "";
  }
}

function describe(node) {
  // Prefer JSDoc description, else nothing (agent fills in narrative).
  try {
    const jsdocs = node.getJsDocs?.() || [];
    if (jsdocs.length) {
      const txt = jsdocs
        .map((d) => d.getDescription?.() || "")
        .join(" ")
        .trim();
      if (txt) return txt.replace(/\s+/g, " ").slice(0, 400);
    }
  } catch {
    /* ignore */
  }
  return "";
}

function nameOf(fn) {
  if (Node.isFunctionDeclaration(fn) || Node.isMethodDeclaration(fn)) {
    return fn.getName() || "<anonymous>";
  }
  if (Node.isConstructorDeclaration(fn)) return "constructor";
  if (Node.isGetAccessorDeclaration(fn)) return `get ${fn.getName()}`;
  if (Node.isSetAccessorDeclaration(fn)) return `set ${fn.getName()}`;
  // Arrow / function expression assigned to a variable or property.
  const varDec = fn.getFirstAncestorByKind?.(SyntaxKind.VariableDeclaration);
  if (varDec) return varDec.getName();
  const prop = fn.getFirstAncestorByKind?.(SyntaxKind.PropertyAssignment);
  if (prop) return prop.getName();
  const propDec = fn.getFirstAncestorByKind?.(SyntaxKind.PropertyDeclaration);
  if (propDec) return propDec.getName();
  return "<anonymous>";
}

function classNameOf(fn) {
  const cls = fn.getFirstAncestorByKind?.(SyntaxKind.ClassDeclaration);
  return cls ? cls.getName() || "<anonymous class>" : null;
}

const FN_KINDS = [
  SyntaxKind.FunctionDeclaration,
  SyntaxKind.MethodDeclaration,
  SyntaxKind.Constructor,
  SyntaxKind.GetAccessor,
  SyntaxKind.SetAccessor,
  SyntaxKind.ArrowFunction,
  SyntaxKind.FunctionExpression,
];

// Only analyze symbols in scope files that are present in the project.
const scopeInProject = [...scopeFiles].filter((p) => sourceFiles.has(p));

for (const path of scopeInProject) {
  const sf = sourceFiles.get(path);

  // Classes (as containers / nodes).
  for (const cls of sf.getClasses()) {
    const start = cls.getStart();
    const id = symbolId(path, start);
    const sym = {
      id,
      kind: "class",
      name: cls.getName() || "<anonymous class>",
      file: path,
      changed: symbolChanged(path, cls.getStartLineNumber(), cls.getEndLineNumber()),
      startLine: cls.getStartLineNumber(),
      endLine: cls.getEndLineNumber(),
      loc: cls.getEndLineNumber() - cls.getStartLineNumber() + 1,
      exported: cls.isExported?.() || false,
      className: null,
      params: [],
      paramCount: 0,
      complexity: null,
      cognitive: null,
      description: describe(cls),
      explanation: "",
      explained: false,
      autoExplanation: "",
      flags: [],
    };
    symbols.push(sym);
    symbolById.set(id, sym);
    declStartToId.set(`${path}:${start}`, id);
  }

  // Functions / methods / arrows.
  for (const kind of FN_KINDS) {
    for (const fn of sf.getDescendantsOfKind(kind)) {
      // Skip anonymous inline callbacks (map/forEach/.then handlers, etc.).
      // At the system level they're part of their parent, not their own unit.
      const name = nameOf(fn);
      if (
        (kind === SyntaxKind.ArrowFunction ||
          kind === SyntaxKind.FunctionExpression) &&
        name === "<anonymous>"
      ) {
        continue;
      }
      const start = fn.getStart();
      const key = `${path}:${start}`;
      if (declStartToId.has(key)) continue;
      const id = symbolId(path, start);
      const params = paramInfo(fn);
      const sym = {
        id,
        kind:
          kind === SyntaxKind.MethodDeclaration ||
          kind === SyntaxKind.Constructor ||
          kind === SyntaxKind.GetAccessor ||
          kind === SyntaxKind.SetAccessor
            ? "method"
            : "function",
        name,
        file: path,
        changed: symbolChanged(path, fn.getStartLineNumber(), fn.getEndLineNumber()),
        startLine: fn.getStartLineNumber(),
        endLine: fn.getEndLineNumber(),
        loc: fn.getEndLineNumber() - fn.getStartLineNumber() + 1,
        exported: fn.isExported?.() || false,
        className: classNameOf(fn),
        params,
        paramCount: params.length,
        complexity: complexityOf(fn),
        cognitive: cognitiveOf(fn),
        description: describe(fn),
        explanation: "",
        explained: false,
        autoExplanation: "",
        flags: [],
      };
      symbols.push(sym);
      symbolById.set(id, sym);
      declStartToId.set(key, id);
      behaviorById.set(id, computeBehavior(fn));
    }
  }
}

// Call graph edges (best effort resolution).
const callSet = new Set();
const calls = [];
for (const path of scopeInProject) {
  const sf = sourceFiles.get(path);
  for (const call of sf.getDescendantsOfKind(SyntaxKind.CallExpression)) {
    // Find enclosing analyzed symbol (caller).
    let callerId = null;
    let anc = call.getParent();
    while (anc) {
      const k = anc.getKind();
      if (FN_KINDS.includes(k)) {
        const cid = declStartToId.get(`${rel(anc.getSourceFile().getFilePath())}:${anc.getStart()}`);
        if (cid) {
          callerId = cid;
          break;
        }
      }
      anc = anc.getParent();
    }
    if (!callerId) continue;

    // Resolve callee declaration.
    let calleeId = null;
    try {
      const expr = call.getExpression();
      let sym = expr.getSymbol?.();
      // For property access (obj.method), symbol of the name node.
      if (!sym && Node.isPropertyAccessExpression(expr))
        sym = expr.getNameNode().getSymbol?.();
      if (!sym && expr.getLastChild) sym = expr.getLastChild()?.getSymbol?.();
      // Follow import aliases (imported fn -> its real declaration).
      const aliased = sym?.getAliasedSymbol?.();
      if (aliased) sym = aliased;
      const decls = sym?.getDeclarations?.() || [];
      for (const d of decls) {
        const dp = rel(d.getSourceFile().getFilePath());
        const cand = declStartToId.get(`${dp}:${d.getStart()}`);
        if (cand) {
          calleeId = cand;
          break;
        }
      }
    } catch {
      /* unresolved */
    }
    if (calleeId && calleeId !== callerId) {
      const k = `${callerId}->${calleeId}`;
      if (!callSet.has(k)) {
        callSet.add(k);
        calls.push({ from: callerId, to: calleeId });
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Auto-explanations (baseline narration; reviewer enriches via render.mjs)
// ---------------------------------------------------------------------------
// Plain, system-level baseline. Lead with what the function actually does
// (read from its body), fall back to shape only when there's no clear signal.
// This is a guess from structure — the reviewer-authored layer replaces it.
function behaviorLead(s, b) {
  const nm = s.name.toLowerCase();
  const guardName = /^(assert|validate|check|ensure|require|is|has|can|should|must)/.test(nm);
  if (b.throws && b.loop) return `Checks each item in a set and rejects any that fail${b.throwMsg ? ` (error: "${b.throwMsg}")` : ""}`;
  if (b.throws && guardName) return `Guards against bad input and stops with an error when a rule is broken${b.throwMsg ? ` (error: "${b.throwMsg}")` : ""}`;
  if (b.throws) return `Checks a condition and throws an error when it fails${b.throwMsg ? ` (error: "${b.throwMsg}")` : ""}`;
  if (b.io && b.awaits) return "Fetches or saves data elsewhere and waits for the result";
  if (b.io) return "Reads or writes data elsewhere in the system";
  if (b.loop && b.returnsVal) return "Works through a collection and returns a result from it";
  if (b.loop) return "Works through a collection of items";
  if (b.builds && b.returnsVal) return "Assembles and returns a new value from its inputs";
  if (b.returnsVal) return "Works out and returns a value from its inputs";
  if (b.awaits) return "Coordinates some async work";
  return null;
}
for (const s of symbols) {
  if (s.kind === "class") {
    const methods = symbols.filter((m) => m.file === s.file && m.className === s.name);
    s.autoExplanation = `Bundles ${methods.length} related function${methods.length === 1 ? "" : "s"} together.`;
    continue;
  }
  const outCount = new Set(calls.filter((c) => c.from === s.id).map((c) => c.to)).size;
  const lead = behaviorLead(s, behaviorById.get(s.id) || {});
  const inputs = s.paramCount === 0 ? "no inputs" : `${s.paramCount} input${s.paramCount === 1 ? "" : "s"}`;
  const parts = [lead || `Takes ${inputs}`];
  if (outCount === 1) parts.push("leaning on one other part of the system");
  else if (outCount > 1) parts.push(`pulling together ${outCount} other parts of the system`);
  s.autoExplanation = parts.join(", ") + ".";
}

// ---------------------------------------------------------------------------
// Flags (architecture smells) + an actionable recommendation per flagged function.
// Thresholds follow published defaults: cognitive complexity > 15 (SonarSource),
// cyclomatic > 10 (SonarSource/McCabe), > 4 params, > 60 lines.
// ---------------------------------------------------------------------------
const THRESH = { params: 4, loc: 60, complexity: 10, cognitive: 15 };
// Turn the breached thresholds into a concrete, plain-language suggestion the
// author can act on — naming the fix, not just the number (after SonarQube's
// "reduce from X to Y" pattern). Cognitive complexity is the headline signal.
function recommend(s) {
  const C = s.complexity, K = s.cognitive, P = s.paramCount, L = s.loc;
  const bits = [];
  if (K != null && K > THRESH.cognitive) {
    const over = K - THRESH.cognitive;
    if (C != null && K > C + 3) {
      bits.push(`Hard to follow (cognitive complexity ${K}, ${over} over the ${THRESH.cognitive} guide) — mostly from nested conditionals/loops. Pull the innermost block out into its own function; each nesting level you remove roughly halves the score.`);
    } else {
      bits.push(`Hard to follow (cognitive complexity ${K}, ${over} over the ${THRESH.cognitive} guide). Split it by responsibility into smaller functions.`);
    }
  } else if (C != null && C > THRESH.complexity) {
    bits.push(`Cyclomatic complexity ${C} is high, but it reads flat (cognitive ${K}) — likely a switch or guard clauses. Low priority; only split if it's really doing two jobs.`);
  }
  if (P > THRESH.params) {
    bits.push(`${P} parameters is a lot to track — group the related ones into an options object, or split the function so each path takes fewer inputs.`);
  }
  if (L > THRESH.loc && !(K != null && K > THRESH.cognitive) && !(C != null && C > THRESH.complexity)) {
    bits.push(`Long (${L} lines) but not complex — fine unless it's two unrelated concerns pasted together.`);
  }
  return bits.join(" ");
}
for (const s of symbols) {
  if (s.kind === "class") continue;
  if (s.paramCount > THRESH.params)
    s.flags.push({ type: "too-many-params", value: s.paramCount, limit: THRESH.params });
  if (s.loc > THRESH.loc)
    s.flags.push({ type: "long-function", value: s.loc, limit: THRESH.loc });
  if (s.cognitive != null && s.cognitive > THRESH.cognitive)
    s.flags.push({ type: "hard-to-follow", value: s.cognitive, limit: THRESH.cognitive });
  else if (s.complexity != null && s.complexity > THRESH.complexity)
    s.flags.push({ type: "high-complexity", value: s.complexity, limit: THRESH.complexity });
  s.recommendation = s.flags.length ? recommend(s) : "";
}

// Cycles among module edges (restricted to scope for signal).
function findCycles(nodes, edges) {
  const adj = new Map();
  for (const n of nodes) adj.set(n, []);
  for (const e of edges) {
    if (adj.has(e.from) && adj.has(e.to)) adj.get(e.from).push(e.to);
  }
  const cycles = [];
  const color = new Map(); // 0 white,1 gray,2 black
  const stack = [];
  const seen = new Set();
  function dfs(u) {
    color.set(u, 1);
    stack.push(u);
    for (const v of adj.get(u) || []) {
      if (color.get(v) === 1) {
        const idx = stack.indexOf(v);
        const cyc = stack.slice(idx);
        const key = [...cyc].sort().join("|");
        if (!seen.has(key)) {
          seen.add(key);
          cycles.push(cyc.slice());
        }
      } else if (!color.get(v)) {
        dfs(v);
      }
    }
    stack.pop();
    color.set(u, 2);
  }
  for (const n of nodes) if (!color.get(n)) dfs(n);
  return cycles;
}
const scopeArr = [...scopeFiles];
const cycles = findCycles(scopeArr, moduleEdges).filter((c) =>
  c.some((p) => changedInProject.has(p))
);

// Entry points for data-flow tracing. A good place to start following data is
// a "root" — a function nothing else in scope calls — ranked by how much of the
// flow you can reach from it. Always produce candidates so the walk is never
// blank; fall back to the widest-reaching functions if there are no clean roots.
const entryPoints = [];
{
  const hasCaller = new Set(calls.map((c) => c.to));
  const calleesBy = new Map();
  for (const c of calls) {
    if (!calleesBy.has(c.from)) calleesBy.set(c.from, []);
    calleesBy.get(c.from).push(c.to);
  }
  const reachOf = (id) => {
    const seen = new Set();
    const stack = [id];
    while (stack.length) {
      const n = stack.pop();
      for (const t of calleesBy.get(n) || []) if (!seen.has(t)) { seen.add(t); stack.push(t); }
    }
    return seen.size;
  };
  const scored = symbols
    .filter((s) => s.kind !== "class")
    .map((s) => {
      const root = !hasCaller.has(s.id);
      const reach = reachOf(s.id);
      const score = reach * 2 + (root ? 6 : 0) + (s.changed ? 4 : 0) + (s.exported ? 1 : 0);
      const reason = root
        ? reach
          ? `starts a chain of ${reach} step${reach === 1 ? "" : "s"}`
          : "a starting point — nothing else calls it"
        : `reaches ${reach} step${reach === 1 ? "" : "s"} downstream`;
      return { s, root, reach, score, reason };
    })
    .sort((a, b) => b.score - a.score);
  const roots = scored.filter((x) => x.root);
  const picked = (roots.length ? roots : scored).slice(0, 8);
  for (const x of picked) {
    entryPoints.push({ id: x.s.id, name: x.s.name, file: x.s.file, reason: x.reason, changed: x.s.changed, reach: x.reach });
  }
}

// ---------------------------------------------------------------------------
// Relevance: which neighbors actually matter for THIS change.
// A file is relevant if its code connects to the CHANGED code — it calls or is
// called by a changed function, or it imports a changed export — not merely
// because it imports the same hub module (types, constants, config). This keeps
// "+ Related" focused instead of dragging the whole app back in.
// ---------------------------------------------------------------------------
const relevantFiles = new Set(changedInProject);
const relevantSymbolIds = new Set(symbols.filter((s) => s.changed).map((s) => s.id));
// (1) call graph: callers and callees of changed functions.
for (const c of calls) {
  const from = symbolById.get(c.from);
  const to = symbolById.get(c.to);
  if (!from || !to) continue;
  if (from.changed) { relevantSymbolIds.add(to.id); relevantFiles.add(to.file); }
  if (to.changed) { relevantSymbolIds.add(from.id); relevantFiles.add(from.file); }
}
// (2) importers that specifically import a CHANGED export (catches consumers of
// changed functions/classes the call resolver missed; ignores files that only
// use unchanged exports of a changed hub).
const changedExportsByFile = new Map();
for (const s of symbols) {
  if (s.changed && s.exported) {
    if (!changedExportsByFile.has(s.file)) changedExportsByFile.set(s.file, new Set());
    changedExportsByFile.get(s.file).add(s.name);
  }
}
for (const changedFile of changedInProject) {
  const changedExp = changedExportsByFile.get(changedFile);
  if (!changedExp || !changedExp.size) continue;
  for (const importer of importedBy.get(changedFile) || []) {
    const sf = sourceFiles.get(importer);
    if (!sf) continue;
    for (const imp of sf.getImportDeclarations()) {
      const tgt = imp.getModuleSpecifierSourceFile?.();
      if (!tgt || rel(tgt.getFilePath()) !== changedFile) continue;
      if (imp.getNamedImports().some((n) => changedExp.has(n.getName()))) {
        relevantFiles.add(importer);
        break;
      }
    }
  }
}
// Mark symbols. A class counts as relevant if it's changed or owns a relevant method.
for (const s of symbols) {
  if (s.kind === "class") {
    s.relevant = s.changed || symbols.some((m) => m.className === s.name && m.file === s.file && relevantSymbolIds.has(m.id));
  } else {
    s.relevant = s.changed || relevantSymbolIds.has(s.id);
  }
  if (s.relevant) relevantFiles.add(s.file);
}

// ---------------------------------------------------------------------------
// Per-file payload (diff + source)
// ---------------------------------------------------------------------------
function readSource(path) {
  const abs = join(repo, path);
  if (!existsSync(abs)) return null;
  try {
    const src = readFileSync(abs, "utf8");
    return src.length > 400_000 ? src.slice(0, 400_000) + "\n/* …truncated… */" : src;
  } catch {
    return null;
  }
}

// Whole-file diff (all lines as context) so the report can render old vs new
// side by side across the entire file, not just the changed hunks.
function fullDiffOf(path) {
  let d = git(["diff", changes.base, "--unified=100000", "--", path]);
  if (!d.trim() && changes.statusOf.get(path) === "A") {
    d = git(["diff", "--no-index", "--unified=100000", "--", nullDevice, path]);
  }
  return d;
}

// Per-line git blame for the working-tree version, so the report can show a
// VS Code-style inline blame with a hover popover. Best effort; large files skipped.
function blameOf(path) {
  const abs = join(repo, path);
  if (!existsSync(abs)) return null;
  let out;
  try {
    out = git(["blame", "--porcelain", "--", path]);
  } catch {
    return null;
  }
  if (!out) return null;
  const commits = {};
  const lines = [];
  let cur = null;
  for (const line of out.split("\n")) {
    const h = /^([0-9a-f]{40}) \d+ (\d+)/.exec(line);
    if (h) { cur = { sha: h[1] }; continue; }
    if (!cur) continue;
    if (line.startsWith("author ")) cur.author = line.slice(7);
    else if (line.startsWith("author-time ")) cur.time = +line.slice(12);
    else if (line.startsWith("summary ")) cur.summary = line.slice(8);
    else if (line.startsWith("\t")) {
      const short = cur.sha.slice(0, 8); // key commits by short sha to match lines[]
      if (!commits[short]) commits[short] = { sha: short, author: cur.author || "", time: cur.time || 0, summary: cur.summary || "" };
      lines.push(short);
      cur = null;
    }
  }
  return { commits, lines }; // lines[i] = short sha for source line i+1
}

const filesOut = [];
for (const path of scopeFiles) {
  const changed = changedCode.has(path);
  filesOut.push({
    path,
    changed,
    relevant: relevantFiles.has(path),
    status: changes.statusOf.get(path) || (changed ? "M" : ""),
    inScope: true,
    language: /\.tsx?$/.test(path) ? "typescript" : "javascript",
    diff: changed ? (changes.diffFor.get(path) || "") : "",
    // Full-context diff (whole file as one hunk) so the full-file view can show
    // the old and new versions side by side, not just the changed hunks.
    fullDiff: changed ? fullDiffOf(path) : "",
    // New-side line numbers that were added/modified, so the full-file view can
    // mark which lines changed in the context of the whole file.
    changedLines: changed ? [...(changes.changedLinesFor.get(path) || [])] : [],
    source: readSource(path),
    blame: changed ? blameOf(path) : null,
    importsTo: [...(importsTo.get(path) || [])],
    importedBy: [...(importedBy.get(path) || [])],
    symbols: symbols.filter((s) => s.file === path).map((s) => s.id),
  });
}

// ---------------------------------------------------------------------------
// Model + render
// ---------------------------------------------------------------------------
const flagCounts = symbols.reduce((acc, s) => {
  for (const f of s.flags) acc[f.type] = (acc[f.type] || 0) + 1;
  return acc;
}, {});

// ---------------------------------------------------------------------------
// PR reviewability score — how hard this change is to review, so the author can
// act on it. Grounded in published findings: review quality drops past ~400
// changed LOC (Cisco/SmartBear) and good reviews touch <10 files (Google's
// study); generated/lockfile/locale and test lines are excluded from the code
// size (as mature size-labelers do), and breadth across packages is penalized.
// ---------------------------------------------------------------------------
function reviewability() {
  const GEN_RE = /(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|\.min\.(js|css)$|\.snap$|(^|\/)(dist|build|vendor|generated)\/|\.generated\.|\.(po|pot|xlf|xliff)$)/;
  let codeLoc = 0, testLoc = 0, genLoc = 0;
  const codeFiles = new Set();
  const testFiles = new Set();
  const pkgs = new Set();
  // Count churn across every changed file from git — not just the scoped code
  // files in `filesOut`. Tests are excluded from the graph by default, so
  // iterating `filesOut` here dropped them from the breakdown entirely (testLoc
  // was always 0). `changes` has all of them, tests and generated included.
  for (const path of changes.files) {
    let ch = 0;
    for (const line of (changes.diffFor.get(path) || "").split("\n")) {
      if (/^\+\+\+|^---/.test(line)) continue;
      if (line[0] === "+" || line[0] === "-") ch++;
    }
    if (GEN_RE.test(path)) { genLoc += ch; continue; }
    if (TEST_RE.test(path)) { testLoc += ch; testFiles.add(path); continue; }
    codeLoc += ch;
    codeFiles.add(path);
    const m = path.match(/^packages\/([^/]+)\//) || path.match(/^([^/]+)\//);
    pkgs.add(m ? m[1] : path);
  }
  const files = codeFiles.size, packages = pkgs.size, nTestFiles = testFiles.size;
  const bLoc = codeLoc > 400 ? 1 : codeLoc >= 200 ? 0.5 : 0;
  const bFiles = files > 10 ? 1 : files >= 5 ? 0.5 : 0;
  const bPkg = packages >= 4 ? 1 : packages >= 2 ? 0.5 : 0;
  const score = Math.round(45 * bLoc + 30 * bFiles + 25 * bPkg);
  const label = score >= 61 ? "Hard" : score >= 31 ? "Moderate" : "Easy";
  const sizeLabel = codeLoc >= 1000 ? "XXL" : codeLoc >= 500 ? "XL" : codeLoc >= 100 ? "L" : codeLoc >= 30 ? "M" : codeLoc >= 10 ? "S" : "XS";
  let note = `${codeLoc} changed line${codeLoc === 1 ? "" : "s"} across ${files} code file${files === 1 ? "" : "s"}`;
  if (packages > 1) note += ` in ${packages} packages`;
  note += ".";
  const extra = [];
  if (testLoc) extra.push(`${testLoc} in ${nTestFiles} test file${nTestFiles === 1 ? "" : "s"}`);
  if (genLoc) extra.push(`${genLoc} generated/locale (ignored)`);
  if (extra.length) note += ` Plus ${extra.join(" and ")}.`;
  let suggestion = "";
  if (label === "Hard") {
    suggestion = packages >= 4
      ? "Consider splitting it — e.g. one PR per package, or the refactor apart from the new behaviour. Stacked PRs (one branch per layer) keep each diff focused."
      : codeLoc > 400
        ? "Consider splitting into smaller, stacked PRs so each stays under a few hundred lines and can be reviewed on its own."
        : "Consider narrowing the scope so a reviewer can hold it in their head.";
  } else if (label === "Moderate") {
    suggestion = "Reviewable, but on the larger side — smaller would go faster.";
  }
  return { score, label, sizeLabel, loc: codeLoc, files, packages, testLoc, testFiles: nTestFiles, generatedLoc: genLoc, note, suggestion };
}
const reviewabilityScore = reviewability();

// ---------------------------------------------------------------------------
// Test-coverage signal — which changed code files got a matching test change in
// the same PR, and which didn't. "Behaviour changed, tests didn't" is a classic
// review red flag, and common in agent-authored PRs (awesomecodereviews.com
// checklist §6, "review the tests first"). It's a prompt, not a verdict: a pure
// refactor, rename, or config tweak may legitimately need no test change.
// ---------------------------------------------------------------------------
function baseNameOf(p) {
  return (p.split("/").pop() || "").replace(/\.(test|spec)\.[jt]sx?$/, "").replace(/\.[jt]sx?$/, "");
}
function testCoverage() {
  const testBases = [...changes.files].filter((p) => TEST_RE.test(p)).map(baseNameOf);
  const codeFiles = [...changedCode]; // changed, non-test code files
  // A test matches a code file when its base equals the code base, or extends it
  // with a qualifier — e.g. `cf-entity.delete.spec.ts` covers `cf-entity.ts`.
  const matches = (codeBase) => testBases.some((tb) => tb === codeBase || tb.startsWith(codeBase + "."));
  const gaps = [], covered = new Set();
  for (const p of codeFiles) {
    if (matches(baseNameOf(p))) covered.add(p);
    else gaps.push(p);
  }
  return { changedCodeFiles: codeFiles.length, withTest: covered.size, gaps, coveredSet: covered };
}
const testCov = testCoverage();
// Annotate changed code files so the report can badge "no test change".
for (const f of filesOut) {
  if (f.changed && !TEST_RE.test(f.path)) f.hasTestChange = testCov.coveredSet.has(f.path);
}

// ---------------------------------------------------------------------------
// New-dependency callout — external packages newly imported by the changed code,
// plus dependency lines added to package.json. Checklist §7: are new deps
// necessary, from a trusted source at a supported version, lockfile updated?
// Surfaced because agents pull in packages easily. A prompt, not a verdict.
// ---------------------------------------------------------------------------
function pkgNameOf(spec) {
  const parts = spec.split("/");
  return spec.startsWith("@") ? parts.slice(0, 2).join("/") : parts[0];
}
function newDependencies() {
  const byPkg = new Map(); // pkg -> Set(files that newly import it)
  const IMPORT_RE = /(?:from|import|require\s*\(|import\s*\()\s*['"]([^'"]+)['"]/;
  for (const p of changedCode) {
    const sf = sourceFiles.get(p);
    // Collect added vs removed import specifiers. A dep counts as new only if it
    // appears on an added line but not a removed one — otherwise a single-line
    // import rewritten across multiple lines, or a reordered import, would look
    // "new" when the package was already there.
    const added = new Set(), removed = new Set();
    for (const line of (changes.diffFor.get(p) || "").split("\n")) {
      const sign = line[0];
      if ((sign !== "+" && sign !== "-") || line.startsWith("+++") || line.startsWith("---")) continue;
      const m = IMPORT_RE.exec(line.slice(1));
      if (!m) continue;
      const spec = m[1];
      if (spec.startsWith(".") || spec.startsWith("/")) continue; // relative/internal
      (sign === "+" ? added : removed).add(spec);
    }
    for (const spec of added) {
      if (removed.has(spec)) continue; // reformatted or reordered, not new
      // If ts-morph resolves the specifier to an in-project file, it's a path
      // alias, not a real dependency — skip it.
      if (sf) {
        const decl = sf.getImportDeclarations().find((d) => d.getModuleSpecifierValue() === spec);
        if (decl && decl.getModuleSpecifierSourceFile && decl.getModuleSpecifierSourceFile()) continue;
      }
      add(byPkg, pkgNameOf(spec), p);
    }
  }
  // Dependency entries added to any changed package.json.
  const SKIP_KEYS = new Set(["name", "version", "description", "main", "module", "types", "typings", "license", "private", "author", "homepage", "repository", "bugs", "scripts", "keywords"]);
  const packageJson = [];
  for (const p of changes.files) {
    if (!/(^|\/)package\.json$/.test(p)) continue;
    const added = [];
    for (const line of (changes.diffFor.get(p) || "").split("\n")) {
      const mm = /^\+\s*"([^"]+)"\s*:\s*"[^"]+"\s*,?\s*$/.exec(line);
      if (mm && !SKIP_KEYS.has(mm[1])) added.push(mm[1]);
    }
    if (added.length) packageJson.push({ file: p, added });
  }
  const imported = [...byPkg.entries()].map(([pkg, files]) => ({ pkg, files: [...files] }));
  return { imported, packageJson };
}
const newDeps = newDependencies();

// GitHub info for line-number permalinks. Only when the tree is committed
// (e.g. a PR checkout) — for uncommitted work the new-side lines aren't on any
// commit, so a permalink would point at the wrong content.
function githubInfo() {
  try {
    if (changes.hasWorkingChanges) return null;
    const url = git(["config", "--get", "remote.origin.url"]).trim();
    const m = url.match(/github\.com[:/]([^/]+)\/(.+?)(?:\.git)?$/);
    if (!m) return null;
    return {
      url: `https://github.com/${m[1]}/${m[2]}`,
      sha: git(["rev-parse", "HEAD"]).trim(),
      baseSha: git(["rev-parse", changes.base]).trim(),
    };
  } catch {
    return null;
  }
}
const github = githubInfo();

const model = {
  meta: {
    repo,
    repoName: repo.split(sep).pop(),
    base: changes.base,
    diffSource: changes.source,
    scope: args.scope,
    thresholds: THRESH,
    generatedAtNote: "timestamp injected by caller",
    github,
    reviewability: reviewabilityScore,
    testCoverage: { changedCodeFiles: testCov.changedCodeFiles, withTest: testCov.withTest, gaps: testCov.gaps },
    newDependencies: newDeps,
    counts: {
      changedFiles: changedCode.size,
      scopeFiles: scopeFiles.size,
      symbols: symbols.length,
      calls: calls.length,
      moduleEdges: moduleEdges.filter((e) => scopeFiles.has(e.from) && scopeFiles.has(e.to)).length,
      cycles: cycles.length,
      flags: flagCounts,
    },
  },
  overview: "",
  themes: [], // review map: reviewer-authored groups of {title, why, files, flow}
  comments: [], // local draft review comments: {file, line?, kind, body}
  files: filesOut,
  symbols,
  calls,
  moduleEdges: moduleEdges.filter((e) => scopeFiles.has(e.from) && scopeFiles.has(e.to)),
  cycles,
  entryPoints,
};

// Optional: merge a reviewer-authored explanations sidecar in one pass.
if (args.explanations && existsSync(args.explanations)) {
  mergeExplanations(model, JSON.parse(readFileSync(args.explanations, "utf8")));
}

const outPath =
  args.out ||
  join(
    tmpdir(),
    "agent-reviews",
    `review-${model.meta.repoName}.html`
  );

const modelJsonPath = outPath.replace(/\.html$/, ".model.json");
try {
  renderModel(model, outPath);
  mkdirSync(dirname(modelJsonPath), { recursive: true });
  writeFileSync(modelJsonPath, JSON.stringify(model, null, 2));
} catch (e) {
  console.error(`[error] ${e.message}`);
  process.exit(1);
}

// Console summary for the agent.
console.log(
  JSON.stringify(
    {
      ok: true,
      out: outPath,
      model: modelJsonPath,
      base: changes.base,
      diffSource: changes.source,
      counts: model.meta.counts,
      cycles: cycles.length,
      entryPoints: entryPoints.map((e) => `${e.name} (${e.file})`),
      topFlags: symbols
        .filter((s) => s.flags.length)
        .sort((a, b) => b.flags.length - a.flags.length)
        .slice(0, 15)
        .map((s) => ({
          name: s.className ? `${s.className}.${s.name}` : s.name,
          file: s.file,
          line: s.startLine,
          loc: s.loc,
          params: s.paramCount,
          complexity: s.complexity,
          flags: s.flags.map((f) => f.type),
        })),
    },
    null,
    2
  )
);
