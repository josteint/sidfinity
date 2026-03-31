# Universal Symbolic Format (USF) Specification

**Version:** 0.2 (2026-03-31)
**Status:** Draft — evolving as we add player support

## Purpose

USF is the intermediate representation between any C64 SID player's native format and the SIDfinity player output. It also serves as the tokenization format for ML training.

All conversions go through USF:

```
  DMC SID ──→ USF ──→ SIDfinity SID
  GT2 SID ──→ USF ──→ SIDfinity SID
  JCH SID ──→ USF ──→ SIDfinity SID
  ...
```

USF must be expressive enough to represent any feature used by any supported player. When a new player uses a feature USF can't represent, USF must be extended — and all converters updated.

## Design Goals

- **Compact**: A 3-minute tune ≈ 2000–4000 tokens
- **Event-based**: Durations attached to events, not grid/frame-based
- **Explicit structure**: Instruments defined once, patterns reused, orderlists reference patterns
- **Fixed vocabulary**: ~300 tokens for transformer tokenization
- **Lossless for supported features**: USF→SID should reproduce the same register output as the original

## Data Structures

### Song

Top-level container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| title | string | '' | Song title |
| author | string | '' | Author name |
| sid_model | string | '6581' | SID chip model: '6581' or '8580' |
| clock | string | 'PAL' | System clock: 'PAL' or 'NTSC' |
| tempo | int | 6 | Default speed: frames per tick |
| instruments | list[Instrument] | [] | Instrument definitions |
| patterns | list[Pattern] | [] | Pattern definitions |
| orderlists | list[list[tuple]] | [[], [], []] | 3 voices, each a list of (pattern_id, transpose) |
| freq_lo | bytes\|None | None | Custom frequency table lo (96 bytes), None = PAL default |
| freq_hi | bytes\|None | None | Custom frequency table hi (96 bytes), None = PAL default |

### Instrument

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | int | 0 | Instrument index |
| ad | int | 0x09 | Attack/Decay byte (SID $D405 format) |
| sr | int | 0x00 | Sustain/Release byte (SID $D406 format) |
| waveform | string | 'pulse' | Primary waveform: 'tri', 'saw', 'pulse', 'noise' |
| gate_timer | int | 2 | Hard restart lead time in frames |
| hr_method | string | 'gate' | Hard restart method: 'none', 'gate', 'test', 'adsr' |
| wave_table | list[WaveTableStep] | [] | Per-frame waveform program |
| pulse_width | int | 0x0808 | Initial pulse width (16-bit) |

### WaveTableStep

One frame of the wave table program.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| waveform | int | 0x41 | SID waveform register value (bits 7-4: wave, bits 3-0: gate/sync/ring/test) |
| note_offset | int | 0 | Relative semitone offset from current note |
| absolute_note | int | -1 | If ≥ 0: absolute note number (overrides note_offset) |
| is_loop | bool | False | If True: this is a loop command |
| loop_target | int | 0 | Loop destination (step index within this instrument's wave table) |

### NoteEvent

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| type | string | 'note' | Event type: 'note', 'rest', 'off', 'on', 'tie' |
| note | int | 0 | Note number 0–95 (C0=0, C1=12, ..., B7=95) |
| duration | int | 1 | Duration in ticks |
| instrument | int | -1 | Instrument index (-1 = no change) |

### Pattern

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | int | 0 | Pattern index |
| events | list[NoteEvent] | [] | Sequence of events |

### Event Types

| Type | Meaning |
|------|---------|
| `note` | Play note with current instrument. Sets frequency, triggers ADSR. |
| `rest` | Silence — no frequency change, no gate trigger. Duration advances. |
| `off` | Gate off — release current note. |
| `on` | Gate on — retrigger without changing frequency. |
| `tie` | Continue previous note without retriggering ADSR. |

### Orderlist Entry

Each voice's orderlist is a list of `(pattern_id, transpose)` tuples:
- `pattern_id`: Index into the song's pattern list
- `transpose`: Semitone offset applied to all notes in this pattern instance (signed int)

## Token Format

For ML training and text serialization. Vocabulary ≈ 300 tokens.

### Grammar

```
song        := SONG header instruments patterns orderlists /SONG
header      := sid_model clock tempo
sid_model   := SID_6581 | SID_8580
clock       := PAL | NTSC
tempo       := T<1-32>

instruments := instrument*
instrument  := INST params wave_table? /INST
params      := AD<00-FF> SR<00-FF> waveform hr_method gate_timer
waveform    := TRI | SAW | PUL | NOI
hr_method   := HR_NONE | HR_GATE | HR_TEST | HR_ADSR
gate_timer  := GT<0-F>
wave_table  := WT[ wt_step+ ]WT
wt_step     := wt_wave | wt_loop
wt_wave     := <WAVE><sign><offset>     (relative: PUL+0, SAW-3)
             | <WAVE>=<note_name>        (absolute: TRI=C4)
wt_loop     := L<target_index>

patterns    := pattern*
pattern     := PAT<id> event* /PAT
event       := inst_change? (note | rest | off | on | tie) duration?
inst_change := I<0-255>
note        := <note_name>               (C0, C#4, G7, etc.)
rest        := .
off         := OFF
on          := ON
tie         := TIE
duration    := d<1-32>                   (omit if duration=1)

orderlists  := ORD voice voice voice /ORD
voice       := V<1-3> order_entry* /V<1-3>
order_entry := transpose? P<pattern_id>
transpose   := T<signed_int>            (T+5, T-3, etc.)
```

### Note Names

96 notes: C0 C#0 D0 D#0 ... B0 C1 ... B7

| Note | Number | SID Freq Hi (PAL) |
|------|--------|-------------------|
| C0 | 0 | $01 |
| C4 | 48 | $11 |
| A4 | 57 | $1D |
| C7 | 84 | $45 |

## Mapping to SIDfinity Player (GT2)

USF maps to the GoatTracker V2 packed format used by the SIDfinity player:

| USF | GT2 Packed |
|-----|-----------|
| note N | $60 + N |
| rest | $BD |
| off | $BE |
| on | $BF |
| duration D | D-1 consecutive $BD bytes after the note |
| instrument I | byte I+1 before the note (1-based) |
| packed rest run | $C0–$FF (256 - count) |

### Wave Table Encoding

GT2 wave table has two parallel columns:
- **Left column** (waveform): raw SID waveform byte. $FF = loop marker.
- **Right column** (note): $80+ = relative offset from current note. $01–$7F = absolute note. $00 = no change. When left=$FF, right = loop target (1-based global index).

### Orderlist Encoding

GT2 orderlists are byte sequences:
- $00–$EF: pattern number
- $F0–$FE: transpose ($F0 + semitones for positive, $E0 + (16 + semitones) for negative)
- $FF $00: loop to start

## Implementation Files

| File | Role | Direction |
|------|------|-----------|
| `src/usf.py` | Data structures, tokenize/detokenize | Core |
| `src/gt2_to_usf.py` | GoatTracker V2 → USF | Input |
| `src/dmc_to_usf.py` | DMC → USF | Input |
| `src/usf_to_sid.py` | USF → SIDfinity .sid | Output |
| `src/sidfinity_packer.py` | Pack USF data with GT2 player | Output |

## Sync Rules

When USF changes (new fields, new event types, new token types):

1. **Update `usf.py`**: dataclasses, tokenize(), detokenize()
2. **Update this spec**: add the new feature to the tables above
3. **Update all `*_to_usf.py` converters**: emit the new data where applicable
4. **Update `usf_to_sid.py`**: consume the new data and map to GT2 format
5. **Update `sidfinity_packer.py`**: if new player features are needed
6. **Update `player/sidfinity_gt2.asm`**: if the player needs new capabilities
7. **Run GT2→USF→SID roundtrip test**: verify no regression

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-03 | Initial: notes, instruments, wave tables, orderlists |
| 0.2 | 2026-03-31 | Spec doc created. Added custom freq tables, tempo pass-through. |

## Known Limitations (to address)

- No pulse width modulation table support (instruments have initial PW only)
- No filter table support
- No vibrato parameters
- No speed/funk tempo changes within a song
- No portamento/glide effects
- No multi-speed support
- Tempo is global, not per-pattern or per-voice
- No sample/digi support
