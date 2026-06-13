---
source_url: multiple — vgmpf.com (multiple pages), remix64.com (interviews), csdb.dk (webservice), hvsc.c64.org/DOCUMENTS/STIL.txt, archive.org, lemon64.com, c64scene.pl/viewtopic.php?t=112
fetched_via: direct (WebFetch / WebSearch)
fetch_date: 2026-06-13
author: various scene members and researchers
content_date: 1989–2024
reliability: secondary (aggregated scene knowledge; no primary source docs)
---

# RoMuzak — Scene Discussion, Known Users, and Format Observations

## Scene adoption and user base

RoMuzak was predominantly used by the **German C64 commercial game scene** in the period 1989–1993.
Most users were German composers working for German game publishers (Software 2000, CP Verlag,
Digital Marketing, Digital Excess, Byteriders, Starbyte). There is also some Italian and Polish
adoption.

### Confirmed composers who used RoMuzak V6.3 (from VGMPF)

| Composer | Nationality | Context | Source |
|----------|-------------|---------|--------|
| Stefan Hartwig | German | "music for various games from Digital Marketing, the Byteriders or Digital Excess" (Remix64 interview); used RoMuzak for Double Sphere, Tube Madness, Brubaker, and others | VGMPF Tube_Madness_(C64), Brubaker_(C64) |
| Thomas Detert | German | "On his first two games (one delayed, one unreleased), he arranged using RoMuzak V6.3. Afterwards, in Compotech." | VGMPF Thomas_Detert |
| Matthias Deutsch | German | "switched between RoMuzak V6.3 and Timecomposer V4.0" — games: Cubin (1992), Colors (1993), Lazytech (1994), Ice Guys (1997), Bomb Mania (1997) | VGMPF Matthias_Deutsch |
| Georg Brandt | German | "His last game used RoMuzak V6.3" — composed for Werner Let's Go!, Tom & Jerry, Donald the Hero, Street Gang, etc. | VGMPF Georg_Brandt |
| Hans-Hermann Franck | German | "Like most for Software 2000, Franck arranged in RoMuzak V6.3." Games: Atomino, Shiftrix, Wild West World | VGMPF Hans-Hermann_Franck |
| Paolo Galimberti | Italian | "arranged in RoMuzak V6.3 and The Sound FX Kit"; MoonShadow (1990), F1 GP Circuits (1991), Lupo Alberto (1991), Clik Clak (1992) | VGMPF Paolo_Galimberti |
| Marc Liedtke | German | "arranged in RoMuzak V6.3 on an 8580 chip"; Kopido (1992), Triget (1992), Dark Star (1995) | VGMPF Marc_Liedtke |
| Lars Hutzelmann | German | "used RoMuzak V6.3, ROM's Fix, Music-Assembler, Soundmaster v3.1, and Cyberlogic Sound Studio"; Ultrix (1991), Oskar (1992), 12 O'Clock (1992), Plutonium (1993) | VGMPF Lars_Hutzelmann |

**Pre-existing project data (from research.md):** Top composers by SID count in HVSC:
- Ass It: 56 tunes
- Stefan Hartwig: 54 tunes
- Sony: 27 tunes
- Thomas Detert: 21 tunes
- Goesta Feiweier: 20 tunes

---

## ROM's Fix — companion sound effects editor

**Source:** VGMPF ROM's_Fix page (https://www.vgmpf.com/Wiki/index.php?title=ROM%27s_Fix)

ROM's Fix is a separate sound effects editor bundled with RoMuzak V6.3. It was created by
Oliver "ROM" Blasnik and released in 1989 (between May and August, same year as RoMuzak V6.3).

### Features (from manual, per VGMPF)
- Up to **64 distinct sound effects** can be created per bank
- Per-effect parameters:
  - **SID channel select:** choose one of the three SID voices ($D400/$D407/$D40E register groups)
  - **Register programming:** set SID registers directly (hex — manual assumes hex familiarity)
  - **Title string:** optional label for each effect
  - **Pitch bend:** modulate frequency over time
  - **Vibrato:** periodic frequency oscillation
  - **Pulse width modulation (PWM):** time-varying duty cycle on the pulse waveform
  - **Waveform change:** single or repeated waveform transitions during effect playback
  - **Sound mixing:** mix up to two additional sounds into the effect
- **Filter is kept off:** the manual explicitly states filter settings are excluded; users are
  expected to know SID register semantics except filtering.

### Interface modes
- Single-effect edit mode
- Multi-effect simultaneous playback mode
- Save mode (write sound bank to disk)

### Bundled examples (12 pre-made sounds)
- whine, wizz, step, bell, diuuuu, lazer, total!
(Names suggest: laser shot, footstep, bell hit, explosion/dive, lazer beam, generics.)

### Notable users of ROM's Fix
- **Markus Schneider** — used for sound effects in Timezone (C64)
- **Stefan Hartwig** — confirmed user per VGMPF

### Technical requirement note
> "The manual assumes that you are familiar with hexadecimal numbering and features of the SID
> chip, except for the filter, which is kept off."

This is significant: ROM's Fix exposes SID registers directly, and RoMuzak itself likely follows
the same philosophy. The filter-disabled constraint in ROM's Fix may or may not apply to RoMuzak's
music player — the research.md instrument block (+$0018) explicitly lists "filter" as a parameter,
so RoMuzak music DOES use the filter, unlike ROM's Fix.

---

## Known bugs

### Bug: "First note sometimes muted" (V6.3 confirmed)

**Source:** VGMPF Tube_Madness_(C64) and Clik_Clak_(C64) pages

Direct quotes:
- (Tube Madness): *"Tracks 2–4 suffer under RoMuzak's most common bug, namely the first note
  sometimes being muted."*
- (Clik Clak): *"The looping songs suffer under its most common bug, namely the first note
  sometimes being muted."*

This is explicitly labelled "RoMuzak's most common bug" in both sources, implying it is a
documented, well-known artefact of the V6.3 player that scene members were aware of.

**Context:**
- Tube Madness (1991, Digital Excess / CP Verlag): affects tracks 2–4 specifically
- Clik Clak (1992, Idea): affects looping songs

**Hypothesis:** The bug is likely a per-voice initialization defect: on song start or loop restart,
the voice-N pattern pointer is advanced one position too early, consuming (and silencing) the
intended first note before it can produce output. This would appear as a muted first note per
affected voice. Whether this was fixed in V7.96 is unknown.

**USF implications:** When extracting patterns from V6.3 SIDs, be aware that the first row of
certain voices may be consumed silently by the player — the extracted pattern data at position 0
IS the intended note but the player skips/mutes it on first play. During verification, the rebuilt
SID must reproduce this behaviour to match the original write-log.

---

## Known RoMuzak songs in HVSC (DEMOS/UNKNOWN with STIL notes)

From HVSC STIL.txt (https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/STIL.txt):

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

All three are attributed to "Link" (Klaus Engell Grøngaard, Danish composer) — the ORIGINAL
source tunes are by Link in Future Composer format. Someone (unknown) ran RoMuzak's FC V1.0
conversion feature to produce these RoMuzak-format versions. These DEMOS/UNKNOWN entries are
the converted output, not authored by Blasnik.

**Significance for RE:** These tunes are known FC→RoMuzak conversions. Comparing the original
FC SID (e.g., /MUSICIANS/L/Link/Game_Intro.sid) against the RoMuzak conversion (Crazy_Granpa.sid)
would directly reveal how RoMuzak translates FC V1.0 instrument structures into its own format.

---

## The Future Composer conversion feature

**Confirmed:** "RoMuzak can convert Future Composer V1.0 songs." (VGMPF Future_Composer page)

**What this likely means (mode analysis):**
From github_fc_relationship.md (pre-existing project doc): the most likely conversion mode is
full re-encode — RoMuzak reads FC V1.0 pattern/instrument data and writes it out in RoMuzak's
native format. The resulting SID contains RoMuzak's player code, not FC's player.

Evidence supporting full re-encode:
1. The sidid byte signatures are unambiguously the RoMuzak player, present in converted tunes.
2. The STIL notes say "converted FROM Future Composer TO RoMuzak" — language implies format change.
3. V7's different note byte encoding (AND #$07) means the conversion target changed between versions.

**What survives the conversion:** Melody data (note values), basic rhythm (durations), and
instrument parameters (ADSR, waveform selection). Complex FC effects that have no equivalent in
RoMuzak's simpler model would be dropped or approximated.

---

## SID chip compatibility notes

Several VGMPF pages note chip model preferences for RoMuzak music:

- Marc Liedtke: "arranged in RoMuzak V6.3 on an 8580 chip"
- Paolo Galimberti: "most songs optimized for the 6581 chip with bias of at least 100 in VICE 3.6"
- Clik Clak: "music constantly toggles SID's filter, causing unpleasant clicks on the 6581 chip,
  but not on the 8580" — filter use causes 6581/8580 incompatibility
- Brubaker: "recorded from the game running in VICE 3.2 with the model 6581 (ReSID) and a filter
  bias of 100" — 6581 is the target chip

This means RoMuzak music frequently uses the filter (confirmed by +$0018 instrument block having
filter parameters), and the filter behaviour differs between 6581 and 8580. Both chips were in
use by composers. **The filter IS part of the instrument model** in RoMuzak (unlike ROM's Fix).

---

## Publisher and game context

Digital Marketing published RoMuzak commercially as a boxed C64 product (1989). The software was
also distributed via the German scene cracker network (Cosmos/Antitrack crack, Apa-Soft import).

Games that used RoMuzak V6.3 music (not a complete list):

| Game | Year | Publisher | Composer |
|------|------|-----------|----------|
| Double Sphere | 1990 | Golden Disk 64 / CP Verlag | Stefan Hartwig |
| Logo | 1990 | Starbyte (dev: Digital Marketing) | Stefan Hartwig |
| Tube Madness | 1991 | CP Verlag / Game On | Stefan Hartwig |
| Brubaker | 1992 | Golden Disk 64 / Byteriders | Stefan Hartwig |
| Clik Clak | 1992 | Idea | Paolo Galimberti |
| MoonShadow | 1990 | ? | Paolo Galimberti |
| F1 GP Circuits | 1991 | ? | Paolo Galimberti |
| Lupo Alberto | 1991 | Idea | Paolo Galimberti |
| Atomino | 1991 | Software 2000 | Hans-Hermann Franck |
| Shiftrix | 1991 | Software 2000 | Hans-Hermann Franck |
| Wild West World | 1990–1991 | Software 2000 | Hans-Hermann Franck |
| Kopido | 1992 | ? | Marc Liedtke |
| Triget | 1992 | ? | Marc Liedtke |
| Ultrix | 1991 | ? | Lars Hutzelmann |
| Oskar | 1992 | ? | Lars Hutzelmann |
| 12 O'Clock | 1992 | ? | Lars Hutzelmann |

Note: Oliver Blasnik himself is an uncredited programmer on Clik Clak (1992) — the game uses
RoMuzak V6.3 for music (by Galimberti) while Blasnik contributed programming code.

---

## Forum64 Digital Marketing thread (blocked during research)

URL: https://www.forum64.de/index.php?thread/83160-digital-marketing/
Status: HTTP 403 during this research session.

From search snippet context, this thread contained:
- Discussion of Digital Marketing as a publisher
- Mention that someone made a Kryoflux image of the RoMuzak disk
- RoMuzak copy protection discussion

Page 3 URL: https://www.forum64.de/index.php?thread/83160-digital-marketing/&pageNo=3
(Also blocked)

**OPEN:** Re-fetch both pages when Forum64 allows access. May contain disk-format documentation
or copy protection analysis that reveals the structure of the editor disk.

---

## Other scene references

### Polish C64 scene forum (c64scene.pl) — NOW FETCHED
URL: https://www.c64scene.pl/viewtopic.php?t=112
Thread poster doing the decomposition: **skull**

**Direct quote from skull (post #13), translated from Polish:**
> "I even got to dividing the generator loops... but unfortunately even 'individually' I could not
> find enough free raster... for a single iteration (for one track) to consume even up to
> twenty-something raster lines is excessive for me."

Key findings from the thread:
- The player was successfully disassembled using **64COPY**
- skull separated each voice channel to be callable individually ("każdy kanał wywołuje indywidualnie")
- skull removed the **author validation routines** — described as
  "validation routines checking author credits and similar data"
  ("zabezpieczenie sprawdzające kilka danych (głównie tekst autora i takie takie)")
- After stripping validation, the per-channel call structure worked correctly for demo use

**In-binary author string (from skull's post #13, exact text):**
```
OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!!
```
This includes a **phone number: 02435-1295** — Oliver Blasnik's personal or business phone
(Germany, 02435 = area code for Bedburg / Erftkreis area, North Rhine-Westphalia). This is
additional biographical data confirming the author's location.

**Raster cost:** ~20+ raster lines per single channel call on the unoptimized original player.
This means three voices = ~60+ raster lines per play() call — a significant CPU burden for
games using RoMuzak alongside other interrupt-driven code.

**Per-channel call structure confirmed:** The original player's voice routines are individually
callable after decomposition. This is consistent with a dispatch-table or jump-table structure
internally, where each voice has its own update loop.

### Woolyss chipmusic trackers listing
URL: https://woolyss.com/chipmusic-chiptrackers.php?s=Commodore
(Returned in search results but not fetched — may list RoMuzak in a C64 tracker index)

### Musik-Demo-Editor (Archive.org disk descriptor)
Publisher on Archive.org listing: **ACT** (not Digital Marketing).
This may be an alternate distributor or a different packaging (demo version vs full).
The disk (Romuzak_Music_Demo-Editor_1989_ACT_501.d64, 170.8 KB) is likely a demo/sampler
distribution of the editor — the "ACT 501" catalogue number suggests ACT is the distributor.
Separately, the "Analyser Play Construction Kit" (also ACT 501, same catalogue number) is a
companion disk — perhaps the "analyser" portion is a separate module from the "editor" portion.

---

## Leads to follow

- **HIGH PRIORITY:** Fetch the three DEMOS/UNKNOWN FC-to-RoMuzak conversion SIDs from HVSC and
  compare against their source FC SIDs. This directly reveals FC→RoMuzak data translation rules.
  Target files:
  - HVSC: /DEMOS/UNKNOWN/Crazy_Granpa.sid → source: /MUSICIANS/L/Link/Game_Intro.sid
  - HVSC: /DEMOS/UNKNOWN/Children_Songs.sid → source: /MUSICIANS/L/Link/Boingsongs.sid
  - HVSC: /DEMOS/UNKNOWN/Alfs_Cat_Rap.sid → source: /MUSICIANS/L/Link/Alf_Theme.sid

- **HIGH PRIORITY:** Polish scene forum thread (https://www.c64scene.pl/viewtopic.php?t=112) —
  user "skull" decomposed the player into per-channel calls. This thread likely contains
  per-channel routine address offsets. Re-fetch and read in full.

- **OPEN:** Woolyss tracker listing — fetch https://woolyss.com/chipmusic-chiptrackers.php?s=Commodore
  and search for RoMuzak entry (may have feature table or links to documentation).

- **OPEN:** Archive.org "Analyser Play Construction Kit" disk
  (https://archive.org/download/d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501/Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501.d64)
  — What is the "analyser" component? Is it a SID-register viewer/analyser tool, or an alternate
  name for the song player? Extract and examine disk directory.

- **OPEN:** VGMPF pages not yet fully fetched:
  - Georg_Brandt (what was "his last game" using RoMuzak?)
  - Brubaker_(C64) (Stefan Hartwig's RoMuzak usage details)
  - Slot_-_Clik_Clak_(AMI,_C64) (cross-platform context for Galimberti's work)
  - Song_Credits:_R (full RoMuzak directory listing with all known songs)

- **OPEN:** Markus Schneider (VGMPF) used ROM's Fix for sound effects in Timezone — but used his
  OWN custom driver for music. Worth confirming: did any Digital Marketing games use BOTH RoMuzak
  music AND ROM's Fix SFX together in the same game binary?

- **OPEN:** The "Ass It" composer (56 RoMuzak tunes in HVSC, largest corpus) is not mentioned in
  any VGMPF page found. Identify who "Ass It" is (handle) and whether they left any scene
  documentation about how they used RoMuzak.
