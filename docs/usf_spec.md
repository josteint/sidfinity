# Universal Symbolic Format (USF) Specification

**Version:** 0.9 (2026-04-09)
**Status:** Draft — 1,688/3,478 GT2 SIDs Grade A through USF pipeline. Player behavior fields may be stripped for ML training (see CLAUDE.md).

## Purpose

USF is the intermediate representation between any C64 SID player's native format and the SIDfinity player output. It also serves as the tokenization format for ML training.

```
  DMC SID ──→ USF ──→ SIDfinity SID
  GT2 SID ──→ USF ──→ SIDfinity SID
  JCH SID ──→ USF ──→ SIDfinity SID
  ...
```

USF must be expressive enough to represent any feature used by any supported player. When a new player uses a feature USF can't represent, USF must be extended — and all converters updated (see Sync Rules).

## Roundtrip Pipeline

The full pipeline validates that USF preserves the musical content of a SID file:

```
Original SID
    |
    v
siddump (libsidplayfp emulation)
    |  register CSV: per-frame $D400-$D418 values
    v
sidxray decompiler (src/gt2_decompile.py, etc.)
    |  identifies player engine, extracts instruments/patterns/orderlists
    v
USF (src/usf.py Song object)
    |  intermediate representation: dataclasses, tokens, or JSON
    v
sidfinity_packer (src/sidfinity_packer.py)
    |  packs USF into binary data + player assembly
    v
Rebuilt SID (.sid file with 6502 player)
    |
    v
siddump (re-emulate rebuilt SID)
    |  register CSV from rebuilt SID
    v
Register comparison (tolerant: ignores inaudible differences)
    |  pass/fail per frame
    v
Audibility grade: A (identical) / B (minor) / C (audible diffs) / F (broken)
```

**Validated:** 2690 GT2 files through decompile-to-USF path. Packer roundtrip validated on subset with register comparison.

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
| orderlists | list x 3 of list[(pat_id, transpose)] | [[],[],[]] | Per-voice play order |
| orderlist_restart | list[int] x 3 | [0,0,0] | Per-voice loop-back point as pattern entry index (0-based into orderlist, not byte offset) |
| speed_table | list[SpeedTableEntry] | [] | Shared vibrato/portamento/funktempo data |
| shared_wave_table | list[(int,int)] | [] | Shared wave table: packed binary (left_byte, right_byte) pairs |
| shared_pulse_table | list[(int,int)] | [] | Shared pulse table: packed binary (left_byte, right_byte) pairs |
| shared_filter_table | list[(int,int)] | [] | Shared filter table: packed binary (left_byte, right_byte) pairs |
| freq_lo | bytes\|None | None | Custom freq table lo (96 bytes), None=PAL. *GT2-specific.* |
| freq_hi | bytes\|None | None | Custom freq table hi (96 bytes), None=PAL. *GT2-specific.* |
| first_note | int | 0 | First playable note index in freq table. GT2 FIRSTNOTE optimization: notes below this are silent. The freq table only contains entries from first_note to 95, saving memory. *GT2-specific.* |
| gt2_player_group | string | '' | Player behavior group: 'A', 'B', 'C', 'D' (see below). *GT2-specific — kept for provenance, not used by player.* |
| adsr_write_order | string | 'sr_first' | ADSR register write order during hard restart and new-note init: 'ad_first' or 'sr_first' |
| loadregs_adsr_order | string | 'sr_first' | ADSR write order in per-frame buffered register writes: 'ad_first' or 'sr_first' |
| newnote_reg_scope | string | 'all_regs' | Registers written on new-note frame: 'all_regs' (buffered) or 'wave_only' (non-buffered) |
| ghost_regs | string | 'none' | Shadow register buffer mode: 'none', 'full', or 'zp' |
| vibrato_param_fix | bool | false | Zero vibrato param when instrument has no vibrato but pattern command does |
| ext_audio_in | bool | false | True if song uses external audio input (filter routing bit 3 set in any filter table step or pattern command 0xB) |

**Player behavior fields:** These 5 fields control how the SIDfinity player processes audio. They are **generic** — not tied to any specific source format. Any transpiler (GT2, DMC, JCH) populates them based on the source player's behavior. The SIDfinity player reads them at assembly time via `-D` flags.

| Field | What it controls | GT2 Group A | GT2 Group B | GT2 Group C | GT2 Group D |
|-------|-----------------|-------------|-------------|-------------|-------------|
| adsr_write_order | HR + new-note ADSR order | ad_first | sr_first | sr_first | sr_first |
| loadregs_adsr_order | Per-frame buffered write ADSR order | ad_first | sr_first | ad_first | sr_first |
| newnote_reg_scope | New-note frame register scope | all_regs | all_regs* | all_regs* | all_regs* |
| ghost_regs | Shadow buffer mode | none | none | none/full/zp | none/full/zp |
| vibrato_param_fix | Zero stale vibrato param | false | false | false | true |

\* Groups B/C/D use `wave_only` when BUFFEREDWRITES=0, but most files use BUFFEREDWRITES=1 (`all_regs`). Detection of BUFFEREDWRITES is TODO.

**gt2_player_group** is retained for provenance (knowing which GT2 version created the file) but the player does NOT read it — it reads the 5 behavioral fields instead. This means non-GT2 formats can set the behavioral fields directly without needing a GT2 group label.

**Shared tables (GT2-specific):** GT2 uses shared wave/pulse/filter tables where multiple instruments reference positions in a single array via pointer indices (wave_ptr, pulse_ptr, filter_ptr). Instruments can share suffixes, prefixes, or even have loop commands that point into other instruments' data. The shared table preserves this layout exactly. Each entry is a (left_byte, right_byte) pair storing the **packed binary format bytes** as they appear in the GT2 data -- not decoded USF objects. The encoding of each byte pair depends on the table type (see Wave Table, Pulse Table, Filter Table sections below for the binary layout). This means the shared tables are opaque byte arrays that the packer writes directly, while the per-instrument `wave_table`/`pulse_table`/`filter_table` lists contain decoded USF step objects used for ML training and human inspection.

**orderlist_restart:** When a song loops, each voice restarts from a specific point in its orderlist. The `orderlist_restart` value is a 0-based index into the orderlist array (counting pattern entries), not a byte offset. For example, if voice 1's orderlist is `[(0,0), (1,0), (2,0)]` and `orderlist_restart[0] = 1`, the voice loops back to the second entry `(1,0)` after reaching the end.

### Instrument

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | int | 0 | Instrument index |
| ad | int | 0x09 | Attack/Decay (SID $D405) |
| sr | int | 0x00 | Sustain/Release (SID $D406) |
| waveform | string | 'pulse' | Primary waveform: tri, saw, pulse, noise |
| first_wave | int | -1 | First-frame waveform override (-1=derive from waveform). GT2: `mt_insfirstwave` byte. *GT2-specific encoding.* |
| gate_timer | int | 2 | Hard restart lead time in frames (0-63) |
| hr_method | string | 'gate' | HR method: none, gate, test, adsr |
| legato | bool | False | No ADSR retrigger on new notes |
| wave_ptr | int | 0 | Index into shared wave table (0=none, 1-based). *GT2-specific.* |
| vib_speed_idx | int | 0 | Speed table index for instrument vibrato (0=none) |
| vib_delay | int | 0 | Vibrato delay in frames |
| pulse_ptr | int | 0 | Pulse table index (0=no pulse modulation). *GT2-specific.* |
| filter_ptr | int | 0 | Filter table index (0=no filter modulation). *GT2-specific.* |
| wave_table | list[WaveTableStep] | [] | Per-frame waveform program (decoded steps for ML/inspection) |
| pulse_table | list[PulseTableStep] | [] | Pulse width modulation program (decoded steps) |
| filter_table | list[FilterTableStep] | [] | Filter modulation program (decoded steps) |
| pulse_width | int | 0x0808 | Initial pulse width (16-bit) |

**Note:** `wave_ptr`, `pulse_ptr`, and `filter_ptr` are raw 1-based table indices used by the GT2 player to reference shared wave/pulse/filter tables. They are set per-instrument for the initial value and can be changed at runtime by pattern commands (cmd 8, cmd 9, cmd A). When USF includes inline `wave_table`/`pulse_table`/`filter_table`, these pointers are redundant for playback but required for binary-identical GT2 roundtrip. Both representations coexist: pointers for the packer, decoded step lists for ML and inspection.

**GT2-specific vs universal fields:** Fields marked *GT2-specific* exist to support lossless roundtrip with GoatTracker V2's binary format. When importing from other players (DMC, JCH), these fields use their defaults. Universal fields (ad, sr, waveform, gate_timer, hr_method, legato, wave_table, pulse_table, filter_table, pulse_width) apply to all source players.

### WaveTableStep

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| waveform | int | 0x41 | SID waveform byte (bits 7-4: wave, 3-0: gate/sync/ring/test) |
| note_offset | int | 0 | Relative semitone offset from current note |
| absolute_note | int | -1 | If ≥0: absolute note (overrides note_offset) |
| is_loop | bool | False | This is a loop/jump command |
| loop_target | int | 0 | Loop destination (step index within this instrument's WT) |
| delay | int | 0 | Delay N frames before this step (GT2: $01-$0F) |
| keep_freq | bool | False | Don't change frequency (GT2 packed: right=$00, player skips freq) |

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

When `type='params'`, the value byte maps to SID register $D417:
- Bits 7-4: resonance (0-15)
- Bit 3: external audio input (EXT IN) filter enable
- Bit 2: voice 3 filter enable
- Bit 1: voice 2 filter enable
- Bit 0: voice 1 filter enable

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
| B | xB | Set filter ctrl | resonance(hi) \| routing(lo). Routing: bit0=v1, bit1=v2, bit2=v3, bit3=EXT IN |
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

| USF WaveTableStep | GT2 Left | GT2 Right |
|-------------------|----------|-----------|
| waveform + note_offset | waveform byte | $00-$5F (up) or $60-$7F (down, signed) |
| waveform + absolute_note | waveform byte | $81-$DF (absolute) |
| waveform + keep_freq | waveform byte | $80 |
| delay N | $01-$0F | $00 |
| loop → target | $FF | target (1-based global) |

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
| `src/usf.py` | Data structures, tokenize/detokenize | ✅ v0.7 |
| `src/gt2_to_usf.py` | GoatTracker V2 → USF | 🔧 needs table extraction |
| `src/dmc_to_usf.py` | DMC → USF | 🔧 needs command mapping |
| `src/usf_to_sid.py` | USF → SIDfinity .sid | 🔧 needs pulse/filter/speed/command support |
| `src/sidfinity_packer.py` | Pack data with GT2 player | 🔧 needs pulse/filter/speed table packing |
| `docs/usf_spec.md` | This spec | ✅ v0.7 |

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
| 0.7 | 2026-04-02 | Add wave_ptr to Instrument, orderlist_restart to Song, document shared table packed binary format, annotate GT2-specific vs universal fields, add Roundtrip Pipeline section, clarify first_note semantics. |
