---
source_url: https://csdb.dk/ (multiple pages), sidid.cfg, hvmec.altervista.org/blog/?p=428
fetched_via: direct (WebFetch)
fetch_date: 2026-06-13
author: synthesised from CSDb metadata + sidid.cfg + HVMEC
content_date: 1989–1995
reliability: secondary (synthesised; no RE performed)
---

# Digitalizer — Version Differences and Technical Lineage

## Version Timeline

| Version | Year | CSDb ID | Distribution | Key change |
|---------|------|---------|-------------|-----------|
| V2.2 | 1989 | 33646 | ZIP | First public release |
| V2.5 | 1989 | 33647 | ZIP (DISK5171.ZIP) + D64 on HVMEC | Feature-stable 1989 build |
| V2.7 | ~1989–1991 | 108478 | Raw D64.GZ (no ZIP wrapper) | Undated; gap release |
| V2.8 | 1991 | 33648 | ZIP | 2-year gap from V2.5 |
| V3.0 | 1992 | 33649 | ZIP; internal version string "v2.9(FF)" | Major revision; sidid-detectable |
| V3.5 | 1995 | 33650 | ZIP | Re-assembled hack of V3.0 by 6R6 + Kjell Nordbo (SHAPE) |

### Gap analysis
- V2.2 → V2.5: same year (1989), parallel builds or rapid iteration
- V2.5 → V2.7: undated; likely 1989–1990 based on scener activity
- V2.7 → V2.8: 1991 — Panoramic Designs was very active (Zoomatic also 1991)
- V2.8 → V3.0: 1992 — new major version; internal string "2.9(FF)" suggests
  V3.0 was preceded by an internal "v2.9" that shipped as the "Final" build
- V3.0 → V3.5: 3-year gap; SHAPE collaboration; not a Olav-only build

---

## V2.x vs V3.0 — sidid.cfg evidence

The sidid.cfg signatures reveal a fundamental architectural difference:

### V2.x signature (short, relocatable):
```
9D ?? ?? 0A 90 ?? B9 END
```
- `9D ?? ??` = `STA $????,X` with wildcard address → player is RELOCATABLE
- Only 7 bytes + 2 wildcard pairs — very short, high false-positive risk
- Pattern: output store → ASL (scale) → BCC (branch) → table read
- Consistent with a simple sample output loop or SID write loop

### V3.0 signature (long, fixed-address):
```
FE 3A 03 B1 FB C8 C9 80 90 22 C9 C0 B0 1E 69 80 9D 3D 03 9D 40 03 C9 3F D0 0C FE 3A 03 B1 FB C8 END
```
- `$033A`, `$033D`, `$0340` are ABSOLUTE addresses — player loads at a FIXED address
- `$FB`/`$FC` = zero-page pointer pair (relocatable within the logic)
- 32 bytes, no wildcards — high confidence match
- The code reads from `($FB),Y`, compares against $80 and $C0 (sample range checks),
  adds $80 (bias/sign-extend), and stores to TWO locations ($033D and $0340)

**INTERPRETATION (OPEN — needs RE to confirm):**
The V3.0 signature appears to be in a SAMPLE PLAYBACK routine (digi channel), not
the tracker sequence engine. The $80/$C0 comparisons and ADC #$80 are classic 1-bit
or 4-bit digi sample processing. The double-store to $033D/$0340 may be a stereo
buffer or a two-voice digi channel. This is corroborated by the separate
"OmegaSupreme_Digi" entry in sidid.cfg:
```
OmegaSupreme_Digi
85 01 A0 00 B1 FB 4A 4A 4A 4A 8D 18 D4 A9 END
```
- `85 01` = `STA $01` (banking register write — important!)
- `A0 00` = `LDY #0`
- `B1 FB` = `LDA ($FB),Y` — same $FB ZP pointer as V3.0 main signature
- `4A 4A 4A 4A` = four LSR A = divide by 16 (4-bit sample → shifted)
- `8D 18 D4` = `STA $D418` — SID volume register (DAC output for digi!)
- This is UNAMBIGUOUSLY a 4-bit digi playback routine writing to $D418

**CONCLUSION:** Digitalizer V3.0 has an integrated digi player that outputs 4-bit
samples to $D418. The STA $01 in OmegaSupreme_Digi implies C64 banking manipulation
during digi playback (reading from ROMs/RAM banks). This is a distinctive feature
not common in all C64 music editors.

---

## Player lineage — "Olav_Moerkrid" vs "Digitalizer" in sidid.cfg

sidid.cfg contains FOUR separate entries related to Olav Mørkrid's player code:

1. **Digitalizer_V2.x** — detects the EDITOR BINARY or player embedded in V2.x SIDs
2. **Digitalizer_V3.0** — detects the V3.0-era SAMPLE PLAYBACK routine (digi)
3. **Olav_Moerkrid** — detects the MUSIC SEQUENCE PLAYER (tracker engine portion)
4. **Panorama** — detects a 3-voice gate/skip dispatch loop (possibly release player)

These are FOUR DIFFERENT detection targets. The working hypothesis is:
- "Olav_Moerkrid" = the melodic/sequence playing engine in SIDs compiled with Digitalizer
- "Digitalizer_V*" = either the editor binary itself or its sample-handling code
- "Panorama" = a standalone player used in Olav's music demos (not the editor)
- "OmegaSupreme_Digi" = the digi/sample output subroutine

### Olav_Moerkrid pattern analysis (cadaver version):
```
Pattern A: 29 80 60 DE ?? ?? ?? ?? ?? 20 ?? ?? 18 BD ?? ?? 7D ?? ?? 8D ?? ?? BD ?? ?? 7D ?? ?? 8D ?? ?? A4
Pattern B: B9 ?? ?? 49 01 29 01 F0 ?? BD
Pattern C: F6 0C C8 B1 FC 30 0F C9 7F D0 E5
```
- Pattern A: envelope/ADSR decrement (`DE`=DEC indexed) + frequency add-accumulate
  (CLC + `LDA,X` + `ADC,X` + `STA` × 2 = two SID frequency writes per voice)
- Pattern B: gate bit toggle (`49 01`=EOR #1, `29 01`=AND #1) — note-on/off logic
- Pattern C: `INC $0C,X` = voice state increment; `LDA ($FC),Y` = pattern data read;
  `CMP #$7F` = end-of-pattern sentinel; `BMI` = negative byte = special command

**KEY DATA:** $7F is the end-of-pattern marker in V2.x/V3.0 sequence data (Pattern C).
`$FC` (+ $FB as seen in V3.0 sig) is the ZP pointer to pattern/song data.

### Olav_Moerkrid pattern analysis (Wilfred version — different player revision):
```
98 18 7D ?? ?? A8 B9 ?? ?? C9 FF D0 ?? BD ?? ?? 18 E9 02 9D
BC ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 DE ?? ?? D0 ?? BC ?? ?? B9 ?? ?? 29 0F 0A
4A 4A 4A 4A 85 ?? BD ?? ?? 38 E5 ?? 9D ?? ?? BD ?? ?? E9 00
```
- `99 01 D4` = `STA $D401,Y` — SID pulse hi write
- `99 00 D4` = `STA $D400,Y` — SID freq lo write
- `C9 FF` = compare with $FF — end-of-sequence marker (DIFFERENT from $7F in cadaver!)
- `4A 4A 4A 4A` = 4 × LSR A = divide by 16 (ADSR step / speed)
- `18 E9 02` = CLC + SBC #2? (unusual; possible `SEC` missing = wraps as ADC #($FE))
- `BC ?? ??` = `LDY $????,X` — table read

**DISCREPANCY:** cadaver's pattern uses `CMP #$7F` as end-sentinel; Wilfred's uses
`C9 FF` (`CMP #$FF`). These are different player revisions OR different song data
encodings. OPEN: which Digitalizer version uses $7F vs $FF end-of-pattern?

---

## V3.5 specifics — SHAPE collaboration

V3.5 is described by 6R6 as "a re-assembled hack of v3.0 with alot of new functions."

**What this means technically:**
- The 6502 assembly source of V3.0 was reconstructed (disassembled or from notes)
  and re-assembled from source
- New features were added BEFORE re-assembly, not patched in as binary hacks
- 6R6 + Kjell Nordbo both contributed code
- The resulting binary may or may not share the V3.0 sidid signature

**Known V3.5 co-coders:**
- **6R6** (real: Glenn Davanger) — coder of SID Duzz' It V2.1.7, Blues Muz' Player,
  DTZ2SDI converter. Still active in scene (Nostalgia/SHAPE).
- **Kjell Nordbo** (handle: El Morell) — coder, graphician, musician in SHAPE/Blues Muz';
  created "music demos" (executable visual+audio C64 demos); died April 2005.

**Blues Muz' Player context:**
SHAPE's own music format is "SID Duzz' It" (SDI). Separately, the Blues Muz' group
(which overlapped with SHAPE; 6R6 was in both) maintained "Blues Muz' Player" through
versions V6.4 to V19.99 (1992–1999). The DTZ2SDI converter converts FROM Digitalizer
V3.x TO SDI format — confirming the formats are distinct.

---

## PD-editor.prg — the zimmers.net file

**URL:** https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/PD-editor.prg
**Size:** ~12 KB
**Format:** C64 .prg binary (x-commodore-program)

Text strings found in the binary:
- `"2085 OLAV MORKRID/PANORAMIC"` — copyright/credit string
- `"SAVE SOUNDTRACK DUMP SOUNDTRACK DISK COMMAND ERROR"` — menu/command strings

**CONCLUSION:** PD-editor.prg IS a Digitalizer binary. The credit string matches
Olav Mørkrid's known crediting style. "SAVE SOUNDTRACK" and "DUMP SOUNDTRACK" are
commands visible in the editor UI — they refer to the two disk-save modes:
- **SAVE SOUNDTRACK**: save the song data file (pattern/sequence/instrument data)
- **DUMP SOUNDTRACK**: raw dump of song memory to disk (backup/export mode)
The "2085" prefix may be a load address (decimal $0825? or $0821?) or a build/version code.
OPEN: disassemble to confirm load address.

---

## Data format clues (synthesised from sidid + UI strings)

These are derived from indirect evidence. ALL are OPEN items pending RE.

### Memory map (V3.0 era — from sidid absolute addresses)
| Address | Probable role |
|---------|--------------|
| $0300–$03FF | Player variables / stack page usage |
| $033A | Absolute index/counter (V3.0 digi loop) |
| $033D | Digi output buffer (voice 1?) |
| $0340 | Digi output buffer (voice 2?) |
| $FB/$FC | ZP pointer pair → song/pattern data |

### Sentinel values
| Value | Probable role |
|-------|--------------|
| $7F | End-of-pattern (cadaver Olav_Moerkrid Pattern C) |
| $FF | End-of-sequence (Wilfred Olav_Moerkrid; possibly different version) |
| $80 | Sample midpoint / MSB flag (V3.0 digi) |
| $C0 | Sample clip upper bound (V3.0 digi) |
| $3F | Special case value in digi loop |

### UI structure (from V3.0 help file — docs/src/digitalizer_v3.0_instructions.txt)

The V3.0 editor has THREE named modes:

1. **Seq-editor** (sequence editor) — primary edit mode
2. **Inst-editor** (instrument editor) — instrument programming
3. **Trk-editor** (track editor) — track/order list editing

**Seq-editor commands (V3.0):**
```
[F1]       Goto TrkEdit
RUN STOP   Goto InstEdit
HOME       Goto home/seq home
CLR HOME   Goto bottom
CRSR       Move cursor
INST/DEL   Insert/delete
,/.        16 steps up/down
T          Tie on/off
I          Declare for instrument
P          Declare for portamento
=          Goto current (follow player)
SH N/M     Block start/end
SH C       Copy
SH D       Double sequence
SH R       Replace current with entry
SH E       Erase from pos
SH K       Kill from pos
(/)        Add empty bar at bottom
</>        Transpose notes
{/}        (Un)expand
SPACE      Set empty bar
```

**Seq-editor data bytes (command language in sequence data):**
```
00-1F    Instrument (select instrument 0-31)
20-3F    Arpeggio (select arpeggio 0-31)
S1-SF    Sustain add 1-15
R0-RF    Rel/Att rate & Switch gate
00-7F    Portamento Rate (-- = tie)
A#7      Notes (a#7 = port)
```

**Inst-editor commands (V3.0):**
```
RUN STOP   Goto SeqEdit
CRSR       Move cursor
HOME       Goto home
CLR HOME   Clear instrument
N          Enter instrument name
+/-        +/- instrument
,/.        +/- arpeggio
CT +/-     +/- speed 1
SH +/-     +/- speed 2
SH I       Instrument
SH W       Waveform
SH P       Pulse
SH F       Filter
SH A       Arpeggio
SH M       Mark instrument
SH C       Copy instrument
INST/DEL   Insert/delete
```
Instrument byte: `01 = pulse/filter tie (only bit0 used)`

**Trk-editor commands (V3.0):**
```
RETURN     Goto SeqEdit
HOME       Goto start
CLR HOME   Goto bottom
CRSR U/D   Next step
CRSR L/R   Move left/right
INST/DEL   Insert/delete step
R          Set restart bar
S          Set stop bar
```

**Shared Seq & Trk commands:**
```
*          Switch track bank
+/-        +/- sequence
SH +/-     +/- transpose
UpArrow    Play from position
```

**Global commands:**
```
?          Help (presumably)
/          Blank screen
SH UpArrow Initialize (Confirm with "OK")   ← matches V2.2 CSDb comment
SH :/;     +/- quantitize
SH 1-3     Voiceoff
SH RETURN  READY. (= exit to BASIC)
F1         Test arpeggio
F3         Test instrument
F5         Turn off
F7         Play
F2         Note+1
F4         Note-1
F6         Note+12 (1 octave)
F8         Note-12 (1 octave)
SH L       Load
SH S       Save
c= S       Dump (= DUMP SOUNDTRACK — raw memory dump)
@          Disk command
```

**KEY FORMAT INFERENCES from help file:**
1. **Sequence data format** uses a MIXED encoding where:
   - Bytes $00–$1F = instrument change (32 instruments max)
   - Bytes $20–$3F = arpeggio change (32 arpeggios max)
   - "S1"–"SF" = sustain commands ($?1–$?F range)
   - "R0"–"RF" = release/attack + gate switch
   - $00–$7F = portamento rate (tie = special)
   - Notes: "A#7" notation (7-octave range, 12 semitones = 84 note slots)
2. **Three sub-tables per instrument:** waveform (SHIFT+W), pulse (SHIFT+P), filter (SHIFT+F), arpeggio (SHIFT+A) — 4 sub-programs
3. **Two speed parameters** per instrument (CT+/- = speed 1, SH+/- = speed 2)
4. **Track bank switching** via `*` — implies more than one track bank (>= 2 banks)
5. **Portamento** declared with `P` in sequence and a rate table in the byte encoding
6. **Quantize** control (SH+:/;) — rhythmic quantization exists
7. **Expand** ({}) — sequence expansion/contraction feature

### Command strings (from PD-editor.prg binary):
- `SAVE SOUNDTRACK` — corresponds to "SH S" (save) from help file
- `DUMP SOUNDTRACK` — corresponds to "c= S" (dump = raw memory dump)
- `DISK COMMAND` — corresponds to "@" disk command entry
- `ERROR` — error handling string

---

## Version-to-format relationship (OPEN)

OPEN questions that require RE of the disk images:
1. Does each version use a DIFFERENT on-disk song format, or is the format stable across V2.2–V3.5?
2. What changed between V2.x and V3.0 structurally? The sidid relocatable → fixed-address shift suggests major player restructuring.
3. What "alot of new functions" did V3.5 add? (6R6's words)
4. Does V3.5 still embed Olav's player or was it replaced with Blues Muz' Player / SDI player?
5. Does the DTZ2SDI converter reveal the Digitalizer V3.x format by its conversion logic?

---

## Cross-format evidence: "Raw JCH Format To SDI Converter V0.1" (SHAPE)

Also listed in SHAPE's tool releases: "Raw JCH Format To SDI Converter V0.1"
(undated, CSDb release; not fetched this session). The existence of BOTH a JCH→SDI
and a Digitalizer→SDI converter confirms that 6R6 systematically converted the
major Norwegian C64 tracker formats of the era into SDI. This suggests SDI was
intended as a successor/unifier format in the SHAPE ecosystem.

JCH editor (Jens-Christian Huus) is a separate player family documented in HVSC.
