---
name: feedback_background_jobs_harness
description: "long background jobs MUST use the harness run_in_background, never nohup&inside a Bash call"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
  modified: 2026-07-22T21:31:36.490Z
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

## NEVER pipe a backgrounded command through `tail`/`head` (2026-07-22)

A backgrounded `cmd | tail -40` writes **nothing** to its output file until the
process EXITS — `tail` buffers the whole stream by construction. So the
progress file stays empty for the entire run, which reads as "stalled", and the
natural next move is to re-run it in the foreground.

**Why:** burned a cycle in the round-88 session — backgrounded
`dmc_next_partial.py 2>&1 | tail -40`, read the empty output file, concluded
nothing was happening, and ran the SAME command in the foreground. Both did
full builds+verifies concurrently, both writing the same queue file
(`tmp/dmc_f1_partials.jsonl`). It survived intact, but that was luck: two
processes rewriting one state file is a corruption hazard, not just wasted CPU.

**The rule:** let a backgrounded job STREAM to its output file (no pipe), and
trim when you READ it (`tail -n 20 <output-file>`). Then a mid-run check
actually shows progress, so there is never a reason to launch a second copy.
Corollary — the tell that you are about to make this mistake is reaching for a
foreground re-run of something already backgrounded: check the task list first,
and prefer waiting for the notification.
