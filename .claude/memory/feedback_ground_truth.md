---
name: Ground truth is sidplayfp --writelog, not py65 or Python reimplementations
description: CRITICAL — the definitive ground truth for audio fidelity is sidplayfp's instruction stream (--writelog). py65 and hubbard_emu.py are proxies that may diverge. Never treat a reimplementation as ground truth.
type: feedback
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
modified: 2026-07-21T20:19:42.764Z
---
The ONLY ground truth for SID audio is **sidplayfp's instruction stream** captured via `tools/siddump <file.sid> --writelog`. This taps libsidplayfp's per-cycle register write log and outputs every (cycle, register, value) tuple — the raw input to the SID chip that produces the audio.

**Do NOT use plain `siddump` (without --writelog) for codegen comparison.** Default siddump only samples one register state per frame, which hides intra-frame write order, timing, and any writes that get overwritten before the frame ends. For Das Model v2 codegen work — where we are matching the instruction stream write-for-write — only `--writelog` is meaningful.

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

## The sharper failure mode: a proxy that is ACCURATE but NARROW (2026-07-21)

Everything above is about the proxy being *wrong*. The worse case is a proxy
that is exactly **right** about what it observes, and observes only part of
the picture — because then the verdict is silently rescoped and nothing looks
suspicious.

Jay_Derrett's RSID members (Osmium / Thundercross / Trigger_Happy) verified
their ORIGINAL via `capture_writes_via_py65`, which follows the IRQ vector at
`$0314` for N frames. Plain siddump reports 0 writes for these tunes
(RSID, `play=$0000`, engine installs its own IRQ), which is why py65 was used
at all. But `siddump --force-rsid` runs the real RSID environment and does
capture them — and shows what py65 could never see:

| | ORIG writes | of which `$D418` | REBUILD |
|---|---|---|---|
| Trigger_Happy | 29,671 | 29,053 (97%) | 713 |
| Thundercross | 37,893 | 37,194 (98%) | 701 |
| Osmium | 708 | 3 | 708 |

Those tunes run a `$D418` volume-register **digi in the main loop**, outside
the IRQ. py65 is structurally blind to it. The two instruments never
*disagreed* — filtering `$D418`, py65 and siddump match the music exactly
(618/618, 705/705). py65 simply saw less, and the part it could not see was
exactly the part the rebuild fails to reproduce. Two members had been passing
for months on a view that excluded 97% of the writes the chip receives.

**The rule this adds:** when choosing a capture instrument, ask not only "is
it accurate?" but "**what can it not see?**" — and check that the rebuild is
not failing precisely there. A verdict is only as wide as its instrument.

**Corollary — asymmetric capture is a smell.** That check compared a py65
capture of the ORIGINAL against a siddump capture of the REBUILD. Two
different observation methods on the two sides is how the gap stayed
invisible; capture both sides the same way and the difference cannot hide.
(Fixed 2026-07-21: the RSID branch now uses `siddump --force-rsid` on both
sides and the standard `compare_instruction_stream`. py65 no longer produces
a verdict anywhere in the project; the two exposed members are recorded as
`KNOWN_PARTIAL_JD` in `tools/regression.py` with the cause stated.)

This is the same disease as the 2026-06-07 removal of the py65-snapshot
verdict (which had false-passed 25 Hubbard subtunes) — that cleanup simply
did not reach this corner. See [[feedback_no_snapshot_verdict]].
