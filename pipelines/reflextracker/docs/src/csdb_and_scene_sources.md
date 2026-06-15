---
source_url: https://csdb.dk/release/?id=43348 + https://www.lemon64.com/forum/viewtopic.php?t=4872 + https://www.pouet.net/prod.php?which=59064
fetched_via: WebFetch 2026-06-15
fetch_date: 2026-06-15
author: various (CSDb community, Lemon64 community, Pouet.net)
content_date: 1995–2017
reliability: secondary
---

# Reflextracker: Scene Database Sources

## CSDb Entry #43348

**Title**: Reflex-Tracker V1.1
**Type**: C64 Tool
**Year**: 1995
**Groups**: Reflex + The Obsessed Maniacs

### Credits
- **Code**: kb (Farbrausch, Reflex, Smash Designs, The Obsessed Maniacs); Quiss (Reflex, The Art Project Studios); Zorc (Reflex)
- **Music**: PVCF (Reflex)
- **Design**: kb and PVCF
- **Documentation & Sampling**: PVCF

### Included Demo Tunes
Three SID files bundled with the release:
1. `MUSICIANS/P/PVCF/Access_Denied_remix.sid` — "Access Denied (remix)"
2. `MUSICIANS/P/PVCF/Gubber.sid` — "Gubber" (possibly intended as "Gabber")
3. `MUSICIANS/P/PVCF/Trance_202.sid` — "Trance 202"

All three are RSID format (run on real C64 hardware), PAL, 6581 SID chip.

### Downloads
Available from CSDb (#43348) and Pokefinder.org mirror.
Archive filenames: `Reflextracker v1.1-Reflex-.zip`, `Reflextracker_V1.1.zip`

### Related Releases (from CSDb/Demozoo)
- **Liquid Sound Designer (demo version)** (1997) — kb and PVCF, follow-up tool
- PVCF's Brainbeat 1/2/3 music selector demos contain additional Reflextracker tunes
  not in HVSC standard collection

## Lemon64 Forum Thread: "Reflextracker Stuff"
URL: https://www.lemon64.com/forum/viewtopic.php?t=4872

Key technical details from PVCF (the composer/documenter):

> "Reflextracker compositions were created using quadrasid (four SID chips). Tunes created
> this way can only be recorded as a midi stream and cannot be directly converted."

> "bladesweet involved a crazy conversion of 10 channels to 3 channels."

PVCF also mentions:
- A Polish Reflextracker competition disk with example instruments
- Brainbeat 4 Side B contains sample compositions
- A manual exists but location was uncertain
- "2-Voiced Digitracker" as a separate related tool
- "LSD (synth duration editor)" as another available instrument editor
- DMC and modified Polonus DigiEditor could recompose PC tracker songs for C64

## Pouet.net Entry
URL: https://www.pouet.net/prod.php?which=59064

Description from user comment: "A **2-channel digital tracker**. Features a weird, unruly
interface with a multi-page instruction note written in German by PVCF. Don't know if anyone
besides the Reflex guys used it for anything worthwhile."

Download mirror: c64.rulez.org

## HVSC SID File Headers (observed)

| File | Init | Play | Load | Songs | Speed |
|------|------|------|------|-------|-------|
| Gubber.sid | $C050 | $0000 | $1700 | 1 | 0 (CIA-timed) |
| Trance_202.sid | $C050 | $0000 | $1000 | 1 | 0 (CIA-timed) |
| Access_Denied_remix.sid | $C006 | $0000 | $4A1C | 1 | 0 (CIA-timed) |

All RSID files, PAL, 6581. Play address $0000 = player sets up its own CIA IRQ.
Init at $C050 = HVSC wrapper (for Gubber/Trance_202) or direct player init (Access_Denied).
The Access_Denied_remix has init at $C006 (= standalone RFXT_PLAYER init entry point).

## PVCF Profile (Demozoo)
URL: https://demozoo.org/sceners/8432/

PVCF (Kai Walter) is primarily a C64 musician affiliated with Reflex since 1993.
He composed the three bundled Reflextracker demo tunes (1994–1995).

## Reflex Group (Demozoo)
URL: https://demozoo.org/groups/7272/

German C64 demo group active 1993+. Notable members: kb, Quiss, Zorc, PVCF.
kb (Tammo Hinrichs) later went on to Farbrausch (PC demoscene) and created TinySID.

## No JC64dis Disassembly Found
The JC64dis project (ice00/jc64, github.com/ice00/jc64) has 75+ .dis disassembly
projects in its doc/example/ directory, but NO Reflextracker entry was found.
Covered engines include Future Composer, Rob Hubbard, Jeroen Kimmel, Barry Leitch,
Keith Bowden Companion, etc., but not Reflextracker.

## No Published Annotated Disassembly Found
Despite searching CSDb forums, GitHub, Lemon64, Pouet.net, chipmusic.org, and
demozoo.org, no publicly available annotated disassembly of the Reflextracker C64
player was found as of 2026-06-15.
