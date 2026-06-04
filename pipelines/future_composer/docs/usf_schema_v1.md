# USF v1 — FC instrument decomposition

Status: **draft** (this session's deliverable).

## Goal

Replace the four v0 opaque per-instrument bytes (`fc_fil_count`,
`fc_fx1`, `fc_fx2`, `fc_fx3`) with named musical fields, addressing
the §7 compromise flagged in `usf_schema_v0.md`. After v1, FC
instruments carry their effect configuration as named attributes
the ML model can reason about, not as integers indexing an engine
library.

## Bit-field source map

Verified against the Cybernoid II ACME source (see
`wayback_cybernoid2_driver.md`) and confirmed against the engine
code at `/tmp/fc_research/Tel_Jeroen_Cybernoid2.asm` lines 539-1300.

### `fx1` (instrument byte +5) — vibrato

| Bits | Mask | Meaning |
|---|---|---|
| 0-3 | `$0F` | Vibrato amplitude (0-15). **0 disables vibrato entirely** (`javib2 lda fx1sto / beq b17jmp2`). |
| 4-6 | `$70` | Vibrato base-speed (0-7) — bit-shifted right by 4 to use as a counter step. |
| 7   | `$80` | Vibrato polarity. 0 = positive (ADC opcode SMC'd to `$BC`), 1 = negative (LDY opcode SMC'd to `$7D`). |

### `fx2` (instrument byte +6) — pulse + filter

| Bits | Mask | Meaning |
|---|---|---|
| 0-2 | `$07` | Pulse program index (1-7; 0 disables pulse program). Selects an entry in `pulsetabel` (4 programs of 8 bytes each). |
| 3   | `$08` | Strange-filter active flag. Bidirectional cutoff sweep on $D416. |
| 4-7 | `$F0` | Pulse increment value (0-15 << 4 = 0..$F0 as default `pulsecountup`). |

### `fx3` (instrument byte +7) — effect-presence flags

| Bit | Mask | Effect | Engine routine |
|---|---|---|---|
| 0 | `$01` | filter program  | walks `filterbytes[$08..]` per `filcount` lo nibble |
| 1 | `$02` | pulse run       | autonomous PWM sweep at `pulserunspeed=$63` |
| 2 | `$04` | tone arpeggio   | cycles `arp[0..N]` from `arplo/arphi` indexed by `fx1 & $0F` |
| 3 | `$08` | pulse arpeggio  | cycles `pulsearp[0..7]` |
| 4 | `$10` | drum routine    | plays waveform+pitch program from `drumtabel`; `fx1 & $0F` selects drum number |
| 5 | `$20` | tone sweep up   | decrements `hinotesto` per frame |
| 6 | `$40` | wave arpeggio   | cycles `wavearp[$80,$10,$80,$10]` through $D404 |
| 7 | `$80` | noise tick      | plays `starttabel` waveform for `startlen` frames |

### `fil_count` (instrument byte +4) — filter selection + auxiliaries

| Bits | Mask | Meaning |
|---|---|---|
| 0-3 | `$0F` | Filter program index (filcount lo nibble — indexes filterbytes via *4). |
| 4-7 | `$F0` | Auxiliary flags. The known bit: bit 3 (`$08`) — **double-voice** detune (the "dubvoice" trick adding $0C to lo freq). Other bits' meaning not yet RE'd; carried opaquely in v1 as `filter.aux_bits`. |

## v1 USF schema additions

Extends the existing `vibrato` block and adds three new instrument
blocks. The choice to extend `vibrato` (rather than introduce a
separate `fc_vibrato`) is principled: vibrato is a cross-engine
musical concept; Hubbard and FC parameterise it differently, but
both write to the same conceptual block.

```usf
instrument N {
  waveform: $14 $41
  adsr:     $08 $DD

  ; Existing fields (Hubbard uses scale/onset/etc):
  vibrato:  scale=0 onset=8                  ; Hubbard
  ; FC adds these subfields:
  vibrato:  amplitude=3 speed=4 direction=up ; FC

  ; NEW v1 blocks (FC-only — emitted only when corresponding bits set):
  pulse_prog:  program=1 increment=4         ; from fx2
  filter_prog: program=8 strange=true        ; from fil_count + fx2.3
                                              ; (double_voice/aux_bits TBD)
  effects: tone_arp pulse_arp drum tonesweep_up wave_arp \
           noise_tick pulse_run filter_program
                                              ; from fx3 bits (any subset)
}
```

### Field-level deviation from "fully principled"

These remain §7 compromises (improved from v0 but not perfect):

- `pulse_prog.program=N` — N indexes an engine-shared `pulsetabel`.
  Full principledness would inline the program contents as 8 named
  byte fields per instrument. v2 deferral.
- `filter_prog.program=N` — same: indexes engine-shared `filterbytes`.
  v2 deferral.
- `filter_prog.aux_bits=$XX` — the high nibble of `fil_count` carries
  bits whose meaning isn't fully RE'd. v1 carries opaquely as a byte.
  v2 deferral.

What v1 DOES achieve:
- The 9 effect FLAGS (`fx3` bits + `double_voice`) become NAMED
  boolean fields — a model can learn "drum-enabled instruments have
  these other features."
- Vibrato amplitude/speed/direction are NAMED scalar parameters —
  a model can interpolate.
- Pulse increment is a NAMED scalar.

## Removed fields

The v0 instrument fields `fc_fil_count`, `fc_fx1`, `fc_fx2`, `fc_fx3`
are removed from the grammar. Pre-existing v0 USFs (Hawkeye.usf,
Cybernoid_II.usf) are regenerated through the v1 pipeline.

## Round-trip invariant

For both canaries, the v1 pipeline preserves byte-exact rebuild:
  - to_usf.py decomposes the original 4 bytes into the new fields
  - composer (binary-patch + asm-data) recomposes the 4 bytes
  - md5(rebuilt) == md5(HVSC original)

This is the load-bearing test that the decomposition is lossless.
