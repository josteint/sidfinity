# Bump Set Spike pipeline

End-to-end rebuild scaffold for Rob Hubbard's *Bump Set Spike* (1986
Entertainment USA). Same shape as the Commando / Monty pipelines; cloned
from Monty and renamed. The engine-specific adaptations needed for an
audibly correct rebuild are listed below — they have **not** been wired
in yet.

## Status

| Metric | Value |
|---|---|
| Scaffold builds end-to-end | yes (`lake build sidgen_bump_set_spike` produces a 3779-byte SID) |
| Engine adapted to Bump Set Spike | **no** (codegen still treats data as Monty) |
| Grade against original | **F** (writelog ~0.1% snapshot match, 1/1500) |

The freq-table extraction is correct (`freq[0] = $0116` matches the binary
at `$B3FF`). The rest of the extract path inherits Monty's assumptions
about instrument structure, fx-flag semantics, and orderlist layout —
which differ from Bump Set Spike's binary. See `disassembly.s` and
`docs/hubbard_bump_set_spike_disassembly.s` for the engine details.

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
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Bump_Set_Spike.sid \
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

## Why a separate pipeline from Monty

Same reason Monty was cloned from Commando rather than parameterised:
cloning kept the older pipeline's verification status safe while the new
engine was being unfolded. Once a second early-Hubbard SID (e.g. one of
Crazy Comets / Confuzion / Action Biker) is wired through this same
scaffold to Grade A, the shared logic can be lifted into a common
"hubbard-1985-86" codegen.
