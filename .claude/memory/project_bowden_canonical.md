---
name: bowden-canonical-engine
description: "Bowden-canonical Companion strain — 17 SIDs instruction-sequence exact (snapshot AND instruction-stream) via pipelines/companion/bowden_canonical. Flat orderlists, 3 fixed-timbre voices, multi-subtune, relocation-aware."
metadata:
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`pipelines/companion/bowden_canonical/` — second Companion engine
strain after Hubbard's 1984 `pipelines/companion/` (Up_up_and_Away).
**17 SIDs** in HVSC #84 instruction-sequence exact through the SID → USF v2 → SID
pipeline, BOTH at the per-frame snapshot level (md5 of $D400-$D418)
AND at the cycle-strict instruction-stream level (siddump --writelog
flat (reg,val) sequence comparison):

- All 12 Vic Berry tunes (MUSICIANS/B/Berry_Vic/)
- Keith Bowden's Roundabout (DEMOS/M-R/)
- Titanic - The Adventure Begins (GAMES/S-Z/)
- Memory_1991 (GAMES/M-R/)
- Karl Hörnell's Melonmania (3 subtunes, MUSICIANS/H/Hoernell_Karl/)
- Steve Kellett's Hyper_Blast (GAMES/G-L/)

## Engine semantics

Much simpler than Hubbard '85:

- 3 voices walking flat orderlists of (oct<<4)|semi pitch bytes
- $80 = rest (engine writes ctrl byte without gate bit)
- $FF = loop terminator (engine substitutes orderlist[0] for the
  current tick, resets v_pos to 1; net effect is a clean K-tick loop
  where K = position of $FF)
- Per-voice locked 5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr)
- Global tempo (frames per tick)
- V1 init_pos = 0 (zeroed by init); V2/V3 init_pos = load-time bytes
  at $C01E / $C025 (different per tune, encoding phase offset)

## The 6502 carry-leak trap

The original engine's PW-write loop is 5 iterations, not 4 (writing
PW_LO, PW_HI, CTRL, AD, **and SR** from a 5-byte timbre block). The
loop limit comes from `ADC #$04` at $C0C2 WITHOUT a preceding CLC —
and the upstream tempo gate's `CPX $C07B / BNE` leaves carry SET
when control falls through. Effective add is 5.

Without spotting this, V_SR is missing from each note's write stream
and the rebuilt SIDs diverge at every note. Lesson reinforced —
6502 mindset, audit flag state across calls. See
[[feedback_6502_mindset]] and [[feedback_deconstruct_not_reproduce]].

## Disabled voices (Melonmania sub 1)

Some Bowden subtunes silence a voice by patching its dispatch JSR
to a BIT (e.g. `JSR $C0AD` → `BIT $C0AD`). The disabled voice never
calls proc_note, so its `RTS-only` path never runs the CMP chain
that affects carry — the carry-leak state is preserved across the
voice.

Our extract initially synthesised a `[$81, $FF]` orderlist for the
disabled voice and let the codegen run it as a normal skip-each-tick
voice. That made the carry-leak emulation incorrectly mark the next
voice's `next_skip_sr=1`, which would silently drop V_SR writes on
the following voice for the rest of the subtune.

Fix: per-subtune `voice_enable_mask` USF param (bit 0=V1, 1=V2, 2=V3;
omitted = all enabled = 7). Composer emits a per-subtune table; init
loads the active subtune's mask into `v{N}_enabled` bytes; each
`voice_step` early-RTSes when its flag is 0 — exactly mirroring orig's
JSR→BIT patching, no proc_note, no carry side-effect. Melonmania
sub 1 has mask=6 (V2+V3) and is now instruction-sequence exact.

## Cluster coverage

The 12 Vic Berry SIDs span 6 different first-256-byte fingerprints
(c8282844 ×7 + 5 single-fingerprint variants) yet share the same
engine model. Per-256-byte differences are per-tune data — tempo
byte, timbre values — not engine code.

## USF representation choices

Single subtune music block per SID. Per-voice:

- One `instrument` (locked timbre) — waveform=[ctrl], pwm.init=PW,
  adsr=(ad,sr), no modulation
- One pattern of K rows (K = orderlist length excluding $FF), each
  row = pitch (or rest) with duration 1
- `orderlist: 1 loop@0` — single looping pattern
- Phase offset carried in `subtune.params.fields['init_pos_v2/v3']`
  (V1 always 0 — carried for symmetry)

Freq table lives in `engine_constants.py` — engine-constant across
the cluster in all 96 musically-meaningful slots (the trailing
$CAFF byte differs but is never indexed).

## Codegen

Clean 6502 reimplementation, not a verbatim binary copy. Same
per-frame final SID state as the original ($D400-$D418 snapshot
identity), via:

- JMP trampolines at LOAD=$1000 for stable PSID entry points
- init zeroing $D400-$D418 + setting baseline AD/SR/vol
- play with tempo gate (INC tempo_ctr; CMP tempo)
- shared proc_note (note byte → SID writes including gated CTRL)
- per-voice step routines handling their own $FF loop-back
- X-addressable timbre tables at offsets 0/7/14 to match the
  engine's natural per-voice indexing

## Two codegen pitfalls hit during iteration

1. **xa65 silently drops forward `* =` PC directives** in the binary
   stream — gaps don't pad. Resolved by laying out everything
   contiguously from LOAD with JMP trampolines.
2. **N flag clobber**: `ldx #X / jmp proc_note` clears N. A `bmi
   pn_rest` test of A=$80 in proc_note never fires because N was
   cleared by the LDX. Resolved with explicit `cmp #$80 / beq`.

## Related

- [[project_companion]] — sister strain (Hubbard 1984 Companion,
  pipelines/companion/, Up_up_and_Away instruction-sequence exact)
- [[feedback_6502_mindset]] — the carry-leak class of bug
- [[reference_usf_v2_format]] — USF v2 grammar; init_pos lives in
  subtune.params.fields since InitVoice fields are Hubbard-shaped
