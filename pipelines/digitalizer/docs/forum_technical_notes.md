---
source_url: multiple (primary: digitalizer_v3.0_instructions.txt, sidid.cfg, SDI.2.1.6-docs.txt)
fetched_via: direct downloads + WebFetch
fetch_date: 2026-06-13
author: research compilation
content_date: 1989–2026
reliability: primary (instruction file = Olav Morkrid's own text; sidid.cfg = cadaver/ice00; SDI docs = 6R6/GT)
---

# Digitalizer — Technical Notes from Forums and Documentation

All concrete technical claims extracted from primary sources.
RE-needed claims are marked OPEN.

---

## 1. Confirmed Architecture (from V3.0 instruction file)

Source: `/home/jtr/sidfinity/pipelines/digitalizer/docs/src/digitalizer_v3.0_instructions.txt`
Primary source: Olav Morkrid, June 1992 (text converted from PETSCII by 6R6, 2013-07-04)

### Three editor modes:
1. **Seq-editor** (sequence editor) — the song/pattern arranger
2. **Inst-editor** (instrument editor) — sound/instrument design
3. **Trk-editor** (track editor) — per-voice step sequencer

Navigation between modes:
- Seq ↔ Inst: RUN-STOP
- Inst → Seq: RUN-STOP
- Seq ↔ Trk: F1 (seq→trk) / RETURN (trk→seq)

### Seq-editor data types (the core encoding document):

```
00-1F    Instrument        (5-bit instrument number, 32 instruments max)
20-3F    Arpeggio          (5-bit arpeggio number; range $20–$3F = 32 arpeggios)
S1-SF    Sustain add 1-15
R0-RF    Rel/Att rate & Switch gate
00-7F    Portamento Rate   (-- = tie, i.e. $00 with P-flag = tie)
A#7      Notes             (a#7 = portamento note)
```

This is a COMMAND-BYTE encoding within the sequence:
- $00–$1F: select instrument 0–31
- $20–$3F: select arpeggio 0–31
- $S1–$SF: sustain sustain command (exact byte encoding OPEN — likely $Sx format)
- $R0–$RF: release/attack rate change + gate switch (OPEN)
- Portamento rate $00–$7F with P-declare flag
- Notes given as pitch name (A#7, etc.) — encoding OPEN (likely HVSC note table indices)

OPEN: The full sequence byte encoding is not given in the instructions text.
The instrument vs arpeggio selection suggests bits[5] distinguishes the two.
Portamento with rate 0 = tie suggests ties are not special opcodes but $00-rate portamentos.

### Track bank switching:
- `*` = Switch track bank (in Seq & Trk-edit)
This implies multiple "banks" of track data — either for multi-song support
or for extended pattern count. OPEN.

### Quantize:
- `SH :/;` = +/- quantize (in Global Commands)
OPEN: Whether "quantize" means note-length quantize, or note-timing, or pattern length.

### Inst-editor: two independent speed controls:
- `CT +/-` = +/- speed 1
- `SH +/-` = +/- speed 2

These two independent speed fields per instrument are the multispeed mechanism.
OPEN: Exact semantics — speed1 may be the primary tick divider (overall note speed),
speed2 may be the table speed (how fast waveform/arpeggio/pulse/filter tables advance).
Or: speed1 = note duration, speed2 = gate timeout. Need RE.

### Inst-editor: five named tables:
Per instrument, the following tables are accessible:
1. `SH W` — Waveform table
2. `SH P` — Pulse table
3. `SH F` — Filter table
4. `SH A` — Arpeggio table
5. (implied by `SH I`) — Instrument data itself (base parameters)

**V3.0 has all four tables: waveform, pulse, filter, arpeggio.**
This is the first version where filter is confirmed present (V2.2/V2.8 show no filter).
OPEN: When was filter table added? V2.7? V3.0 is the first confirmed presence.

### Pulse/filter tie flag:
```
01 = pulse/filter tie (only bit0 used)
```
This is a 1-byte field with only bit 0 meaningful: when set, the pulse/filter
programs continue running instead of restarting when a new note begins.
This is a global per-instrument flag (not a per-table entry).
The byte value $01 means "tied", $00 means "restart on new note".

### Portamento:
- `P` in seq = "Declare for portamento" (marks a note as having portamento)
- `00-7F` portamento rate in sequence
- `a#7` note marker for portamento (the pitch to slide to/from)
OPEN: Portamento direction, slide-time semantics, exact hardware implementation.

### Inst-editor: arpeggio navigation:
- `,/.` = +/- arpeggio (navigate arpeggio programs within inst-editor)

This means arpeggios are a sub-table of the instrument, not fully independent.
OR: it means the instrument editor has a quick-browse of arpeggios used by this instrument.
OPEN.

### Track-editor: restart and stop markers:
- `R` = Set restart bar (loop point in track)
- `S` = Set stop bar (song end)

These are per-voice loop and stop markers within the track sequencer.
OPEN: How these interact with multi-song (subtune) support.

### Dump vs Save:
- `SH S` = Save (editor format, includes all data)
- `c= S` = Dump (player-only format, music data without editor)

The "dump" operation exports the music data in a format compatible with the
standalone player ("Newplayer 3.5" in V3.5). This is the binary format that
becomes embedded in SID files. The dump format and save format differ.
OPEN: exact byte layout of the dump format.

### Initialize:
- `SH UpArrow` = Initialize (Confirm with "OK")

Confirms with "OK" keypress. Clears all editor state.
The V3.5 docs.txt contains: "cbm+k then type 'ok' to clear memory."
`CBM+K` likely triggers the same init sequence in V3.5 from BASIC.

---

## 2. Version History — Technical Changes

### V2.2 (1989) — earliest confirmed version
- Tables: waveform, pulse, arpeggio (NO filter)
- 3-voice
- Basic seq + instrument + track editors
- Keyboard shortcut for disk: F1

### V2.5 (1989) — same year as V2.2
- Tables: waveform, arpeggio visible (pulse shortcut NOT listed in HVMEC; possibly absent or unlisted)
- RUN-STOP navigation same pattern
- Slightly different disk menu (F1/F3/F7 vs V2.2's F1 only)
OPEN: Was the pulse table removed in V2.5 then restored in V2.8? Or just undocumented?

### V2.7 (date unknown, between 1989–1991)
- Credit: "Olav Mørkrid of Offence, Panoramic Designs" (Offence = later group affiliation)
- No HVMEC page found; no separate sidid signature (covered by V2.x signature)
OPEN: technical differences from V2.2/V2.8 unknown.

### V2.8 (1991)
- Tables: wave, pulse, arpeggio (still no filter confirmed)
- Load/save via SHIFT+L/SHIFT+S (vs F1 disk menu in V2.2/V2.5)
OPEN: Other differences vs V2.2.

### V3.0 (1992) — first version with full instruction text available
- **Filter table added** (SH F)
- Two-speed instrument controls: speed1 (CT+/-), speed2 (SH+/-)
- Portamento system: P-declare + rate + pitch
- Sustain commands in seq ($S1–$SF)
- Rel/Att commands in seq ($R0–$RF)
- Tie flag in seq (T key, sets a parameter)
- Arpeggio navigation in inst-editor (,/.)
- Track bank switching (*)
- Dump vs save distinction
- Quantize (+/-)
- 12-year dev note: "I have been working on this for 3-4 years" (since ~1988)
- Author thanks Prosonix ("vi kaller det herming!" = "we call it copying/imitating")

### V3.5 (1995) — collaborative (GRG, Kjell Nordbo, Olav Morkrid)
- "Newplayer 3.5" as separate player component
- F1/F3 for play/stop (vs F7/F5 in V2.x/V3.0)
- Tick-rate adjustment feature (new vs V3.0)
- "Address manipulation" in editor (OPEN: what this means)
- "Nice interface" per CSDb user (visual improvement)
- DTZ2SDI converter written by 6R6 for this version

---

## 3. sidid.cfg Binary Signatures — Decoded

Source: cadaver/sidid + WilfredC64/player-id
(See src/sidid_signatures_raw.txt for raw data)

### V3.0 signature bytes (in player code at runtime):
```
FE 3A 03   = DEC $033A        ; decrement page-3 counter
B1 FB      = LDA ($FB),Y     ; load from ZP pointer $FB/$FC
C8         = INY              ; advance Y (data pointer)
C9 80      = CMP #$80        ; range check: is byte ≥ $80?
90 22      = BCC +$22        ; branch if < $80 (relative)
C9 C0      = CMP #$C0        ; range check: is byte ≥ $C0?
B0 1E      = BCS +$1E        ; branch if ≥ $C0 (relative)
69 80      = ADC #$80        ; add $80 (adjust value in $40–$7F range → $C0–$FF)
9D 3D 03   = STA $033D,X     ; store to page-3 state (X-indexed)
9D 40 03   = STA $0340,X     ; store second byte to $0340+X
C9 3F      = CMP #$3F        ; range check: is byte ≤ $3F (instrument/arpeggio select)?
D0 0C      = BNE +$0C        ; branch if not
FE 3A 03   = DEC $033A       ; decrement counter again (double-dec = tied pattern?)
B1 FB      = LDA ($FB),Y     ; load next byte from ZP pointer
C8         = INY              ; advance Y
```

Technical interpretation:
- ZP $FB/$FC = pointer to current sequence/pattern data (OPEN: big-endian or low/high?)
- $033A = a counter (tick counter or step counter) decremented in player loop
- $033D + X = per-voice state byte (likely current command/instrument number)
- $0340 + X = second per-voice state byte
- The `C9 80 / C9 C0` checks: 3-range byte encoding:
  - < $80: one meaning (note or instrument reference)
  - $80–$BF: second meaning
  - $C0+: third meaning (possibly waveform control byte)
- `ADC #$80` applied to bytes in $40–$7F range shifts them to $C0–$FF
- The `C9 3F` check (≤ $3F): instrument/arpeggio reference range (matches seq encoding: $00–$1F instrument, $20–$3F arpeggio)

OPEN: The full state variable map at $033A–$03XX. Existing research.md notes $0334–$03A4.

### V2.x signature:
```
9D ?? ??   = STA table,X    ; store to a table (X-indexed)
0A         = ASL A          ; shift A left (×2)
90 ??      = BCC +N         ; branch if no carry (value was < $80 before shift)
B9         = LDA table,Y    ; load from table (Y-indexed) — prefix only
```

This is a table-scan routine with range-test: store the current value to a table
(possibly the note/instrument table), ASL to test bit 7, then branch on result.
The `B9` prefix for LDA abs,Y follows — reads a table by Y index.
OPEN: Which tables and what the exact range-split means.

### Olav_Moerkrid separate player (3-pattern chain):
Pattern 1 key bytes: `29 80 60 DE ?? ?? ?? ?? ?? 20 ?? ?? 18 BD ?? ?? 7D ?? ?? 8D`
- `29 80` = AND #$80 (test bit 7)
- `60` = RTS (!) — the AND result decides which path; RTS here = early return from subroutine
- `DE ?? ??` = DEC abs,X
- `7D ?? ??` = ADC abs,X (adds table_hi,X)
- `8D ?? ??` = STA abs (stores to absolute address)
Pattern 2: `B9 ?? ?? 49 01 29 01 F0 ?? BD`
- `B9 ?? ??` = LDA abs,Y
- `49 01` = EOR #$01 (toggle bit 0)
- `29 01` = AND #$01 (mask bit 0)
- `F0 ??` = BEQ (branch on zero)
- `BD` = LDA abs,X prefix
Pattern 3: `F6 0C C8 B1 FC 30 0F C9 7F D0 E5`
- `F6 0C` = INC $0C (increment ZP address $0C)
- `C8` = INY
- `B1 FC` = LDA ($FC),Y (ZP pointer $FC/$FD)
- `30 0F` = BMI (branch if negative / bit 7 set)
- `C9 7F` = CMP #$7F
- `D0 E5` = BNE (loop back)

This player uses ZP $FC/$FD as data pointer (vs $FB/$FC in V3.0) — OPEN.
The `INC $0C` / loop suggests a different ZP layout from V3.0.

---

## 4. SDI Format Comparison (Closest Known Relative)

SDI (SID Duzz'It) was "built on ideas from JCH/Vibrants editor, Olav Morkrid/Panoramic
'Digitalizer' editor" per official SDI documentation.

**SDI instrument, 10 fields per instrument:**
| Field | Byte | Description |
|-------|------|-------------|
| Waveform Program | 1 | $00=none; $01–$55=program index |
| Attack/Decay | 1 | ADSR attack/decay nibbles |
| Sustain/Release | 1 | ADSR sustain/release nibbles |
| Gate Timeout | 1 | Frames before releasing gate |
| Vibrato Program | 1 | $00=none; $01–$55=program index |
| Pulse Program | 1 | $00=none; $01–$40 standard; $41–$80 infinite |
| Filter Program | 1 | $00=none; $01–$40; $41+ sweep modes |
| Band/Resonance | 1 | Filter configuration |
| Detune High | 1 | Freq detune direction ($01–$7F up; $80–$FF down) |
| Detune Low | 1 | Freq detune amount |

SDI arpeggio: 48 programs, activated by waveforms $90–$F0 in waveform table.
SDI tempo: 48 programs, called from Track 4.
SDI has a 4th track for filter control (values $71–$7F = cutoff high).

**OPEN: Does Digitalizer V3.0/V3.5 have a 4th filter track?**
V3.0 instructions mention 3 voices (SHIFT+1,2,3 for voice-off), and the filter
table is per-instrument (SH F in inst-editor). SDI's 4th-track approach is different.
The filter table in Digitalizer may be per-instrument table-based rather than track-based.

**OPEN: Does Digitalizer have vibrato as a named table separate from the waveform table?**
V3.0 instructions list: waveform, pulse, filter, arpeggio — but NOT vibrato as a named table.
SDI has a separate vibrato program table. Digitalizer may encode vibrato within the
waveform table (as a special command), or vibrato may not exist in Digitalizer V3.0.

---

## 5. GRG (6R6) Family Relationship Summary

```
Prosonix (Stein Pedersen)
    |
    | "inspiration" (Olav's words, 1992)
    v
Digitalizer V2.x–V3.0 (Olav Morkrid / Panoramic Designs, 1989–1992)
    |
    | co-developer
    v
Digitalizer V3.5 (Olav Morkrid + 6R6 GRG + Kjell Nordbo / SHAPE, 1995)
    |
    |----> DTZ2SDI (6R6, converts V3.x data to SDI format)
    |
    | "built on ideas from"
    v
SID Duzz'It / SDI (Geir Tjelta + 6R6 GRG / SHAPE, released 2002, developed earlier)
```

Geir Tjelta appears in Digitalizer V3.0 credits as "Geir/Mozicart" (helpful discussions)
and then became co-coder of SDI. This suggests SDI inherited design elements from
conversations between Olav and Geir that occurred during V3.0 development.

---

## 6. Open Technical Questions (RE Required)

| # | Question | Approach |
|---|----------|----------|
| 1 | Full sequence byte encoding ($00–$FF map to data types) | Disassemble V3.0 player |
| 2 | Exact instrument struct size and field layout | Disassemble V3.0/V3.5 player |
| 3 | Table sizes (how many entries per waveform/pulse/filter/arpeggio program) | RE |
| 4 | Speed1 vs speed2 semantic (tick div vs table speed?) | RE player loop |
| 5 | Portamento encoding (direction, rate, distance) | RE |
| 6 | Sustain ($S1–$SF) and Rel/Att ($R0–$RF) seq commands exact encoding | RE |
| 7 | Subtune support: does Digitalizer support multiple songs in one file? | RE |
| 8 | Multispeed implementation: CIA timer or just call-count divider? | RE + PSID header check |
| 9 | When was filter table added? (V2.7? V3.0?) | Compare V2.7 vs V3.0 binaries |
| 10 | ZP pointer layout: $FB/$FC in V3.0; does it differ in V2.x? | RE V2.x player |
| 11 | Page-3 variable layout: $0334–$03A4 assumed; full map? | RE + sidid sig bytes |
| 12 | DTZ2SDI exact field mapping (Digitalizer → SDI) | Disassemble DTZ2SDI |
| 13 | "Olav_Moerkrid" 3-pattern player: which HVSC tunes use it? | sidid scan of HVSC |
| 14 | "Panorama" player: related to Morkrid or separate? | RE + HVSC scan |
| 15 | Track bank switching (*): multi-song vs extended range? | RE |
| 16 | Does V3.5 have vibrato table? (not present in V3.0 inst-editor) | RE V3.5 |
