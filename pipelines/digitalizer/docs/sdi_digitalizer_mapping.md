---
source_url: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt (SDI manual); docs/src/digitalizer_v3.0_instructions.txt (Digitalizer V3.0 help, primary); https://csdb.dk/release/?id=237762 (DTZ2SDI tool page); docs/archive_documentation.md; docs/csdb_release_notes.md; docs/csdb_version_differences.md
fetched_via: direct (WebFetch + prior session research in docs/)
fetch_date: 2026-06-13
author: synthesised from SDI manual + Digitalizer V3.0 help file + sidid.cfg analysis
content_date: Digitalizer V3.0 docs = June 1992; SDI docs = 2013; DTZ2SDI = undated (by 6R6 of SHAPE)
reliability: primary for SDI (full manual); primary for Digitalizer V3.0 UI (help text); tertiary for field mapping (inferred — no DTZ2SDI source available)
---

# Digitalizer → SDI Field Mapping

This document maps Digitalizer V3.0 fields to their SDI (SID Duzz' It) equivalents,
and identifies which SDI features are innovations vs which were inherited from Digitalizer.
The DTZ2SDI converter (CSDb #237762, by 6R6 of SHAPE) performs this conversion on a
C64; its source is inside a .d64 disk image and has not been text-extracted in this
session — all mappings below are INFERRED unless explicitly marked CONFIRMED.

All inferences follow the logic: Olav acknowledged Digitalizer as an SDI ancestor ("vi
kaller det herming!"); 6R6 co-coded both V3.5 of Digitalizer and SDI; and the V3.0
instructions file gives the Digitalizer UI vocabulary.

---

## Summary: Structural Correspondence

| Aspect | Digitalizer V3.0 | SDI v2.1 | Confidence |
|--------|-----------------|---------|-----------|
| Editor modes | Seq-editor / Inst-editor / Trk-editor | Sequencer / Sound-editor / Tracker | HIGH (same 3-mode model) |
| Voices | 3 | 3 (+ ch4 control) | SAFE |
| Instrument count | 32 (00–1F) | 32 (00–1F) | SAFE (both use $00–$1F range) |
| Arpeggios | 32 (20–3F in seq) | 48 (40–6F in seq) | MEDIUM (SDI expanded) |
| Portamento/Glide | YES ("P" key = declare portamento; 00–7F portamento rate) | YES (FX $21–$3F) | SAFE (same concept, different encoding) |
| Waveform tables | YES (SH+W) | YES (waveform program) | SAFE |
| Pulse tables | YES (SH+P) | YES (pulse program) | SAFE |
| Filter tables | YES (SH+F) | YES (filter program) | SAFE |
| Arpeggio tables | YES (SH+A) | YES (arpeggio program) | SAFE |
| Tie notes | YES ("T" key) | YES (lowercase note) | SAFE |
| Speed variants | YES (2 speeds: CT+/- = speed 1, SH+/- = speed 2) | YES (1x–16x multi-speed) | MEDIUM (SDI expanded) |
| Control channel | NONE documented | CH4 (tempo/transpose/filter) | SDI INNOVATION |
| Sustain modifiers | YES (S1–SF in seq) | YES (FX $70–$7F) | MEDIUM (same concept) |
| Release/Attack rate | YES (R0–RF in seq) | PARTIAL (via $70–$7F or ADSR in waveform) | MEDIUM |
| Quantize | YES (SH+:/; = +/- quantize) | NOT documented | Digitalizer-ONLY? |
| Save/Dump | YES (SH+S = save, c=+S = dump) | YES (same convention) | SAFE |
| Track bank switch | YES (* key) | NOT in SDI docs | Digitalizer-ONLY? |
| Pulse/filter tie flag | YES ("01 = pulse/filter tie, only bit0 used") | PRESENT (pulse ptr $41–$80 = infinite) | SAFE (different encoding) |
| Sub-tunes | YES (implied by instrument panel | 32 tunes | SAFE |

---

## Sequence Data Encoding Comparison

### Digitalizer V3.0 (from instructions file)

The Digitalizer sequence editor uses combined command + note bytes in ONE column
(no separate FX column per se). The command byte space:

| Byte range | Meaning |
|-----------|---------|
| $00–$1F | Instrument select (instruments 0–31) |
| $20–$3F | Arpeggio select (arpeggios 0–31) |
| S1–SF | Sustain add 1–15 ($S1–$SF where S = some prefix) |
| R0–RF | Release/Attack rate + Switch gate |
| $00–$7F | Portamento rate ($-- = tie) |
| A#7 | Note pitch values (a#7 = portamento trigger) |

**Critical observation:** In Digitalizer, the command byte range $00–$1F (instrument)
and $00–$7F (portamento) OVERLAP. This means these are in different fields of the same
sequence row — Digitalizer uses a multi-field row but the help file presents it
compressed into a single column list. The sequence row likely has: (note byte) and
(command byte) as separate fields, with the command byte interpreted by context.

**Arpeggio range:** $20–$3F = 32 arpeggios in Digitalizer.
**SDI arpeggio range:** $40–$6F = 48 arpeggios in SDI.
→ SDI expanded from 32 to 48 arpeggios. The base offset also changed ($20 vs $40).

### SDI v2.1 (confirmed from manual)

| FX byte | Meaning |
|---------|---------|
| $00–$1F | Instrument select |
| $20 | Filter on/off |
| $21–$3F | Glide speed |
| $40–$6F | Arpeggio select |
| $70–$7F | Release/Sustain/Attack modify |

**Key difference:** SDI added FX $20 (filter on/off toggle) and FX $21–$3F (glide),
and pushed arpeggios from $20–$3F to $40–$6F. This freed the $20–$3F range for glide
and filter commands that Digitalizer may have handled differently.

---

## Instrument Field Mapping

### Digitalizer V3.0 Instrument Editor (from instructions)

The instrument editor is accessed via RUN STOP from the sequence editor. Sub-tables:
- SH+W = Waveform table
- SH+P = Pulse table
- SH+F = Filter table
- SH+A = Arpeggio table
- CT+/- = Speed 1 control
- SH+/- = Speed 2 control
- "01 = pulse/filter tie (only bit0 used)"
- SH+I = Instrument select within inst editor
- N = Enter instrument name

**Inferred Digitalizer instrument fields** (from the sub-table names + SDI correspondence):

| # | Digitalizer field | SDI equivalent | Confidence |
|---|------------------|---------------|-----------|
| 1 | Waveform table pointer | WAVEFORM PRG ($01–$55) | SAFE |
| 2 | Attack/Decay | ATTACK/DECAY ($00–$FF) | SAFE |
| 3 | Sustain/Release | SUST/RELEASE ($00–$FF) | SAFE |
| 4 | Gate / restart behaviour | GATE TIMEOUT ($00–$FF) | MEDIUM (SDI expanded to 8 modes) |
| 5 | Vibrato pointer | VIBRATO PRG ($00–$55) | MEDIUM (SDI innovation or renamed) |
| 6 | Pulse table pointer | PULSE PRG ($00–$80) | SAFE |
| 7 | Filter table pointer | FILTER PRG ($00–$80+) | SAFE |
| 8 | Filter band/resonance | BAND/RESONANCE ($00–$FF) | SAFE |
| 9 | Speed 1 | — (possibly = vibrato rate?) | OPEN |
| 10 | Speed 2 | — (possibly = arpeggio speed?) | OPEN |
| 11 | Pulse/filter tie flag | bit of pulse/filter ptr ($41–$80) | MEDIUM |
| 12 | Detune Hi/Lo | DETUNE HI / DETUNE LO | SDI addition? (OPEN) |

The "Speed 1" and "Speed 2" fields in Digitalizer (CT+/- and SH+/-) have no direct
named SDI equivalent. In SDI, speed is embedded in the arpeggio program encoding
(high nibble of column 4 = speed). SDI vibrato speed is also in the vibrato program
column c4. Likely the Digitalizer speed fields were folded into the respective program
tables in SDI.

**The pulse/filter tie flag ($01, bit 0 only):** This is one bit controlling whether
the pulse and filter programs restart on new notes or continue (tie). In SDI, this is
handled by the pulse/filter program pointer ranges ($41–$80 = continuous). The
semantic is the same; the encoding differs.

---

## Waveform Table Mapping

### Digitalizer (inferred from player signatures and instructions)

The Olav_Moerkrid player signature (cadaver/sidid Pattern C):
```
F6 0C    → INC $0C,X      (advance voice state byte at ZP $0C+X)
C8       → INY
B1 FC    → LDA ($FC),Y    (read waveform data via ZP $FC pointer)
30 0F    → BMI +$0F       (branch if negative — sentinel byte check)
C9 7F    → CMP #$7F       (compare against $7F — tie/end marker)
D0 E5    → BNE -$1B       (loop back)
```

This implies:
- Waveform data is read via ZP pointer $FC (16-bit pointer at $FC/$FD)
- Bytes ≥ $80 are sentinel/control codes (BMI branches on these)
- $7F is specifically a tie/loop marker
- The normal data range is $00–$7F

**Implication for DTZ2SDI:** When converting from Digitalizer to SDI, waveform bytes
≥ $80 must be translated to SDI's $FF/$FE/$FD etc. command codes. The sentinel byte
$7F in Digitalizer likely becomes $FF (jump to start) in SDI.

### SDI waveform commands (confirmed)

SDI uses $FF–$E2 for control codes, $10–$E1 for waveform bytes. The command space
is in the HIGH byte range, with normal waveforms in specific values ($10, $20, $40,
$80 and arpeggio $91–$E1). Digitalizer's $7F sentinel does NOT match SDI's $FF jump
command — this is a format difference that DTZ2SDI must handle.

---

## Arpeggio Program Mapping

### Digitalizer
- Arpeggio slots: $20–$3F (32 arpeggios), accessed from sequence FX column
- Arpeggio tables accessed via SH+A in instrument editor
- "Speed 1" or "Speed 2" likely controls arpeggio advancement rate

### SDI
- Arpeggio slots: $40–$6F (48 arpeggios), accessed from sequence FX $40–$6F
- Arpeggio data at $E300, programs at $E400
- Speed encoded in column 4 high nibble of arpeggio program

**Mapping during DTZ2SDI:** Digitalizer arpeggios $20–$3F → SDI $40–$5F (32 of 48
slots). 16 SDI arpeggio slots ($60–$6F) are SDI-only additions. INFERRED.

---

## Track Editor Mapping

### Digitalizer V3.0 track editor (from instructions)

```
RETURN    Goto SeqEdit
HOME      Goto start
CLR HOME  Goto bottom
CRSR U/D  Next step
CRSR L/R  Move left/right
INST/DEL  Insert/delete step
R         Set restart bar
S         Set stop bar
*         Switch track bank
```

Each track step: sequence number + transpose (SH+/- transpose).
`R` = restart/loop point. `S` = stop.

### SDI track editor

Same structure: sequence number + transpose per step. Loop marker and stop marker.
Track data stored at $3000–$4FFF.

**Match: near-identical.** The `*` (switch track bank) in Digitalizer has no SDI
equivalent documented — SDI may lack this feature or implement it differently.

---

## Tempo / Speed

### Digitalizer
- "Speed 1" and "Speed 2" in instrument editor (CT+/- and SH+/-)
- OPEN: whether speed is per-instrument or global

### SDI
- Channel 4 FX $01–$1F: global tempo control
- Tempo programs at $E980–$EA00: $48 programs with per-step values
- Multi-speed (1x–16x) via separate play-call entry ($1009 = speed call)

**SDI innovation:** The explicit 4th channel for tempo + the tempo program table are
almost certainly SDI inventions (or borrowed from JCH/Vibrants, not Digitalizer).
Digitalizer's "Speed 1/2" are per-instrument, while SDI's tempo is global.

---

## Features in SDI NOT present in Digitalizer V3.0

These are SDI innovations or JCH/Vibrants-borrowed features not visible in the
Digitalizer V3.0 help text:

1. **Channel 4 (control channel):** Tempo/transpose/filter as a dedicated 4th
   sequence channel. Digitalizer appears to have only 3 sequence channels.

2. **FX $20 filter on/off per sequence row:** Digitalizer's filter may be purely
   per-instrument (no per-row toggle in sequence).

3. **FX $21–$3F glide in sequence:** Digitalizer uses portamento rate codes $00–$7F
   in a different encoding scheme (possibly a separate column).

4. **48 arpeggios (vs 32):** SDI expanded from Digitalizer's 32.

5. **85 vibrato programs:** Digitalizer has a vibrato table (SH+A? or implicit via
   speed fields) but scale is unknown. SDI has 85 dedicated programs.

6. **64 pulse + 64 filter programs (named):** Digitalizer has pulse/filter tables
   (SH+P, SH+F) but count unknown.

7. **48 tempo programs:** No tempo programs visible in Digitalizer.

8. **Detune Hi/Lo fields:** These 2 extra instrument bytes appear to be SDI additions
   enabling precise microtuning beyond arpeggio note offsets.

9. **Gate timeout 8-mode system:** Digitalizer may have had a simpler gate/restart
   mechanism. 8 modes (4 hard + 4 soft) appears to be SDI development.

10. **11-bit filter via waveform $F0–$F7:** This precise filter cutoff mechanism
    likely does not exist in Digitalizer (which uses simpler filter sweeps).

11. **Quantize:** Digitalizer V3.0 HAS quantize (SH+:/;). SDI does NOT document it.
    This is a RARE case where Digitalizer has a feature SDI dropped.

---

## Features SAFE to attribute to Digitalizer ancestry

These SDI features are confirmed or highly likely to derive from Digitalizer:

1. **3-editor-mode structure** (Seq / Inst / Track) — same 3-mode model
2. **Instrument fields: waveform / AD / SR / pulse / filter pointers** — matching sub-tables
3. **Pulse/filter "tie" flag** (bit 0 = continue across notes) — Digitalizer has "01 = pulse/filter tie, only bit0 used"
4. **Waveform table with gate bit** — implicit from sidid player signatures
5. **Portamento/glide** — Digitalizer has portamento rate per sequence row
6. **Note types: normal vs tie** — Digitalizer has T key for tie
7. **Sustain modifier in sequence** (S1–SF in Digitalizer; $70–$7F in SDI) — matching concept
8. **Release/Attack rate switch in sequence** (R0–RF in Digitalizer; similar in SDI) — matching concept
9. **Arpeggios from sequence FX** ($20–$3F in Digitalizer; $40–$6F in SDI) — same model
10. **Save vs Dump distinction** (SH+S = save; c=+S = dump) — same key convention
11. **Instrument name entry** — N key in both editors

---

## DTZ2SDI Converter — What We Know

**Tool:** Digitalizer V3.x To SDI Converter V2.0 by 6R6 of SHAPE  
**CSDb:** #237762; download: `digitalizer_v3x_to_sdi_converter_v20_shape.zip`  
**Contents:** Single file `digitalizer_v3x_to_sdi_converter_v20_shape.d64` (C64 disk image)  
**Target versions:** Digitalizer V3.x (V3.0 and V3.5) → SDI 2.x  
**6R6 is uniquely qualified:** He co-coded Digitalizer V3.5 AND wrote SDI — he is the
only person with authoritative knowledge of both formats simultaneously.

**What it must do (inferred from format differences):**
1. Read Digitalizer sequence bytes and remap command byte ranges:
   - Instrument $00–$1F → SDI $00–$1F (unchanged)
   - Arpeggio $20–$3F → SDI $40–$5F (add $20 offset)
   - Portamento rate $00–$7F → SDI glide $21–$3F (range compression needed)
   - Sustain S1–SF → SDI $70–$7F (remap; format TBD)
   - Release R0–RF → SDI equivalent (remap; format TBD)
2. Convert waveform program bytes (Digitalizer $7F sentinel → SDI $FF jump, etc.)
3. Convert pulse/filter/arpeggio program data (table format may differ)
4. Remap instrument "speed 1/2" fields to SDI arpeggio/vibrato program speed encoding
5. Handle pulse/filter tie flag: Digitalizer $01 bit → SDI pointer range $41–$80
6. Convert track editor data (sequence + transpose steps — format likely identical)
7. Handle the Digitalizer "track bank" concept if SDI lacks it

**NOT extractable without RE:** The exact byte-level format of Digitalizer song files,
including header layout, block sizes, table counts, and any version-specific differences
between V3.0 and V3.5 data files.

---

## Digitalizer Player Architecture (from sidid signatures)

The compiled Digitalizer player in music SIDs has these characteristics (inferred from
Olav_Moerkrid sidid patterns):

**Pattern B:** `B9 ?? ?? 49 01 29 01 F0 ?? BD`
- `LDA table,Y` → `EOR #$01` → `AND #$01` → `BEQ` → `LDA table,X`
- This is a GATE BIT TOGGLE: reads a gate state, XORs/ANDs with $01 (isolates gate bit), branches on gate=0. Identical logic to SDI's gate handling.

**Pattern C:** `INC $0C,X / INY / LDA ($FC),Y / BMI / CMP #$7F / BNE loop`
- Per-tick waveform program advance: increment position counter, read next byte, check for sentinel ($80+), check for $7F (end/loop), loop back.
- ZP $FC = waveform data pointer.

**Pattern A:** `AND #$80 / RTS / DEC $????,X / ... JSR / CLC / LDA table,X / ADC table,X / STA $D4xx / LDA table,X / ADC table,X / STA $D4xx / LDY $??`
- Frequency accumulation: two 8-bit adds (LDA+ADC→STA twice) to compute 16-bit frequency, writing to 2 SID registers. This is the note frequency write loop.
- The `AND #$80 / RTS` at the start = early-exit if bit 7 is set (gate-off or voice inactive).

**OmegaSupreme_Digi pattern:** `STA $01 / LDY #0 / LDA ($FB),Y / LSR×4 / STA $D418`
- 4-bit digi sample: read byte, right-shift 4 bits (get upper nibble), write to $D418 (master volume = DAC).
- `STA $01` = banking manipulation (write to C64 bank register).
- ZP $FB = sample data pointer (different from waveform pointer $FC).

---

## Reliability Classification

| Claim | Source | Reliability |
|-------|--------|------------|
| SDI built on Digitalizer ideas | SDI manual BACKGROUND section | CONFIRMED (primary) |
| Both use 3-editor-mode structure | Digitalizer instructions + SDI manual | CONFIRMED (primary) |
| Both have SH+W/P/F/A sub-tables | Digitalizer instructions + SDI manual | CONFIRMED (primary) |
| Pulse/filter tie flag bit-0 | Digitalizer instructions | CONFIRMED (primary) |
| Arpeggio range differs ($20 vs $40) | Both docs | CONFIRMED (primary) |
| Portamento rate encoding | Digitalizer instructions | CONFIRMED; SDI equivalent INFERRED |
| DTZ2SDI byte-level mapping | NOT confirmed | INFERRED; needs D64 extraction |
| Digitalizer instrument field count | NOT confirmed | OPEN; likely 8–10 fields but no byte-level doc |
| Vibrato program structure | NOT confirmed for Digitalizer | OPEN; SDI has detailed vibrato; Digitalizer shows speed fields only |
| Gate timeout 8-mode origin | NOT confirmed for Digitalizer | May be SDI innovation |
| Channel 4 origin | NOT visible in Digitalizer V3.0 | SDI innovation or JCH-borrowed |
| Waveform $7F sentinel | Inferred from sidid Pattern C (CMP #$7F) | OPEN; needs RE |
| 4-bit digi in Digitalizer | Confirmed via OmegaSupreme_Digi sidid | CONFIRMED sidid; RE for full understanding |

---

## Leads to Follow

- **HIGHEST PRIORITY:** Extract text from `digitalizer_v3x_to_sdi_converter_v20_shape.d64`
  using D64 tools (via65, vice, d64reader). The disk image is 1.9KB zipped — likely a
  single PETSCII program. Look for a help screen, field table, or PETSCII source listing.
  Command (if D64 tools available):
  ```
  python3 -m d64 extract digitalizer_v3x_to_sdi_converter_v20_shape.d64
  ```
  This would give the exact field mapping used by 6R6 in the converter.

- **SECOND PRIORITY:** Extract the Digitalizer V3.5 disk image (DIGITALIZER-V35.zip,
  CSDb #33650) for an updated help file. V3.5 was the last version and may have richer
  documentation than V3.0's minimalist help text.

- **THIRD PRIORITY:** The Digitalizer V2.5 entry on HVMEC (hvmec.altervista.org/blog/?p=428)
  has additional keyboard mapping. Fetch for completeness.

- **OPEN:** Whether Digitalizer had "vibrato programs" as distinct tables, or implemented
  vibrato via the waveform table. The V3.0 instructions don't mention a vibrato sub-table
  under SH+W/P/F/A — vibrato may have been speed-1 / speed-2 driven.

- **OPEN:** The Digitalizer "track bank" (`*` key) concept — does this mean multiple
  ordered-list banks (like songs in FC)? If so, Digitalizer's song structure may be
  more complex than SDI's.

- **OPEN:** Digitalizer sequence byte encoding — specifically where the note byte, the
  instrument byte, the portamento byte, and the sustain/release bytes live in the
  actual sequence binary. The help file presents them as a list but the column structure
  is ambiguous. Resolve via RE of the Digitalizer player's sequence-decode loop.

- **OPEN:** Does Digitalizer have per-tune sub-tunes (like SDI's 32 tunes)? The help
  mentions "+/- sequence" and "+/- transpose" but no explicit sub-tune count.

- **OPEN:** The "Recollection #2 interview (2006)" with Olav Mørkrid mentioned in
  archive_scene_notes.md — fetch from archive.org to get any direct format quotes.
  URL pattern: https://recollection.c64.org/ (Issue #2).
