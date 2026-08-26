#!/usr/bin/env node
// Golden gate — runs the REAL classifier (no mocks) over labeled real cases.
// Cost-asymmetric scoring: a FALSE ROUTE (fired the wrong concrete action) fails
// the gate no matter how good aggregate F1 looks; a DEFER MISS (fell through to
// the fallback) only warns. Aggregate F1 averages false routes away — the hard
// gate is what surfaces them.
//
// Usage:
//   node golden-gate.mjs --module <path.mjs> --cases <cases.jsonl> \
//     [--no-match "(fallback)"] [--min-f1 0.90] [--export classify]
//
// Module contract: exports (text: string) => string | null | Promise<...>
//   (default export or named `classify`; override the name with --export).
//   null/undefined return = defer to fallback (the NO_MATCH label).
// Cases file: one JSON object per line: {"input":"...","intent":"..."}
//   Label defer-expected cases (hard negatives) with the NO_MATCH label.
//
// Exit codes: 0 = gate passes, 1 = gate fails, 2 = usage/data error.

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

function arg(name, dflt) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] !== undefined ? process.argv[i + 1] : dflt;
}

const modPath = arg('module');
const casesPath = arg('cases');
const NO_MATCH = arg('no-match', '(fallback)');
const MIN_F1 = parseFloat(arg('min-f1', '0.90'));
const exportName = arg('export');

if (!modPath || !casesPath || Number.isNaN(MIN_F1)) {
  console.error('usage: node golden-gate.mjs --module <path.mjs> --cases <cases.jsonl> [--no-match "(fallback)"] [--min-f1 0.90] [--export classify]');
  process.exit(2);
}

const mod = await import(pathToFileURL(resolve(modPath)).href);
const fn = exportName ? mod[exportName] : (mod.default ?? mod.classify);
if (typeof fn !== 'function') {
  console.error(`golden-gate: ${modPath} does not export a function (default or \`classify\`; use --export <name>).`);
  process.exit(2);
}

const lines = readFileSync(resolve(casesPath), 'utf8').split('\n').filter(l => l.trim());
if (lines.length === 0) {
  console.error(`golden-gate: ${casesPath} is empty — an empty gate proves nothing.`);
  process.exit(2);
}
const cases = lines.map((l, i) => {
  let c;
  try { c = JSON.parse(l); } catch (e) {
    console.error(`golden-gate: bad JSON on line ${i + 1}: ${e.message}`);
    process.exit(2);
  }
  if (typeof c.input !== 'string' || typeof c.intent !== 'string') {
    console.error(`golden-gate: line ${i + 1} needs string fields "input" and "intent".`);
    process.exit(2);
  }
  return c;
});

const results = [];
for (const c of cases) {
  const raw = await fn(c.input);            // await supports sync and async classifiers
  const pred = raw == null ? NO_MATCH : String(raw);
  results.push({ ...c, pred, ok: pred === c.intent });
}

const misses = results.filter(r => !r.ok);
const falseRoutes = misses.filter(m => m.pred !== NO_MATCH); // wrong concrete action — hard fail
const deferMisses = misses.filter(m => m.pred === NO_MATCH); // fell through to fallback — warn only

// macro F1 over concrete intents (the defer label is not an intent)
const intents = [...new Set(cases.map(c => c.intent))].filter(x => x !== NO_MATCH);
const f1s = intents.map(intent => {
  const tp = results.filter(r => r.pred === intent && r.intent === intent).length;
  const fp = results.filter(r => r.pred === intent && r.intent !== intent).length;
  const fng = results.filter(r => r.pred !== intent && r.intent === intent).length;
  const p = tp + fp === 0 ? 0 : tp / (tp + fp);
  const r = tp + fng === 0 ? 0 : tp / (tp + fng);
  return p + r === 0 ? 0 : (2 * p * r) / (p + r);
});
const macroF1 = f1s.length ? f1s.reduce((a, b) => a + b, 0) / f1s.length : 1;

console.log(`golden-gate: ${results.length} cases, ${results.length - misses.length} correct, macro-F1 ${macroF1.toFixed(3)} (min ${MIN_F1})`);
for (const m of falseRoutes) console.log(`  FALSE ROUTE  "${m.input}"  expected=${m.intent}  got=${m.pred}`);
for (const m of deferMisses) console.log(`  defer miss   "${m.input}"  expected=${m.intent}  fell through to ${NO_MATCH}`);

const pass = falseRoutes.length === 0 && macroF1 >= MIN_F1;
console.log(pass ? 'PASS' : `FAIL — ${falseRoutes.length} false route(s), macro-F1 ${macroF1.toFixed(3)}`);
process.exit(pass ? 0 : 1);
