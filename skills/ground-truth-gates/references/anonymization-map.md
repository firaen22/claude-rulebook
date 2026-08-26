# Structure-preserving anonymization map

Replace PII VALUES, keep the SHAPE the classifier keys on — `REDACTED` breaks
a regex that expects a digit run. Pointer target of ground-truth-gates
"Building the case set" step 2.

| PII | Replace with |
|---|---|
| digit runs (phone/policy/ID) | `12345678` (same-shape digits) |
| email | `client@example.com` |
| HKID / govt ID | `X123456(7)` |
| `@handles` | `@user` |
| separator-grouped account numbers | `ACCT000` |
| letter-prefixed case IDs | `CASE123456` |
| names (CJK or Latin) | `陳大文` / `John Doe` |
| JWT / API keys | `[JWT]` / `[KEY]` |

The map is a floor, not a ceiling: any new PII class found in a real export
gets a same-shape stand-in added here before the line is promoted. The full
anonymizer/self-test design (export-from-X flow) is in the source doc named
in the skill's Sources section.
