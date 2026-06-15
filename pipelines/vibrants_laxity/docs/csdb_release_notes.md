---
source_url: https://csdb.dk/release/?id=122333 (v/32-3.34); https://csdb.dk/release/?id=142168 (v/34-3.35); https://csdb.dk/release/?id=215790 (TFA v3.24)
fetched_via: direct
fetch_date: 2026-06-15
author: Laxity (Thomas Egeskov Petersen)
content_date: 1989-1990
reliability: primary
---

# Laxity Editor CSDb Release Notes

## Release Lineage

The Laxity Editor has three known CSDb entries forming a clear lineage:

| CSDb ID | Title | Year | Notes |
|---------|-------|------|-------|
| 215790 | TFA Editor V3.24 (a.k.a. "TFA Editor v/26-3.24") | 1989 | Precursor; released while Laxity was in The Flexible Arts / Starion |
| 122333 | Laxity Editor v/32-3.34 | 1990 | Main release; precursor to v/34-3.35 |
| 142168 | Laxity Editor v/34-3.35 | 1990 | Final version; likely last incarnation |

Version string format: `v/<sequencer_version>-<driver_version>` (e.g. v/32-3.34 = sequencer v32, driver 3.34).

---

## TFA Editor V3.24 (CSDb #215790)

- **Code/Music/Concept:** Laxity (Starion / The Flexible Arts)
- **Additional music:** Zenox (Starion)
- **Included SIDs:** "Def Con One" by Laxity + two by Zenox
- **Download:** D64 disk image, 105 downloads

### Production Note
"The TFA Editor #3.24 is the precursor to Laxity Editor v/32-3.34, Laxity Editor v/33-3.35 and
Laxity Editor v/34-3.35, released while Laxity still was a member of The Flexible Arts."

### Trivia (Twoflower, 2022-03-24)
"Load and save doesn't seem to have been implemented yet. Simply reset and save your music from
0F00 to 2000 + $80 per pattern used if you want the complete tune."
Also mentions: instrument data at **$1700**, SYS 2304 to restart.

**Key technical implication:** Music data range is $0F00–$2000 (+ $80 per pattern). Instruments
are at $1700. SYS 2304 ($0900) is the restart/init address. This is early-version layout — may
differ from v3.34/3.35.

---

## Laxity Editor v/32-3.34 (CSDb #122333)

- **Code/Music:** Laxity (at this point affiliated with Maniacs of Noise, Vibrants)
- **Additional music:** Scortia
- **Included SIDs:** DXYCP Scroll (Scortia), Fast Stuff 1 (Laxity), In the Mood Mix (Scortia),
  Lethal C. (Scortia), Spacemilk (Scortia)
- **Download:** T64 (358 downloads) + D64 (49 downloads), also Pokefinder.org
- **Forum threads:** 11

### Production Note
"Laxity Editor v/32-3.34 is the precursor to Laxity Editor v/33-3.35 and Laxity Editor v/34-3.35.
**Unlike the later two, this version won't patch loaded music with the current musicroutine,
allowing you to edit earlier music with its intended driver.**"

### Trivia (Twoflower, 2022-03-22)
"Fast Stuff, Wow Reggae, Squamp, Ghosts, Funk Off and the Laxity Editor attempts by Scortia and
Zonix are all created in this incarnation - 3.34. Likely released in the last months of 1989."

User comment (Twoflower, 2022-03-23): "Added a D64 with five demotunes (made in this version) included."

---

## Laxity Editor v/34-3.35 (CSDb #142168)

- **Code:** Laxity (Maniacs of Noise, Starion, The Flexible Arts, Vibrants)
- **Released:** October 17, 1990 (post Laxity joining Vibrants on 9 Sep 1990)
- **Download:** 312 downloads, also Pokefinder.org
- **Notes:** 1 goof entry; 1 trivia entry

### User Comment (Twoflower, 2022-03-24)
"Correct releasedate is likely somewhere between 9/9 -1990 (Laxity joining Vibrants) and
30/11 -1990 (Scortia leaving X-Factor). Routine was likely used by Laxity prior to this date."

### Trivia (Twoflower, 2022-03-22)
"Zimxusaf I, Well Baby, Syncopated, Sax Nuddle, Pige Bluse, Oh That, On One, A Trace of Space
and the Laxity Editor attempts by Drax are all created in this incarnation - 3.35."
"This represents likely the last incarnation of both sequencer (v/34) and driver (3.35)."

---

## Related Tools

| CSDb ID | Title | Notes |
|---------|-------|-------|
| 126841 | Laxity Relocator V1.20 | Relocates Laxity tunes; D64; 324 downloads |
| 128192 | Laxity Relocator V1.18 | Older version; displays "All code was done by Thomas Egeskov Petersen" at $8000; D64; 316 downloads |

Both relocators are by Laxity himself.

Also available at zimmers.net: `audio/Vibrants/utils/Relocate Laxity.prg` (3921 bytes)

---

## HVSC Corpus Stats (hvsc84.db)

Engine `Vibrants/Laxity` in sidid: **179 SIDs** in HVSC#84.

Users of this engine (from HVSC paths):
- MUSICIANS/L/Laxity/ (primary author)
- MUSICIANS/D/DRAX/
- MUSICIANS/F/Future_Freak/
- MUSICIANS/H/HeatWave/ (including youtH and Yavin sub-artists)
- MUSICIANS/J/JCH/
- MUSICIANS/M/MAC2/
- MUSICIANS/M/Mc_Whisper/
- MUSICIANS/S/Scortia/
- MUSICIANS/S/Scott_Ian/
- MUSICIANS/S/Slide_Gorissen_Udo/
- MUSICIANS/S/Sonic_Graffiti/
- MUSICIANS/Z/Zenox/
- MUSICIANS/Z/Zonix/

Related HVSC engine classifications (all use Laxity-family players):
- `Vibrants/Laxity`: 179 SIDs
- `Laxity_NewPlayer_V21`: 313 SIDs (JCH's 2006 player for JCH editor tunes, but Laxity-coded)
- `SidFactory/Laxity`: 39 SIDs (2005-era SID Factory player)
- `SidFactory_II/Laxity`: 377 SIDs (current SID Factory II)
- `256bytes/Laxity`: 2 SIDs
- `Vibrants/JO`: 130 SIDs (different engine, same group)
