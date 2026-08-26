---
name: reference-browser-pane-gotchas
description: Verified Browser-pane / claude-in-chrome tool quirks that corrupt in-browser verification — resize no-op, persistent JS context, stale frames, smooth-scroll false reads, tabId typing
metadata:
  type: reference
---

# Browser-pane verification gotchas (mined 2026-07-21, all reproduced in-session)

Two toolsets coexist: `mcp__Claude_Browser__*` (in-app Browser pane) and
`mcp__claude-in-chrome__*` (real Chrome extension). They have different tabId
typing — mid-workflow, keep every call on ONE server; a stray call to the twin
fails schema validation ("expected string, received undefined" for tabId).
Some runtimes require explicit `tabId` even with a single tab open. A
`"No preview is open. Use preview_start..."` result from `mcp__Claude_Browser__*`
mid-workflow is the same mixup in the other direction: you called the
preview-pane browser when you meant the extension — re-issue the identical
action on `mcp__claude-in-chrome__*`, don't debug the page.

**Verification-corrupting quirks** (each cost retries in real sessions):

- `resize_window` preset (`mobile`) can silently no-op — response says
  "Viewport set to 375x812" while `window.innerWidth` stays 1280. Pass explicit
  width/height and confirm via `window.innerWidth` before trusting any
  responsive-layout observation.
- `javascript_exec` page context PERSISTS across calls in the same tab —
  top-level `const` collides with earlier snippets ("Identifier already
  declared"). Wrap every probe in an IIFE. (Reproduced in two projects.)
- Screenshots can serve a stale/cached frame at a scroll position, and
  `computer scroll` can hang on some pages — verify contrast/layout via
  `getComputedStyle` / `get_page_text`, and JS-scroll with explicit waits.
- Computed styles read at t=0 of a theme flip show OLD values — re-read after
  the CSS transition (~700ms) before declaring a failure.
- Reading `scrollLeft`/positions right after setting them returns stale values
  under `scroll-smooth` — force `scrollTo({behavior:'instant'})` before reading.
- A click returning "ok" only proves a handler ran — verify the intended state
  change (tab switched, modal open); text-match selectors can resolve to a
  different or off-screen element (see [[feedback-verify-click-target-before-state-theory]]).
- claude-in-chrome `scroll_amount` caps at 10 — repeat scrolls instead.
- Browser `find` can 529 (upstream overload) — fall back to coordinate click
  from the last screenshot rather than retrying find in a loop.
- Virtualized lists (Outlook message list, any infinite-scroll UI) defeat
  single-shot DOM queries: only the ~6-8 RENDERED rows exist, so a "count
  all matching X" JS pass returns a confident undercount with no error.
  Scroll incrementally and accumulate into a persistent window var
  (`window.__acc`), then read the accumulated set. (2026-07-22, Outlook via
  claude-in-chrome: single pass saw 8 of 26 in-scope emails; mechanism is
  page-side so it applies to both browser MCPs.)
- Hidden scroll container: when synthetic scroll (wheel, click-then-scroll,
  Page_Down) doesn't move a long page, the scrollable element is usually a
  nested container, not `body`/`document`. Walk the ancestor chain dumping
  `{overflowY, scrollHeight, clientHeight}`; the real container has
  `overflowY:auto|scroll` AND `scrollHeight > clientHeight`. Set its
  `scrollTop` directly and READ IT BACK — a decoy accepts the write but reads
  back `scrollTop:0` (not actually scrollable). Read-back is what rejects
  decoys (same expected-vs-actual discipline as R0, applied to DOM state).
  (2026-07-24, Outlook email body via claude-in-chrome.)
- Another app stealing focus mid-sequence (Safari, the Windows taskbar
  Widgets board) silently truncates or misdirects the `type`/paste that
  follows: keystrokes land in the wrong window or hit a `>>` continuation
  prompt. Screenshot to detect the drift, refocus the intended window, and
  recover (Ctrl+C a stuck prompt) rather than assuming the prior action
  landed. (2026-07-24, computer-use over RDP; applies to any pixel-driven
  automation, not just the browser.)
