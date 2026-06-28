---
name: feedback_no_self_matching_waiters
description: "Never poll with `while pgrep -f 'PATTERN'; do sleep N; done` — the pattern self-matches the waiter's own command line and loops forever; rely on harness task notifications instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31df618e-1d05-4346-8dfa-a60476d0a5cc
---

**TRIPWIRE — do NOT write `while pgrep -f 'PATTERN' >/dev/null; do sleep N; done`
waiter loops to block on a background job.** The waiter's OWN command line
contains `PATTERN` (e.g. `pgrep -f 'family_batch.py'`, `pgrep -f 'verify_usf'`),
so `pgrep -f` matches the waiter itself → the condition is always true → the
loop never exits → it spawns `sleep` forever. This leaked ~15 stuck waiters in
one session (2026-06-27), each respawning a `sleep`, and needed a manual
PID-by-PID kill to clean up (while carefully sparing the PARALLEL DMC session's
real `dmc_family_batch.py` workers + its own poller).

**Why:** a foreground `sleep` is blocked by the harness, so the instinct is to
background a poll loop — but `pgrep -f` over a self-describing command is the
classic self-match. Escaping the dot (`family_batch\.py`) avoids matching the
literal-dot form but is fragile and easy to forget.

**How to apply:**
- The harness already RE-INVOKES you with a `<task-notification>` when a
  `run_in_background: true` Bash task finishes. WAIT for that notification —
  don't build your own waiter. Read the output file when it fires.
- If you truly must poll external state the harness can't track, match a string
  that CANNOT appear in the poller's own argv (e.g. `pgrep -x sleep` then filter
  by parent, or grep the OUTPUT FILE growing, or check a pidfile), never
  `pgrep -f '<the script name in this very command>'`.
- Shared-host hygiene: when killing strays, a parallel session's processes use a
  DIFFERENT bash snapshot id; identify yours vs theirs by snapshot before any
  kill, and never `pkill -f` a broad pattern that could hit the other session.

Related: [[feedback_background_jobs_harness]] (long batches use the harness
background, not `nohup&`), [[feedback_subagents_no_git]] (don't disrupt shared
state another session relies on).
