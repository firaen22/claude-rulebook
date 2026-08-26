# When stuck — wrong-direction check, retry gate, mechanism replacement

Consult this when a step keeps failing or a fix isn't converging. The one-line
trigger in operational-rigor §3 points here.

## Wrong-direction check (rubrics §4)

If ≥2 hold, stop retrying, write down what you know, change approach or escalate:

- [ ] Each fix resolves one symptom and creates another.
- [ ] You've added 2+ special cases to keep the approach alive.
- [ ] You can't state in one sentence WHY the last attempt failed.
- [ ] Diff keeps growing while criteria-met stays flat.
- [ ] You're editing things you don't understand to see what happens.

## Mandatory pre-retry gate

Write "attempt N failed because ___" with a MECHANISM in the blank. Can't fill it
→ you may not retry; go reproduce the failure in isolation first. Hard cap: 2
rounds of the same approach, then change something structural (tier,
decomposition, approach).

## Three defects, one mechanism → replace the mechanism

A review returning ≥3 defects that share one MECHANISM means don't patch each:
replace the mechanism with a tool that excludes the class by construction
(hand-rolled regex parsing → a real tokenizer), prototyped as a standalone script
against its own input→expected matrix BEFORE wiring it in.

GOOD: "Attempt 2 failed because the click lands on a modal title with the same
text as the button — selector problem, not form state. New approach: disambiguate
the selector." BAD: five rounds theorizing about React state without checking what
element the click resolved to. (Cheap structural check before expensive theory.)
