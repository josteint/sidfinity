---
name: Ground truth is sidplayfp --writelog, not py65 or Python reimplementations
description: CRITICAL — the definitive ground truth for audio fidelity is sidplayfp's instruction stream (--writelog). py65 and hubbard_emu.py are proxies that may diverge. Never treat a reimplementation as ground truth.
type: feedback
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
The ONLY ground truth for SID audio is **sidplayfp's instruction stream** captured via `tools/siddump <file.sid> --writelog`. This taps libsidplayfp's per-cycle register write log and outputs every (cycle, register, value) tuple — the raw input to the SID chip that produces the audio.

**Do NOT use plain `siddump` (without --writelog) for codegen comparison.** Default siddump only samples one register state per frame, which hides intra-frame write order, timing, and any writes that get overwritten before the frame ends. For Das Model v2 codegen work — where we are matching the instruction stream byte-for-byte — only `--writelog` is meaningful.

**Why:** py65 (Python 6502 emulator) and hubbard_emu.py (Python reimplementation) are PROXIES. They may differ from sidplayfp in:
- Cycle counting (sidplayfp is cycle-accurate, py65 may not be)
- Memory mapping (sidplayfp emulates C64 ROM/IO, py65 uses flat RAM)
- Undocumented opcodes
- Page-crossing cycle penalties

We proved this matters: a "100% match" against py65/hubbard_emu.py still produced audio that "glitches at 15-16 seconds" when played through sidplayfp.

**The chain of trust:**
```
Original SID binary
     ↓
sidplayfp 6502+SID emulation  ← produces the audio the user hears
     ↓
siddump --writelog             ← taps the instruction stream
     ↓
(cycle, register, value)      ← THE ground truth
```

**Rule:** NEVER claim "100% match" based on py65 or hubbard_emu.py comparison alone. Always verify against `siddump --writelog` of the original SID. The user's ear is the final judge, but `--writelog` is the automated oracle that removes the human from the loop.

**How to apply:**
1. Capture: `tools/siddump original.sid --writelog --duration N > ground_truth.log`
2. Capture: `tools/siddump das_model.sid --writelog --duration N > candidate.log`
3. Compare: parse both logs, match (register, value) per frame + check cycle proximity
4. Fix every discrepancy against the sidplayfp stream, not py65

**Why:** sidplayfp IS the renderer. Matching its instruction stream = matching its audio. Matching py65 only matches a different emulator that nobody listens to.
