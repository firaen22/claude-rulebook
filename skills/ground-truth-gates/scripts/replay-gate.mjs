#!/usr/bin/env node
// Replay gate — locks a pure transform's output (redaction, PII scrubbing, text
// normalization) against a frozen baseline. Any drift on any line fails the gate.
// This makes "did my edit change what leaks?" a one-command answer.
//
// Usage:
//   node replay-gate.mjs --module <path.mjs> --corpus <corpus.jsonl> \
//     --baseline <baseline.json> [--update] [--export transform]
//
// Module contract: exports (text: string) => string | Promise<string>
//   (default export or named `transform`; override the name with --export).
// Corpus file: one JSON value per line — either a JSON string ("raw text")
//   or an object {"input":"raw text"}.
// Baseline: written by --update, then committed frozen. Re-freeze ONLY after an
//   intentional change whose diff you have eyeballed line by line.
//
// Exit codes: 0 = no drift (or baseline updated), 1 = drift, 2 = usage/data error.

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

function arg(name, dflt) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] !== undefined ? process.argv[i + 1] : dflt;
}
const flag = name => process.argv.includes(`--${name}`);

const modPath = arg('module');
const corpusPath = arg('corpus');
const baselinePath = arg('baseline');
const exportName = arg('export');

if (!modPath || !corpusPath || !baselinePath) {
  console.error('usage: node replay-gate.mjs --module <path.mjs> --corpus <corpus.jsonl> --baseline <baseline.json> [--update] [--export transform]');
  process.exit(2);
}

const mod = await import(pathToFileURL(resolve(modPath)).href);
const fn = exportName ? mod[exportName] : (mod.default ?? mod.transform);
if (typeof fn !== 'function') {
  console.error(`replay-gate: ${modPath} does not export a function (default or \`transform\`; use --export <name>).`);
  process.exit(2);
}

const lines = readFileSync(resolve(corpusPath), 'utf8').split('\n').filter(l => l.trim());
if (lines.length === 0) {
  console.error(`replay-gate: ${corpusPath} is empty — an empty gate proves nothing.`);
  process.exit(2);
}
const inputs = lines.map((l, i) => {
  let v;
  try { v = JSON.parse(l); } catch (e) {
    console.error(`replay-gate: bad JSON on line ${i + 1}: ${e.message}`);
    process.exit(2);
  }
  const input = typeof v === 'string' ? v : v?.input;
  if (typeof input !== 'string') {
    console.error(`replay-gate: line ${i + 1} must be a JSON string or {"input":"..."}.`);
    process.exit(2);
  }
  return input;
});

const actual = {};
for (const input of inputs) actual[input] = String(await fn(input));

if (flag('update')) {
  writeFileSync(resolve(baselinePath), JSON.stringify(actual, null, 2) + '\n');
  console.log(`replay-gate: baseline frozen — ${inputs.length} lines → ${baselinePath}`);
  console.log('Eyeball the diff before committing; the baseline IS the spec now.');
  process.exit(0);
}

if (!existsSync(resolve(baselinePath))) {
  console.error(`replay-gate: no baseline at ${baselinePath}. Run once with --update to freeze one (then eyeball it).`);
  process.exit(2);
}
const baseline = JSON.parse(readFileSync(resolve(baselinePath), 'utf8'));

let drift = 0;
for (const input of inputs) {
  if (!(input in baseline)) {
    drift++;
    console.log(`  NEW LINE (no baseline)  "${input}" → "${actual[input]}"`);
  } else if (baseline[input] !== actual[input]) {
    drift++;
    console.log(`  DRIFT  "${input}"`);
    console.log(`    baseline: "${baseline[input]}"`);
    console.log(`    actual:   "${actual[input]}"`);
  }
}
const removed = Object.keys(baseline).filter(k => !inputs.includes(k));
for (const k of removed) console.log(`  note: baseline entry no longer in corpus: "${k}"`);

console.log(`replay-gate: ${inputs.length} lines, ${drift} drifted`);
console.log(drift === 0 ? 'PASS' : 'FAIL — output drifted; if intentional, eyeball then re-freeze with --update');
process.exit(drift === 0 ? 0 : 1);
