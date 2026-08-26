---
name: reference-obsidian-mcp-gotchas
description: Verified Obsidian MCP write/read quirks — wrong-param-name silent failures with misleading errors, and oversized-read handling via the persisted tool-results file
metadata:
  type: reference
---

# Obsidian MCP gotchas (mined 2026-07-24, reproduced in secondbrain digest runs)

The obsidian MCP validates parameter names loosely and returns misleading
errors on the wrong key — diff your param names against the schema FIRST when
a write fails with a weird message, before theorizing about empty content or a
server bug:

- `patch_note` wants `newString`/`oldString` (camelCase). Passing `new_string`
  (snake_case) → `"newString cannot be empty"` — reads like an empty-value bug,
  is actually a dropped key.
- `write_note` wants `path`. Passing `file_path` → `"Error: Cannot read
  properties of undefined (reading 'replace')"` — a cryptic internal crash, not
  an "unknown parameter" message.

Oversized reads persist, don't vanish:

- `read_note` on a large single-line file (e.g. a ~58KB daily `index.md`) errors
  with `"exceeds maximum allowed tokens"` but SAVES the full payload to a
  `tool-results/*.txt` path named in the error. Don't retry the read — `grep -n`
  or python-slice that persisted file to locate the anchor line, then edit with
  an anchored `patch_note` (exact-string match, `matchCount:1`) instead of a
  read-modify-write. Avoids both the token cap and clobber risk on a
  daily-growing note. See also [[reference-notebooklm-mcp-v077]] for the
  response-envelope gotchas of a different MCP.
