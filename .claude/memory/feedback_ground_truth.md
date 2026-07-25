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

## The third failure mode: py65 for EXTRACTION reads DIVERGENT memory (2026-07-24, DMC Roots)

The two sections above are about py65 as a VERDICT/capture. This one is about
py65 used legitimately for EXTRACTION — running a member's own code to read a
value the pipeline needs (post-init RAM leftovers, an off-table byte, a loop
target). That is a real, sanctioned use (`_postinit_window`, the ghost sim,
`_offtable_eventdriven`). The trap: **the value py65 reads can DIFFER from
libsidplayfp whenever it depends on memory the file image did not load and the
player's own execution did not deterministically write** — i.e. uninitialized
RAM, or any byte reached only after py65's execution has DIVERGED from
libsidplayfp's.

DMC `Hank/Roots` cost most of a session to this. Its patched `$FF`-loop handler
reads the loop-to offset through a null zero-page pointer, so it reads ZERO
PAGE at `$0000+otrk+1`. I ran py65 to the loop and read those bytes: py65 said
voice 1 loops to `$00` and even plays NOISE post-loop. **siddump/libsidplayfp —
the verdict engine — plays SILENT, voice 1 loops to `$87`.** py65's `$0031` was
`$00` (its power-on fill) where libsidplayfp's was `$87` (player-written), and
because the whole player is riddled with null-pointer / environment reads, the
two emulators' *entire playback state* had diverged by the loop. Only voice 2
happened to agree, because its source (`$0058` = the track-pointer-hi slot) is
a byte BOTH emulators define identically.

**The rule:**
- py65 is trustworthy ONLY for reads of memory that the file image LOADED or
  the code just RAN provably wrote. A value that depends on an UNINITIALIZED
  byte, or on DEEP PLAYBACK of a player that does null-pointer / off-image /
  environment reads (the C29 class), is emulator-dependent and py65 is NOT
  ground truth for it.
- **Before shipping any py65-DERIVED value that reaches the write stream, VERIFY
  it against the SAME quantity measured from siddump/libsidplayfp.** For the
  loop targets: `siddump --memwatch-on-write`; for a captured burst: compare
  py65's SID writes at that frame to `siddump --writelog`. If they diverge, py65
  has diverged — use the siddump number.
- The tell you're in danger: the member does anything C29-flavoured (null/stale
  pointers, off-image sectors, reads of `$00xx` / power-on RAM), OR the py65
  value comes from playback far past init rather than from init itself.

**Code tripwire:** `pipelines/dmc/v4/extract/engine_model._TaintMemory` — a py65
memory that records every written address and flags reads of never-written
(uninitialized) memory. A py65 extraction that reads a tainted byte is reading
emulator fill, not the player's data; measure it from siddump instead. See its
docstring for the safe (`__getitem__`) vs must-verify (`read_trusted`) split.

**The STRUCTURAL fix (beyond the tripwire):** stop using py65 for
divergence-prone / slow observation at all — observe from the ground-truth engine
(libsidplayfp) instead. **Architecture DECIDED 2026-07-25** (Phase-0 survey →
[`docs/siddump_native_capture_decision.md`](../../../docs/siddump_native_capture_decision.md)):
declarative siddump flags over observe-only overlay taps; an in-process binding
over the same taps only as a deferred escalation. Phase 1 shipped
`--reinit-snapshot` (the DMC ghost sim's py65 path deleted; gate = byte-identical
windows + FULL). ⚠ New-tap discipline: a bare `addr==PC` bus check false-fires
on DATA reads of the trigger address (ledger C36) — discriminate execution by
the consecutive-read signature, and validate every new tap by cross-emulator
byte-identity. Plan + inventory + phased path:
[`docs/siddump_native_capture_plan.md`](../../../docs/siddump_native_capture_plan.md)
(also linked from `tools/INVESTIGATION_BACKLOG.md`). Standing default: observe
from libsidplayfp, not py65.

**⚠ The boundary of that default (2026-07-25, Super_Seven):** a py65 site
whose PURPOSE is an IDEALIZED / counterfactual environment is a **simulation,
not an observation — do not migrate it.** `_postinit_window` wants "RAM as if
only the image + init existed"; the real machine cannot produce that
counterfactual (psiddrv is always resident — its bytes landed in the
extraction's base memory and Super_Seven sub 1 went partial; reverted). Such
sites read image-loaded / init-written bytes (trustworthy py65 per this
file's own rule), and their genuine environment reads are served separately
by the C29 `--peek-post-init` path. Ask of every candidate: does it observe
the real machine, or simulate an idealized one?
