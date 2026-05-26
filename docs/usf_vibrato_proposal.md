# USF Vibrato Extension Proposal

**Status:** Draft  
**Date:** 2026-04-29  
**Author:** Design session following Hubbard engine reverse-engineering  

---

## Motivation

The Hubbard engine vibrato system has been reverse-engineered and differs fundamentally from
the GT2 vibrato system that USF currently represents. Encoding it requires extending USF with
a first-class `VibratoSpec` structure so that:

1. Multiple engine types can express their vibrato without engine-specific hacks in the spec.
2. ML models see vibrato as a discrete, learnable feature rather than opaque speed-table bytes.
3. The V2 player can synthesize vibrato without relying on the GT2 speed-table binary format.

---

## Current State of Vibrato in USF

### What exists today

The `Instrument` dataclass has two vibrato fields:

```
vib_speed_idx : int   # index into Song.speed_table (0=none, GT2 convention)
vib_delay     : int   # delay in frames before vibrato begins
```

`Song.speed_table` is a list of `SpeedTableEntry(left, right)` where the binary meaning
is GT2-specific:

- `left`: vibrato speed byte (bit 7 = note-independent flag)
- `right`: vibrato depth byte

`vib_logarithmic` was added to `Instrument` as a forward-looking flag but the semantics
are underspecified: there is no LFO shape, no period, no explicit centre point.

Pattern command 4 (`CMD_VIBRATO`) allows per-note vibrato override via speed-table index,
but it refers to the same opaque `speed_table` entries.

### What is missing

- LFO shape (triangle, sine, square, sawtooth)
- LFO period in frames (GT2 uses a derived speed, Hubbard uses fixed period-8)
- Whether depth is a fixed frequency delta or a pitch-proportional (logarithmic) delta
- Onset delay (already present as `vib_delay`, but the semantics need precision)
- Interaction contract with arpeggio (wave table note offsets)

---

## Hubbard Vibrato: Concrete Specification

The Hubbard engine computes vibrato as follows each frame after `note_age >= 6`:

```
lfo_phase  = note_age mod 8          # 0-7
lfo_table  = [0, 1, 2, 3, 3, 2, 1, 0]  # triangle, always positive (0..depth)
lfo_depth  = lfo_table[lfo_phase]

semitone_delta = freq_hi[pitch + 1] - freq_hi[pitch]   # one-semitone delta at pitch
raw_delta      = semitone_delta >> byte5                # byte5 is instrument byte 5

applied_freq   = base_freq_hi + raw_delta * lfo_depth
```

Observations:

1. The LFO is a triangle that never goes below zero — it oscillates between 0 and `max_depth`
   rather than between `-max_depth` and `+max_depth`. This is a half-wave (unipolar) triangle.
2. Depth is pitch-proportional: `semitone_delta` depends on the current note. This is
   logarithmic vibrato (equal-ratio depth across the keyboard).
3. The depth control parameter (`byte5`) is a right-shift count (1→half semitone, 2→quarter).
4. Period is fixed at 8 frames; there is no speed parameter.
5. Onset delay is 6 frames (hardcoded in the Hubbard engine).

---

## Proposed Extension: `VibratoSpec`

### Design decisions

**Per-instrument, not per-note.** Vibrato is an instrument property in both GT2 and Hubbard.
Pattern command 4 can reference a `VibratoSpec` by index, so it remains possible to override
vibrato per-note — but the spec lives in a defined table, not inline on the note event. This
keeps the token vocabulary bounded.

**Explicit struct, not opaque bytes.** The GT2 speed-table format encodes vibrato as two
binary bytes with GT2-specific bit packing. That encoding cannot represent Hubbard vibrato
(different period, different depth model, unipolar LFO). The `VibratoSpec` struct replaces
the implicit vibrato meaning in `SpeedTableEntry` with explicit named fields. `SpeedTableEntry`
is retained for GT2 portamento and funktempo, which are still opaque binary.

**LFO shape as enum.** The shape vocabulary needed across known engines:
- `triangle` — Hubbard (unipolar, period 8), GT2 (bipolar, variable speed)
- `sine` — commonly needed for smoother vibrato in demo-scene engines
- `square` — used for pitch-wobble effects
- `sawtooth` — used for glide-like vibrato

Shape covers the composition space. Additional shapes can be added without changing the struct.

**Unipolar vs bipolar.** Hubbard's LFO goes from 0 to depth (unipolar). GT2's LFO goes from
-depth to +depth (bipolar). This is a boolean flag on `VibratoSpec`. Most engines are bipolar.

**Depth model: linear vs logarithmic.** Linear = fixed freq_hi delta regardless of pitch
(GT2 right byte = direct freq_hi delta). Logarithmic = delta scales with pitch so the
perceived semitone ratio stays constant (Hubbard right-shifts the one-semitone interval).
This maps directly to the existing `vib_logarithmic` flag, but now it lives on `VibratoSpec`
where it belongs.

**Depth unit: shift count vs direct value.** Hubbard encodes depth as a right-shift count
of the one-semitone interval (`depth_shift`). GT2 encodes it as a direct freq_hi addend
(`depth_direct`). The proposal uses two fields — `depth_shift` and `depth_value` — exactly
one of which is nonzero, selected by `logarithmic`:

- `logarithmic=True` → `depth_shift` is used (Hubbard: semitone_delta >> depth_shift)
- `logarithmic=False` → `depth_value` is used (GT2: add depth_value directly to freq_hi)

**Period vs speed.** GT2 expresses vibrato rate as a speed byte (added to a phase accumulator
each frame). Hubbard uses a fixed 8-frame period with no speed control. Both representations
should be supported:

- `period`: LFO period in frames (0 = use speed accumulator instead)
- `speed`: per-frame phase increment (0-255), used when period=0

**Onset delay.** Already present as `vib_delay` on `Instrument`. Move it into `VibratoSpec`
so the full vibrato definition is self-contained. Keep `vib_delay` on `Instrument` as an
override (engine-level init delay on top of the spec delay), defaulting to 0.

**Interaction with arpeggio.** The wave table controls note_offset each frame. Vibrato adds
a freq_hi delta on top of the note_offset-derived frequency. They are additive and independent.
The player must apply vibrato AFTER the wave table sets the frequency for the frame. This is
the correct ordering in both the GT2 and Hubbard engines: wave table sets pitch, vibrato
modulates it.

There is no conflict to resolve: arpeggio changes note_offset, vibrato changes freq_hi.
The only edge case is when the wave table uses `keep_freq=True`: vibrato should still apply
on top of the kept frequency. This is already correct in both engines.

---

## Proposed Data Structure

```python
@dataclass
class VibratoSpec:
    """Self-contained vibrato LFO definition.

    Replaces the implicit vibrato meaning in SpeedTableEntry for ML training
    and multi-engine representation. For GT2 roundtrip, vib_speed_idx still
    references SpeedTableEntry; VibratoSpec is decoded for inspection and ML.
    """
    id: int = 0                  # index in Song.vibrato_table (0-based)

    # LFO shape
    shape: str = 'triangle'      # 'triangle', 'sine', 'square', 'sawtooth'
    unipolar: bool = False        # False=bipolar (-depth to +depth), True=unipolar (0 to depth)

    # LFO rate: exactly one of period or speed is nonzero
    period: int = 0              # LFO period in frames (>0 overrides speed)
    speed: int = 0               # GT2-style: per-frame phase accumulator increment (0-255)

    # Depth model
    logarithmic: bool = False     # False=linear (depth_value added to freq_hi)
                                  # True=logarithmic (semitone delta right-shifted by depth_shift)
    depth_value: int = 0         # Linear mode: freq_hi addend at full LFO amplitude
    depth_shift: int = 0         # Logarithmic mode: right-shift count of one-semitone delta

    # Note independence
    note_independent: bool = False  # True=continue LFO phase across note changes (GT2 bit 7)

    # Onset
    onset_delay: int = 0         # frames before vibrato begins after note-on
```

### Field encoding for GT2

When importing from GT2:

```
speed_byte = SpeedTableEntry.left
depth_byte = SpeedTableEntry.right

VibratoSpec:
  shape = 'triangle'
  unipolar = False
  period = 0
  speed = speed_byte & 0x7F
  note_independent = bool(speed_byte & 0x80)
  logarithmic = False
  depth_value = depth_byte
  depth_shift = 0
  onset_delay = Instrument.vib_delay
```

### Field encoding for Hubbard (1985/1986 driver)

```
byte5 = instrument table byte offset 5

VibratoSpec:
  shape = 'triangle'
  unipolar = True
  period = 8
  speed = 0
  note_independent = False
  logarithmic = True
  depth_value = 0
  depth_shift = byte5        # right-shift count of semitone delta
  onset_delay = 6            # hardcoded in Hubbard engine
```

---

## Integration with `Instrument`

The `Instrument` struct gains an optional `VibratoSpec` reference:

```python
vib_spec: VibratoSpec | None = None  # decoded vibrato definition (ML / inspection)
vib_speed_idx: int = 0               # GT2: raw speed table index (for binary roundtrip)
vib_delay: int = 0                   # kept for GT2 binary roundtrip (onset override)
```

`vib_spec` is the canonical representation for the player and ML. `vib_speed_idx` and
`vib_delay` are retained for GT2 binary roundtrip only. Non-GT2 converters set `vib_spec`
directly and leave `vib_speed_idx = 0`.

`Song` gains a new table:

```python
vibrato_table: list[VibratoSpec] = []  # indexed by VibratoSpec.id
```

---

## Token Grammar Extension

### New tokens

```
vibrato_table := VIB_TABLE[ vib_spec+ ]VIB_TABLE

vib_spec      := VIB<id> vib_shape vib_rate vib_depth vib_flags vib_delay?

vib_shape     := VS_TRI | VS_SIN | VS_SQR | VS_SAW
vib_rate      := VP<period>               period in frames (>0 = fixed period)
              |  VS<speed>                 per-frame phase increment (GT2 style)
vib_depth     := VD<depth_value>           linear: direct freq_hi addend
              |  VDS<depth_shift>           log: right-shift count
vib_flags     := VU                        unipolar flag (omit if bipolar)
              |  VNI                       note-independent flag (omit if note-dependent)
vib_delay     := VDEL<frames>              onset delay (omit if 0)

In instrument params, reference a VibratoSpec by id:
  vibrato      := VIB<id>                  (replaces VIB<H> VD<H> in current grammar)
```

### Backward compatibility

The current grammar token `VIB<H> VD<H>` encodes a GT2 speed-table reference. This remains
valid for GT2 songs. When a song has a `vibrato_table`, instruments use `VIB<id>` to reference
it. Without a `vibrato_table`, `VIB<H> VD<H>` retains its existing meaning (GT2 speed table
index + delay).

The two forms are distinguishable during detokenization by presence/absence of `VIB_TABLE` in
the song header.

---

## Player Synthesis

The V2 player must compute vibrato as follows:

```
For each frame, after wave table frequency is set:
  if note_age < vib_spec.onset_delay: skip
  if vib_spec.period > 0:
    phase = note_age mod vib_spec.period    (or global_frame if note_independent)
    lfo = shape_table[vib_spec.shape][phase * shape_resolution / vib_spec.period]
  else:
    phase_acc += vib_spec.speed
    lfo = shape_table[vib_spec.shape][phase_acc >> (8 - log2(shape_resolution))]

  if vib_spec.unipolar:
    lfo = (lfo + shape_max) >> 1            # map [-max..+max] to [0..max]

  if vib_spec.logarithmic:
    semitone_delta = freq_hi[note + 1] - freq_hi[note]
    delta = semitone_delta >> vib_spec.depth_shift
  else:
    delta = vib_spec.depth_value

  freq_hi += (lfo * delta) >> shape_fractional_bits
```

Shape tables are stored as ROM constants in the player. For the fixed-period-8 triangle
(Hubbard), the table is `[0, 1, 2, 3, 3, 2, 1, 0]` — 8 entries, already at full amplitude.

---

## Interaction with Existing Features

### Arpeggio (wave table note_offset)

Additive and independent. Vibrato is applied to whatever freq_hi the wave table set, whether
from note_offset, absolute_note, or keep_freq. No special interaction needed.

### Pulse width modulation

No interaction. PW and vibrato are orthogonal.

### Portamento

Portamento slides `freq_hi` toward a target note. Vibrato is applied on top of the current
portamento position. This matches both GT2 and Hubbard behaviour.

### Pattern command 4 (CMD_VIBRATO)

The command value is a `VibratoSpec` id (when `vibrato_table` exists) or a GT2 speed-table
index (legacy). When a pattern command 4 fires, it overrides the instrument's `vib_spec` for
the duration of the note. On next note-on, the instrument's own `vib_spec` is restored.

---

## Migration Path

1. Add `VibratoSpec` dataclass to `src/usf/format.py`.
2. Add `vibrato_table: list[VibratoSpec]` to `Song`.
3. Add `vib_spec: VibratoSpec | None` to `Instrument`.
4. Update `src/converters/rh_to_usf.py` to populate `VibratoSpec` from `byte5`.
5. Update `src/converters/gt2_to_usf.py` to decode `SpeedTableEntry` → `VibratoSpec`
   when the entry is used as vibrato (detected by context: instrument `vib_speed_idx` reference).
6. Update `src/usf_text.py` tokenizer/detokenizer with new grammar.
7. Update `src/player/codegen_v2.py` to emit vibrato synthesis code for `vib_spec` paths.
8. Update `docs/usf_spec.md` with the new `VibratoSpec` section and grammar changes.

The GT2 binary roundtrip is unaffected: `vib_speed_idx` still points into `speed_table` for
the packer. `VibratoSpec` is an additional decoded layer, not a replacement of the binary path.

---

## Open Questions

1. **Sine table size.** A 64-entry or 256-entry sine lookup table in the player ROM? 64 entries
   costs 64 bytes and gives adequate audio quality for music. 256 entries gives smoother curves
   but costs 256 bytes. Recommendation: 64 entries (6-bit phase index), interpolate linearly for
   higher-resolution shapes.

2. **Fixed-period vs accumulator unification.** Could express Hubbard's period-8 as
   `speed = 256/8 = 32` in the accumulator model. This would eliminate the `period` field.
   However, this loses the exact phase lock to note age that Hubbard requires. Keeping both
   fields is safer and more explicit.

3. **Multi-engine vibrato table sharing.** If a song has instruments using both GT2-style and
   Hubbard-style vibrato (e.g., a future multi-engine USF composition), both coexist in
   `vibrato_table` with their respective flags. No conflict.

4. **Phase accumulator on note-independent vibrato.** GT2 speed-table bit 7 (`note_independent`)
   means the LFO phase continues counting across note boundaries rather than resetting on
   note-on. The `note_independent` flag captures this. When `period > 0` (fixed period),
   note-independent means `phase = global_frame mod period` instead of `note_age mod period`.
