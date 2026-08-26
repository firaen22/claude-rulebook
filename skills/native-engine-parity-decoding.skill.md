---
name: native-engine-parity-decoding
description: Reverse-engineer an Android NDK-shipped C++ calculation engine (libcalcfacade.so style) to bring a TypeScript port into byte-level parity with the APK. Use when porting Chinese divination engines (六壬/奇門/八字), or any closed-source native algorithm where you need to match the APK's exact output rather than textbook doctrine. Triggers: "match the APK", "parity with libXxx.so", "decode setXxxInfo", "reverse-engineer this algorithm", "the web output differs from the app", or any work in `moira-web/scripts/{liuren,qimen}-oracle/`.
tools: Agent, Read, Edit, Write, Bash, Grep, Glob, TodoWrite
---

# Native-Engine Parity Decoding

A playbook for cracking an Android `.so` calculation engine and porting it to TypeScript with byte-level parity. Battle-tested on 2 Chinese divination APKs (C6R 六壬, QM 奇門遁甲) over 5 PRs (#22–#26 in `moira-web`); decoded ~10 algorithms including 通道 filter, 取局法 dispatcher, 5-source 驛馬, 反吟/伏吟, 刻家 起局.

## When to use

- The TS port disagrees with the APK on a specific field and classical doctrine doesn't reconcile it.
- The APK ships a native lib (`libcalcfacade.so`, `libXxxEngine.so`) that you can extract.
- Stakes justify byte-level parity (chart correctness, regression test ground truth).

Do NOT use for:
- Pure UI/rendering parity (use screenshots).
- Pure Flutter/Dart logic (use `blutter` / `reFlutter` on `libapp.so` instead).
- Algorithms cheaper to capture visually (one-off rule, no recurring divergences).

## The hard constraint: parity > doctrine

This is non-negotiable. From `AGENTS.md`:

> moira-web must match Moira.jar output, not classical doctrine. Never "fix" toward external doctrine if it breaks Moira output.

The APK is the oracle. If your decode disagrees with a textbook, the textbook loses. Three real examples from this codebase:

1. **取局法 default** — classical doctrine says 拆補 is the default 取局法. The APK's `decideJSHour` dispatcher defaults to **置潤 (`zr`)**. Decoded at `0x61dec0`, verified by 7 boundary fixtures. The TS port was "matching doctrine" and silently wrong.
2. **刻家 起局** — `decideJSQuarterType0` does a non-classical noon-pivot 陰陽遁 split. No textbook describes it. The disasm is the spec.
3. **`h_fz_*` fields** — an audit doc previously guessed they were a per-palace 20-vector 神煞 layer. The oracle confirmed they're chart-level prose strings (e.g. `h_fz_bh = "逃不能遠，易獲。"`). The APK ships no per-palace 神煞 layer; do not invent one.

When the disasm and your intuition conflict, **the disasm is right**.

## The workflow

```
extract APK → ABI select → demangle symbols → facade audit
  → output-key map (via *2Json serializer) → oracle harness
  → fixture probe → algorithm decode → TS port → fixture tests → PR
```

### 1. Extract the APK and pick the ABI

```bash
unzip -d /tmp/qm-apk reference/奇門_QM_20260122_2330_APKPure.apk
ls /tmp/qm-apk/lib/
# armeabi-v7a/  arm64-v8a/  x86_64/
```

Pick `arm64-v8a` — that's what modern devices and BlueStacks-on-Apple-Silicon run, and `aarch64-linux-android21-clang++` is the easiest cross-compile target. The relevant .so files:

| File | Role |
|---|---|
| `libcalcfacade.so` | C++ engine + JSON facade — **the prize** |
| `libapp.so` | Flutter AOT snapshot (Dart UI binding) |
| `libflutter.so` | Flutter runtime |

### 2. Demangle the symbol table

```bash
NDK=/opt/homebrew/share/android-ndk
TOOL=$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin

# Demangled function symbols (T = text)
$TOOL/llvm-nm --defined-only /tmp/qm-apk/lib/arm64-v8a/libcalcfacade.so \
  | awk '$2=="T"' \
  | $TOOL/llvm-cxxfilt > /tmp/qm-symbols.txt

# Full disasm (large; redirect or pipe-grep)
$TOOL/llvm-objdump -d /tmp/qm-apk/lib/arm64-v8a/libcalcfacade.so > /tmp/qm.s

# Read-only data section (for inline string literals)
$TOOL/llvm-objcopy --dump-section .rodata=/tmp/qm-rodata.bin libcalcfacade.so
```

Grep for the symbols you'll need:

- **Facade entries** (the dlopen surface): `grep '::calc\|::get.*Info' /tmp/qm-symbols.txt`
- **Util\* methods** (the engine internals): `grep '^Util\|^Calc.*Util' /tmp/qm-symbols.txt`
- **`*2Json` serializers** (the output schema oracle): `grep '2Json' /tmp/qm-symbols.txt`
- **`JsonStr2*` deserializers** (the input schema oracle): `grep 'JsonStr2\|InParm' /tmp/qm-symbols.txt`
- **In/Out parm types**: `grep 'InParm\|OutParm' /tmp/qm-symbols.txt`

### 3. Facade audit — real vs demo stubs

**Critical disambiguator.** Vendor APKs in this family ship facade entries that may be demo-only — they return hardcoded fixtures regardless of input. You MUST audit each entry before assuming it's an oracle.

Read the first ~80 instructions of each `Facade::*(std::string)` method. The pattern:

| Shape | Verdict |
|---|---|
| Calls `JsonStr2InParm*` → `Util*::do(InParm*)` → `Out*2Json` | Real, input-respecting |
| Stores literal year/month/day/hour onto a local InParm, ignoring input | Demo stub |
| Branches early on `input.empty()` then loads constants | Demo stub |

Audit results from the two APKs we cracked:

| APK | Facade | Verdict |
|---|---|---|
| C6R 六壬 | 5 entries, **1 real** (`getXNInfo` only) | Mostly demo — abandon, decode statically |
| C8W 八字 | 10 entries, **0 real** | All demo — abandon, decode statically |
| QM 奇門 | 5 entries, **all 5 real** | Build the oracle harness |

If the facade is mostly demo, two options:
1. **Pure static decode** (the C6R route): read disasm of `Util*` methods, decode by hand.
2. **Decode `InParm*`/`OutParm*` struct layouts**, then call lower-level `Util::do(InParm*)` directly via dlopen — nontrivial because you must construct the typed struct correctly. Worth it only if 5+ open questions remain.

### 4. Map the output schema via the `*2Json` serializer

This is the highest-leverage decode step. The serializer (e.g. `OutParmCalcqm2Json` at `0x4ce078`) is essentially a labeled dump of every field on the OutParm struct. By reading it linearly you get a complete map of (struct offset) → (JSON key) → (type).

Two emission patterns to recognize:

**A) Scalar keys** — single `operator[](const char*)` on a `.rodata` string:
```
adrp  x1, page             ; page-aligned addr
add   x1, x1, #offset      ; full addr of "i_jn\0" in .rodata
bl    Json::Value::operator[]
```
Resolve the addr → grep the rodata for the null-terminated string.

**B) Vector keys (libc++ SSO strings built inline)** — this is the one you must master:
```
mov   w8, #0x6c6c          ; 'l','l'   (low 16 bits)
movk  w8, #0x745f, lsl #16 ; '_','t'   (high 16 bits) → "ll_t"
stur  w8, [sp, #0x21]      ; into SSO buffer (offset +1)
mov   w9, #0x70            ; 'p','\0'
sturh w9, [sp, #0x25]
mov   w10, #(6<<1)         ; SSO size byte = (length<<1) | sso_flag
sturb w10, [sp, #0x20]     ; into SSO size byte (offset 0)
```

libc++ short-string layout (24 bytes on arm64):
- byte 0: `size << 1` (low bit = 0 means SSO mode)
- bytes 1–22: content
- byte 23: padding

So `0x0c` at offset 0 = size 6, content at +1 = `"lst_dp"`. Decode every key this way at every call to `IntLst2JsonLst` / `StrLst2JsonLst` / `operator[]`. The struct offset just-loaded (`ldr x0, [x21, #0x30]`) tells you which field maps to that key.

Result: a complete `OutParm` field map like the one in `tasks/plan-qimen-audit.md` §1.

### 5. Build the dlopen+ADB oracle harness

If the facade is real (QM case), build a 50-line shim that calls it on an Android device. See `scripts/qimen-oracle/` for the canonical exemplar.

Prerequisites:
```bash
brew install --cask android-ndk
brew install --cask android-platform-tools
# arm64 device/emulator with ADB (BlueStacks on Apple Silicon reports arm64-v8a)
adb devices
```

Minimal `oracle.cc`:
```cpp
#include <dlfcn.h>
#include <cstdio>
#include <iostream>
#include <sstream>
#include <string>

int main(int argc, char** argv) {
  const char* entry = argc > 1 ? argv[1] : "calcqm";
  void* h = dlopen("./libcalcfacade.so", RTLD_NOW | RTLD_LOCAL);
  using Fn = char* (*)(const char*);
  auto fn = reinterpret_cast<Fn>(dlsym(h, entry));
  std::stringstream b; b << std::cin.rdbuf();
  std::string in = b.str();
  std::fputs(fn(in.c_str()), stdout);
  std::fputc('\n', stdout);
}
```

Build + push:
```bash
NDK=/opt/homebrew/share/android-ndk
$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/aarch64-linux-android21-clang++ \
  -O2 -fno-exceptions -static-libstdc++ oracle.cc -o oracle -ldl
unzip -joq $APK lib/arm64-v8a/libcalcfacade.so -d .
adb push oracle libcalcfacade.so /data/local/tmp/
adb shell chmod 755 /data/local/tmp/oracle
```

Run:
```bash
printf '%s' '{"year":2015,"month":4,"day":8,"hour":11,"minute":30,"qmtype":"hour","qmss":"auto"}' \
  | adb shell 'cd /data/local/tmp && ./oracle calcqm'
```

**ABI quirk to remember**: C++ methods on empty classes (like `CalcqmFacade::calcqm`) have `this` elided in the AArch64 ABI. Calling them as `(self, input)` thunks segfaults. The vendors helpfully ship plain-C wrappers at unmangled symbol names (`calcqm`, `calcSearchQm`, etc.) — use those.

### 6. Fixture-probe technique

Once the oracle works, design fixtures to invalidate hypotheses fast:

- **Vary one input field at a time** while holding the rest constant. Diff the JSON outputs. The diff narrows what each input controls.
- **Design boundary cases** — 節氣 transitions (within ±2 hours), month/day rollovers, 旬 transitions. Most rules differ only at boundaries.
- **Capture a fixture matrix** — e.g. `qmss_hour_mg.json`: 5 取局法 modes × 7 datetimes. Lets you confirm "mode X equals mode Y" relationships, which is how we found `auto == zr` (not `auto == chaibu` as doctrine suggested).
- **Use the oracle to invalidate**, not just confirm. If your hypothesis says "this changes when input X changes", probe X first. Silent identical output = falsified.

Capture scripts live at `scripts/qimen-oracle/capture-*.sh`. Each builds a small fixture matrix and writes to `fixtures/`.

### 7. Decode a specific algorithm

For the target function (e.g. `UtilCalcqm::decideJSHour`):

1. Find its address: `grep decideJSHour /tmp/qm-symbols.txt` → cross-ref with disasm.
2. Read the disasm in chunks of 20–50 instructions. Look for:
   - **Dispatcher**: `ldr x0, [inParm, #0x80]` (load a field) + string-compare chain. The field's identity comes from `JsonStr2InparmCalcqm` — look at the same `+0x80` offset there.
   - **Helper calls**: `bl Util*::*` — these are the building blocks. Decode them first if shared.
   - **Tight loops**: `cmp x_, #N; b.lt loop` — usually iterating a vector. The `#N` is the size.
   - **Lookup tables**: `adrp/add/ldrb` reading from `.rodata` — dump the relevant rodata bytes.
3. Write pseudocode with inline disasm address comments. Keep it close to the asm structure first; clean up later.
4. Test the pseudocode against fixtures before porting to TS.

See `tasks/plan-tongdao-filter.md` for a fully-worked example of this process.

## Anti-patterns and traps

These cost session-hours in this codebase. Each is a story.

### Trap 1: Probing an int field as if it were a string (or vice versa)

The QM `qmss` input field is an int (取局方式 mode flag). The prior session tried probing it with strings like `"auto"`/`"chaibu"`. The JSON deserializer silently no-ops on type mismatch, so the engine kept reading whatever default the inParm initializer set (`0`). Output never changed → "this field doesn't seem to matter" → wrong dispatcher field guessed.

The real field was **`hour_mg`** (a string with default `"zr"`) at offset `+0x80`, found by reading `JsonStr2InparmCalcqm` at `0x4cd2d0`.

**Defense**: before probing, find the deserializer line for the field and confirm its type. Cost: 30 seconds. Saves: a half-day rabbit hole.

### Trap 2: Trusting audit notes from before the oracle existed

The first QM audit pass guessed `h_fz_*` was a 20-vector per-palace 神煞 layer (based on the 20 suffixes). The oracle later showed they're chart-level prose strings. If you'd implemented the speculation, you'd have shipped invented data labeled as 神煞 doctrine.

**Defense**: re-verify any audit claim made before the oracle was built. The oracle is ground truth; pre-oracle notes are hypotheses.

### Trap 3: Implementing textbook algorithms when the APK does something non-classical

`decideJSQuarterType0` (刻 起局) does a noon-pivot 陰陽遁 split that no textbook describes. If you'd implemented classical doctrine, the chart-diff harness would have caught it eventually — but with hours of bisection. Reading the disasm first is faster.

**Defense**: invoke the `AGENTS.md` parity rule before opening any reference book. Decode first; classify against doctrine second (and only as a sanity check).

### Trap 4: Confusing demo facades with real ones

The C6R team initially built the dlopen oracle, fed it inputs, and got the same 1980-01-01 12:30 output every time. It took an hour to realize 4 of 5 entries were demo stubs. The QM facade looked similar at a glance but was actually real.

**Defense**: audit step 3 (facade audit) is mandatory. Read the first 80 instructions and look for `JsonStr2InParm` calls. No deserializer call ⇒ demo.

### Trap 5: Reading `+0x30` as "first vector" without checking the serializer

OutParm structs have many vectors; the offset alone doesn't tell you which JSON key it serializes to. The 通道 decode initially assumed `+0x30` was 三傳 (3 entries); the serializer call site revealed `cmp x22, #0xc` (12-entry iteration) → it was actually `lst_dp`. Saved by reading the `*2Json` map first.

**Defense**: always cross-reference struct offsets through the `*2Json` serializer map before naming them.

## TS port pattern

Once decoded, the port should be:

1. **Pure function**, no side effects, deterministic.
2. **Disasm-address-anchored doc block** at the top — every decoded function gets a reference to its `0x...` address and the symbol name. Future debuggers can re-derive your work from the binary.
3. **Pseudocode in the doc block** matching the disasm structure, with verified fixture rows inline.
4. **Vitest fixture tests** using oracle JSON as ground truth — the `.json` files live alongside the test.
5. **Default-off rollout** when divergent — gate behind a flag while you verify, flip the default after fixture pass.

Canonical exemplars in this repo:

- `src/lib/chinese/qimen-jufa.ts` — 取局法 dispatcher with full per-mode pseudocode and bucket-mapping verification table.
- `src/lib/chinese/liuren/tongdao.ts` — 通道 filter with 5-pair loop, 干合 化氣 table inlined.
- `src/lib/chinese/qimen.ts` — main 奇門 engine; see how decoded rules wire into the existing engine.

Commit message convention: `feat|docs(<module>): <action> <symbol> @ 0x<addr>` — makes commits greppable by binary address later. See `git log --oneline master | head -20` for examples.

## Tool inventory

| Tool | Purpose | Path on this machine |
|---|---|---|
| `llvm-objdump` | Disasm `.so` | `$NDK/toolchains/llvm/prebuilt/darwin-x86_64/bin/` |
| `llvm-nm` | Symbol table | same |
| `llvm-cxxfilt` | Demangle C++ symbols | same |
| `llvm-objcopy` | Dump `.rodata` for string lookup | same |
| `aarch64-linux-android21-clang++` | Cross-compile oracle | same |
| `adb` | Push/run oracle on emulator | `brew install --cask android-platform-tools` |
| BlueStacks | arm64-v8a emulator on Apple Silicon | App Store / vendor site |
| `blutter` | Decompile Flutter AOT (`libapp.so`) — backup path when native facade is fully demo | https://github.com/worawit/blutter |
| `reFlutter` | Alternative Flutter AOT inspector | https://github.com/Impact-I/reFlutter |
| `vitest` | Fixture-based parity tests | `npm test` |
| `gh` | PR-driven incremental landing (one decoded algorithm per PR) | `brew install gh` |

`NDK ?= /opt/homebrew/share/android-ndk` (set in oracle Makefiles).

## Canonical exemplars in this repo

When in doubt, read these first:

- `tasks/plan-tongdao-filter.md` — the original full disasm decode that established the technique. Read this for the JSON-key SSO decode pattern and the 5-pair outer-loop shape.
- `tasks/plan-qimen-audit.md` — facade audit + complete `OutParmCalcqm` vector-key map. The exemplar for step 4.
- `scripts/qimen-oracle/README.md` + `oracle.cc` + `Makefile` — the canonical oracle harness. 50 lines of C++, 30 lines of Make.
- `scripts/qimen-oracle/capture-*.sh` — the fixture-probe pattern (5 modes × 7 datetimes matrices).
- `scripts/liuren-oracle/README.md` — the cautionary tale: build the harness, discover the facade is demo, document the dead end, abandon. Time-saver for the next person.
- `src/lib/chinese/qimen-jufa.ts` — the gold standard for disasm-anchored TS port doc blocks.
- Commits `d2a9fc3`, `6357e44`, `aaeac3c`, `5c363d0`, `48ee372` on `master` — one decode per PR, each PR body explains what was decoded and why.

## Sequencing for a new target

If you're starting fresh on a new algorithm:

1. **Reproduce the divergence** — get a TS-output vs APK-output diff on one fixture you can keep open in two windows.
2. **Find the symbol** — `grep` the demangled symbol table for keywords matching the divergent field. Pattern: `set<FieldName>Info`, `decideJS<Thing>`, `getNext<Thing>`.
3. **Find the field in OutParm** — read the relevant `*2Json` serializer, locate the JSON key, note the struct offset.
4. **Audit if oracle is live** — already done for QM; skip if so.
5. **Run an oracle fixture matrix** — boundary cases for the suspected inputs.
6. **Read the target function disasm** — pseudocode it.
7. **Implement, test against fixtures, PR.**

Time budget per algorithm in this codebase: 1–4 hours for a clean decode once the workflow is internalized. Most of the budget is reading disasm, not writing code.
