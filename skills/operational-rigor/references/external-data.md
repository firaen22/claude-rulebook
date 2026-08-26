# Handling external / untrusted data — fail loud, verify the real shape

Consult when writing a parser, adapter, importer, or any code that reads data
whose shape you did not define (third-party APIs, logs, another repo's output,
user uploads). The one-line trigger in operational-rigor §4 points here.

## Data-path integrity — fail loud on *unspecified* ambiguity

Never emit a silently-wrong value. Honor an explicit documented contract (a
declared default, precedence, or freshness window); what is forbidden is
*silently* inventing one. When a value is unavailable and no contract covers it:

- a missing input is not silently `0`/default — carry the unknown through; an
  estimate stays labelled estimated, not exact;
- conflicting values fail fast or apply a *declared* precedence, never insertion
  order;
- an unmatched record is surfaced, not silently dropped;
- an unreadable/unknown reading is not a positive verdict — fail closed; never
  infer "fresh/healthy/present/safe" from inability to check.

✅ blank / `—` when genuinely unknown. ❌ "null rate → show 0% so the chart still
renders."

## A clue about external data is a map, not a schema

A field shape learned from docs, a blog, another repo, or memory tells you where
to look, never what is there — sample the real shape on a real instance before
writing the parser/adapter (the failure is a mis-imagined storage format, not
merely a wrong path). A third-party field's NAME is not its contract: verify its
semantics on real output before branching, and keep a redacted sample (not raw
third-party values — they may carry secrets/PII) to re-derive anything you
compute from it.
