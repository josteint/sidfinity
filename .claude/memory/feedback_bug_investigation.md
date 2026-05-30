---
name: How to investigate F-grade songs
description: Proven methodology for finding and fixing bugs — pick one song, trace the exact wrong frame, fix root cause, batch test
type: feedback
---

The pattern that works (yielded +124, +118, +48, +37, +46, +12 Grade A per fix):

1. **Pick the highest-scoring F-grade song** — closest to passing, smallest fix needed
2. **Run the pipeline** and get detailed comparison output per voice
3. **Find the first wrong frame** — show orig vs rebuilt fhi/wav/ad/sr with context (±3 frames)
4. **Classify the error**: timing jitter (comparison issue) vs wrong note (real bug) vs silent voice playing (comparison issue)
5. **If comparison issue**: improve gt2_compare.py tolerance, verify with 3,478-song regression
6. **If real bug**: trace to the specific pattern/instrument/wave table entry, find root cause in decompiler or player codegen
7. **Fix and batch test** — must not regress any of 3,478 songs

**Common error patterns:**
- Vibrato phase drift → global value set check or ±8 window check in gt2_compare.py
- Silent voice freq writes → skip when waveform bits are 0
- Toneporta snap/slide → ce_runfx guard or ce_tp_note handler
- Missing speed table → _detect_speed_table_from_binary fallback scan
- Wrong data layout → alternate layout detection in gt2_decompile.py (Group A large-code)

**How to apply:** Always start with ONE song. Don't try to fix categories abstractly. The concrete song gives you the exact bytes to compare.
