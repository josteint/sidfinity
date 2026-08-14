# The Core Tenet

**The verification target is the SID write-log stream, not the engine code.**

Every composer / codegen / migration in this repo is judged ONLY by whether
the rebuilt SID emits the same `$D400..$D418` write sequence (frame-by-frame
for tracker music; cycle-strict for digi) as the HVSC original. Nothing
else is the target.

This means the composer is FREE to invent any runtime architecture it wants —
different dispatch path, different instrument layout, different orderlist
scheme, different memory map, completely re-arranged effect-chain emitters,
zero-page reassignment, JSR/RTS where the original had inline code, inline
where the original had subroutines. The original engine's machine code is a
historical artifact, not a blueprint.

When you are stuck on "I need to add N bytes but there's no room" or "the
disassembly forces me to do X" — the answer is almost always to **re-state
the problem in terms of the write-log stream**, then restructure the code
to produce that stream more compactly. Do NOT reach for hacks like
shifting data addresses, reproducing self-modifying code mechanisms, or
emitting verbatim byte regions from HVSC.

Concrete corollaries:
- USF carries only musical content, never engine-positional artifacts
  (sub-jump tables, abs pointers, raw inst-program bytes, SMC slots).
- Per-engine config fields parametrise differences between engines'
  write-log streams (e.g. `nextvoice_write_order`, `fx_drum_d401_offset`,
  `held_note_clears_stod404_gate`) — they never describe HVSC's code layout.
- When a disasm shows SMC, do NOT reproduce it; emit clean code that
  produces the same writes (see [[feedback_smc_disasm_check]]).
- For FC family see [[feedback_deconstruct_not_reproduce]] for the Hawkeye
  sub-0 worked example (match=133 → 1538 after this reframing).

If you find yourself reading a long disasm and asking "how do I mirror this
structure," stop and ask "what writes does this produce in this frame?"
instead.

## The two verification modes — read alongside the tenet above

The project has EXACTLY TWO modes for declaring a rebuild correct — i.e.
**per-frame instruction-sequence exact** (the rebuilt SID is NOT byte-for-byte
identical to HVSC's binary; we compose our own engine — only the `$D400-$D418`
write stream matches). Anything else is wrong. Three traps eat hours of
session time; each is explicitly documented.

**Mode 1 — frame-by-frame instruction sequence (tracker music).**
Each PSID `play()` invocation emits a finite, ordered sequence of writes
to `$D400-$D418`. The rebuild matches iff that per-`play()` sequence
matches the original, frame by frame, for the whole song. WITHIN a frame
the ORDER of writes matters (gate edges, test bit, ADSR delay, $D418
clicks). The CYCLE TIMESTAMPS within a frame do NOT. This is what 99% of
HVSC needs.

- Tool: `tools/siddump --writelog` (capture).
- Comparator: `pipelines.hubbard.verify_cycle.compare_instruction_stream`
  (flat-prefix over `(reg, val)`, cycle dropped). Robust against siddump
  frame-bucket drift (Trap C).
- Localizer: `tools/find_first_divergence.py`.
- **Engines that emit their OWN init (pure trichotomy):** when the composer
  emits a universal reset + typed priming instead of reproducing the original
  engine's init write SEQUENCE (e.g. FC `init_style='universal_reset'`), the
  two streams share an identical play stream but differ by a short init prefix
  of different length — so a flat prefix match diverges at frame 0. Use
  `compare_instruction_stream(mode='trichotomy')`: it recovers the play-stream
  shift, then checks (A) the end-of-init chip STATE matches (the priming) and
  (B) the aligned play stream matches (+ close length tolerance). It reduces to
  a full prefix match when inits coincide, so verbatim-init engines are
  unaffected. This is the answer to "how do we compare when we have our own
  init" — see the_trichotomy.md + [[project_adrenalin]].
- **CIA-timed tunes (PSID `speed != 0`):** the flat per-50Hz-frame capture
  buckets init + first play() out of phase between orig and a rebuild with a
  different init length (Trap C specialised to CIA), so `verify_all` captures
  these subtunes PER `play()` via `tools/siddump --writelog-per-irq`
  (`writelog_per_irq_capture`, init prefix dropped) and flat-compares the
  flattened play stream. Detected by the PSID `speed` bit; vblank subtunes
  use the flat path unchanged. Validated against the `--pc-trace` oracle.

**Mode 2 — cycle-exact (digi only).**
For digi (sample playback timing IS the signal), every `(cycle, reg, val)`
must match. Used for Chimera and similar.

- Tool: same `--writelog`.
- Comparator: `pipelines.hubbard.verify_cycle.compare_strict`.

**Trap A — snapshotting registers instead of capturing the write
sequence.** Half the early project did this. Loses within-frame writes
and order. Never use register snapshots for Mode 1 verdict.

**Trap B — chasing cycle-exactness for music.** Within-frame cycle
position is observation, not signal. Don't try to make cycles match for
tracker music; same writes in the same order at different cycles within
a frame are equivalent.

⚠ **Trap B's boundary — when intra-frame POSITION becomes signal**
(measured 2026-08-14 on Moog/Techno-Rap; owner-caught before it shipped).
Trap B holds because a normal player does all of its work in ONE burst
per frame, so where inside that burst a write lands is inaudible. It
STOPS holding when the original deliberately SPREADS work across the
frame at a sub-frame IRQ rate. Techno-Rap runs TWO independent tunes on
one chip: each burst is ~4% of a frame, and the bursts sit 50.2% of a
frame apart. Emitting both bursts back-to-back in a single frame
reproduces the flat write stream EXACTLY — while shifting one whole
tune's gate edges, envelope starts and per-frame modulation steps half a
frame (~10 ms) earlier against the other. The flat verdict is blind to
it and would record a confident FULL on an audibly wrong rebuild. RULE:
when the original's play() runs faster than the frame AND successive
calls do DIFFERENT work, the per-call boundary is SIGNAL — reproduce the
schedule (C18 phase schedules / C27 complementary per-call schedules),
never collapse it into one frame. Corollary for verification: a flat
prefix match is necessary, not sufficient, for this class; check the
per-call structure too.

**Trap C — siddump frame buckets ≠ PSID `play()` invocations.** siddump's
loop calls `engine.play(cyclesPerFrame=19688)`, but `cyclesPerFrame` counts
**event-scheduler ticks** (`c64::clock()`=`eventScheduler.clock()`, each <1
CPU cycle), so a siddump "frame" advances only **~18,000 CPU cycles** — NOT
19,688, and NOT the 19,656-cycle PAL play period. So per siddump "frame" the
PSID `play()` (which fires every 19,656 cycles = true 50 Hz) runs **~0.92×**:
usually 1, regularly 0, rarely 2. (NB: this is the OPPOSITE direction from the
old "19688 > 19656 so sometimes 2" framing — ~18,000 < 19,656.) Full detail +
the ρ unit-conversion this forces for RSID-vs-PSID timing:
[[reference_siddump_frame_cycles]]. Consequences:

- `compare_instruction_stream` is ROBUST (flat concatenation across
  frames; sequence is identical regardless of bucket boundary).
- `tools/state_diff.py` (memwatch snapshots) is NOT robust — state is
  sampled at siddump frame boundaries, not at IRQ boundaries. A state
  "divergence" at siddump-frame N may be IRQ misalignment, not a real
  engine bug. Cross-check against `find_first_divergence.py` (writelog
  ground truth) before treating state_diff localization as a verdict.

Full discussion (with worked Hawkeye examples for each trap) in
[`feedback_verification_modes`](../.claude/memory/feedback_verification_modes.md).

