---
source_url: https://csdb.dk/ (multiple release pages — see per-entry URLs below)
fetched_via: direct (WebFetch per page)
fetch_date: 2026-06-13
author: CSDb community + Olav Mørkrid
content_date: 1989–1995 (releases); comments 2006–2013
reliability: primary
---

# Digitalizer — CSDb Release Notes

All known CSDb release entries for the Digitalizer music editor by Olav Mørkrid /
Panoramic Designs (Norway). Seven versions across 1989–1995; one additional SHAPE
conversion tool. Two further sidid.cfg-identified player labels ("Olav_Moerkrid",
"Panorama") may detect the compiled player routine in music SIDs rather than the
editor binary.

---

## Release 1: Digitalizer V2.2 (1989)

**CSDb ID:** 33646
**URL:** https://csdb.dk/release/?id=33646
**Webservice:** https://csdb.dk/webservice/?type=release&id=33646
**Download:** http://csdb.dk/getinternalfile.php/23398/Digitalizer_V2.2.zip
**Download count:** 676
**Screenshot:** https://csdb.dk/gfx/releases/33000/33646.png
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** 1989
**Group:** Panoramic Designs (PD)

**Credits:**
- Code: Olav Mørkrid (Panoramic Designs)
- Design: Olav Mørkrid (Panoramic Designs)

**Rating:** Awaiting 8 votes

**Production notes:** 1 entry listed on the page; content not recovered by WebFetch
(page sections not fully expanded in fetched HTML).

**User comments recovered:**
> 6R6 (grg_shape) on 23.05.2006:
> "To clear sequences, tracks or instruments you have to press: shift + up arrow,
> then type 'ok' when screen flashes."

**Technical implication:** The clear-confirmation dialog (shift+up-arrow → type "ok")
suggests a destructive-operation guard built into the editor UI. This is the ONLY
keyboard-shortcut comment for V2.2 recovered from CSDb.

---

## Release 2: Digitalizer V2.5 (1989)

**CSDb ID:** 33647
**URL:** https://csdb.dk/release/?id=33647
**Download:** http://csdb.dk/getinternalfile.php/25553/DISK5171.ZIP
**Download count:** 700
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** 1989
**Group:** Panoramic Designs (PD)

**Credits:**
- Code: Olav Mørkrid (Panoramic Designs)
- Design: Olav Mørkrid (Panoramic Designs)

**Rating:** Awaiting 8 votes

**Production notes / comments:** None recovered from CSDb.

**Key resource — HVMEC (hvmec.altervista.org):**
The HVMEC (High Voltage Music Engine Collection) has a dedicated page for V2.5:
  https://hvmec.altervista.org/blog/?p=428

Keyboard controls extracted from that page (most complete UI documentation found):

| Action | Key(s) |
|--------|--------|
| Start playback | F7 |
| Stop playback | F5 |
| Toggle editor ↔ instrument section | RUN-STOP |
| Open disk operations | F1 |
| Return to BASIC | SHIFT+RETURN |
| **Disk operations** | |
| Load file | F1 |
| Save file | F3 |
| Dump data | F7 |
| Execute disk command | @ |
| Show directory listing | $ |
| Back from disk menu | RUN-STOP |
| **Editor mode** | |
| Switch to track view | / |
| Activate/deactivate individual tracks | SHIFT + number key |
| Adjust pattern (+/-) | + / - |
| Erase pattern data | SHIFT+E |
| **Instrument editing** | |
| Navigate between instruments | + / - |
| Access wave tables | SHIFT+W |
| Open arpeggio tables | SHIFT+A |

**Related versions listed on HVMEC page:** V2.2, V2.8, V3.5.
V2.5 appears to be the "feature-stable" 1989 release; V2.2 is the earliest.

**Download also available as:**
Disk image DISK5171.D64.gz (via gzip-compressed D64 format on HVMEC).

---

## Release 3: Digitalizer V2.7 (undated, ~1989–1991)

**CSDb ID:** 108478
**URL:** https://csdb.dk/release/?id=108478
**Download:** http://csdb.dk/getinternalfile.php/105675/panoramic_designs_-_digitalizer_v2_7.d64.gz
**Download count:** 393
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** Undated in CSDb (scener release list shows it between 1989 and 1991 tools)
**Group:** Panoramic Designs (PD)

**Credits:**
- Code: Olav Mørkrid (also listed as Offence member; multi-group credit)
- Design: Olav Mørkrid

**Rating:** Awaiting 8 votes

**Production notes / comments:** None recovered.

**Key observation:** V2.7 download is a raw `.d64.gz` (gzip-compressed D64 disk image),
NOT a ZIP file. This is the only Digitalizer version distributed as a bare D64. The
disk image likely contains the editor plus example songs and possibly a README on disk.

---

## Release 4: Digitalizer V2.8 (1991)

**CSDb ID:** 33648
**URL:** https://csdb.dk/release/?id=33648
**Download:** http://csdb.dk/getinternalfile.php/23400/Digitalizer_v2.8.zip
**Download count:** 714
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** 1991
**Group:** Panoramic Designs (PD)

**Credits:**
- Code: Olav Mørkrid (Panoramic Designs)
- Design: Olav Mørkrid (Panoramic Designs)

**Rating:** Awaiting 8 votes

**Production notes:** 1 entry listed; content not recovered by WebFetch.

**User comments:** None recovered.

**Notes:** Two-year gap between V2.5 (1989) and V2.8 (1991); V2.7 fills part of that gap
(undated). Suggests active development through 1991.

---

## Release 5: Digitalizer V3.0 (1992)

**CSDb ID:** 33649
**URL:** https://csdb.dk/release/?id=33649
**Also known as:** "v2.9 (FF)" — the version string embedded in the editor binary
**Download:** http://csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff) v3.0.zip
**Download count:** 376
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** 1992
**Group:** Panoramic Designs (PD)

**Credits:**
- Code: Olav Mørkrid (Panoramic Designs)
- Design: Olav Mørkrid (Panoramic Designs)

**Rating:** Awaiting 8 votes

**User comments recovered:**
> 6R6 on 06.07.2013:
> "Uploaded missing file. And converted help file to a text file."

**HELP FILE RECOVERED:** The V3.0 zip contains a help file converted from C64
PETSCII to ASCII by 6R6. It has been saved to:
  `docs/src/digitalizer_v3.0_instructions.txt`
This is the PRIMARY documentation source for the Digitalizer format. Key findings
from the help file are summarised in csdb_version_differences.md.

**Author's comment from the help file (verbatim):**
> "I have been working on this musiceditor for 3-4 years now. When I finally
> decided to spread it, I had to reprogram it totally. I tried to make it as user-
> friendly as possible."
>
> "I would like to thank prosonix for inspiration (vi kaller det herming!) and
> Geir/Mozicart for helpful discussions."
>
> "The crew consists of: Lars Hoff (Prosonix), Ole-Marius Pettersen (Prosonix),
> Stein Pedersen (Prosonix), Geir Tjelta (Mozicart), Trond Lindanger (Mozicart),
> Henning Rokling (Panoramic), Richard Nygaard (Panoramic), Olav Morkrid (Panoramic)"

**Key Norwegian phrase:** "vi kaller det herming" = "we call it imitation/mimicry"
— Olav's humorous public admission that Digitalizer was inspired by (read: derived from)
Prosonix's editor. Combined with the Recollection interview admission, this is
definitive: Digitalizer descended from SteinTronic / Prosonix Music Editor.

**Version string note:** The internal version string "v2.9(FF)" is unusual — "FF"
may indicate "Final" or refer to a revision suffix in Olav's versioning scheme.
The CSDb community labeled it V3.0. This dual naming is important for sidid
identification: a SID file generated by V3.0 may embed the "2.9(FF)" string.

---

## Release 6: Digitalizer V3.5 (1995)

**CSDb ID:** 33650
**URL:** https://csdb.dk/release/?id=33650
**Download:** http://csdb.dk/getinternalfile.php/23372/DIGITALIZER-V35.zip
**Download count:** 1,418 (most downloaded Digitalizer version)
**External source:** Pokefinder.org
**Type:** C64 Tool
**Year:** 1995
**Groups:** Panoramic Designs (PD) + SHAPE (SHP) — co-release

**Credits:**
- Code: Olav Mørkrid (Panoramic Designs) [original engine]
- Code: 6R6 (Blues Muz', SHAPE) [re-assembly + new functions]
- Code: Kjell Nordbo / El Morell (Blues Muz', SHAPE) [co-coder]
- Design: Olav Mørkrid (Panoramic Designs)

**Rating:** Awaiting 8 votes (7 remaining)
**Forum threads:** 4 discussion threads on CSDb

**Production note recovered:**
> 6R6 (05.05.2006):
> "A re-assembled hack of v3.0 with alot of new functions."

**User comments recovered:**
> ready. (04.05.2006):
> "No download link??? Not even Pokefinder helps :("

**KEY TECHNICAL FINDING:** V3.5 is NOT a Olav-original codebase. It is a re-assembly
of V3.0 (1992) with new features added by 6R6 and Kjell Nordbo (both of Blues Muz' /
SHAPE, Norway). This explains why V3.5 appears in the SHAPE group releases as well.

**Implication for sidid coverage:** There is NO discrete sidid.cfg entry for
"Digitalizer_V3.5" — V3.5-generated SIDs likely match either "Digitalizer_V3.0"
(if the player code was not changed) or potentially "Blues_Muz_Player" (if 6R6
substituted the SHAPE playback engine). OPEN: which player does V3.5 embed?

**Kjell Nordbo note:** Kjell Nordbo died in April 2005 (suicide). V3.5 (1995)
was one of his last large creative contributions to the scene.

---

## Release 7: Digitalizer V3.x To SDI Converter V2.0 (undated)

**CSDb ID:** 237762
**URL:** https://csdb.dk/release/?id=237762
**Also known as:** "Digitalizer v3.x -> SDI Convert v2.0", "DTZ2SDI"
**Download:** digitalizer_v3x_to_sdi_converter_v20_shape.zip (93 downloads)
**Type:** C64 Tool
**Year:** Undated
**Group:** SHAPE (SHP) only

**Credits:**
- Code: 6R6 (Blues Muz', Fairlight, Nostalgia, Onslaught, SHAPE)

**Production notes / comments:** None recovered.

**KEY TECHNICAL FINDING:** This is a C64-native conversion tool that reads
Digitalizer V3.x format song data and writes it in SDI (SID Duzz' It) format.
"SDI" = SHAPE's own music tracker/editor format (SID Duzz' It by 6R6 and GT
of SHAPE, released 2014). The converter's existence implies:
1. Digitalizer V3.x and SID Duzz' It formats are DIFFERENT enough to require
   a purpose-built converter.
2. 6R6 had deep knowledge of both formats (he co-coded V3.5 and wrote SDI).
3. There may be a "Raw JCH Format To SDI Converter V0.1" (also SHAPE, also
   undated) using similar logic — listed in the SHAPE group release inventory.

---

## Related: Sounddigitalizer (1989, Lazer crack)

**CSDb ID:** 178054
**URL:** https://csdb.dk/release/?id=178054
**Also known as:** "Sound-Digi"
**Download:** Sounddigi-Lazer.d64, SoundDig.prg
**Type:** C64 Crack
**Year:** 06.03.1989
**Group:** Lazer (LZR)

**Credits:**
- Crack: Mr Disk (Austrian Cracking Crew, Lazer, X-Large)

This is a crack of some 1989 software titled "Sounddigitalizer" — possibly an
early Digitalizer release or a completely different "sound digitizer" tool
(hardware audio digitizer software for the C64 was common in 1989). Connection
to Panoramic Designs' Digitalizer tracker is UNCONFIRMED. The 1989 date aligns
with V2.2 / V2.5.

---

## Prosonix Music Editor — the "borrowed editor" connection

**CSDb ID:** 179618
**URL:** https://csdb.dk/release/?id=179618
**Also known as:** "SteinTronic"
**Type:** C64 Tool
**Group:** Prosonix
**Author:** Stein Pedersen (Offence, Panoramic Designs, Prosonix)

In the Recollection #2 interview (2006), Olav Mørkrid admitted:
> "I admit to the crime. Stein deserves the true credit for making the first
> and best music editors."
(Responding to a question about borrowing Stein Pedersen's music editor via
freeze backup.)

Stein Pedersen was a fellow Panoramic Designs member who independently ran
the Prosonix music group and created the "SteinTronic" / Prosonix Music Editor.
This confession implies Digitalizer V2.2 (1989) was based on or heavily
influenced by Stein's prior editor — a significant lineage note.
Prosonix note: "the prosonix team is now a part of panoramic" — from Panoramic
Designs group XML metadata. This confirms the groups overlapped.

The Prosonix Music Editor disk image: SteinTronic1.d64 (via CSDB download).
JCH (Jens-Christian Huus) added SteinTronic to DeepSID on 16 July 2019.
