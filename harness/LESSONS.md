# LESSONS — write-backs after mistakes (format: 40-maintenance.md §3)

Append-only between compressions. Compress at >150 lines / >20 entries.

## 2026-07-05 — Stop hook pointed at /tmp; script got wiped, feature died silently
- What happened: the `settings.json` Stop hook ran `bash /tmp/hook-debug.sh`
  (context-size monitor, asyncRewake at ~50% full). macOS periodically cleans
  /tmp; the script no longer existed, so the hook failed on every session stop
  with no visible symptom — the context-warning feature was dead for weeks.
- Root cause: hook wired to a scratch path during debugging, never repointed to
  the permanent copy at `~/.claude/compact-context-monitor.sh`.
- Rule change needed: NONE — but a convention worth holding: hook commands and
  scheduled scripts must live on permanent paths (`~/.claude/...`), never /tmp
  or a scratchpad.
- Status: applied-on 2026-07-05 (hook repointed to the permanent script;
  verified: JSON valid, script runs, exit 0 on small transcript)

## 2026-07-05 — Context monitor nagged forever after /compact (size proxy never reset)
- What happened: once fixed, the Stop-hook monitor fired on EVERY session stop.
  The transcript JSONL is append-only ACROSS compactions, so raw file size only
  grows; after the first /compact the 1MB threshold stayed permanently exceeded.
- Root cause: raw `wc -c` used as the context proxy; compaction shrinks the
  context but not the file.
- Rule change needed: NONE — script fix: measure bytes AFTER the last
  `"subtype":"compact_boundary"` marker (grep -b offset). Embedded copies of the
  marker in message content are JSON-escaped, so they can't false-match.
- Status: applied-on 2026-07-05 (verified: live transcript with 2 boundaries →
  exit 0 post-compact at ~310KB effective; tiny transcript → exit 0; backup at
  `~/.claude/backups/compact-context-monitor.sh.2026-07-05.bak`)
