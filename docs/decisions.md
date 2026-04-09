# Decision Log

Architectural decisions and dead ends. If you're about to try something listed here as "didn't work," read why first.

## Dead Ends

### Toneporta init timing (2026-04-08)
**Tried:** Making V2's `mt_fullinit` run channel execution on the init frame (matching GT2's behavior). Both `jmp mp_run` and adding a waste frame.
**Result:** 115 regressions (jmp mp_run) or 41 regressions (waste frame). Most songs were already correctly aligned with the 2-frame init.
**Root cause:** The 1-frame offset between V2 and GT2 init is real but absorbed by jitter tolerance. The real toneporta bug was the `ce_runfx` guard and `mt_chnnewfx` overwrite, not init timing.
**Lesson:** When comparing two players, don't assume the init frame is the cause of timing differences. Check the continuous effect handlers first.

### Byte-saving optimizations causing regressions (2026-04-08)
**Tried:** Peephole branch-over-JMP inversion, zero-page variable migration, various code restructurings to save bytes.
**Result:** Every byte saved shifts 6502 page boundaries, changing ±1 cycle penalties. This causes ~1% of songs to change grade.
**Resolution:** Sequence-level jitter detection absorbs most layout shifts. Accept that code size changes cause measurement noise, not audio differences.
**Lesson:** On 6502, code layout affects timing. Don't chase zero-byte-overhead — fix the comparison methodology instead.

### Global tempo change cross-channel timing (2026-04-09)
**Tried:** Investigating whether global tempo changes (cmd=$F) from one voice cause timing desync on other voices.
**Result:** The tempo change fires at frame 680 (past the 500-frame dump) for Schnitzel-Fritz. The actual bug was the `mt_chnnewfx` overwrite in the pattern reader, not cross-channel tempo propagation.
**Lesson:** Always check WHEN an effect fires before theorizing about its impact. Use siddump to verify timing.

## Settled Decisions

### V2 per-song codegen over monolithic player (2026-04-03)
**Why:** Each song only gets the 6502 code for features it actually uses. Unused effect handlers, table processors, and code paths are stripped. Saves 200-800 bytes per song and reduces cycle count.
**Trade-off:** More complex codegen, harder to debug. But the tools (Z3 verifier, py65 harness, cycle_model) compensate.

### Comparison jitter tolerance layers (2026-04-08)
**Why:** Register-level comparison is too strict — it flags inaudible timing differences as errors. Each tolerance layer was added because a specific class of false positives was identified.
**Order matters:** ±3 window → 1-frame transient → test-bit → silent voice → sequence-level → global value set → vibrato drift. Each layer catches what the previous ones missed.
**Rule:** Only add a new layer when you've confirmed the difference is genuinely inaudible (use `audio_compare.py` if unsure).

### Wave table +2 offset as paired bug (2026-04-02)
**Why:** The decompiler extracts wave_right with a +2 offset that compensates for the player's INY-before-read. Fixing one without the other breaks all songs. This is documented in CLAUDE.md invariants.
**Rule:** Never change the +2 without also changing the player's read order, and testing all 3,478 songs.

### USF as mandatory intermediate (2026-04-01)
**Why:** The entire project exists to build USF for ML training. Bypassing USF (e.g., raw binary round-trip) proves nothing about USF's completeness.
**Rule:** Every pipeline path goes through USF. No shortcuts.
