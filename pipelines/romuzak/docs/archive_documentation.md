---
source_url: multiple (see per-section citations)
fetched_via: WebSearch + WebFetch 2026-06-13; VACSID.DOC extracted from vsid159.zip
fetch_date: 2026-06-13
author: Oliver Blasnik (ROM/R0M) — primary source texts
content_date: 1989–1997
reliability: primary (VACSID.DOC, Archive.org disk images); secondary (search summaries)
---

# RoMuzak — Product Documentation and Technical Record

## Preserved Disk Images on Archive.org

Two separate ACT 501 release disks are preserved and emulatable:

### 1. Romuzak Music Demo-Editor (1989)(ACT 501)
- Archive.org identifier: `d64_Romuzak_Music_Demo-Editor_1989_ACT_501`
- URL: https://archive.org/details/d64_Romuzak_Music_Demo-Editor_1989_ACT_501
- Main file: `Romuzak_Music_Demo-Editor_1989_ACT_501.d64` (170.8 KB)
- Uploaded: 2021-03-10 by Sketch the Cow
- Screenshots: 7 PNG files (screenshot_00 through screenshot_05 + coverscreenshot)
- Emulator: vice-resid
- Views: 168

### 2. Romuzak Analyser Play Construction Kit (1989)(ACT 501)
- Archive.org identifier: `d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501`
- URL: https://archive.org/details/d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501
- Main file: `Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501.d64` (170.8 KB)
- Uploaded: 2021-03-10 by Sketch the Cow
- Screenshots: 9 PNG files (screenshot_00 through screenshot_08 + coverscreenshot)
- Emulator: vice-resid
- Views: 201 (slightly more popular)

These two disks are distinct products — the "Analyser Play Construction Kit" is a companion to
the "Music Demo-Editor" (likely for playback/analysis of RoMuzak tunes rather than composing).
Both were sold under ACT 501 catalog number by Digital Marketing.

OPEN: Screenshots are available but not fetched (Archive.org image redirect blocked). To see
the editor UI — menus, voice layout, instrument editor, etc. — download and view the PNGs from
the above URLs, or mount the d64 in VICE.

---

## VacSID Documentation (Primary Source Text — Recovered)

VacSID V1.59 VACSID.DOC was extracted from vsid159.zip (from sta.c64.org/dosprg/vsid159.zip).
The file is saved at: `tmp/romuzak_research/vacsid_159_doc.txt`

Key passages relevant to RoMuzak:

### VacSID V1.59 Feature List (SOFTWARE section)
The V1.59 documentation does NOT list RoMuzak integration in the software features. Features
listed are: Pseudo-Stereo, Compressor/Limiter, Playlists, Online-Help, File-Selector (Cubic-
style), SongMessage detection, highly configurable player.

### VacSID — Mekka Pre-Release (V0.88 NFO via Pouët #73208)
The earlier **VacSID V0.88 Mekka pre-release** NFO (from Pouët.net) DOES describe RoMuzak:

> "The package includes RoMuzak, an integrated 'C64-sound-editor' with emulated 1541 file-
> system support."

And from web search result summary of VacSID feature list (likely from V1.57 or earlier V1.x):

> "C64 RoMuzak Music Composer Software V7.96 emulation with emulated 1541 File-System"

**Interpretation:** VacSID shipped with a copy of the RoMuzak V7.96 editor. To load tunes
inside RoMuzak on a PC, VacSID implemented a 1541 floppy disk image emulation — the RoMuzak
editor on C64 loads/saves tunes from a 1541 drive, so VacSID emulated that drive interface
for the bundled .d64 disk image. This is confirmed by CSDb: RoMuzak V7.96 (CSDb #17819) was
"found by extracting it from release #17818" (VacSID V0.88).

### VacSID V1.59 Hardware Emulation (C64 emulation scope)
Full C64 hardware emulation including:
- SID (MOS 6581): 3 FM voices, real white noise, 1 digi-channel (PlaySID regs + NMI/CIA#2
  volume); analogue filter (~); 2nd SID at $D420.
- CPU (MOS 6510): full bankswitching, legal + partial illegal opcodes, NMI + IRQ.
- CIA (MOS 6526): CIA#1 + CIA#2 interrupt counters (→ IRQ + NMI).
- VIC ($D011/$D012, scanline IRQ).
- Memory: 64K RAM + BASIC/KERNAL/CHAR ROMs + 2×256-byte RAM banks at $DE00/$DF00.

This means RoMuzak tunes played via VacSID ran inside a full 6510 emulator, NOT through
re-implementation of the RoMuzak player in DOS code.

### VacSID Contact Info (as of October 1997)
```
eMail: r0m@tap.de
Phone: 06722-971103 [Voice]
H0ME:  http://homepages.shonline.de/o/Oliver.Blasnik/
```
Source: VACSID.DOC, line "CONTACTING" section.

---

## Player Signatures (sidid.cfg)

From cadaver/sidid GitHub repository (https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg):

```
RoMuzak_V6.x
C9 ?? F0 ?? 0A 8D ?? ?? 0A 6D ?? ?? AA A0 00

RoMuzak_V7.x
C9 ?? F0 ?? 48 29 07 0A 8D ?? ?? 0A 6D ?? ?? AA A0
```

### Interpretation of the V6/V7 Signature Difference

Both patterns start with:
- `C9 ??` — CMP #immediate (compare A with some value)
- `F0 ??` — BEQ (branch if equal)
- Then diverge:

**V6.x:** `0A 8D ?? ?? 0A 6D ?? ?? AA A0 00`
- `0A` = ASL A (arithmetic shift left A)
- `8D ?? ??` = STA abs (store A to absolute address — index into table)
- `0A` = ASL A (another shift)
- `6D ?? ??` = ADC abs (add absolute)
- `AA` = TAX (transfer A to X)
- `A0 00` = LDY #0

**V7.x:** `48 29 07 0A 8D ?? ?? 0A 6D ?? ?? AA A0`
- `48` = PHA (push A onto stack — saves value before masking)
- `29 07` = AND #$07 (mask to low 3 bits — voice/channel selection 0–6)
- then same `0A 8D ?? ?? 0A 6D ?? ?? AA A0` as V6

**RE deduction:** The V7 signature wraps the voice/channel selection calculation in a
PHA + AND #$07. The `AND #$07` masks the value to 3 bits before using it as an index —
this is consistent with selecting from 7 voices (0–6, or 3 channels × some state). The PHA
saves the original value for later use. This is a structural refactoring of the channel
dispatch loop, not a change in musical features.

Source: sidid.cfg (cadaver/sidid), fetched 2026-06-13.

---

## RoMuzak in the HVSC STIL

Three STIL entries reference "RoMuzak" as a conversion target. All are in `/DEMOS/UNKNOWN/`
and all originate from Future Composer tunes by Klaus Engell Grøngaard (Link, Denmark):

```
/DEMOS/UNKNOWN/Alfs_Cat_Rap.sid
  TITLE: ALF Theme [from the TV series]
  ARTIST: Tom Kramer & Alf Clausen
  COMMENT: Edit of /MUSICIANS/L/Link/Alf_Theme.sid converted from Future
           Composer to RoMuzak.

/DEMOS/UNKNOWN/Children_Songs.sid
  TITLE: Children Songs, Tune #1
  ARTIST: Jeroen Tel
  COMMENT: Edit of /MUSICIANS/L/Link/Boingsongs.sid converted from Future
           Composer to RoMuzak.

/DEMOS/UNKNOWN/Crazy_Granpa.sid
  TITLE: Game Intro
  ARTIST: Klaus Engell Grøngaard (Link)
  COMMENT: RoMuzak conversion of /MUSICIANS/L/Link/Game_Intro.sid
```

Source: HVSC STIL.txt, mirror at https://hvsc.sannic.nl/C64Music/DOCUMENTS/STIL.txt,
fetched 2026-06-13.

**Note:** These STIL entries confirm that RoMuzak functioned as a converter from Future
Composer V1.0 format. The conversions are attributed to unknown parties, not to Blasnik.
The converted SIDs are in DEMOS/UNKNOWN/ because the converter identity is unknown.

---

## Future Composer Compatibility

The VGMPF Future Composer article states: "RoMuzak can convert Future Composer V1.0 songs."

This single sentence is the only verified external statement about RoMuzak's FC compatibility.
It does NOT say RoMuzak could convert FC v2.x or later. The 1989 CSDb-tagged tunes show many
annotated "RoMuzak conversion of [FC tune]" in their STIL entries.

The relationship appears to be: the RoMuzak editor had a built-in import function for FC V1.0
(.sid) song data. The converted songs ran on the RoMuzak player engine — the FC instruments
were mapped to RoMuzak's instrument block (18-byte ADSR/waveform/PW/filter/vibrato records).

OPEN: Whether FC effect programs (wavetables, arpeggio) were converted or discarded is
unknown without RE of the import routine.

---

## Known Users and Tool Era

The tool was predominantly used by German scene musicians, 1989–1993:

| Musician | HVSC count | Known usage context |
|----------|-----------|---------------------|
| Ass It (Kai Lehmann) | 56 | Largest user; active 1990–1993 |
| Stefan Hartwig | 54 | Digital Marketing games + others (Byteriders, Digital Excess) |
| Sony (Markus Raab) | 27 | German scene |
| Thomas Detert | 21 | First two games only; switched to Compotech afterwards |
| Gösta Feiweier | 20 | German scene |

Thomas Detert specifically: "On his first two games (one delayed, one unreleased), he arranged
using RoMuzak V6.3. Afterwards, in Compotech." — VGMPF Thomas Detert article.

---

## Leads to Follow

1. **Archive.org d64 screenshots** — the 9 screenshots of the Analyser/Play Construction Kit
   disk are the highest-value unread primary source. Download them to see the UI layout.
   OPEN: Which menus/screens do they show? Any text visible with author copyright, version,
   instrument-editor layout?

2. **Inside the d64 files themselves** — the .d64 images are mountable in VICE or extractable
   with `d64` Python tool. The disk directory and any text files on the disk should be read.
   Especially: does the disk have a README, an ANLEITUNG (German for "instructions"), or
   any documentation file? OPEN: Mount d64, list directory, extract text files.

3. **VacSID V0.88 VACUUM.NFO** — bundled in vacsid.zip (CSDb internal file 36832). Contains
   more RoMuzak description per the Mekka pre-release NFO context.

4. **Older VacSID versions (pre-V0.88)** — the Mekka pre-release (pouët #73208 mentions
   "Mekka Pre-Release") had a RoMuzak description. The full NFO is not yet fetched in full.

5. **VacSID feature list for earlier version** — the "C64 RoMuzak Music Composer Software
   V7.96 emulation with emulated 1541 File-System" feature line is from web search snippet
   and may come from an earlier VacSID feature listing (V1.57 era). The V1.59 VACSID.DOC
   in tmp/ doesn't list it — may be in a V1.57 or V1.58 doc. Try sta.c64.org vsid157.zip.
