# Lens: false green

For any guard, gate, assertion, fixture, or check that can PASS. A false green is
worse than no check: it converts an unverified state into a reported-verified one.

Report each hit as location + the exact input that passes wrongly + the fix.

- **Feed the guard EMPTY.** Zero bytes, empty string, empty array, empty object,
  zero rows. Does the check pass? (Measured 2026-08-29: `gzip -c` of a 0-byte file
  produces a valid **32-byte** archive, so `[ ! -s "$ARCHIVE" ]` passed for an
  archive containing nothing.)
- **Feed it MISSING vs EMPTY separately.** These are different inputs and a fixture
  written for one does not cover the other. The 32-byte case above survived a
  negative fixture that only proved the missing-file branch.
- **Name what the check actually asserts, then name what the caller BELIEVES it
  asserts.** The gap between those two sentences is the defect. "The file exists" is
  not "the file has the content we wrote."
- **Does a PASS require the work to have happened?** A check that passes when the
  step was skipped entirely (no-op, early return, caught exception) is a false green.
  Ask: what is the smallest edit to the subject that this check would NOT catch?
- **Exit status vs output.** A command that prints an error and exits 0, a pipeline
  masking a failing stage, `${PIPESTATUS[0]}` under zsh (yields nothing) — verify the
  status plumbing itself with a deliberately failing input before trusting a green.
- **Can this check FAIL?** Run it against known-bad input. A regression test that
  does not fail against the old buggy code is not a regression test. A gate nobody
  has seen red is unproven.
- **Count-based greens.** "12 tests passed" says nothing if the suite silently
  collected 12 of 40 — check the denominator, not the numerator.
- **Silent default on absence.** `.get(k, "")`, `|| []`, `?? 0` inside a validation
  path turns a missing input into a passing one. Absence must fail loud.
- **A harness protocol exit is not a green.** Exit 0 meaning "do not block the
  session" is not a claim that anything was verified. Apply this lens to the POLICY
  DECISION (did we allow a commit, or a destructive command, without the check having
  run?) — never to the fail-open plumbing of a PreCompact/SessionStart logger, whose
  contract is to exit 0 always. See `shell-and-hooks.md` for which class applies.
