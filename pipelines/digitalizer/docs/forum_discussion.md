---
source_url: multiple (see per-section headers)
fetched_via: WebFetch/WebSearch
fetch_date: 2026-06-13
author: research compilation
content_date: various 2006-2026
reliability: primary (CSDb forum posts), secondary (database entries), tertiary (search summaries)
---

# Digitalizer — Forum and Community Discussion

Compiled from CSDb forums, Lemon64, ChipMusic.org, Demozoo, HVMEC, and related scene sources.
All material gathered 2026-06-13. RE-needed claims are marked OPEN.

---

## 1. CSDb Release Forum Threads

### 1.1 Digitalizer V3.5 (CSDb id=33650) — 4 forum posts

Source: https://csdb.dk/forums/?csdbentrytype=release&csdbentry=33650&entrytopic=1

**Post 1 — Bamu® — 2006-05-06 07:00**
> "Does someone can add a download link - please?"

**Post 2 — cba — 2006-05-06 07:40**
> "I've already sent a message to GRG, asking him to upload the files :)"

Context: GRG = Glenn Rune Gallefoss (6R6 / Blues Muz' / SHAPE), co-coder of V3.5.
"The files" = the editor and player disk images.

**Post 3 — Bamu® — 2006-05-06 19:31**
> "V3.5 seems to have a quite nice interface."

No technical content.

**Post 4 — ready. — 2011-02-28 12:55**
Asks about stereo sampling schematic compatible with the V3.5 release;
references a stereo sampling schematic found online and asks if a
single-channel variant would work.

Technical implication (OPEN): V3.5 may have had a sampling/digitizing
component alongside the music editor — the "ready" user appears to think
the schematic is connected to the release. This could be a confusion
between the music editor Digitalizer and an earlier audio-digitizer hardware
accessory also associated with Olav Morkrid. Needs RE to confirm.

**CSDb V3.5 metadata (extracted):**
- Released 1995 by Panoramic Designs and SHAPE
- Code: 6R6 (GRG), Kjell Nordbo, Olav Mørkrid (Panoramic Designs)
- Design: Olav Mørkrid
- Download: DIGITALIZER-V35.zip → DTL35-EDITOR.D64 + DTL35-PLAYER.D64 + docs.txt
- docs.txt content: "cbm+k then type 'ok' to clear memory." (only line in file)
- 1418 downloads as of 2026-06-13
- 4 forum threads total (content of threads 2–4 not accessible via URL pattern tried)

---

### 1.2 DTZ2SDI Converter (CSDb id=237762) — forum not accessible

Source: https://csdb.dk/release/?id=237762

**CSDb metadata:**
- Full name: "Digitalizer V3.x To SDI Converter V2.0" / "DTZ2SDI"
- Code: 6R6 (Blues Muz', Fairlight, Nostalgia, Onslaught, SHAPE)
- 93 downloads as of 2026-06-13
- No user comments or production notes visible

Technical significance: 6R6 (Glenn Rune Gallefoss) — who co-authored both
Digitalizer V3.5 and SID Duzz'It (SDI) — wrote this converter.
The existence of DTZ2SDI implies:
1. Digitalizer V3.x and SDI share enough structure that automated
   conversion is possible.
2. 6R6 had access to Digitalizer V3.x internals (he co-coded V3.5).
3. SDI was "built on ideas from JCH/Vibrants editor, Olav Morkrid/Panoramic
   'Digitalizer' editor" (see SDI documentation, Section 3 below).

**Format implication (OPEN):** The two-way relationship
(Digitalizer → SDI conversion) means the table structures are similar enough
for a deterministic mapping. Reverse-engineering DTZ2SDI would document
the exact Digitalizer V3.x binary layout. The file is at:
tmp/digitalizer_research/DTZ2SDI.zip / digitalizer_v3x_to_sdi_converter_v20_shape.d64

---

### 1.3 Other CSDb release pages — minimal content

| Release             | CSDb id | Notes                                            |
|---------------------|---------|--------------------------------------------------|
| Digitalizer V2.2    | 33646   | Code+Design: Olav Mørkrid of Panoramic Designs. 676 downloads. Production notes: 1 entry (content not accessible). No user comments visible. |
| Digitalizer V2.5    | 33647   | Same credits. 700 downloads. DISK5171.ZIP (binary).                  |
| Digitalizer V2.7    | 108478  | Code+Design: Olav Mørkrid of Offence, Panoramic Designs. 393 downloads. |
| Digitalizer V2.8    | 33648   | Code+Design: Olav Mørkrid of Panoramic Designs. 714 downloads. 1 production note (not accessible). |
| Digitalizer V3.0    | 33649   | Alternate designation "v2.9 (FF)". 376 downloads. Help file converted to text 2013-07-04 by 6R6 (see src/digitalizer_v3.0_instructions.txt). |

---

## 2. Demozoo / ExoticA

Source: https://demozoo.org/groups/1250/ (Panoramic Designs profile)
Fetched: 2026-06-13

Panoramic Designs: "all-Norwegian c64 demo group, born early months of 1990 by former
members of The Shadows and Abnormal. Members used their real names — an unusual practice."

Olav Mørkrid: Bergen, Hordaland, Norway. Coder, musician. Member of Panoramic Designs
and later Offence. Known aliases: OFF, Omega Supreme, The Disk Ripper. Co-founder of
Funcom (games: Anarchy Online, Dreamfall). Later worked at Opera Software.

30+ productions by Panoramic Designs 1989–2025.

No technical detail about Digitalizer format in Demozoo or ExoticA data.

---

## 3. SDI Documentation — Digitalizer Lineage Claim

Source: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt
Fetched: 2026-06-13 (via SourceForge redirect)
Reliability: PRIMARY (official SID Duzz'It documentation)

**Verbatim quote from SDI documentation:**
> "SDI was built on ideas from JCH/Vibrants editor, Olav Morkrid/Panoramic 'Digitalizer' editor"

This is the only explicit published technical genealogy statement found for Digitalizer.
Implications:
- SDI (SID Duzz'It) shares conceptual heritage with both JCH Editor and Digitalizer.
- 6R6 (who co-wrote SDI) was familiar with Digitalizer's design.
- SDI and Digitalizer may share table structures for instruments, arpeggio, pulse, filter.

**SDI instrument structure (documented, for comparison with Digitalizer):**
SDI instruments have 10 fields:
1. Waveform Program (1 byte, $00=none, $01–$55=programs)
2. Attack/Decay
3. Sustain/Release
4. Gate Timeout
5. Vibrato Program (1 byte, $00=none, $01–$55=programs)
6. Pulse Program (1 byte, $00=none, $01–$40 standard, $41–$80 infinite sweep)
7. Filter Program (1 byte, $00=none, $01–$40 standard, $41+ sweep modes)
8. Band/Resonance
9. Detune High
10. Detune Low

32 instruments total ($00–$1F direct; $20–$2F via arpeggio routine only).

SDI arpeggio: 48 programs ($40–$6F in sequencer). Activation via waveforms $90–$F0.
SDI has 85 vibrato programs, 64 pulse programs, 64 filter programs, 48 tempo programs.

**OPEN:** Whether Digitalizer's instrument/table count matches SDI is unknown without RE.
DTZ2SDI may document the mapping exactly.

---

## 4. HVMEC (High Voltage Music Engine Collection) Entries

Source: hvmec.altervista.org (various pages)
Fetched: 2026-06-13

Four editor pages + one players page found. Key technical content per version:

### 4.1 Digitalizer V2.2 (page id=427)
Controls extracted:
- F7 Play / F5 Stop
- RUN-STOP: toggle between editor and instrument sections
- F1: disk menu (load/save)
- SHIFT+1,2,3: toggle track 1/2/3 on/off
- +/-: pattern navigation
- Instrument editor: SHIFT+W (wave table), SHIFT+P (pulse table), SHIFT+A (arpeggio table)

Tables confirmed present in V2.2: **wave, pulse, arpeggio**.
Filter table: NOT listed for V2.2.

### 4.2 Digitalizer V2.5 (page id=428)
Controls extracted:
- F7 Play / F5 Stop
- RUN-STOP: editor ↔ instrument
- F1: disk menu; SHIFT+RETURN: return to BASIC
- /: switch to track view
- SHIFT+1,2,3: toggle tracks
- SHIFT+E: erase pattern
- Instrument editor: SHIFT+W (wave table), SHIFT+A (arpeggio table)

Tables confirmed present in V2.5: **wave, arpeggio**.
Pulse table shortcut (SHIFT+P): NOT listed — **possible regression or omission** from V2.2.
Filter table: NOT listed.
OPEN: Whether pulse table was removed in V2.5 or merely unlisted needs RE.

### 4.3 Digitalizer V2.8 (page id=429)
Controls extracted:
- F7 Play / F5 Stop
- RUN-STOP: editor ↔ instrument
- SHIFT+L / SHIFT+S: load / save
- Track editor: 3 voices, pattern navigation
- Instrument editor: wave table, pulse table, arpeggio table

Tables confirmed present in V2.8: **wave, pulse, arpeggio**.
Filter table: NOT listed.

### 4.4 Digitalizer V3.5 (page id=418)
Additional features over V2.x:
- "Newplayer 3.5" as associated playback component (separate from editor)
- Instrument editor includes **wave tables, pulse tables, filter tables, and arpeggio settings**
- Tick-rate adjustment feature present
- Address manipulation in editor
- F1 play / F3 stop

Tables confirmed present in V3.5: **wave, pulse, filter, arpeggio**.
Filter table: appears in V3.5 (and V3.0 per instruction file) but NOT in V2.2/V2.8.
OPEN: When exactly was filter added — V2.7? V2.9? V3.0? RE of the binaries will confirm.

### 4.5 Players [Digitalizer] (page id=416)
- Lists "Digitalizer V3.5 player" version "5.00d"
- Download: DTL35-PLAYER.D64.gz
- The player is called "Newplayer 3.5" (per V3.5 editor page)

---

## 5. Recollection Magazine Interview (Olav Morkrid)

Source: https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=129
Also: http://www.atlantis-prophecy.org/recollection/?load=online_issues&issue=1&sub=article&id=16
Published: Recollection #1 and #2
Interviewer: Jazzcat

Technical content about Digitalizer: **NONE**.

The interview covers scene history, Zoomatic (a graphics tool), Funcom, and Opera Software.
Key quote about music: "Stein [Pedersen of Prosonix] deserves the true credit for
making the first and best music editors." This is consistent with Olav acknowledging
Stein Pedersen (Prosonix) as an inspiration for Digitalizer (see V3.0 credits: "thank
prosonix for inspiration (vi kaller det herming!)" — 'vi kaller det herming' = Norwegian
for "we call it copying/imitating").

---

## 6. sidid Player Identification Database

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
Also: https://github.com/TCRF/vgmid/blob/master/c64.nfo
Fetched: 2026-06-13
Authors: cadaver (Lasse Ööyrni), Ian Coog, ice00, Ninja, Yodelking, Wilfred, Prof.Chaos

Digitalizer signatures (see src/sidid_signatures_raw.txt for full content):

**Digitalizer_V3.0** (single-pattern signature):
```
FE 3A 03 B1 FB C8 C9 80 90 22 C9 C0 B0 1E 69 80 9D 3D 03 9D 40 03 C9 3F D0 0C FE 3A 03 B1 FB C8 END
```

Key bytes decoded:
- `FE 3A 03` = DEC $033A (decrement player state byte at page 3)
- `B1 FB` = LDA ($FB),Y (read from zero-page pointer $FB/$FC)
- `C8` = INY
- `C9 80` / `C9 C0` / `C9 3F` = compare A with $80, $C0, $3F (range checks)
- `69 80` = ADC #$80
- `9D 3D 03` / `9D 40 03` = STA $033D,X / STA $0340,X (write to page-3 state)

Two accesses to page 3: $033A (DEC'd = counter) and $033D/$0340 (written via X-indexed).
The `C9 3F` check (≤ $3F = 63 dec) aligns with a 6-bit pattern/sequence index.
The `C9 80` / `C9 C0` range checks suggest 2-bit field encoding (bits 7:6 of a data byte).

**Digitalizer_V2.x** (compact, high-wildcard signature):
```
9D ?? ?? 0A 90 ?? B9 END
```
- `9D ?? ??` = STA abs,X (store to table)
- `0A` = ASL A (shift left)
- `90 ??` = BCC rel (branch if no carry)
- `B9` = LDA abs,Y (load from table, Y-indexed)

Suggests table-walk loop using X-index storage and Y-index reading.

**Olav_Moerkrid** (separate player family, 3-pattern chain):
Pattern 1: `29 80 60 DE ?? ?? ?? ?? ?? 20 ?? ?? 18 BD ?? ?? 7D ?? ?? 8D ?? ?? BD ?? ?? 7D ?? ?? 8D ?? ?? A4 END`
Pattern 2: `B9 ?? ?? 49 01 29 01 F0 ?? BD END`
Pattern 3: `F6 0C C8 B1 FC 30 0F C9 7F D0 E5 END`

This is a DIFFERENT player identified separately from "Digitalizer_V2.x" —
suggests at least one Morkrid player variant not covered by the Digitalizer sigs.

**Oeyvind_Jergan** (separate entry in same database):
```
A2 78 A9 00 9D 34 03 CA 10 F8 ...
```
- `A2 78` = LDX #$78 (120 dec)
- `9D 34 03` = STA $0334,X (init page-3 from $0334)
This clears 120 bytes of page 3 starting at $0334. Consistent with known
Digitalizer variable layout ($0334–$03A4 from existing research.md).

**Panorama** (separate entry):
```
AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? 29 01 D0
```
Three-voice dispatch: LDA abs / BNE / JMP structure × 3 voices.
OPEN: Whether "Panorama" is a separate Morkrid player or an unrelated engine.

---

## 7. CSDb Player Relationships — Mozicart / Geir Tjelta

From V3.0 instruction file author's comment:
> "I would like to thank prosonix for inspiration (vi kaller det herming!) and
>  Geir/Mozicart for helpful discussions (I hope you got some help too!)."

Musicians listed as "the crew":
- Lars Hoff, Ole-Marius Pettersen, Stein Pedersen (Prosonix)
- Geir Tjelta, Trond Lindanger (Mozicart)
- Henning Rokling, Richard Nygaard, Olav Morkrid (Panoramic)

Geir Tjelta of Mozicart later co-coded SID Duzz'It (SDI) with 6R6/Glenn Rune Gallefoss.
Prosonix's Stein Pedersen is explicitly credited as an inspiration ("we call it copying").
OPEN: Which specific Prosonix editor inspired Digitalizer's design?

---

## 8. GRG (6R6/Glenn Rune Gallefoss) — Blues Muz' connection

Source: CSDb scener id=8098, HVSC, demozoo
Fetched: 2026-06-13

Glenn Rune Gallefoss (GRG/6R6) is the main Blues Muz' composer in HVSC (154 tunes).
He is the same person who:
1. Co-coded Digitalizer V3.5 (1995) alongside Kjell Nordbo and Olav Morkrid
2. Co-coded SID Duzz'It (SDI) with Geir Tjelta
3. Wrote DTZ2SDI (Digitalizer V3.x → SDI converter)

SDI documentation URL: http://home.eunet.no/~ggallefo/sdi/ (now offline;
was maintained by "Glenn" per CSDb comment from Mace, 2008-11-03).

This triangle (Digitalizer → 6R6 → SDI + DTZ2SDI) is the key lineage for
understanding the format. DTZ2SDI is the most direct format-to-format
documentation artifact available without RE.

---

## 9. Lemon64 / ChipMusic.org — No substantive Digitalizer content

Multiple forum threads checked (see leads below for thread IDs). None contained
technical discussion of Digitalizer format, instrument layout, or player internals.

The SDI-focused Lemon64 threads (t=31585, t=24599) described SDI's own format
in passing but did not reference Digitalizer or the DTZ conversion.

---

## 10. Usenet / comp.sys.cbm

Narkive archive search: only "Audio Digitalizer" post found (1995, hardware schematic
request — unrelated hardware, not the music editor). No Usenet discussion of the
Olav Morkrid music editor found.

---

## 11. Diskmag Coverage

Vandalism News archive checked; no Digitalizer entries found in Issue 1.
C64 Diskmag Wiki checked. No technical articles on Digitalizer located.
OPEN: Earlier Vandalism News issues (#2–#10, covering 1991–1993) not checked.
Norwegian-language diskmags from 1989–1993 (Panoramic group productions) not found
online.

---

## Leads to follow

1. **DTZ2SDI binary (highest priority)**: `tmp/digitalizer_research/DTZ2SDI.zip` and
   `tmp/digitalizer_research/digitalizer_v3x_to_sdi_converter_v20_shape.d64` are already
   downloaded. Disassembling DTZ2SDI would document the exact Digitalizer V3.x binary
   layout (table offsets, sizes, encoding) from the converter's read routines.

2. **Digitalizer V3.0 binary**: `tmp/digitalizer_research/digitalizer_v2.9(FF)(v3.0).d64`
   is already downloaded. Direct disassembly of the player (not editor) would give the
   authoritative format spec. Cross-reference with known V3.0 sidid signature bytes.

3. **Digitalizer V3.5 editor/player binaries**: `tmp/digitalizer_research/DTL35-EDITOR.D64`
   and `tmp/digitalizer_research/DTL35-PLAYER.D64` are already downloaded.
   Disassemble to find: instrument table format, table sizes, arpeggio encoding,
   pulse/filter table layout, speed/multispeed mechanism, subtune handling.

4. **SDI documentation vs Digitalizer comparison (OPEN)**:
   The SDI docs list 10-field instruments, 32 instruments, 48 arpeggios, 85 vibrato,
   64 pulse, 64 filter, 48 tempo programs. Verify how many of these counts match
   Digitalizer V3.5 by RE. The counts may differ (Digitalizer appears older and smaller).

5. **Oeyvind_Jergan player** (in sidid.cfg, clears $0334+ on page 3): Possibly a
   Morkrid-adjacent or Panoramic-adjacent player. Check HVSC for tunes identified as
   Oeyvind_Jergan; the `LDX #$78 / STA $0334,X` init may indicate 120-byte variable
   block at $0334–$03AB — larger than the $0334–$03A4 block in research.md.

6. **Panorama player** (sidid.cfg): Three-voice dispatch pattern; relation to Morkrid
   and Digitalizer players unknown. OPEN.

7. **Olav_Moerkrid player** (sidid.cfg, 3-pattern chain): A THIRD identified player
   family beyond Digitalizer_V2.x and Digitalizer_V3.0. The `F6 0C` = INC $0C
   instruction (incrementing zero page $0C) and `B1 FC` = LDA ($FC),Y suggests a
   different ZP pointer convention from V3.0 (which uses $FB/$FC). OPEN.

8. **CSDb production notes**: V2.2 (id=33646) and V2.8 (id=33648) each have 1
   production note listed — URL pattern for production notes not found. Try
   `csdb.dk/release/prodinfo.php?id=NNNNN` or equivalent endpoint.

9. **Vandalism News issues #2–#40 (1991–1995)**: Norwegian scene magazine covering
   the exact years Digitalizer was active. May contain reviews or technical notes.
   Access via untergrund.net or scene.org archives.

10. **6R6's personal SDI website** (http://home.eunet.no/~ggallefo/sdi/) is offline.
    Try Wayback Machine: https://web.archive.org/web/*/home.eunet.no/~ggallefo/sdi/
    May contain DTZ2SDI documentation, Digitalizer ↔ SDI format comparison notes.

11. **V3.5 "filter table" first appearance**: HVMEC data shows filter table added in
    V3.5 (not in V2.2/V2.8). V2.7 and V3.0 binaries are in tmp/ — check whether
    filter table appears in those versions to narrow the introduction version.
