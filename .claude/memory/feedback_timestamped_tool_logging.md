---
name: feedback_timestamped_tool_logging
description: "Owner directive: dev tools print timestamped flushed phase lines (src.tslog) — silent long-running phases read as hangs and burn trust."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 622a2e59-f483-485f-bd8c-b76fa8a60103
  modified: 2026-08-19T21:07:31.147Z
---

**Owner directive (2026-08-19):** add timestamped logging to all our
development tools.

**Why:** one evening produced three separate confusions from silent tools —
`dmc_build_one`'s 7.5-minute serial build phase (factory observation probes
over a 5-player compilation) was killed as a hang; its verify output sat
invisible in a block-buffered redirect (empty log mid-run); and a
background run's completion notification was mistaken for a 2-minute build,
spawning a phantom performance discrepancy that took a re-measure to
dispel. Every one of these is answered by lines that say WHAT phase started
WHEN, and how big its input is.

**How to apply:** `from src.tslog import ts, phase`. `phase('name ...')`
context manager prints start + end-with-elapsed (and FAILED-with-elapsed on
exception); `ts(msg)` for one-liners. Always `flush=True` (tslog does it) so
redirects and `tail -f` see lines live. Minimum bar: a start line naming the
input scale ("capture 25 subtune pairs, 8 workers") and an end line per
phase that can exceed a few seconds. The convention lives in CLAUDE.md
(Working conventions); wire it into any tool you touch that lacks it — the
full retrofit of ~50 existing tools is opportunistic, not a big-bang pass.
Wired so far: pipelines/dmc/build_one.py (build + capture phases).

Related: [[feedback_background_jobs_harness]] (long commands run
backgrounded — timestamped logs are what make their progress READABLE).
