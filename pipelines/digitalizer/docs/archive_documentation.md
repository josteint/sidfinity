---
source_url: multiple — see per-section headers
fetched_via: direct|wayback as noted
fetch_date: 2026-06-13
author: Olav Morkrid (primary); 6R6; strings extracted from disk images
content_date: 1989–2023
reliability: primary (disk image extraction); secondary (sidid analysis already in other docs)
---

# Digitalizer — Documentation Recovered from Disk Images and Archives

## Status of Prior Docs

The following already exists in this docs/ directory (do not duplicate):
- `csdb_release_notes.md` — CSDb entries for all 7 releases
- `csdb_version_differences.md` — version lineage, sidid analysis, memory map
- `github_player_detection.md` — sidid.cfg signatures
- `github_sidid_signature.md` — full pattern analysis
- `github_parser_notes.md` — corpus counts, HVSC84 engine tags
- `src/sidid_signatures_raw.txt` — raw sidid.cfg text

**This file adds:** content extracted directly from disk image binaries + the V3.0 help text + V3.5 field labels. NEW material only.

---

## V3.0 Instructions File (PRIMARY DOCUMENTATION)

**Source:** `digitalizer_v2.9(FF)(v3.0)-instructions.txt` inside `Digitalizer-2.9(ff) v3.0.zip`  
**URL:** `http://csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff)%20v3.0.zip`  
**Converted by:** 6R6 (Glenn Rune Gallefoss) from C64 PETSCII, 2013-07-04  
**Full verbatim text:** saved to `docs/src/digitalizer_v3.0_instructions.txt`

### Key structural findings from the instructions

**Three distinct editor modes:**
1. **Seq-editor** (Sequence editor) — primary composition surface; reached from Trk-editor via [F1]
2. **Inst-editor** (Instrument editor) — reached from Seq-editor via RUN STOP
3. **Trk-editor** (Track editor) — reached from Seq-editor via [F1]

**Sequence data encoding (from Seq-editor key table):**
The sequence data uses a combined note + command byte space:

| Byte range | Meaning |
|------------|---------|
| `00`–`1F`  | Instrument select (32 instruments, 0–31) |
| `20`–`3F`  | Arpeggio select (32 arpeggios, 0–31) |
| `S1`–`SF`  | Sustain add 1–15 (sustain level modifier) |
| `R0`–`RF`  | Release/Attack rate + Switch gate |
| `00`–`7F`  | Portamento rate (`--` = tie) |
| `A#7`      | Note values (a#7 = portamento trigger note) |

**OPEN (RE):** The overlap in byte ranges (instruments 00–1F overlap portamento 00–7F) implies these are in different fields (note field vs effect field), not the same byte position. Encoding is ambiguous without RE of the actual sequence binary.

**Instrument editor sub-tables:**
- Waveform table: SHIFT+W
- Pulse table: SHIFT+P
- Filter table: SHIFT+F
- Arpeggio table: SHIFT+A
- Speed controls: CT+/- (speed 1), SHIFT+/- (speed 2)
- Pulse/filter tie flag: value `01` (only bit 0 used)

**Track editor structure:**
- Each track step: sequence + transpose (SHIFT+/- transpose)
- R = set restart bar (loop point)
- S = set stop bar (end marker)
- `*` = switch track bank (implies multiple banks of track data)

**Global disk commands:**
- `SH L` = Load
- `SH S` = Save (PETSCII: full file save)
- `c= S` = Dump (Commodore logo + S = raw dump / "DUMP SOUNDTRACK")
- `@` = Disk command (direct DOS)

**Quantize:** `SH :/;` = +/- quantize (timing grid control — unusual for 1992 C64 editor)

**Author's comment — key quotes:**
> "I have been working on this musiceditor for 3-4 years now."
(Written June 1992 → development started ~1988–1989, confirming pre-V2.2 history)

> "I would like to thank prosonix for inspiration (vi kaller det herming!)"
("vi kaller det herming" = Norwegian for "we call it mimicry/imitating" — a joking/ironic acknowledgment that he copied from Prosonix/Stein Pedersen's editor)

> "...and Geir/Mozicart for helpful discussions"
(Geir Tjelta of Mozicart — later co-creator of SID Duzz' It with Glenn Gallefoss)

**Musicians listed as available for hire (June 1992):**

| Name | Group |
|------|-------|
| Lars Hoff | Prosonix |
| Ole-Marius Pettersen | Prosonix |
| Stein Pedersen | Prosonix |
| Geir Tjelta | Mozicart |
| Trond Lindanger | Mozicart |
| Henning Rokling | Panoramic |
| Richard Nygaard | Panoramic |
| Olav Morkrid | Panoramic |

**Implication:** As of 1992, Digitalizer was used by at least the Prosonix and Mozicart circles (not just Panoramic Designs). All three groups are Norwegian scene groups.

---

## V3.5 Disk Image Strings

**Source:** `DTL35-EDITOR.D64` inside `DIGITALIZER-V35.zip`  
**URL:** `http://csdb.dk/getinternalfile.php/23372/DIGITALIZER-V35.zip`  
**Extraction method:** `strings -n 4` + targeted Python extraction  

### Instrument editor field labels (V3.5)

Extracted from binary at offset ~53k–60k:

```
ACK/DECAY.SUSTAIN/RELEASE.GATE.PULSE PRG/TIE.VIB DELAY/WIDTH.VIB RATE.FILTER PRG/TIE.FILTER RESONANCE.
```

This is the instrument editor field header row. Fields separated by `.`:

| Field | Description |
|-------|-------------|
| `ACK/DECAY` | Attack + Decay (SID ADSR — first two nibbles of $D405) |
| `SUSTAIN/RELEASE` | Sustain + Release (SID ADSR — last two nibbles of $D406) |
| `GATE` | Gate bit control |
| `PULSE PRG/TIE` | Pulse program or tie flag |
| `VIB DELAY/WIDTH` | Vibrato: delay steps + depth |
| `VIB RATE` | Vibrato: rate/speed |
| `FILTER PRG/TIE` | Filter program or tie flag |
| `FILTER RESONANCE` | SID filter resonance value |

### Instrument table column headers (V3.5)

```
WAVES  PULSE  F-CUT  ARP    TRANSPOSE SEQUENCE  STEP      NOTE      WAVEFORM  PULSE     INSTRUMENT
```

Columns visible in the tracker/sequence view:
- `WAVES` — waveform display
- `PULSE` — pulse width
- `F-CUT` — filter cutoff
- `ARP` — arpeggio
- `TRANSPOSE` — transpose value
- `SEQUENCE` — sequence number
- `STEP` — current step within sequence
- `NOTE` — note display
- `WAVEFORM` — waveform value
- `PULSE` — pulse width (repeated — may be raw + program)
- `INSTRUMENT` — instrument number

### V3.5 version strings

```
2085 V3.5 BY GRG        (editor binary credit — 6R6/Glenn Gallefoss re-authored)
DIGITALIZER V3.5
SHAPE
DIGITALIZER 3.5 NEWPLAYER 3.5    GRG/
```

**KEY FINDING:** The V3.5 EDITOR binary credits GRG (Glenn Rune Gallefoss/6R6), not Olav Mørkrid, in the `2085` credit string. Olav's name appears only in the PLAYER component:
```
OLAV MORKRID/PD    (from DTL35-PLAYER.D64)
```

This confirms the V3.5 split: GRG rewrote the editor; Olav's player survived.

### V3.5 player strings

```
DIGITALIZER 3.5
IGITALIZER PLAYER V3.5     (truncated "D" — offset artifact)
TURBO-ASS IMPROVED BY PANORAMIC DESIGN
V3.5        ;
V3.5            ; = NEW
.V35NEWPLAYER
.V35PLAYER OK!!
OLAV MORKRID/PD
```

The player disk contains a Turbo Assembler (assembled by Panoramic Design's version of TURBO-ASS+). The strings `.V35NEWPLAYER` and `.V35PLAYER OK!!` suggest the disk includes both a new player and the original V3.5 player, with a selection mechanism.

### V3.5 docs.txt

Content of `docs.txt` (37 bytes):
```
cbm+k then type "ok" to clear memory.
```

(The `c=` key + `K` is the Commodore key on a C64 keyboard.) Same "OK" confirmation dialog as V2.2.

---

## V2.5 Disk Image Strings

**Source:** `DISK5171.D64` inside `DISK5171.ZIP`  
**URL:** `http://csdb.dk/getinternalfile.php/25553/DISK5171.ZIP`  

### Effect command labels in sequence data (V2.5)

Extracted from binary at offset ~53k (the sequence-end handler code strings):

```
;END OF SEQ
NEW
RELEASE
$HOLD
&FILTER
%SLIDE
```

These appear to be **sequence command tokens** or **UI labels** for effect types available in V2.5 sequences:

| Label | Probable meaning |
|-------|----------------|
| `;END OF SEQ` | End-of-sequence marker |
| `NEW` | New/restart command |
| `RELEASE` | Release / note release command |
| `$HOLD` | Hold (sustain) |
| `&FILTER` | Filter effect |
| `%SLIDE` | Pitch slide / portamento |

**OPEN (RE):** These labels may correspond to sequence byte commands, not UI labels. The `$`, `&`, `%` prefixes may be assembler label prefix artifacts (the Digitalizer was likely assembled with Turbo-Ass). Their byte values are not confirmed.

### V2.5 disk directory (from "PANORAMA DIGITALIZER V2." string context)

```
SEQUENCE/TRACK EDI        PANORAMA DIGITALIZER V2.
DISK COMMUNICATIO

F1 - LOAD MUSIC
F3 - SAVE MUSIC
F7 - DUMP MUSIC
@  - DISK COMMAND
$  - DIRECTORY ERROR SZ<=
```

**KEY FINDING:** Disk menu in V2.5 shows function keys F1/F3/F7/@ for disk ops. This matches HVMEC documentation. The disk header string is "PANORAMA DIGITALIZER V2." (truncated version number).

### V2.5 key label section

```
BLOCK  REPLACE BY KILL MARK   F-KEY RESE TOO MANY LABELS  DEVICE NOT PRESEN
GOTO LABEL  KEY (F3-F6)  SEQUENCE  BLOCK UNDEFINE  BLOCK WRITE/KILL/COPY/PRINT
```

The Turbo Assembler is integrated (V2.5 contains the TURBO-ASS IMPROVED BY PANORAMIC DESIGN). The assembler labels like "TOO MANY LABELS", "DEVICE NOT PRESENT" etc. are assembler error strings, not editor commands.

**OPEN (RE):** The "KEYBOARDEDI" string in V2.5 suggests a keyboard editor mode — possibly a piano-keyboard layout for note entry (distinct from step-entry mode).

### V2.5 credit strings

```
PANORAMA DIGITALIZER V2.5 -OLAV-
2085 DIGITALIZER V2.5 -OLAV-
OLAV M0RKRID OF PAN
-GRG-     (Glenn Rune Gallefoss credited even in V2.5/1989)
BENDER V2.0 /RDI     (separate utility on disk)
EMAX DIGIT           (another on-disk file — possibly a sample)
```

**KEY FINDING:** GRG (6R6/Glenn Rune Gallefoss) is credited in V2.5 (1989) — five years before he officially joined Blues Muz' (1994). He was involved with Panoramic Designs' music circle from the start.

### V2.2 credit strings

```
1989 PANORAMIC
2085 DIGITALIZER V2.1 (C) DD     (V2.1 internal version? Or different sub-build?)
DIGITALIZER V2.2
ER MEKKA AV OLAV                 (Norwegian: "made by Olav")
-GRG-                            (GRG again)
```

**NOTABLE:** The V2.2 d64 contains an internal string "DIGITALIZER V2.1 (C) DD" — either a sub-build or mislabeled. The "(C) DD" suffix is unknown (Digital Delight? Panoramic's "DD" was a 1990 demo titled "Digital Delight"). The V2.2 is labeled V2.2 externally but V2.1 internally.

---

## DTZ2SDI Converter Strings

**Source:** `digitalizer_v3x_to_sdi_converter_v20_shape.d64`  
**URL:** `https://csdb.dk/getinternalfile.php/251569/digitalizer_v3x_to_sdi_converter_v20_shape.zip`  
**CSDb ID:** 237762 (listed as 6R6's work; actual credit inside = DJ GRUBY / TRIAD, 2023)

### Strings extracted

```
TALIZER V3.X ->        (truncated: "DIGITALIZER V3.X ->")
ONVERT V2.0            (truncated: "CONVERT V2.0")
PROGRAMMING BY
 = $30                 (a memory address or flag — $30 = 48 decimal)
OAD MUSIC INTO MEM WITH  (truncated: "LOAD MUSIC INTO MEM WITH")
MUSIC BANKS ARE IN USE.
 TO BEGIN!
OMPLETELY AUTOMATIC!   (truncated: "COMPLETELY AUTOMATIC!")
>NAME
DJ GRUBY / TRIAD
2023!
DTZ   2SDI/SHAPE
```

**KEY FINDING:** The DTZ2SDI converter (CSDb ID 237762, listed under 6R6) was actually programmed by **DJ GRUBY / TRIAD** in **2023**. It was released under SHAPE's group name. This is a RECENT (2023) conversion tool, not a 1990s-era one.

**Operational procedure (from strings):**
1. Load Digitalizer V3.x music file into memory
2. Ensure only ONE music bank is in use (Digitalizer uses bank switching)
3. The conversion is "COMPLETELY AUTOMATIC"
4. The tool converts the loaded data and exports SID Duzz' It (SDI) format

**`$30` constant:** May be a memory bank selector ($30 = %00110000 = both BASIC and KERNAL ROMs banked out, RAM visible at $A000 and $E000). Consistent with C64 memory banking needed to access Digitalizer's song data.

---

## Leads to Follow

1. **V3.0 instructions address redaction** — the physical address (street + phone) was redacted by Olav or the CSDb uploader. If needed for historical accuracy, the original PETSCII disk contains it. The town was "N-1415" postal code = Oppegård, south of Oslo.

2. **V2.1 internal version** — V2.2's disk contains an internal label "DIGITALIZER V2.1 (C) DD". This may indicate a V2.1 release never uploaded to CSDb. "(C) DD" = unknown, possibly "Digital Delight" (Panoramic group) or "Digital Design" or just initials.

3. **ARPEGGIO and PORTAMENTO data format** — the V3.0 instructions list portamento rate as `00`–`7F` and arpeggio as `20`–`3F` in the sequence. These are separate tables. The instrument editor navigates them with `,/.` (next arpeggio). OPEN: what is the arpeggio table binary format? How many entries?

4. **"Switch track bank" (`*` key)** — implies V3.0 supports more track data than fits in one bank. This is a rare feature; most C64 editors had a fixed track count. OPEN: how many banks, and how are they stored on disk?

5. **Quantize feature** — `SH :/;` = +/- quantize is notable for a 1992 C64 editor. This suggests real-time or step-time recording with quantization. OPEN: is this recorded from keyboard in real time?

6. **GRG (Glenn Rune Gallefoss) early involvement** — credited in V2.2 (1989) and V2.5 (1989), a decade before Blues Muz' Player V6.4 and before he was formally in Blues Muz'. His Panoramic association predates his scene-database group membership. He may have contributed music samples or intros on the Digitalizer disks, not necessarily code.

7. **Mozicart group** — Geir Tjelta + Trond Lindanger = Mozicart. Mozicart is listed in sidid.cfg as a separate player (not fetched this session). The connection between Mozicart and Digitalizer's development (acknowledged in V3.0 help text) warrants checking the Mozicart sidid entry for format overlap.

8. **V3.5 "NEWPLAYER"** — the strings `.V35NEWPLAYER` vs `.V35PLAYER` suggest V3.5 ships with TWO players: the original Olav player and a new GRG-coded one. OPEN: which player do the SIDs identified as `Digitalizer_V3.0` in sidid actually use?

9. **HVMEC page for V2.5** — `https://hvmec.altervista.org/blog/?p=428` documents keyboard controls for V2.5 (referenced in csdb_release_notes.md). Not fetched in this session.
