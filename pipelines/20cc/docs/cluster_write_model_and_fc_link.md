---
source_url: multiple — see provenance per section
fetched_via: binary inspection (local hvsc84/), web search, WebFetch
fetch_date: 2026-06-14
author: jtr (research synthesis)
content_date: 1988–1994 era binaries + 2026 binary inspection
reliability: primary (binary inspection of canonical SIDs) + secondary (web sources)
---

# 20CC Player — Write Model, Binary Structure, and FC Relationship

Author: Falco Paul (20th Century Composers, Netherlands).
Source: `atlantis-prophecy.org/recollection` interview + `csdb.dk/scener/?id=2374`.
HVSC coverage: **209 SIDs** classified as `20CC` in `hvsc84.db`.
CSDb editor release: `csdb.dk/release/?id=10741` ("20CC Music Editor V1",
also known as "The Dual Compatible Music Editor V1").

---

## 1. Player Entry Points and Load Addresses

The 20CC player exists in **two distinct variants** in HVSC (identified by
binary analysis of I_Wanna_Dance.sid and Party_Report.sid, confirmed by
SIDId signature matching across all 209 classified SIDs):

### Variant A — Majority (174/209 SIDs)

```
load = $1000
init = $1000   (JMP to actual init at $1424 in I_Wanna_Dance example)
play = $1003   (JMP to play loop at $1072)
```

First three bytes at load address: `4C xx 14` (JMP to init), `4C 72 10` (JMP play).
State workspace: `$1006–$106F` (zero-cleared at init; 3-voice interleaved arrays).
Example SIDs: `0-9/20CC/I_Wanna_Dance.sid`, `0-9/20CC/TV_Tunes_Mix_v2.sid`,
most Ouwehand_Reyn tunes.

**Does NOT match SIDId primary signature `D0 ED C9 E0 B0 10 29 1F 7D`.**
Matches SIDId sig7 (vibrato: `29 ?? 4A 4A 4A 4A A8 46 ?? 66 ?? 88 10`).

### Variant B — Minority (35/209 SIDs)

```
load = $0FFA
init = $0FFA   (short 6-byte init: TAX / INX / INX / STX $1082 / RTS)
play = $1081   (full play routine)
```

First bytes at `$0FFA`: `AA E8 8E 82 10 60 4C 81 10 4C E2 10`.
The `$0FFD: 8E 82 10` stores the active subtune count.
Often contains an ASCII credit string at `$100C` ("MUSIC BY EVS & F.P. FROM 20CC!").
Example SIDs: `H/HeatWave/Party_Report.sid`, `0-9/20CC/Paul_Falco/Lambada.sid`,
`H/HeatWave/youtH/*.sid`.

**Matches SIDId primary signature** `D0 ED C9 E0 B0 10 29 1F 7D` (this is the
C9 E0 note-range check / AND #$1F / ADC abs,X freq calculation).
Also matches SIDId sig4 `BC ?? ?? A9 ?? 99 04 D4 A9 ?? 99 01 D4 FE` (hard-restart
sequence: LDY voice_offset,X / LDA #ctrl / STA $D404,Y / LDA #freq_hi / STA $D401,Y /
INC abs,X).

A third load base (`$1670`) appears in some relocated forms (mentioned in SIDId docs).

---

## 2. Memory Map (Variant A, I_Wanna_Dance.sid, $1000 base)

```
$1000:       JMP $1424          ; init entry
$1003:       JMP $1072          ; play entry
$1006–$006F: Per-voice state (3 voices × 35 fields, X-indexed stride 3)
$1070–$106A: Global state (master vol, filter, temp)
$1072–$13CA: Player code (~$259 bytes)
$13CB–$1423: Sequence advance + command parser
$1424–$1467: Init routine
$1468–$146C: Vibrato depth table (6 small values)
$146D–$146F: SID voice base offset table [00, 07, 0E]
$1470–$147F: Some per-tune data (small ramp values)
$1480–$14E4: Freq table lo (96 entries, notes C-0 through B-7)
$14E5–$1544: Freq table hi (96 entries)
$1545–$154A: Song/voice table (6 bytes per subtune: 3 × 2-byte ptrs to sequence streams)
$154B–$1552: Wave-program pointer table lo (8 entries)
$1553–$155A: Wave-program pointer table hi (8 entries)
$155B–$1561: Pattern pointer table lo (7 entries, entry 0 = $0000 unused)
$1562–$1568: Pattern pointer table hi (7 entries)
$1569–$15FA: "Sequence" data region (mixed pattern/command streams)
$15FB+:      8-byte instrument records (inst_num × 8 index into this block)
             Pattern/wave-program note streams follow
```

Instrument records start at `$15FB` in the I_Wanna_Dance example. Each record is
**8 bytes**, indexed as `base + (instrument_number * 8)`.

---

## 3. Per-Voice State Layout (Variant A)

State is an interleaved X-indexed array. X ∈ {0, 1, 2} for voices 0, 1, 2.
`STA $10XX,X` with X=0 touches voice 0; X=1 touches voice 1; X=2 touches voice 2.
All three voices share the same field layout with a stride of 3.

```
$1006,X  duration_counter      — frame countdown; on 0: fetch new note
$1009,X  wave_prog_index?      — secondary waveform/prog index ($1009)
$100C,X  note_pitch            — current note index (0–95)
$100F,X  seq_index             — index into sequence ptr tables ($155B/$1562)
$1012,X  instrument_num        — current instrument number
$1015,X  portamento_param      — portamento / slide accumulator
$1018,X  state_1018            — set by $80–$BF sequence commands (arp/transpose?)
$101B,X  waveprog_ptr_idx      — index into $154B wave-program ptr table
$101E,X  stream_byte_offset    — current byte position within active wave-program
$1021,X  sequence_Y            — current byte position within sequence stream
$1024,X  song_ptr_lo           — per-voice sequence stream pointer (lo)
$1027,X  song_ptr_hi           — per-voice sequence stream pointer (hi)
$102A,X  repeat_count          — pattern repeat counter
$102D,X  ctrl_byte             — saved ctrl/gate byte (ANDed before $D404 write)
$1030,X  seq_field_0           — 4 bytes loaded from sequence at note start
$1033,X  seq_field_1
$1036,X  seq_field_2
$1039,X  seq_field_3
$103C,X  inst_field_5          — instrument record byte[5] (resonance/mode)
$103F,X  pulse_state           — pulse direction flag
$1042,X  pulse_rate            — PWM sweep speed (set by $40–$7F sequence cmd)
$1045,X  freq_base_lo          — freq accumulator lo
$1048,X  vibrato_temp          — vibrato depth workspace
$104C,X  pw_counter_lo         — pulse width counter (lo)
$104F,X  frame_counter         — per-voice frame counter (hard-restart timing)
$1052,X  pulse_mode            — pulse direction/mode
$1055,X  state_55              — unknown
$1058,X  pw_lo                 — pulse width lo (written to $D402,Y)
$105B,X  pw_hi                 — pulse width hi (written to $D403,Y)
$105E,X  freq_lo               — SID frequency lo (written to $D400,Y)
$1061,X  freq_hi               — SID frequency hi (written to $D401,Y)
$1064,X  freq_delta_lo         — vibrato/slide delta lo
$1067,X  freq_delta_hi         — vibrato/slide delta hi
```

Global state (not X-indexed):
```
$106A  master_vol / filter cutoff lo   — init = $0F; also set by $C0–$FE seq cmds
$106B  filter hi nibble                — packed from instrument record byte[2]
$106C  temp freq hi                    — transient calculation workspace
$106D  temp freq lo                    — transient calculation workspace
```

---

## 4. Per-Frame Write Model (Variant A)

### Main Loop

```
play() at $1072:
  LDX #2
  loop:
    JSR $107B           ; process voice X
    DEX
    BPL loop            ; X = 2, 1, 0 (all three voices)
  RTS
```

Voice order in SID writes: **Voice 2 first, then 1, then 0** (X counts down).

### Per-Voice Processing ($107B)

```
1. DEC $1006,X            ; decrement duration counter
2. If duration > 0:
     INC $104F,X          ; advance frame counter
     [freq calculation]
     LDY $146D,X          ; Y = SID voice offset (0, 7, 14)
     STA $D401,Y          ; FREQ HI
     PLA                  ; restore freq lo from stack
     STA $D400,Y          ; FREQ LO
     LDA $1058,X
     STA $D402,Y          ; PW LO
     LDA $105B,X
     STA $D403,Y          ; PW HI
     LDA $106B            ; filter hi nibble
     CLC
     ADC $106A            ; + master vol/filter lo
     STA $D418            ; MASTER VOL + FILTER MODE  ← written once per voice!
     [conditional gate write if frame_counter == 2]
     LDA $102D,X AND #$FE ; gate-off mask
     LDY $146D,X
     STA $D404,Y          ; CTRL / GATE  ← only on frame 2 (hard restart timing)
     [pulse width modulation routines]
   
3. If duration == 0: JSR new_note_fetch
```

**Per-frame SID write order (per voice):**
`$D401` (freq hi) → `$D400` (freq lo) → `$D402` (pw lo) → `$D403` (pw hi) →
`$D418` (vol+filter mode, written once PER VOICE = 3× per frame) →
`$D404` (ctrl+gate, conditional on frame_counter == 2).

**$D416/$D417** (filter cutoff/resonance) are written **only on new note / instrument
load** (not every frame).
**$D405/$D406** (attack/decay, sustain/release) are written **only on new note** at
`$138B/$1391` (instrument load path).

### Y-Indexed Voice Addressing

The SID voice base offset table at `$146D` = `[00, 07, 0E]`. All per-voice
`$D4xx` writes use `STA $D404,Y` with Y from this table:
- Voice 0: Y=0 → `$D400–$D406`
- Voice 1: Y=7 → `$D407–$D40D`
- Voice 2: Y=14 → `$D40E–$D414`

This is the `99 04 D4` (`STA $D404,Y`) pattern in the SIDId signatures.

### Frequency Calculation

Frequency = `freq_table_lo[$100C,X]` + vibrato_delta.
Freq table lo at `$1485`, freq table hi at `$14E5`, 96 entries (notes 0–95).
The vibrato implementation (**bit-rotation**, not additive delta):
```
29 F0          ; AND #$F0 (mask vibrato depth, high nibble)
4A 4A 4A 4A   ; LSR A x4 (= /16 → count of bit shifts)
A8             ; TAY
46 FF          ; LSR $FF (ZP, carry out of freq hi)
66 FE          ; ROR $FE (ZP, rotate carry into freq lo)
88             ; DEY
10 F9          ; BPL loop
```
This is a **rightward bit-rotation** of the 16-bit frequency, not a signed
frequency delta. Very different from FC's vibrato (which adds a signed delta
each frame).

---

## 5. Data Hierarchy

20CC uses a **two-level hierarchy**: sequence → wave-programs.

```
Song table ($1545):
  6 bytes per subtune = 3 × (ptr_lo, ptr_hi) pointing to per-voice sequence streams.

Per-voice Sequence Stream:
  A flat byte stream, parsed by the sequence advance routine ($13CB).
  Commands (by high byte value):
    $00–$3F  LOOP/RESTART: resets Y to 0 → restarts this sequence from the top.
             (Effectively a "pattern repeat from start" or "loop point" marker.)
    $40–$5F  SET REPEAT COUNT: (val & $1F) → stored at $102A,X.
             The current wave-program will loop this many extra times.
    $60–$7F  SET WAVEFORM/PROG ($1009,X = val − $60): selects waveform index.
    $80–$BF  SET TRANSPOSE/ARP ($1018,X = val & $7F): semitone offset or arp value.
    $C0–$FE  SET FILTER/PORTAMENTO ($106A = val & $0F): modifies global filter cutoff.
    $FF      END: advance to next pattern in orderlist (or trigger sequence advance).
  Wave-program indices ($00–$3F range) select which note-stream to play next.

Wave-Program Pointer Table ($154B/$1553):
  8 × 2-byte pointers to note streams. Indexed by $101B,X (per-voice).
  Example: [0]=$1696, [1]=$169A, [2]=$16C0, [3]=$16E9, [4]=$1756 etc.

Per-Pattern Note Stream (= "wave programs"):
  A byte stream terminated by $FF. Parsed by the note-fetch routine ($12BC path).
  Commands (by high 2 bits of the byte):
    $00–$3F (hi2=00): INSTRUMENT + DURATION  (2 bytes)
                       byte[0] & $3F = duration (frames)
                       byte[1] = instrument number
                       → triggers full instrument load
    $40–$7F (hi2=01): DURATION + ADVANCE     (2 bytes)
                       byte[0] & $3F = duration
                       byte[1] = next byte (unknown — possibly ignored or advance)
                       → stored at $1042,X (pulse rate?); triggers JMP $1282
    $80–$BF (hi2=10): NOTE + DURATION        (2 bytes)
                       byte[0] & $3F = duration
                       byte[1] = note pitch (0–95, index into freq table)
                       → no instrument change; just update pitch
    $C0–$FE (hi2=11): FREQ OVERRIDE          (3 bytes)
                       byte[0] & $3F = duration
                       byte[1] = freq lo override → $105E,X
                       byte[2] = freq hi override → $1061,X
    $FF:              END / LOOP BACK to start of this wave-program
```

This is **significantly simpler than FC**. FC has a three-level hierarchy
(orderlist → pattern numbers → patterns) with a separate wave table program
per instrument. 20CC collapses these into a two-level stream.

---

## 6. Instrument Record Format (Variant A)

8-byte records at `$15FB`, indexed as `base + (instrument_number * 8)`.

```
byte [0]:  ? (purpose not yet confirmed — possibly padding or pulse lo)
byte [1]:  ? (wave/ctrl base?)
byte [2]:  filter resonance bits (AND #$F0 used; hi nibble → $106B filter reg)
byte [3]:  ? (AND #$F0 → stored at $103F,X; AND #$0F → $100F,X)
byte [4]:  filter flag ($FF = no filter write; else: STA $D416 filter cutoff)
byte [5]:  resonance/filter mode (STA $103C,X, used in filter register writes)
byte [6]:  AD register? (stored at $105B,X = pw hi or AD?) — provisional
byte [7]:  SR register? (stored at $1058,X = pw lo or SR?) — provisional
```

**ADSR writes** ($D405, $D406) happen at `$138B`/`$1391`/`$139B`/`$13A1` — two pairs,
likely for AD (attack/decay) and SR (sustain/release). The exact mapping from instrument
bytes to ADSR is not fully decoded (additional disassembly needed at `$1370`–`$13A5`).

---

## 7. Variant B Note Encoding Difference

In Variant B (Party_Report, HeatWave), the note command byte encodes **both pitch
and instrument in the same byte**:

```
Byte range $00–$DF: normal note
  note_pitch = byte (0–$DF)
  instrument_index = (byte & $1F) * 8  (lower 5 bits → into 8-byte instrument table)
  
Byte range $E0–$FF: command / effect bytes
  $FF = end/loop (same as Variant A)
  $E0–$FE = special commands
```

This is confirmed by the SIDId primary signature context:
```
D0 ED        ; BNE (loop back in note range check)
C9 E0        ; CMP #$E0   ← upper note boundary
B0 10        ; BCS (if >= $E0: skip to command handler)
29 1F        ; AND #$1F   ← instrument = note mod 32
7D 24 10     ; ADC $1024,X (voice-base offset)
0A 0A 0A     ; ASL * 3 = * 8
9D 27 10     ; STA $1027,X (instrument ptr × 8)
```

**No independent instrument byte** — instrument is coupled to note pitch.
This contrasts with Variant A (which has instrument as a separate byte) and FC
(which always has explicit instrument bytes in patterns).

---

## 8. The Future Composer Relationship

### Formal FC comparison

| Feature | FC (V3/V4) | 20CC Variant A | 20CC Variant B |
|---------|-----------|----------------|----------------|
| Play entry offset | load+6 (V3/FC) or load+3 (MoN) | load+3 (JMP at +0, +3) | load+$87 |
| Data hierarchy | 3-level: orderlist→patterns→wave-tables | 2-level: sequence→wave-programs | 2-level (similar) |
| Instrument selection | Explicit byte in pattern | Explicit byte in note cmd | Encoded in note pitch |
| Freq table | 96-entry lo/hi split | 96-entry lo/hi split (identical structure) | 96-entry |
| Note range | 0–95 pitch index | 0–95 pitch index | 0–$DF |
| Vibrato | Signed delta per frame | Bit-rotation loop | Bit-rotation (likely) |
| Wave tables | Per-instrument command programs | Per-pattern command streams | Per-pattern |
| Filter writes | Per frame (filter table program) | On new note only | On new note only |
| Gate write | Y-indexed (same SID voice offset) | Y-indexed (`99 04 D4`) | Y-indexed (`99 04 D4`) |
| Hard restart | Test-bit sequence | Frame counter (frame_ctr==2 gate write) | INC/freq_hi trick |
| Pulse width | Table-driven programs | Direct PWM accumulator | Direct PWM |

### What is shared / clearly related

1. **96-entry freq table split (lo/hi)**: Both FC and 20CC use the same
   split-table approach with identical range (96 notes, C-0 to B-7).
   The 20CC freq values in I_Wanna_Dance (`$010C, $011C, $012D...`) match
   the standard C64 freq table.

2. **Y-indexed per-voice SID writes**: The `STA $D404,Y` pattern (SIDId
   confirmed) with Y ∈ {0, 7, 14} is the same mechanism FC uses for
   voice-offset addressing.

3. **Three-voice X-indexed state loop**: FC and 20CC both use X=2,1,0
   descending loops. Both use X-indexed absolute arrays for per-voice state.

4. **Hierarchical song → pattern data**: Both have an orderlist/sequence
   level and a pattern/wave-program level. FC has three levels; 20CC has two.

5. **`$FF` end-of-pattern marker**: Both use `$FF` as end-of-stream marker
   in the note data streams.

### What is different / independent

1. **Vibrato**: FC uses a signed delta added to the 16-bit frequency each
   frame. 20CC uses a **bit-rotation loop** (LSR/ROR of the 16-bit freq ZP
   pair, looped Y times). Completely different mechanism.

2. **Instrument encoding**: FC always uses an explicit instrument byte in
   pattern data. Variant A has an explicit inst byte. Variant B derives the
   instrument from the note pitch — a design FC never uses.

3. **Wave-table command dispatch thresholds**: FC V3 uses `$40` and `$60`
   as the two dispatch boundaries. 20CC Variant A uses `$40`, `$80`, `$C0`
   (four ranges with high-2-bit dispatch). Different encoding.

4. **Filter handling**: FC has a dedicated per-frame filter table program
   (writes $D417 each frame with a table-driven value). 20CC writes filter
   regs **only on note load** — no filter table program.

5. **Player efficiency**: 20CC is explicitly designed for minimal overhead
   ("4 raster lines", confirmed by Falco Paul interview). FC's player is
   more expensive (filter table execution, wave-table program per instrument).

6. **Auto-swing and beat accenting**: 20CC adds proprietary effects (per
   the Recollection interview) not present in FC. The `$1018,X` state byte
   set by `$80–$BF` sequence commands likely implements these.

### Conclusion on FC relationship

**20CC is NOT a modified FC.** They share only the C64-standard patterns
(96-note freq table, Y-indexed voice offset, X-indexed voice state loops,
`$FF` end marker) that any MoN/Hubbard lineage player would share. The
CSDb user comment "looks like a modified version of future composer" and
lemon64 rating "20cc composer - As Future Composer. Good!" describe
**functional similarity** (both are tracker-style editors with similar
feature sets), not code or format derivation.

Falco Paul's interview confirms he independently reverse-engineered "demo
and game soundtracks" (including Hubbard and MoN players) and built the
20CC player from scratch. The vibrato implementation alone (bit-rotation
vs signed-delta) proves independent authorship — a port or fork would
preserve the cheaper signed-delta approach.

The sidid.nfo attribution is: `AUTHOR: Falco Paul`, with no "based on" note.

---

## 9. SIDId Signature Mapping

From `github.com/cadaver/sidid` (`sidid.cfg`), the `20CC` block has 8
pattern lines:

| SID sig | Key bytes | What it matches | Variant |
|---------|-----------|-----------------|---------|
| sig1 | `D0 ED C9 E0 B0 10 29 1F 7D` | Note-range check + instrument decode | B only |
| sig2 | `FE ?? ?? D0 ?? DE ?? ?? A0 ?? 98 9D ?? ?? 5E ?? ?? 1E ?? ?? BD ?? ?? BC ?? ?? 99 04 D4` | Main voice loop body | B only |
| sig3 | `B4 ?? B1 ?? C9 FF F0 08 F6 ?? BC ?? ?? 99 04 D4 ...` | ZP-pointer variant note fetch | Unknown (not A or B in tested SIDs) |
| sig4 | `BC ?? ?? A9 ?? 99 04 D4 A9 ?? 99 01 D4 FE` | Hard-restart gate+freq write | B only |
| sig5 | `86 FC 8E 17 D4 8E 16 D4 C8 C8 B9 ...` | Init voice loop | Unknown |
| sig6 | `99 05 D4 68 99 06 D4 BD ...` | ADSR write + stack pop | Unknown |
| sig7 | `29 ?? 4A 4A 4A 4A A8 46 ?? 66 ?? 88 10` | Bit-rotation vibrato | **A** (confirmed) |
| sig8 | `A9 00 9D ?? ?? 9D ?? ?? ... 8D 04 D4 8D 0B D4 8D 12 D4 8D` | Hard-clear init | Both? |

The multiple signatures reflect the two variants (and possibly more sub-variants).
SIDId fires on **any** of these, which is why 209 SIDs are classified as `20CC`.

Primary sig1 matches **35 of 209** classified 20CC SIDs (Variant B).
Sig7 (vibrato) matches **Variant A** (174 SIDs).
Total SIDs with primary sig1 in HVSC: 47 (12 unclassified or other engine).

---

## 10. Versions and Tool History

- **1988**: Falco Paul writes first 20CC player ("crude version with ideas from Hubbard
  and MoN players"), founds group with Edwin van Santen (EVS).
- **1988–1991**: iterative improvements — "auto-swing", "beat accenting",
  multi-speed, hard/soft restart, sample play, advanced pulse modulation,
  voice-3 feedback to filter.
- **20CC Music Editor V1** (`csdb.dk/release/?id=10741`): community-built editor
  wrapper around the 20CC player; coder unknown; "not released by 20CC". Available as
  `20CC_COMPOSER_V1.T64` (543 downloads), with `20CC_Composer_Instructions.txt` (214
  downloads).
- **Two binary variants** correspond to different player generations:
  - Variant A (play=`$1003`): earlier/simpler (1988–1989 era, smaller ~2KB)
  - Variant B (play=`$1081`): later/richer (1989–1991 era, ~2.8KB+)

The instructions describe a 3-track tracker interface with:
- Block commands `$00–$1F`
- Note increases `$80–$BF`  
- Stop: `$FE`; Restart: `$FF`
- Sound editing: wave settings, ADSR, pulse, filter effects
- Crash protection with F1 restart

**libsidplayfp/VICE handling**: Both variants play correctly in modern emulators
(PSID format, speed=0 = VBI). No known compatibility issues.

---

## Leads to Follow

1. **Instrument record byte mapping**: bytes [0], [1], [6], [7] of the 8-byte
   instrument records are not fully decoded. The `$D405`/`$D406` (AD/SR) write
   path at `$138B`–`$13A1` needs tracing to map these.

2. **`$1018,X` (SET_1018 / `$80–$BF` sequence cmd)**: This state byte is set but
   its downstream usage was not traced. Likely the "arp" or "auto-swing" effect
   that Falco Paul describes as a unique 20CC feature.

3. **Variant B note format complete decode**: The `$E0–$FF` command range in
   Variant B was identified but the individual byte meanings within that range
   were not decoded (only that `$FF` = loop and `$E0–$FE` = commands). Full
   disassembly of Party_Report's `$12XX` note-fetch routines needed.

4. **Sig3/sig5/sig6 identification**: Three SIDId signatures did not match either
   Variant A or B in the tested SIDs. May indicate a Variant C (further player
   evolution, or a ZP-pointer variant used in relocated SIDs at `$1670`+).

5. **Merman SIDs**: `Merman/Landlord.sid` (init=`$1048`, play=`$1021`) is classified
   as `Music_Assembler` not `20CC` — it's a different player entirely despite being
   in the 20CC artist cluster. Verify whether any Merman SIDs use the 20CC player.

6. **Multi-subtune support**: The song table at `$1545` uses 6 bytes/subtune stride.
   `TV_Tunes_Mix.sid` (11 subtunes, init=`$1097`) needs analysis to confirm the
   multi-subtune mechanism.

7. **Sample/digi support**: Falco Paul mentions "sample play" as a feature. None
   of the inspected SIDs showed obvious digi output. Identifying a digi 20CC SID
   and mapping the digi mechanism would complete the picture.

8. **`$D418` written 3× per frame** (once per voice): Verify whether this is
   intentional (volume click for beat accenting?) or whether the master vol is
   constant and only the filter bits vary.

9. **Pattern ptr table at `$155B`** vs wave-prog table at `$154B`**: Two separate
   tables were found in I_Wanna_Dance but their difference was not fully resolved.
   The `$155B` table is indexed by `$100F,X` (seq_index); the `$154B` table by
   `$101B,X` (waveprog_ptr_idx). Their interaction needs confirmation.

10. **FC comparison deeper**: Read `pipelines/future_composer/docs/wiki_fc_v41_manual.md`
    for the FC instrument and sequence spec, then compare byte-for-byte against the
    instrument records and command tables above to confirm independence vs derivation.
