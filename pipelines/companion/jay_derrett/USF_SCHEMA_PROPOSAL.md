# USF schema for jay_derrett (proposal)

The 24-byte instrument program decomposes into four musical
primitives. The mapping below comes from tracing Ninja_Hamster's
per-frame block (`$C6DD..$C86A`) and note-start (`$C86E..$C8F6`).

## Voice-state byte layout (= 24-byte instrument program)

After note-start copies the instrument bytes into voice state, each
byte plays a defined role in the per-frame modulation block:

| offset | addr (V1) | role | reader pc |
|---|---|---|---|
| `$00` | `$C92D` | **bit-flags**: bit0=slide direction (0=up/ADC, 1=down/SBC), bit1=bidir mode, bit2=bound-mode (0=zero step at bound, 1=swap to other bound), bit7=use high-oct freq variant | C6F8, C73A, C761, C768, C77F, C7D1, C7D8, C7DB |
| `$01` | `$C92E` | freq cur lo (written to `$D400+v*7`) | C703, C740, C753, C77F, C7B0 |
| `$02` | `$C92F` | freq cur hi (`$D401+v*7`) | C706, C74A, C759, C7BA |
| `$03` | `$C930` | freq bound 1 lo — **delta** from note freq; at note-start: `bound1 = freq_table[note] + delta` | C8A4, C770, C77F |
| `$04` | `$C931` | freq bound 1 hi delta | C8B1 |
| `$05` | `$C932` | freq bound 2 lo delta — `bound2 = freq_table[note] - delta` | C8BB |
| `$06` | `$C933` | freq bound 2 hi delta | C8C4 |
| `$07` | `$C934` | freq slide step lo | C744, C7B4 |
| `$08` | `$C935` | freq slide step hi | C74D, C7BD |
| `$09` | `$C936` | (unused / not referenced) | — |
| `$0A` | `$C937` | PW hi current (`$D403+v*7`); ADC carry from lo | C71E, C7FA, C816, C838, C856 |
| `$0B` | `$C938` | PW first-phase bound (compared against PW hi) | C802, C81E |
| `$0C` | `$C939` | PW first-phase step | C7F4 |
| `$0D` | `$C93A` | (unused / not referenced) | — |
| `$0E` | `$C93B` | PW initial direction: 0=up/ADC, non-zero=down/SBC | C7EB |
| `$0F` | `$C93C` | PW oscillation state (init 0=up; flipped after first bound) | C829, C842, C865 |
| `$10` | `$C93D` | PW oscillation upper bound | C840 |
| `$11` | `$C93E` | PW oscillation lower bound | C85E |
| `$12` | `$C93F` | PW oscillation step | C832, C850 |
| `$13` | `$C940` | (unused / not referenced) | — |
| `$14` | `$C941` | **CTRL** byte (waveform + gate-on) → `$D404+v*7` | C731, C8DB |
| `$15` | `$C942` | **AD** (attack/decay) → `$D405+v*7` | C8F0 |
| `$16` | `$C943` | **SR** (sustain/release) → `$D406+v*7` | C8F6 |
| `$17` | `$C944` | CTRL alt — OR'd onto offset $14 to form the actual CTRL write. Init = offset $14. Mutated by `$80` (gate off) handler to flip gate bit. | C522, C734 |

Three bytes (`$09`, `$0D`, `$13`) are never read — padding / future
flags. The rest decompose into four musical primitives:

## Musical primitives

1. **Envelope** — CTRL gate-on (`$14`), AD (`$15`), SR (`$16`),
   CTRL alt (`$17`). Same shape as Hubbard '85's `envelope` field.

2. **Freq slide / sweep** — bit-flags (`$00` bits 0/1/2/7), 4 bound
   delta bytes (`$03..$06` = upper_delta lo/hi + lower_delta lo/hi),
   step 2 bytes (`$07..$08`). Three operating modes:
   - **One-shot, swap-to-other**: bit1=0, bit2=1. Slide toward
     bound 1; at bound, jump to bound 2.
   - **One-shot, halt**: bit1=0, bit2=0. Slide toward bound 1; at
     bound, step → 0 (freeze freq).
   - **Bidirectional ricochet**: bit1=1. Slide toward bound 1;
     at bound, flip direction; slide toward bound 2; flip; repeat.
   - bit7=1 selects high-octave freq variant (`freq_table[note+16]`)
     for the SID write — engine bound-crossing arpeggio.

3. **Pulse-width modulation** — two-phase. First phase: ADC/SBC
   `step1` against `bound1` (offsets `$0B/$0C/$0E`). On crossing,
   transition to bidirectional oscillation phase: bounds (`$10/$11`),
   step (`$12`), direction state (`$0F`).

4. **High-octave arp variant** — `$18/$19` in voice state, NOT in
   the 24-byte instrument program. Computed at note-start from
   `freq_table[note+$10]`. Selected by `$00` bit 7. No schema field
   needed — it's a derived runtime value.

## USF Instrument shape (proposed)

Re-uses existing fields where the mapping is clean; adds two new
typed sub-configs for the modulation that doesn't fit Hubbard's
single `freq_slide: bool` knob.

```
instrument N {
  waveform: $40                       # gate-on CTRL (single byte — same as clever_music)
  adsr: $09 $28                       # (AD, SR)
  envelope: gate_off_ctrl=$01         # offset $17 — what OR'd onto waveform at gate-off

  pwm:
    initial: ($0E00)                  # 16-bit PW init; lo always zeroed by engine
    phase1_dir: up | down             # offset $0E
    phase1_bound: $80                 # offset $0B
    phase1_step: $08                  # offset $0C
    osc_upper: $C0                    # offset $10
    osc_lower: $40                    # offset $11
    osc_step:  $04                    # offset $12

  freq_slide:
    mode: none | one_shot_halt | one_shot_swap | bidirectional
    initial_dir: up | down            # bit 0
    high_oct_arp: false               # bit 7 (true → use note+16 freq variant)
    upper_delta: $0100                # offsets $03/$04 — SIGNED 16-bit
    lower_delta: $0080                # offsets $05/$06
    step: $0020                       # offsets $07/$08
}
```

The existing `pwm: mode=… speed=… init=… min_hi=… max_hi=…` and
`freq_slide: bool` fields stay for backward compat with Hubbard '85
USFs. jay_derrett uses the new richer sub-configs.

## Row vocabulary (per-voice byte stream → NoteRows)

Walk each voice's captured byte stream (from play-capture's
min..max ptr range), emit one row per instruction:

| byte | row | notes |
|---|---|---|
| `$00..$7F` | `NoteRow(Pitch(name,oct), duration=1)` | semitone 12..15 → `fx:raw_NN` rest |
| `$80` | `NoteRow(rest, duration=1)` | gate-off — the engine ORs offset $17 onto CTRL |
| `$81` | folded → prev row `.duration += 1` | clever_music pattern |
| `$82 N` | `NoteRow(rest, duration=1+N, fx_flags=('set_dur=$NN',))` | the $82 byte takes 1 frame + N idle frames |
| `$Bx` | `NoteRow(rest, dur=1, fx_flags=('tempo=N',))` | clever_music vocabulary |
| `$Cx` | `NoteRow(rest, dur=1, fx_flags=('vol=N',))` | clever_music vocabulary |
| `$Dx` | `NoteRow(rest, dur=1, instr=i{N+1})` | engine INCs the value (+1 quirk) |
| `$Ex` | `NoteRow(rest, dur=1, fx_flags=('section_end=N',))` | composer is free to re-architect orderlist scheme |
| other | `NoteRow(rest, dur=1, fx_flags=('fx:raw_NN',))` | engine-skip fallback |

`set_dur=$NN` and `section_end=N` are new parametric fx flags (same
shape as the existing `tempo=N`/`vol=N`/`song_pos=N`/`porta=N`).

Pattern length = sum(row.duration).

## Top-level USF shape

Same as clever_music. No schema additions beyond the two
sub-configs above.

```
psid {…}                            # standard
params {}                           # engine-neutral
init { voice 1 { instr: i1 } … }    # placeholder; first $Dx in stream sets actual
freq_table { … }                    # inlined PAL freq table (192 bytes)

instrument 1 { … }                  # N instruments, decoded musically
…

subtune 0 music {
  tempo: <engine init tempo>
  voice 1 {
    orderlist: 1 loop@0
    pattern 1 length=N { rows… }
  }
  voice 2 { … }
  voice 3 { … }
}
```

## Schema additions summary

Two new typed dataclasses on `Instrument`:

1. `FreqSlideConfig` (mode + initial_dir + high_oct_arp + bounds +
   step). 5 fields.
2. Expanded `PwmConfig` adding phase1/oscillation distinction.
   Either extend in-place or add a `PwmModulationConfig` alongside.

Two new parametric fx flags (no schema work — they're just strings):

1. `set_dur=$NN` on rest rows for `$82` set-duration.
2. `section_end=N` on rest rows for `$Ex` pattern-jump.

## Open questions before implementation

1. Should `FreqSlideConfig` extend the existing `freq_slide: bool` /
   Hubbard's params, or stand alone as a richer separate field?
2. How to model offset $17 (CTRL alt — OR'd at gate-on, mutated at
   gate-off): goes on `envelope`? Or a new `gate_off_ctrl` field?
3. Bytes $09, $0D, $13 are unread — silently drop, or surface as
   `_padding` bytes to preserve round-trip?
