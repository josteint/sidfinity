---
name: Meta-process for continuous improvement
description: How to evaluate and evolve the SIDfinity development process itself — the meta-meta rule
type: feedback
---

On compaction (PreCompact hook will remind), evaluate whether the current process is working:

1. **Check ROI**: Read docs/benchmark.csv. Is the Grade A curve still rising? If it flattened, the current approach has diminishing returns — time to try something new.

2. **Check memories**: Read all memory files. Remove stale ones. Update numbers. Memories that reference specific file:line locations may be outdated — verify before acting on them.

3. **Check procedure**: Read docs/formal/procedure.md. Is it still accurate? Has a "NOT USEFUL" tool become useful? Has a "USEFUL" tool stopped helping?

4. **Check CLAUDE.md**: Is the status line current? Are the Key Files up to date? Are the Working Conventions being followed?

5. **Check what's working NOW vs what was working BEFORE**: The highest-ROI approaches change over time:
   - Early: fixing pipeline bugs (decompiler, codegen) had the biggest impact
   - Mid: trace equivalence mining gained +393 songs from 3 rule changes
   - Future: when GT2 gains plateau, non-GT2 engines (Hubbard, DMC, JCH) become the frontier
   - The meta-rule: always work on whatever has the highest expected Grade A gain per hour invested

6. **Update this memory**: If the process itself changed, update this file so future sessions know.

**Why:** Without periodic self-assessment, sessions tend to repeat the same approach even when it stops working. The meta-rule prevents getting stuck.

**How to apply:** The PreCompact hook triggers the review automatically. Compaction is a natural pause point — the context is about to shrink, so it's the right time to make sure memories and CLAUDE.md are current before state is lost.
