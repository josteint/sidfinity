# Bump Set Spike pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild scaffold for Rob Hubbard's *Bump Set Spike* (1986
Entertainment USA). Same shape as the Commando / Monty pipelines; cloned
from Monty and renamed. The engine-specific adaptations needed for an
audibly correct rebuild are listed below — they have **not** been wired
in yet.

## Status

| Metric | Value |
|---|---|
| Scaffold builds end-to-end | yes (`lake build sidgen_bump_set_spike` produces a 3675-byte SID) |
| Codegen base | Commando (Bump Set Spike is the same 1985-86 Hubbard engine family) |
| Engine quirks wired in | freq table base $B3FF + hardcoded PWM bounds + 22 instruments correctly extracted |
| Grade against original | **F** (writelog 0.1% snapshot match, 1/1500) |
| Per-voice progress (first 23 frames) | V1 freq: 19/23, V2 freq: 11/23, V3 freq: 15/23 |

Extract is verified correct: freq table extracts `freq[0] = $0116`
matching binary at `$B3FF`; instrument 0 extracts `PW=$0800 ctrl=$41
AD=$0F SR=$0C` matching binary at `$B513`. Three sequential codegen
upgrades:

1. **Switched codegen base from Monty to Commando** (Bump Set Spike
   is the same 1985-86 Hubbard engine family). V3_PW_LO frame 1
   ($C0) now matches.
2. **Decoded packed vibrato byte + relaxed onset threshold.** BSS's
   vib byte is `frame_limit<<3 | shift`, not a raw shift count;
   onset is "dur ≥ 1" not "dur ≥ 21". Activates vibrato.
3. **Per-voice walking-counter vibrato model** (replaces Commando's
   hardcoded triangle from the global frame counter). New zp arrays
   `v_vib_counter` (init `[2,2,2]` from binary `$B4E3,X`) and
   `v_vib_dir` (init `[0,0,0]`); new `i_viblimit` table per
   instrument; ascending/descending walk with bipolar centering
   `freq = freq[note] - delta*(limit/2) + delta*counter`. Skips
   the post-clamp DEC at `$B203` to match BSS's empirically-observed
   peak-hold behavior.

Result on the first 23 frames of subtune 0:

| Voice freq | matches |
|---|---|
| V1 | 19 / 23 |
| V2 | 11 / 23 |
| V3 | 15 / 23 (frames 0-9 all perfect) |

V3 vibrato pattern matches the original's `A9, B5, B5, AF, A9, A3,
A3, A9, AF, B5` exactly. Drift on V2 / late-V3 is mostly the next
note triggering at slightly different cycle times (cycle-precise
note onset is bounded by Bump Set Spike's tempo-divider polarity
and per-note-tempo counter, both still inherited from Commando).

The whole-snapshot writelog grade is still F (2/1500) because the
PW and ctrl registers diverge for similar reasons — V3 PW frame 2
is `$00C0` in the original but `$0100` in the rebuild because the
PWM block uses Commando's stepping model, not BSS's.

## Layout

Identical to Commando / Monty — see `pipelines/commando/README.md` for the
layout explanation. The directories present here are:

```
bump_set_spike/
  README.md           this file
  disassembly.s       hand-annotated 6502 listing of the original binary
                      (init at $BF0D, play at $B016, freq table at $B3FF,
                      instrument table at $B513, etc.)
  extract/            Python: SID → USF Lean source (Monty's logic)
  codegen/BumpSetSpike/   Lean 4: USF → rebuilt SID (Monty's codegen)
  build/bump_set_spike.sid   output (currently audibly wrong)
  tests/              pytest smoke tests (inherited from Monty)
```

## How to run

```bash
# Extract — writes codegen/BumpSetSpike/SongData.lean
python -m pipelines.bump_set_spike.extract.emit_usf            # subtune 0
python -m pipelines.bump_set_spike.extract.emit_usf 0,1         # both subtunes

# Build the Lean exe and produce the rebuild
lake build sidgen_bump_set_spike
./.lake/build/bin/sidgen_bump_set_spike
# → pipelines/bump_set_spike/build/bump_set_spike.sid

# Grade against the original
python src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Bump_Set_Spike.sid \
    pipelines/bump_set_spike/build/bump_set_spike.sid
# Currently: Grade F (engine adaptation pending)
```

## Engine quirks vs. Monty (still to be wired in)

The binary is **the same Hubbard engine family** as Action Biker /
Confuzion / Crazy Comets — pattern/orderlist pointers per voice,
8-byte instrument records, vibrato + portamento + PWM + auto-arp
driven by a per-instrument flag byte. The differences from Monty:

1. **Play-rate divider polarity is BPL, not BMI.** `$B016 DEC $B4F4 /
   BPL $B021` → work when the counter is *positive*. Reload value
   patched per-subtune at `$B01C` (subtune 0 = $09, subtune 1 = $03).
   1 of every 10 frames is silently skipped on subtune 0.
2. **Per-note tempo reload table at `$B4ED+S`** (S=0 → $02, S=1 → $01).
3. **Per-subtune voice-state seed at `$B5E1+S*6`** (6 bytes: three
   orderlist-pointer los then three his). Subtune 0 V1=$B663,
   V2=$B689, V3=$B6E2.
4. **PWM bouncing thresholds are HARDCODED `$0E` and `$08`** at $B2D3
   and $B2ED. Matches Commando — *not* Monty's per-instrument bounds.
5. **No skydive effect.** The fx-flag bits used here are:
   b0 = portamento-target-lock, b1 = auto-arpeggio, b2 = octave-jump,
   b3 = PW-slide (vs. bouncing PWM).
6. **End-of-song trampoline at `$B003` → `$BF4C`** sets `$B4F7 = $C0`
   (bit 7 = end, bit 6 = pending silence pass). Monty uses different
   end-of-song signalling.

Until the codegen mirrors items 1–6, the rebuild will diverge from the
original at the very first note.

## Pushing toward Grade A — what's left

Empirically the highest-impact missing item is the **vibrato** at
`$B1B6..$B287`. Voice 3 at frame 0 plays note 21 (freq $03A9); frames
1-7 modulate to {$03B5, $03B5, $03AF, $03A9, $03A3, $03A3, $03A9}, a
triangle vibrato of amplitude $0C around the centre $03A9. Bump Set
Spike's vibrato config byte is at instrument byte 5 (vib=$1B for
inst 2 → frame_limit=3, shift=3, base delta = (freq[note] -
freq[note-1]) >> 3 = $06). Commando's codegen produces no such
modulation, so V3_FREQ_LO diverges in 1438 of the 1500 frames.

Item 2 (per-note tempo divider) and item 5 (fx-flag bit remapping)
likely also each impact hundreds of frames; expect Grade A to require
all six engine adaptations.

## Why a separate pipeline from Monty

Same reason Monty was cloned from Commando rather than parameterised:
cloning kept the older pipeline's verification status safe while the new
engine was being unfolded. Once a second early-Hubbard SID (e.g. one of
Crazy Comets / Confuzion / Action Biker) is wired through this same
scaffold to Grade A, the shared logic can be lifted into a common
"hubbard-1985-86" codegen.
