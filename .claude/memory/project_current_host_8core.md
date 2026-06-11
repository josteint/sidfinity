---
name: project_current_host_8core
description: Since 2026-06-11 sessions run on an 8-core machine (not the 64-core EPYC CLAUDE.md describes); no pytest available. Size worker pools to 8; regression/batches take proportionally longer.
metadata: 
  node_type: memory
  type: project
  originSessionId: 1a969f4b-cad3-4dc0-a302-0b489914e62f
---

As of 2026-06-11 the working machine is an **8-core** computer, not the
64-core EPYC / 512 GB box described in CLAUDE.md's "Build environment".
Also: **no pytest** is installed (system python, `.venv`, `.pylocal` all
lack it), so `pytest pipelines/` smoke tests cannot run here — use
`tools/regression.py` (writelog verdict) as the gate.

**How to apply:** multiprocessing pools at 8 workers (user-confirmed
Pool(8) for the FC wide batch); expect long wall times for corpus-wide
batches; don't assume CLAUDE.md's hardware claims. If the 64-core box
returns, update or delete this memory (and consider fixing CLAUDE.md).
