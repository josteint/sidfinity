---
name: Meta-process for continuous improvement
description: At natural pause points (PreCompact, end of a workstream), re-evaluate whether the current approach is still highest-ROI and whether memories / CLAUDE.md reflect reality.
type: feedback
---

At natural pause points — PreCompact hooks, end of a workstream,
finishing an engine migration — pause and run the checklist:

1. **Check ROI.** Is the current approach still the highest-value
   thing to do? The frontier shifts: early-project parser bugs gave
   way to USF v2 design, which gave way to per-engine migrations,
   which gave way to the composer dissolution, etc. Always ask
   "is THIS still where my hour buys the most progress?"

2. **Check memories.** Walk the index. Remove stale ones. Correct
   wrong numbers. Memories that name a specific file:line are claims
   that the file:line existed when the memory was written — verify
   before acting on them.

3. **Check CLAUDE.md.** Is it still accurate? Are the Key Files up
   to date? Are the working conventions being followed? Volatile
   info (counts, dates, in-flight workstream status) belongs in
   `tools/regression.py` output or `git log`, not CLAUDE.md.

**Why:** Without periodic self-assessment, sessions tend to repeat
the same approach even after it stops being highest-value, and the
memory index drifts away from reality.

**How to apply:** Triggered by the PreCompact hook in
`.claude/settings.json` and at natural end-of-workstream pauses
(after an engine reaches byte-exact, after a refactor lands, etc).
