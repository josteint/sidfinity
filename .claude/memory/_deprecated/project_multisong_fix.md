---
name: Multi-song GT2 fix
description: Multi-song SID support in gt2_decompile.py — what was fixed and remaining issues
type: project
---

Multi-song GT2 SIDs have a song table with songs*3 lo + songs*3 hi bytes (not just 6).
The decompiler now reads the PSID header's song count and default_song fields.

**Key details:**
- Song table at freq_end: songs*3*2 bytes total
- Default subtune selects which 3 orderlist addresses to use (0-based index)
- Validation: all selected addresses must be within binary; falls back to songs=1 if invalid
- Some SIDs declare songs>1 in PSID but the GT2 data only has 1 song's song table — the fallback handles these

**Why:** 153 F-grade songs were multi-song. Fixing this gained +93 Grade A.

**How to apply:** If investigating a failing song, always check `PSID songs field` first. If songs>1, the bug may be in song table sizing/subtune selection, not in the data extraction itself.
