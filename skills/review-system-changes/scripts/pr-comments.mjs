#!/usr/bin/env node
// Fetch a GitHub PR's inline review comments and write them in the shape the
// report understands, so real reviewer feedback shows up next to the diff
// alongside any local drafts.
//
// Usage:
//   node pr-comments.mjs --pr <number|url> [--repo <owner/repo>] [--out <file.json>]
//
// Reads only (gh api GET); never posts. Requires the `gh` CLI, authenticated.
// Output: { "comments": [ { file, line, kind:"review", author, source:"github", body } ] }
// Merge into a report with: render.mjs <model.json> --comments <this file>

import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 ? process.argv[i + 1] : def;
}
function gh(args) {
  try {
    return execFileSync("gh", args, {
      encoding: "utf8",
      maxBuffer: 128 * 1024 * 1024,
      stdio: ["ignore", "pipe", "pipe"],
    });
  } catch (error) {
    if (error && error.code === "ENOENT") {
      throw new Error("GitHub CLI (gh) is not installed or is not on PATH");
    }
    const detail = error && error.stderr ? String(error.stderr).trim() : "";
    throw new Error(`gh ${args[0]} failed${detail ? `: ${detail}` : ""}`);
  }
}

const prArg = arg("--pr");
if (!prArg) {
  console.error("Usage: node pr-comments.mjs --pr <number|url> [--repo <owner/repo>] [--out <file.json>]");
  process.exit(1);
}

// Resolve owner/repo + PR number from a URL or a number (+ optional --repo).
let owner, repo, num;
const urlMatch = /github\.com\/([^/]+)\/([^/]+)\/pull\/(\d+)/.exec(prArg);
if (urlMatch) {
  [, owner, repo, num] = urlMatch;
} else {
  num = prArg.replace(/[^0-9]/g, "");
  const repoArg = arg("--repo");
  let nwo;
  try {
    nwo =
      repoArg ||
      gh(["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).trim();
  } catch (error) {
    console.error(`[error] ${error.message}; pass --repo owner/repo or use a PR URL`);
    process.exit(1);
  }
  [owner, repo] = nwo.split("/");
}
if (!owner || !repo || !num) {
  console.error(`[error] could not resolve owner/repo/number from --pr "${prArg}"${arg("--repo") ? "" : " (pass --repo owner/repo)"}`);
  process.exit(1);
}

let arr;
try {
  arr = JSON.parse(gh(["api", `repos/${owner}/${repo}/pulls/${num}/comments`, "--paginate"]));
} catch (e) {
  console.error(`[error] gh api failed: ${e.message}`);
  process.exit(1);
}

const comments = (Array.isArray(arr) ? arr : [])
  .map((c) => ({
    file: c.path,
    line: c.line ?? c.original_line ?? null,
    kind: "review",
    author: c.user && c.user.login,
    source: "github",
    body: (c.body || "").trim(),
  }))
  .filter((c) => c.file && c.body);

const out = resolve(arg("--out", `pr-${num}-comments.json`));
writeFileSync(out, JSON.stringify({ comments }, null, 2));
console.log(JSON.stringify({ ok: true, out, pr: `${owner}/${repo}#${num}`, count: comments.length }, null, 2));
