---
name: feedback_background_jobs_harness
description: "long background jobs MUST use the harness run_in_background, never nohup&inside a Bash call"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
---

Long-running jobs (the ~1hr DMC/FC family batches, mass-writes, etc.) MUST be
launched with the **Bash tool's `run_in_background: true`** flag — the harness
detaches them, keeps them alive across turns, and notifies on completion.

**Do NOT** launch them with `nohup python3 ... &` inside a normal (foreground)
Bash tool call. The backgrounded process is killed when the tool call's shell
exits, so it never actually runs — and any waiter you set up just sees it die
instantly and reports whatever STALE output file already existed.

**Why:** burned a cycle (2026-06-17) — launched a V5 closeout batch via
`nohup ...&`, set a `kill -0` waiter, and the waiter reported the PREVIOUS
batch's stale jsonl (842 FULL, the 5 regressions still partial) because the new
batch never ran. The tell: the results-file mtime was OLDER than the source
edit it was supposed to reflect. Always sanity-check a batch result's mtime vs
the fix's mtime before trusting it.

**How to apply:** for any job > a few seconds that must survive the turn, call
Bash with `run_in_background: true`; then wait on the harness task
notification, not a hand-rolled `nohup`+`kill -0` loop.
