---
name: logic-matching
description: |
  Java-to-TypeScript logic matching and porting verification skill. Use this skill whenever the user wants to: compare calculation results between an original Java app and its TypeScript/web port; find logic discrepancies in ported code; trace why a web app produces different output from the original; fix ported calculation bugs by referencing the Java source; or verify that a TS port faithfully reproduces Java behavior. Especially relevant for the Moira (七政四餘) astrology project, but applicable to any Java→TS porting scenario. Trigger on phrases like "對比", "對多次", "logic matching", "同原app比", "port", "porting bug", "計算唔同", or when the user provides reference output and asks why the web version differs.
---

# Logic Matching: Java → TypeScript Port Verification

You are helping verify that a TypeScript web port faithfully reproduces the calculation logic of an original Java application. This skill captures hard-won lessons from porting the Moira (七政四餘) astrology engine.

## Core Workflow

### Phase 1: Establish Ground Truth

Before touching any code, establish what the correct output should be.

1. **Get a reference case** — Ask the user for a specific test input and the expected output from the original Java app. Screenshots, text dumps, or the original app running live all work.
2. **Run the same input in the web app** — Capture the FULL output (use `get_page_text` or equivalent to get structured data, not just visual inspection).
3. **Diff field by field** — Create a comparison table of every output value. Don't just check what looks wrong visually — compare ALL fields systematically. Discrepancies in one field often reveal bugs affecting other fields too.

**Example comparison table:**
```
| Field      | Original App | Web App    | Match? |
|------------|-------------|------------|--------|
| 年柱        | 甲戌         | 乙亥       | WRONG  |
| 月柱        | 丙子         | 戊寅       | WRONG  |
| 日柱        | 壬辰         | 戊申       | WRONG  |
| 命宮宿位    | 壁0水        | 室10火      | WRONG  |
```

### Phase 2: Trace Each Discrepancy to Source Code

For each wrong field, follow this investigation path:

1. **Find the TS calculation function** — Use Grep/Glob to locate the function that produces the wrong value.
2. **Find the equivalent Java method** — Search the Java source (typically in `moira-source/` or similar) for the same algorithm.
3. **Compare the algorithms side by side** — Look for these common porting pitfalls:

#### Common Porting Pitfalls (ranked by frequency)

**1. Calendar/Time System Mismatches**
The #1 source of bugs in calendar-heavy applications. Different systems use different epoch boundaries:
- Solar calendar year (Jan 1) vs 立春 (~Feb 4) vs 冬至 (~Dec 22) for year changes
- Calendar month (Jan=1) vs solar term month (節氣) for month boundaries
- Clock time vs Local Apparent Time (LAT / 真太陽時) for time-sensitive calculations
- **Detection**: If multiple output fields are wrong simultaneously, suspect a systemic calendar/time issue rather than individual calculation bugs.

**2. Reference Point / Offset Errors**
When a calculation uses a known reference date/value and offsets from it:
- Wrong reference value (e.g., claiming Jan 1 2001 = 庚辰 when it's actually 甲子)
- Off-by-one in the offset calculation
- **Detection**: The output is consistently wrong by a fixed amount. Verify reference points independently using standard formulas.

**3. Integer Math / Modulo Differences**
JavaScript's `%` operator preserves the sign of the dividend, unlike Java's:
- `-7 % 3` → `-1` in JS, `2` in some Java contexts
- Always use `((x % n) + n) % n` for positive modulo in JS
- `Math.floor()` vs integer division truncation

**4. Missing Intermediate Corrections**
The Java code may apply corrections that aren't obvious:
- True solar time (LAT) adjustments before time-sensitive calculations
- Precession corrections for astronomical positions
- Timezone vs longitude-based time offsets
- **Detection**: Results are close but not exact, or differ depending on geographic location.

**5. Parameter Passing Differences**
The Java method may receive pre-processed data that the TS version constructs differently:
- Check what the Java caller passes — trace the call site, not just the function
- Look for `_adj` or `adjusted` variables that hint at pre-processing
- A function might receive LAT-corrected time in Java but raw clock time in TS

### Phase 3: Fix and Verify

For each bug found:

1. **Fix the TS code** to match the Java logic
2. **Run `tsc --noEmit`** to catch type errors
3. **Re-run the test case** and verify the specific field is now correct
4. **Check that other fields didn't regress** — fixing one bug can reveal or create others

### Phase 4: Cross-Validate with Additional Cases

One matching test case doesn't guarantee correctness. After fixing:
- Test dates near boundaries (e.g., Feb 3 vs Feb 5 for 立春)
- Test different locations (different timezone offsets exercise longitude corrections)
- Test edge cases in the specific domain

## Moira-Specific Knowledge

When working on the Moira (七政四餘) project specifically:

### Key Files
- **Java source**: `moira-source/org/athomeprojects/base/ChartData.java` — main calculation engine
- **Java math**: `moira-source/org/athomeprojects/base/Calculate.java` — Julian Day, LAT, ephemeris
- **TS pillars**: `moira-web/src/lib/chinese/stems-branches.ts` — 八字 four pillars
- **TS calculations**: `moira-web/src/lib/ephemeris/calculations.ts` — main calculation orchestrator
- **TS mansions**: `moira-web/src/lib/ephemeris/mansions.ts` — 28 mansions

### Known Fixed Issues (Reference)
These were identified and fixed — if they recur or if similar patterns appear elsewhere, apply the same fix pattern:

1. **Day Pillar JDN offset**: Reference point JDN 2451911 (2001-01-01) is 甲子 (offsets 0,0), not 庚辰 (offsets 6,4). Verify with: `stem = (JDN+9) % 10`, `branch = (JDN+1) % 12`.

2. **Year Pillar 立春 boundary**: BaZi year changes at 立春 (Sun at ecliptic longitude 315 degrees), not Jan 1. If Sun longitude is between 270 and 315 degrees, use `year - 1`.

3. **Month Pillar solar terms**: BaZi month is determined by Sun's ecliptic longitude, not calendar month. Formula: `monthIndex = floor(((sunLong - 315) % 360 + 360) % 360 / 30)`.

4. **命宮 LAT correction**: The original Java app applies Local Apparent Time correction to both sunrise and birth times before the life palace calculation. The longitude correction `(observerLong - tzOffset*15) / 15` hours can shift sunrise across a 時辰 boundary, changing the result by 30 degrees. This is the kind of bug that's invisible until you compare with specific test cases at specific locations.

5. **Display vs Calculation bugs**: Sometimes the calculation is correct but the display reads from the wrong data source (e.g., using Ascendant's mansion instead of lifeSign's mansion). Always verify both the underlying value AND how it's displayed.

## Investigation Checklist

When the user reports a discrepancy, work through this checklist:

- [ ] Get exact test input (date, time, location) and expected output
- [ ] Run web app with same input, capture full output text
- [ ] Create field-by-field comparison table
- [ ] For each wrong field: find TS function → find Java function → compare
- [ ] Check the Java call site (what parameters are passed, any pre-processing?)
- [ ] Look for calendar boundary issues (立春, 節氣, time zones)
- [ ] Look for time system issues (LAT vs clock time)
- [ ] Look for reference point / offset errors
- [ ] Fix, type-check, verify
- [ ] Test additional cases near boundaries
