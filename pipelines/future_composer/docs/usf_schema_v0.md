# FutureComposer USF schema — v0 design draft

Status: **first cut, not yet implemented.** Designed against Hawkeye
specifically; some choices likely need rework once more engines land.

## Goal

A USF representation for the FC engine family (Deenen MoN 1987 + Tel /
Bjerregaard / FC editor variants) that satisfies the
`docs/usf_representation_principle.md` discipline: musical content
in USF, engine mechanism in the composer; no engine identification;
no opaque categorical tokens.

Scope: Hawkeye-class V3.x-lineage SIDs first. The 6 FC editor releases
(V1-V5) probably share enough format to use the same USF schema; SFX
records likewise.

## What the engine model has

Per `pipelines/future_composer/hawkeye/engine_model.py`:

| Layer | FC concept | Structured Python type |
|---|---|---|
| song | per-PSID metadata + 12 subtunes | `FCSong` |
| subtune | speedbyte + per-voice seq + music/sfx flag | `Subtune` |
| sequence | per-voice command stream | `Sequence` + `SeqCommand` enum |
| pattern | byte stream of note + control events | `Pattern` + `PatEvent` enum |
| instrument | 8-byte record | `Instrument` |
| freq table | 96 PAL entries | `list[int]` |

## Principle bind — what is musical, what is mechanism?

For each FC concept, decide whether it's MUSICAL (goes in USF) or
ENGINE MECHANISM (resolved at extract or runtime, stays in
composer):

### Sequence commands

| Command | Verdict | Reason |
|---|---|---|
| `SeqPatternJump` | musical | composer chose to play pattern N at this step |
| `SeqTranspose` | **engine mechanism for data compression** | composer wrote one pattern + several transpositions; USF can hold the MUSICAL OUTPUT (notes at absolute pitches) and the composer can re-compress if desired. **→ apply at extract time** |
| `SeqRepeats` | engine mechanism | RLE-style compression. **→ expand at extract time** |
| `SeqVoiceinc` | musical | sets the wave-table advance rate, audibly changes the timbre. Different orderlist steps may use different voiceinc. **→ per-orderlist-step attribute** (until we understand it well enough to absorb into instrument) |
| `SeqEnd` / `SeqWrap` | musical structure | end-of-song or loop point. → `loop@N` / `stop` like existing USF |

Net result: **orderlist is just pattern ids with optional `voiceinc=N` attribute. Transpose and repeats are baked in at extract time.**

Cost: patterns might be duplicated when transposed. Trade: USF carries
absolute musical content (better ML signal) at the cost of larger files.
Hawkeye's 156-byte V1 sequence becomes ~97 orderlist entries (one per
PatternJump after expansion).

### Pattern events

| Event | Verdict |
|---|---|
| `PatNote` | musical (it IS the music) → note row pitch |
| `PatSetLength` (possibly chained) | musical (composer chose the duration) → note row duration |
| `PatInstrumentChange` | musical → `iN` on the next note row |
| `PatGlide(delay)` + target | musical → per-note `glide=N` attribute (delay frames) |
| `PatNoGlide` | musical (or absence of glide) → omit attribute |
| `PatWaveAdjust(delta)` | musical (timbre tweak) → per-note `wave_adjust=N` |
| `PatFilterSet(value)` | musical (composer wrote a $D417 value) → per-note `filter=$NN` |
| `PatEnd` | structural → derived from pattern length |

### Instruments — the 8 bytes

The known fields map onto existing USF instrument fields:
- `pulse_hi` → existing `pwm.init` (initial pulse-width high)
- `waveform` → existing `waveform` (ctrl byte)
- `ad`, `sr` → existing `adsr: $AD $SR`

The unknown fields (per FC research):
- `fil_count` — pointer into filter table (TBD format)
- `fx1` — vibrato-related
- `fx2` — arpeggio-related
- `fx3` — drum / skydive flags

**⚠️ For v0 these are opaque bytes** in USF (`fc_fx1: $40` etc.).
This **violates the principle** (§7 — opaque categorical token). The
follow-up work: trace the engine handling fx1/fx2/fx3 across multiple
patterns, identify what musical parameters they each control, decompose
into named musical attributes (e.g. `vibrato.depth: 4` instead of
`fc_fx1: $40`).

This is the same kind of work that produced the Hubbard `FreqSlideConfig`
/ `IncBy2Config` / etc. from raw bytes in the Phase-2 principled-instrument
refactor.

### Freq table

96 entries of 16-bit PAL values. Goes in USF as `freq_table { … }` per
the existing convention (Hubbard schema).

### Subtune kind: music vs SFX

FC has 6 music + 6 SFX. Structurally identical at the
note/pattern/sequence level — SFX is just "short music." The
distinction is in how the player handles them ($7BAE flag) but the
musical content is the same shape.

**Verdict:** use `subtune N music` for both. Add a `kind` attribute
when SFX semantics matter (e.g. for the playback host to know not to
sustain the song-end gate). Don't reuse Hubbard's 16-byte SFX
record shape — that's a different engine's mechanism.

```
subtune 6 music {
  is_sfx: true     ; engine-runtime distinction; not strictly required
  tempo: 3
  voice 1 { ... }
  voice 2 { ... }
  voice 3 { ... }
}
```

### Tempo

FC's `speedbyte` = frames-per-step. The engine decrements a counter
from speedbyte until rollover. So `tempo: speedbyte + 1` (matching
Hubbard's convention where `tempo: 4` = 4 frames per step).

## Draft schema

```usf
psid {
  title:      "Hawkeye"
  author:     "Jeroen Tel"
  released:   "1988 Thalamus"
  clock:      PAL
  sid:        6581
  start_song: 1
  speed:      0
}

params {
  engine: future_composer    ; engine family marker (already used by Hubbard)
}

freq_table {
  $1C $01 $2D $01 $3E $01 ...    ; 96 entries lo + hi interleaved (192 bytes)
}

instrument 1 {
  waveform: $14 $41           ; pulse_hi + ctrl (waveform+gate bits)
  adsr:     $08 $DD
  ; FC-specific (opaque pending decomposition; see usf_schema_v0.md
  ; principle bind section)
  fc_fil_count: $F0
  fc_fx1:       $40
  fc_fx2:       $61
  fc_fx3:       $00
}

; ... 14 more instruments (inst 0 omitted if all-zero)

subtune 0 music {
  tempo: 4
  voice 1 {
    orderlist: 0 1 1 1 1 1 1 1 1 ... loop@0
    pattern 0 length=33 {
      C-3 33 i:1
    }
    pattern 1 length=24 {
      D#3   4   i:2
      E-3   4
      G-3   4
      C-4   4   glide=8
      ...
    }
  }
  voice 2 { ... }
  voice 3 { ... }
}

subtune 6 music {
  is_sfx: true
  tempo: 3
  voice 1 { ... }
  voice 2 { ... }
  voice 3 { ... }
}
```

### Note row attributes (additions for FC)

In addition to the existing pitch / duration / `iN` / `tie` / `porta=N`
columns, FC needs:
- `glide=N` — pitch slide with N-frame delay before engaging (FC's
  `PatGlide(delay)`)
- `wave_adjust=N` — per-note wave-table-position delta (`PatWaveAdjust`)
- `filter=$NN` — per-note direct $D417 write (`PatFilterSet`)

Reuse `i:N` / `i:name` for instrument references. Note: pitch values
0-95 are the freq-table index (preserved as the engine emits them);
the USF pitch should be the SEMITONE-NAMED equivalent (`C-3` not raw
`32`) after applying any active transpose at extract time.

## What's principled, what's still suspicious

**Principled:**
- Notes carry pitch + duration + instrument (musical primitives)
- Glide / filter / wave-adjust are named per-note attributes with
  numeric ranges (model can interpolate)
- Sequence becomes a flat orderlist with optional voiceinc attribute
- Transpose and repeat are baked in at extract time (musical output
  preserved, engine compression dropped)
- SFX vs music is just a kind attribute on the same subtune shape

**Still suspicious (v0 compromises):**
- `fc_fil_count`, `fc_fx1`, `fc_fx2`, `fc_fx3` — opaque bytes per
  instrument. §7 forbidden shape. **Follow-up**: trace + decompose
  into named musical attributes.
- `voiceinc` as a per-orderlist-step opaque value (0-15). It controls
  wave-table advance rate; should eventually become a named musical
  attribute (e.g. `wave_speed: N` per orderlist step) or absorbed into
  instrument.

## Extract path sketch

```python
def fcsong_to_usf(song: FCSong) -> UsfFile:
    return UsfFile(
        psid=PsidMeta(...),
        params=Params(fields={'engine': 'future_composer'}),
        freq_table=song.freq_table,
        instruments=[_instrument_to_usf(i) for i in song.instruments
                     if any(i.raw)],
        subtunes=[_subtune_to_usf(s, song) for s in song.subtunes],
    )

def _subtune_to_usf(sub: Subtune, song: FCSong) -> MusicSubtune:
    return MusicSubtune(
        id=sub.id, tempo=sub.speedbyte + 1, is_sfx=sub.is_sfx,
        voices=[_voice_to_usf(sub, v, song) for v in range(3)],
    )

def _voice_to_usf(sub, voice_idx, song) -> VoiceBlock:
    seq = find_seq(sub, voice_idx, song.sequences)
    # Walk seq.commands; expand transposes+repeats into per-note rows
    # Collect distinct (pattern_id, applied_transpose) combinations
    # → one USF pattern per unique combination
    # Build orderlist as list of USF pattern ids in play order
    ...
```

## Open issues for the next session

1. **Decompose `fc_fx1`/`fx2`/`fx3`** — requires per-frame trace
   focused on each fx-flag bit. Until done, the schema violates §7.
2. **Validate transpose-expansion** — does it actually produce a
   bit-exact-equivalent USF? Need round-trip test once extract + composer
   exist.
3. **`voiceinc` musical meaning** — name it after we understand it.
4. **Per-pattern length** — derive from sum of note row durations (USF
   convention); make sure FC's chained `PatSetLength` summing produces
   correct values.
5. **`PatNoGlide` representation** — currently absence of `glide=N` ≡
   no-glide. Confirm this is sufficient or whether explicit
   `no_glide` flag is needed.
6. **Pattern-pointer table size** — FC has 64 entries at $8409 (54
   referenced by sequences); ensure USF pattern IDs map cleanly.

## Cross-engine sanity check

Before implementing this schema, sketch how it would handle:
- A second FC tune from a different composer (Bjerregaard variant?)
- A Deenen-MoN tune (Noisy Pillars)
- An FC V4 editor tune (which the V4.1 manual documents differently)

If any of these surface new musical concepts that this schema can't
hold, the schema needs revision before extract code is written. This
is the "informed by structural diversity" check the deferred
composer-unification work argues for.
