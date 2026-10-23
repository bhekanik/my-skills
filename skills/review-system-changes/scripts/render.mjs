#!/usr/bin/env node
// Render a model.json into the interactive HTML report, optionally merging an
// explanations sidecar (authored by the reviewer) that powers the Follow-data
// walkthrough narration.
//
// Used as a library by analyze.mjs and as a CLI to re-render after enriching:
//   node render.mjs <model.json> [--explanations <expl.json>] [--comments <comments.json>]
//                   [--pr <number>] [--out <file.html>] [--template <file>]
//
// explanations.json shape (all optional):
//   {
//     "overview": "one-paragraph plain-language summary of the change",
//     "symbols": { "<symbolId>": "what this function does to the data" },
//     "calls":   { "<fromId>-><toId>": "what data flows on this hop and why" }
//   }

import { readFileSync, writeFileSync, mkdirSync, existsSync, realpathSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export function mergeExplanations(model, expl) {
  if (!expl) return model;
  if (typeof expl.overview === "string") model.overview = expl.overview;
  // Review map: themes group the change by reason, with the files involved and
  // how the data flows across them.
  if (Array.isArray(expl.themes)) model.themes = expl.themes;
  // Draft review comments anchored to file[+line].
  if (Array.isArray(expl.comments)) model.comments = expl.comments;
  if (expl.symbols) {
    for (const s of model.symbols) {
      if (expl.symbols[s.id]) {
        s.explanation = expl.symbols[s.id];
        s.explained = true;
      }
    }
  }
  if (expl.calls) {
    for (const c of model.calls) {
      const k = `${c.from}->${c.to}`;
      if (expl.calls[k]) c.note = expl.calls[k];
    }
  }
  return model;
}

export function renderModel(model, outPath, templatePath) {
  const tpl = templatePath || join(__dirname, "..", "assets", "report-template.html");
  if (!existsSync(tpl)) throw new Error(`template not found: ${tpl}`);
  // Escape "<" so embedded source/diff can't break the inline JSON <script>.
  const json = JSON.stringify(model).replace(/</g, "\\u003c");
  const html = readFileSync(tpl, "utf8").replace('"__MODEL_JSON__"', () => json);
  mkdirSync(dirname(outPath), { recursive: true });
  writeFileSync(outPath, html);
  return outPath;
}

// ---- CLI ---- (realpath compare: skill dir is often symlinked)
function isMain() {
  try {
    return realpathSync(process.argv[1]) === fileURLToPath(import.meta.url);
  } catch {
    return false;
  }
}
if (isMain()) {
  const argv = process.argv.slice(2);
  const modelPath = argv.find((a) => !a.startsWith("--"));
  const opt = (name) => {
    const i = argv.indexOf(name);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  if (!modelPath) {
    console.error("Usage: node render.mjs <model.json> [--explanations <expl.json>] [--comments <pr-comments.json>] [--pr <number>] [--out <file.html>] [--template <file>]");
    process.exit(1);
  }
  const model = JSON.parse(readFileSync(resolve(modelPath), "utf8"));
  const explPath = opt("--explanations");
  if (explPath) mergeExplanations(model, JSON.parse(readFileSync(resolve(explPath), "utf8")));
  // --comments appends (doesn't replace), so fetched PR comments and authored
  // local drafts can both be shown.
  const cmtPath = opt("--comments");
  if (cmtPath) {
    const extra = JSON.parse(readFileSync(resolve(cmtPath), "utf8"));
    if (Array.isArray(extra.comments)) model.comments = (model.comments || []).concat(extra.comments);
  }
  // --pr <number> lets the report build a `gh` command to post a draft comment.
  const pr = opt("--pr");
  if (pr && model.meta) model.meta.pr = pr.replace(/[^0-9]/g, "");
  const out = resolve(opt("--out") || modelPath.replace(/\.model\.json$/, ".html").replace(/\.json$/, ".html"));
  renderModel(model, out, opt("--template"));
  writeFileSync(modelPath, JSON.stringify(model, null, 2)); // persist merged explanations
  console.log(JSON.stringify({ ok: true, out }, null, 2));
}
