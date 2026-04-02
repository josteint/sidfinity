# Universal Symbolic Format (USF) Specification

**Version:** 0.6 (2026-04-02)
**Status:** Draft — data roundtrip validated on 2690 GT2 files, player behavior groups detected

## Purpose

USF is the intermediate representation between any C64 SID player's native format and the SIDfinity player output. It also serves as the tokenization format for ML training.

```
  DMC SID ──→ USF ──→ SIDfinity SID
  GT2 SID ──→ USF ──→ SIDfinity SID
  JCH SID ──→ USF ──→ SIDfinity SID
  ...
```

USF must be expressive enough to represent any feature used by any supported player. When a new player uses a feature USF can't represent, USF must be extended — and all converters updated (see Sync Rules).

## Design Goals

- **Compact**: A 3-minute tune ≈ 2000–4000 tokens
- **Event-based**: Durations attached to events, not grid/frame-based
- **Explicit structure**: Instruments defined once, patterns reused via orderlists
- **Fixed vocabulary**: ~300 tokens for transformer tokenization
- **Lossless for supported features**: roundtrip through USF preserves register output

## Data Structures

### Song

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| title | string | '' | Song title |
| author | string | '' | Author name |
| sid_model | string | '6581' | SID chip: '6581' or '8580' |
| clock | string | 'PAL' | Clock: 'PAL' or 'NTSC' |
| tempo | int | 6 | Default speed: frames per tick |
| instruments | list[Instrument] | [] | Instrument definitions |
| patterns | list[Pattern] | [] | Pattern definitions |
| orderlists | list×3 of list[(pat_id, transpose)] | [[],[],[]] | Per-voice play order |
| speed_table | list[SpeedTableEntry] | [] | Shared vibrato/portamento/funktempo data |
| shared_wave_table | list[(int,int)] | [] | Shared wave table: (left_byte, right_byte) pairs |
| shared_pulse_table | list[(int,int)] | [] | Shared pulse table: (left_byte, right_byte) pairs |
| shared_filter_table | list[(int,int)] | [] | Shared filter table: (left_byte, right_byte) pairs |
| freq_lo | bytes\|None | None | Custom freq table lo (96 bytes), None=PAL |
| freq_hi | bytes\|None | None | Custom freq table hi (96 bytes), None=PAL |
| first_note | int | 0 | First note in freq table (GT2 FIRSTNOTE optimization) |
| gt2_player_group | string | '' | Player behavior group: 'A', 'B', 'C', 'D' (see below) |
| ad_param | int | 0x0F | Hard restart AD value (SID $D405). Detected from player binary. *GT2-specific.* |
| sr_param | int | 0x00 | Hard restart SR value (SID $D406). Detected from player binary. *GT2-specific.* |

**Player behavior group (GT2 only):** The GT2 player has 4 behavior groups that produce audibly different output from the same song data. The group determines ADSR write order, new-note register behavior, and vibrato handling. See `docs/gt2_player_versions.md` for full details.

| Group | GT2 Versions | Key Behavior |
|-------|-------------|--------------|
| A | 2.65-2.67 | AD-before-SR writes, new-note writes all regs |
| B | 2.68-2.72 | SR-before-AD writes, new-note writes wave-only |
| C | 2.73-2.74 | B + ghost register support |
| D | 2.76-2.77 | C + vibrato parameter fix |

**Shared tables:** GT2 uses shared wave/pulse/filter tables where multiple instruments reference positions in a single array via pointer indices (wave_ptr, pulse_ptr, filter_ptr). Instruments can share suffixes, prefixes, or even have loop commands that point into other instruments' data. The shared table preserves this layout exactly. Each entry is a (left_byte, right_byte) pair. **Wave table** entries are stored in .sng-equivalent format (pre-transform), NOT the packed binary format. The encoder re-applies the packed format transforms (left column +$10 for NOWAVEDELAY=0, right column XOR $80) when building the SID binary. Pulse and filter tables currently store packed format values (transform cleanup is planned).

### Instrument

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | int | 0 | Instrument index |
| ad | int | 0x09 | Attack/Decay (SID $D405) |
| sr | int | 0x00 | Sustain/Release (SID $D406) |
| waveform | string | 'pulse' | Primary waveform: tri, saw, pulse, noise |
| first_wave | int | -1 | First-frame waveform override (-1=derive from waveform) |
| gate_timer | int | 2 | Hard restart lead time in frames (0-63) |
| hr_method | string | 'gate' | HR method: none, gate, test, adsr |
| legato | bool | False | No ADSR retrigger on new notes |
| vib_speed_idx | int | 0 | Speed table index for instrument vibrato (0=none) |
| vib_delay | int | 0 | Vibrato delay in frames |
| pulse_ptr | int | 0 | Pulse table index (0=no pulse modulation) |
| filter_ptr | int | 0 | Filter table index (0=no filter modulation) |
| wave_table | list[WaveTableStep] | [] | Per-frame waveform program |
| pulse_table | list[PulseTableStep] | [] | Pulse width modulation program |
| filter_table | list[FilterTableStep] | [] | Filter modulation program |
| pulse_width | int | 0x0808 | Initial pulse width (16-bit) |

**Note:** `pulse_ptr` and `filter_ptr` are raw table indices used by the GT2 player to reference shared pulse/filter tables. They are set by pattern commands (cmd 9, cmd A) and stored per-instrument for the initial value. When USF includes inline `pulse_table`/`filter_table`, these pointers are redundant. Both representations coexist for roundtrip fidelity with GT2.

### WaveTableStep

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| waveform | int | 0x41 | SID waveform byte (bits 7-4: wave, 3-0: gate/sync/ring/test) |
| note_offset | int | 0 | Relative semitone offset from current note |
| absolute_note | int | -1 | If ≥0: absolute note (overrides note_offset) |
| is_loop | bool | False | This is a loop/jump command |
| loop_target | int | 0 | Loop destination (step index within this instrument's WT) |
| delay | int | 0 | Delay N frames before this step (.sng: $01-$0F) |
| keep_freq | bool | False | Don't change frequency (.sng right=$80, packed right=$00) |

### PulseTableStep

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| is_set | bool | False | True=set pulse width, False=modulate |
| value | int | 0 | Set: PW high nib. Modulate: signed speed. |
| low_byte | int | 0 | Set: PW low byte |
| duration | int | 1 | Modulate: frame count |
| is_loop | bool | False | Loop command |
| loop_target | int | 0 | Loop destination step index |

### FilterTableStep

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| type | string | 'cutoff' | 'cutoff', 'modulate', 'params', 'loop' |
| value | int | 0 | Cutoff value, signed speed, or resonance<<4\|routing |
| duration | int | 1 | Modulation frame count |
| is_loop | bool | False | Loop command |
| loop_target | int | 0 | Loop destination step index |

### SpeedTableEntry

Shared table for vibrato, portamento, and funktempo. Referenced by index from instruments and pattern commands.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| left | int | 0 | Vibrato: speed (bit7=note-independent). Portamento: MSB. Funktempo: tempo1. |
| right | int | 0 | Vibrato: depth. Portamento: LSB. Funktempo: tempo2. |

### NoteEvent

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| type | string | 'note' | note, rest, off, on, tie |
| note | int | 0 | Note number 0–95 (C0=0, C4=48) |
| duration | int | 1 | Duration in ticks |
| instrument | int | -1 | Instrument index (-1=no change) |
| command | int\|None | None | Pattern command 0–15, or None for no command |
| command_val | int | 0 | Command parameter byte |

**Important:** `command=None` and `command=0` are distinct. `None` means no effect processing on this row. `command=0` means "effect 0" (instrument vibrato reload in GT2), which actively triggers vibrato parameter loading. The GT2 packed format encodes `command=0` as an FX/FXONLY byte ($40/$50), while `command=None` emits no FX byte.

### Pattern Commands

| Cmd | Token | Name | Param |
|-----|-------|------|-------|
| 0 | — | None / inst vibrato | — |
| 1 | x1 | Portamento up | speed table index |
| 2 | x2 | Portamento down | speed table index |
| 3 | x3 | Tone portamento | speed table index ($00=tie) |
| 4 | x4 | Vibrato | speed table index |
| 5 | x5 | Set AD | value |
| 6 | x6 | Set SR | value |
| 7 | x7 | Set waveform | waveform byte |
| 8 | x8 | Set wave ptr | wave table index |
| 9 | x9 | Set pulse ptr | pulse table index |
| A | xA | Set filter ptr | filter table index |
| B | xB | Set filter ctrl | resonance(hi) \| routing(lo) |
| C | xC | Set filter cutoff | cutoff value |
| D | xD | Set master volume | $00–$0F |
| E | xE | Funktempo | speed table index |
| F | xF | Set tempo | $03–$7F=global, $83–$FF=channel |

### Event Types

| Type | Meaning |
|------|---------|
| note | Play note. Sets frequency, triggers ADSR (unless legato). |
| rest | Silence — no change, duration advances. |
| off | Gate off — release current note. |
| on | Gate on — retrigger without changing frequency. |
| tie | Continue previous note without retriggering ADSR. |

## Token Format

### Grammar

```
song         := SONG header instruments speed_table? patterns orderlists /SONG
header       := sid_model clock tempo
sid_model    := SID_6581 | SID_8580
clock        := PAL | NTSC
tempo        := T<1-99>

instruments  := instrument*
instrument   := INST params tables /INST
params       := AD<HH> SR<HH> waveform hr gate_timer legato? vibrato? first_wave?
waveform     := TRI | SAW | PUL | NOI
hr           := HR_NONE | HR_GATE | HR_TEST | HR_ADSR
gate_timer   := GT<H>
legato       := LEG
vibrato      := VIB<H> VD<H>
first_wave   := FW<HH>

tables       := wave_table? pulse_table? filter_table?
wave_table   := WT[ wt_step+ ]WT
wt_step      := L<idx>                     loop
             | W<n>                         delay n frames
             | <WAVE>~                      keep freq
             | <WAVE>=<note>                absolute note
             | <WAVE><sign><offset>         relative note
             | $<HH><sign><offset>          raw waveform byte + relative
pulse_table  := PT[ pt_step+ ]PT
pt_step      := L<idx> | =<HHHH> | m<sign><n>x<dur>
filter_table := FT[ ft_step+ ]FT
ft_step      := L<idx> | C<HH> | R<HH> | m<sign><n>x<dur>

speed_table  := SPD[ <HHHH>+ ]SPD

patterns     := pattern*
pattern      := PAT<id> event* /PAT
event        := inst_change? (note|rest|off|on|tie) command? duration?
inst_change  := I<n>
note         := <note_name>
rest         := .
off          := OFF
on           := ON
tie          := TIE
command      := x<H><HH>                    command + param
duration     := d<n>                         (omit if 1)

orderlists   := ORD voice voice voice /ORD
voice        := V<1-3> order_entry* /V<1-3>
order_entry  := transpose? P<pattern_id>
transpose    := T<signed>
```

Where `<H>` = hex digit, `<HH>` = 2 hex digits, `<HHHH>` = 4 hex digits, `<n>` = decimal.

## Mapping to SIDfinity Player (GT2)

### Packed Pattern Encoding

| USF | GT2 Packed Byte |
|-----|----------------|
| note N | $60 + N |
| rest | $BD |
| off | $BE |
| on | $BF |
| instrument I | I+1 before note (1-based) |
| command C val V | $40+C before note (FX), or $50+C (FXONLY for rest) |
| duration D | D-1 consecutive $BD after note |
| packed rests | $C0–$FF (256 - count) |

### Instrument Columns

GT2 stores instruments column-major:

| USF Field | GT2 Column |
|-----------|-----------|
| ad | mt_insad |
| sr | mt_inssr |
| wave_table[0] → wave_ptr | mt_inswaveptr (1-based index into global wave table) |
| pulse_table[0] → pulse_ptr | mt_inspulseptr |
| filter_table[0] → filter_ptr | mt_insfiltptr |
| vib_speed_idx | mt_insvibparam |
| vib_delay | mt_insvibdelay |
| gate_timer \| (legato<<6) \| (no_hr<<7) | mt_insgatetimer |
| first_wave (or derived) | mt_insfirstwave |

### Wave Table

GT2 wave table = two parallel columns (left + right), shared across instruments. Each instrument's `wave_ptr` indexes into the global table (1-based).

**Values are stored in .sng-equivalent format** (pre-transform, musical intent), NOT the packed binary format. The GT2 packer (greloc.c) applies two transforms when building packed binaries:

1. **Left column:** Waveforms $10-$DF get +$10 added (only when NOWAVEDELAY=0, to make room for delay values $01-$0F). Silent waves $E0-$EF are masked to low nibble then +$10.
2. **Right column:** Non-command, non-jump entries are XOR $80 (flips the relative/absolute bit).

The encoder (usf_to_sid.py) re-applies these transforms. The parser (gt2_to_usf.py) reverses them.

| USF WaveTableStep | .sng Left | .sng Right |
|-------------------|-----------|------------|
| waveform + note_offset | waveform byte ($10-$DF) | $00-$5F (up) or $60-$7F (down, signed offset) |
| waveform + absolute_note | waveform byte ($10-$DF) | $81-$DF (absolute note = right - $80) |
| waveform + keep_freq | waveform byte ($10-$DF) | $80 |
| delay N | $01-$0F | (same right column encoding) |
| wave command | $F0-$FE (command + table index) | parameter (no XOR) |
| silent wave | $E0-$EF | (same right column encoding) |
| loop → target | $FF | target (1-based global, no XOR) |

### Pulse Table

| USF PulseTableStep | GT2 Left | GT2 Right |
|--------------------|----------|-----------|
| set PW | $80+ (high nib) | low byte |
| modulate speed for dur | duration ($01-$7F) | signed speed |
| loop → target | $FF | target (1-based) |

### Filter Table

| USF FilterTableStep | GT2 Left | GT2 Right |
|---------------------|----------|-----------|
| set cutoff | $00 | cutoff value |
| set params | $80+ | resonance<<4 \| routing |
| modulate for dur | duration ($01-$7F) | signed speed |
| loop → target | $FF | target (1-based) |

### Speed Table

Stored as-is: array of (left, right) byte pairs.

### Orderlist

| USF | GT2 |
|-----|-----|
| (pat_id, 0) | pat_id byte |
| (pat_id, +N) | $F0+N, then pat_id |
| (pat_id, -N) | $E0+(16-N), then pat_id |
| end + loop | $FF, $00 |

## Implementation Files

| File | Role | Status |
|------|------|--------|
| `src/usf.py` | Data structures, tokenize/detokenize | ✅ v0.3 |
| `src/gt2_to_usf.py` | GoatTracker V2 → USF | 🔧 needs table extraction |
| `src/dmc_to_usf.py` | DMC → USF | 🔧 needs command mapping |
| `src/usf_to_sid.py` | USF → SIDfinity .sid | 🔧 needs pulse/filter/speed/command support |
| `src/sidfinity_packer.py` | Pack data with GT2 player | 🔧 needs pulse/filter/speed table packing |
| `docs/usf_spec.md` | This spec | ✅ v0.3 |

## Sync Rules

When USF changes (new fields, event types, token types):

1. Update `src/usf.py` — dataclasses + tokenize() + detokenize()
2. Update `docs/usf_spec.md` — this document
3. Update ALL `*_to_usf.py` converters — emit the new data
4. Update `src/usf_to_sid.py` — consume the new data
5. Update `src/sidfinity_packer.py` — if new assembly defines needed
6. Update player assembly — if player needs new capabilities
7. Run roundtrip test — verify no regression

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-03 | Initial: notes, instruments, wave tables, orderlists |
| 0.2 | 2026-03-31 | Spec doc created. Custom freq tables, tempo pass-through. |
| 0.3 | 2026-03-31 | Full GT2 coverage: pulse/filter/speed tables, pattern commands 0–F, instrument vibrato, legato, first_wave, wave table delay/keep_freq. |
| 0.6 | 2026-04-02 | Player behavior groups (A-D), first_note field. GT2 player version detection. |
| 0.7 | 2026-04-02 | Wave table stores .sng-equivalent values (pre-transform). Left column: reversed +$10 offset (NOWAVEDELAY). Right column: reversed XOR $80. Encoder re-applies transforms. Fixed detect_flags wave command range ($F0-$FE, was incorrectly $E0-$EF). |
