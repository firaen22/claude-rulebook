# Lens: shared state and concurrency

For any artifact that reads or writes a file, directory, or record that another
session, process, or future run also touches.

Report each hit as location + the interleaving or lifecycle that breaks it + the fix.

- **Name every writer.** Who else writes this path? Another session of the same
  agent, a hook, a cron job, the user, a subordinate with write access. If more than
  one, the interleaving is a real case, not a theoretical one. (Measured: a
  subordinate holding write access has reverted or wiped concurrent work twice.)
- **Concurrent append.** Two processes appending to one file: is each record written
  in a single write, and is it under the atomic-append size? A record assembled by
  multiple writes interleaves and corrupts both.
- **Line protocol integrity.** For any line-delimited format, can a field contain a
  newline or tab? If the writer does not escape (JSON-encode, quote), one malformed
  value silently destroys every downstream read.
- **Read-then-write races.** Any check-then-act on shared state (size cap, "does it
  exist", "is it locked") is stale by the time it acts. Where an ATOMIC primitive
  exists for the operation — `O_CREAT|O_EXCL`, `flock`, `mkdir`, atomic rename — the
  fix is that primitive, not a tighter check; recommending a re-check where an atomic
  primitive was available is itself the finding. Re-validating immediately before the
  side effect is the fallback when no atomic primitive exists: it narrows the race
  and does not close it, and the code must say so.
- **Key derivation must be identical at every site.** If two components derive the
  same key (a hash, a session id, a path-based name), diff the derivation code
  character by character. A spelling mismatch is a total silent lookup failure that
  is indistinguishable from "no data yet." For a PATH used as a key, canonicalize
  first: `/tmp` vs `/private/tmp` (macOS — `realpath /tmp` IS `/private/tmp`), a
  trailing slash, and a relative path all hash to different buckets. Verified
  2026-08-29.
- **Lifecycle: who creates, who reads, who deletes, in what order?** A consumer that
  can run before the producer's first write must handle absence as a normal state,
  not an error. Check the very first run and the run after a wipe.
- **Unbounded growth and cleanup.** Same as the shell lens: caps, and never delete
  what this run did not demonstrably create (attribute by record AND by current
  identity, never by pattern-matching what looks like our output).
- **Does anything assume an id is stable across a lifecycle boundary?** Session ids,
  pids, and temp names may not survive a restart, resume, or compaction. If the code
  assumes stability, that assumption must be measured, not asserted.
