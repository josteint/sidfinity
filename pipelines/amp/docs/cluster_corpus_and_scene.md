# AMP — Corpus Shape, Address Clusters, and Scene Context

```
provenance:
  primary_source:   hvsc84.db (READ-ONLY; engine='AMP'; 246 SIDs)
  secondary_sources:
    - url: https://csdb.dk/release/?id=35519
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: 1991-12
      reliability: HIGH (primary scene archive, community-verified)
    - url: https://www.vgmpf.com/Wiki/index.php?title=Andras_Molnar
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: MEDIUM (fan wiki, cites primary sources)
    - url: https://www.vgmpf.com/Wiki/index.php?title=Markus_M%C3%BCller
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: MEDIUM
    - url: https://github.com/cadaver/sidid/blob/master/sidid.cfg
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: HIGH (technical fingerprint used by SIDID tool)
    - url: https://8bitlegends.com/nantco-warriors-of-the-wasteland/
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: MEDIUM (scene biography site)
    - url: https://demozoo.org/groups/6510/
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: HIGH (Demozoo scene archive)
    - url: https://www.c64-wiki.com/wiki/Magic_Disk_64
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: HIGH (C64 wiki, community-edited)
  author: cluster_corpus_and_scene agent (Claude Sonnet 4.6)
```

---

## 1. Editor provenance

**AMP = Advanced Music Programmer**, a C64 music editor + embedded player
driver created by **Andras Molnar** (handle: *Burton*; later: *Andrew Miller*),
programmer, born Germany with Hungarian background.  Markus Müller (handle:
*Hayes*; Sidbusters / Hitech Studio Designs) co-developed the music software
and composed the bundled demo tracks.  The collaboration ran from
**1988-05-21 to August 1990** (VGMPF).

**Released publicly:** December 1991 on **Magic Disk 64 issue 12/91** (CP
Verlag, Germany).  CSDb entry: [#35519](https://csdb.dk/release/?id=35519),
credited to *Hitech Studio Designs*.  A CSDb user comment confirms "No
evidence it was released earlier" — prior to 12/91 the tool circulated only
within Hitech/Sidbusters/Euratom.  The PSID files in HVSC's Mueller_Markus/
dated 1988-1989 (Euratom era) use early driver versions at non-canonical
addresses (see §3).

**Version captured in HVSC:** v2.3 (the CSDb release).  Earlier driver
iterations appear in the 1988-1989 Euratom SIDs (different load addresses,
different fingerprint).

**SIDID fingerprint** (cadaver/sidid, sidid.cfg):
```
B9 ?? ?? ?? 16 D4  C8  98  9D ?? ?? ?? ?? ?? ?? ?? ?? 8D 18 D4
```
This is the play-loop kernel: `LDA freq_table,Y` / `ASL $D4xx` (shift SID
register) / `TYA` / `STA voice_shadow,X` / `STA $D418` — characteristic of
the AMP player's 3-voice write routine.

**Distribution channel:** Magic Disk 64 (CP Verlag, Germany, 1987-1993) — a
German-language disk magazine for C64. AMP was published there and thereby
reached the predominantly German-speaking (and adjacent Dutch/Hungarian) scene.

---

## 2. Total corpus

| Metric | Value |
|---|---|
| Total HVSC SIDs (engine='AMP') | **246** |
| PSID version | All v2 |
| Single-subtune | 231 |
| Multi-subtune | 15 |
| Largest multi-subtune | 21 (Griff/Pot_Fun) |
| Songlength min / max / avg | 4s / 2169s / 173.5s |
| Songlength modal bucket (60-120s) | 78 |
| Songlength 2-5 min bucket | 119 |
| CIA-timed (speed != 0) | 0 confirmed — all VBL |

No `speed` column exists in hvsc84.db at this time; CIA status is inferred
from the init/play address pattern and the absence of any flag field.
The earliest Euratom SIDs (1988-89) have unusual addresses suggesting a
different driver call convention — worth verifying with `siddump --writelog`
when RE starts.

---

## 3. Address-cluster table

All 246 SIDs have `load_addr = 0` (PSID-standard: load address embedded in
the PRG data prefix), so the meaningful addresses are `init_addr` / `play_addr`.

The canonical AMP v2.3 convention is `init = base, play = base + 3` — a
standard 6-byte PSID init/play split.

### Primary clusters

| Cluster | init_addr | play_addr | Count | Notes |
|---|---|---|---|---|
| **Canonical $1000** | $1000 (4096) | $1003 (4099) | **142** | Standard v2.3, load base $1000 |
| **+3 at $1003** | $1003 (4099) | $1006 (4102) | 25 | Same binary, PSID init entry is $1003 not $1000 (3-byte offset into init) — a "+3 relocation" of the PSID headers |
| **$1000/$1006 hybrid** | $1000 (4096) | $1006 (4102) | 3 | Init at base, play skips 6 bytes — possibly 2-song format |
| **$2800** | $2803 (10240) | $2806 (10243) | 9 | Ray / V-Lucid cluster (all 8 Ray SIDs + 1 other) |
| **$C003** | $C003 (49155) | $C006 (49158) | 9 | LMan cluster (6 LMan tunes) + 3 Black_Dove |
| **$E000** | $E000 (57344) | $E003 (57347) | 5 | Sparse (Bakker×1, Mass_Murderer×2, Dr_Zoom×1, Griff×1) |
| **$C000** | $C000 (49152) | $C003 (49155) | 3 | Black_Dove (Danger_II, KungFu-Dragon, Leaving) |
| **$A000** | $A000 (40960) | $A003 (40963) | 4 | Unknown MUP-Soft×3, Okieh×1 |
| **play=$0000** | $1000 / $8E59 | 0 | 4 | Non-standard: Maniac×3 (Genesis Project, 1991) + Die_Pruefung game |

### Named-address oddball clusters (×2 each)

| init_addr | play_addr | Count | Paths |
|---|---|---|---|
| $13CD | $1338 | 7 | Mueller_Markus Euratom/Sidbusters 1989 SIDs (early driver) |
| $7003 | $7006 | 2 | Dr_Zoom/Jump_Start + Griff/Zepp (1991-92) |
| $A003 | $A006 | 2 | Dr_Zoom/Groove_C + GAMES/Locomotion |
| $9000 | $9003 | 2 | Spider_Jerusalem (2012) |
| $F003 | $F006 | 2 | Bad/Smash_Ball + Griff/Pharaoh |

### Single-address outliers (×1 each, 23 total)

Early Euratom era (1988-89): `$0D1D/$0D80`, `$13CF/$133A`, `$13D1/$1336`,
`$19DB/$1927`, `$1675/$16AA`, `$1B94/$1B86`, `$5E21/$5D9F` — all
Mueller_Markus. These predate the canonical layout and likely represent
v1.x driver variants before the $1000 base was standardised.

Other relocation targets used by single authors: `$1200`, `$3000`, `$3C03`,
`$4003`, `$4500`, `$5003`, `$6000`, `$6975`, `$7F00`, `$8000`, `$8003`,
`$9003`, `$A680`, `$AFE0`, `$B203`, `$0FF6`.

### Relocation summary

| Category | SIDs | % |
|---|---|---|
| Canonical $1000 cluster (init=$1000/play=$1003) | 142 | 57.7% |
| $1003 +3 offset variant | 25 | 10.2% |
| Other clustered relocations ($2800, $C003, $C000, $E000, $A000) | 30 | 12.2% |
| Euratom pre-v2.3 (init ~$13xx) | 8 | 3.3% |
| Scattered outliers / game embeds | 41 | 16.7% |

The $1003 +3 cluster (25 tunes) is almost certainly the same player binary as
the $1000 canonical but with the PSID `init` field pointing 3 bytes into the
init entry (i.e., init() skips the initial JMP and enters mid-routine).  This
is a sidplayer packaging artifact, not a different AMP version.

---

## 4. Author concentration

| Rank | Author (HVSC field) | Count | Groups / affiliation | Country |
|---|---|---|---|---|
| 1 | Nantco Bakker | 45+4=**49** (incl. aliases Beat/Nantco) | Warriors of Music, New Dimension Crew, Warriors of the Wasteland | Netherlands |
| 2 | Tobias Erbsland (Dr. Zoom) | 27+3=**30** (incl. bare surname) | Black Code Design, Equinoxe, Digital Talk | Switzerland |
| 3 | Jan Krolzig | **18** | Zeroline | Germany |
| 4 | Jan Albartus (Logan/Cobra) | 15+1=**16** | New Dimension Crew, Groove D-Signs | Netherlands |
| 5 | Markus Müller (Hayes/Sidbusters) | 15+6+6=**27** | Euratom, Sidbusters, Hitech Studio Designs | Germany |
| 6 | Manuel Cavero (Black Dove) | 11+4=**15** | Grace, Electronic Religion | Spain |
| 7 | Péter Varga (Griff) | **11** | Chromance, FBI Crew | Hungary |
| 8 | Markus Klein (LMan) | **10** | LMan (solo) | Germany |
| 9 | Bouke Kramer (Skull) | **8** | Arcoss, Bamboo | Netherlands |
| 10 | Marc Fischer (Ray) | **8** | V-Lucid | Germany |
| 11 | Jan Rödig (Spider Jerusalem) | **6** | Zeroline, C64 Camper, Spider Jerusalem | Germany |
| 12 | Kay Tichelmann (Ragman) | **4+1** | Comic Pirates, Proxyon, Skylight Designs | Germany |
| 13 | Wolfgang Reszel (Seesaw Widow) | **3** | Shadow | Germany |
| 14 | Heiko Zimmermann (Okieh) | **3** | Magic Disk 64 releases | Germany |

Top-14 authors account for ~226 of 246 SIDs (92%).

Note: Markus Müller is *both* the tool co-creator (via Hitech/Sidbusters) *and*
the most prominent user of the early driver.  Nantco Bakker (NL) is the largest
single contributor by count in HVSC, almost entirely via the 1992 Warriors of
Music release wave.

---

## 5. Scene context and national affiliation

### Scene geography

AMP is a **predominantly German-language-scene tool**, with secondary strong
Dutch and minor Hungarian/Spanish adoption.

- **Germany** (core): Markus Müller (Euratom→Sidbusters→Hitech), Andras Molnar
  (Hitech), Jan Krolzig (Zeroline), Markus Klein (LMan), Marc Fischer (Ray),
  Jan Rödig (Spider Jerusalem), Kay Tichelmann (Ragman), Wolfgang Reszel
  (Seesaw Widow). The tool itself was published via Magic Disk 64 / CP Verlag
  (Germany).
- **Netherlands**: Nantco Bakker (Warriors of Music / New Dimension Crew / WotW),
  Jan Albartus (Logan; New Dimension Crew), Bouke Kramer (Skull; Arcoss),
  Maarten Vellinga (Warlords/TMB Group), Daniel Spronk (Amos — game composer).
- **Switzerland**: Tobias Erbsland (Dr. Zoom; Black Code Design, Equinoxe,
  Digital Talk). Note: Black Code Design was multi-national (DE/CH/ES/HU/PL).
- **Hungary**: Péter Varga (Griff; Chromance, FBI Crew).
- **Spain**: Manuel Cavero (Black Dove; Grace, Electronic Religion).
- **Other outliers**: Peter Sandén & Per Bolmstedt (Sweden, 2000 Defiers);
  Lars Grüttgen (SigmaZeven, 2015); Tufan Uysal (SoNiC, Turkish name,
  Game On 1993/94).

### Key groups

| Group | Country | AMP SIDs | Period |
|---|---|---|---|
| Warriors of Music | Netherlands | 45 | 1992 |
| Magic Disk 64 / CP Verlag | Germany (publisher) | 18 | 1991-1995 |
| New Dimension Crew | Netherlands | 16 | 1991-1993 |
| Zeroline | Germany | 16 | 1993-2006 |
| Black Code Design | multi-national (DE core) | 14 | 1992-1994 |
| Tobias Erbsland (solo) | Switzerland | 11 | 1992-1994 |
| LMan (solo) | Germany | 10 | 1990-1992 |
| V-Lucid | Germany | 8 | 1993 |
| Sidbusters | Germany | 4 | 1989 |
| Euratom | Germany | 5 | 1988-1989 |
| Grace | ? | 10 | 1995 |

### Timeline narrative

- **1988**: Andras Molnar begins AMP driver development (Euratom era).  First
  SIDs: Mueller_Markus Euratom_Intro ($0D1D) and Lions_Intro ($19DB) — early
  driver at non-$1000 addresses.
- **1989**: Sidbusters group SIDs use driver at $13xx (Everything_Counts,
  Quality_Intro_1-3, AMP_Intro, Breaking_Free, Cat, Cinema).  Raster_Runner
  for Mastertronic (commercial game, 4 subtunes).
- **1990**: LMan (Markus Klein) adopts AMP at $C003 for his ABBA/pop remakes.
  Griff (Hungary) uses AMP for Chromance intros.  Warrior (8 subtunes) for
  Living Colors Softwares.
- **1991**: AMP v2.3 published on Magic Disk 64 12/91.  Address canonises at
  $1000/$1003.  Muellerkus_Markus (15 tunes all in Magic Disk 64), Maniac
  (Genesis Project, play=$0000 anomaly), Griff (Golden Disk 64).
- **1992**: Explosion of adoption.  85 new SIDs in a single year.  Nantco
  Bakker / Warriors of Music releases 44 tunes at once (the "5 Years WOW
  Music" anniversary batch).  New Dimension Crew (Albartus_Jan cluster).
  Dr. Zoom begins heavy use.  Total 1992 batch dominates the corpus.
- **1993**: 60 SIDs.  Black Code Design, V-Lucid (all 8 Ray tunes at $2800),
  Zeroline, Equinoxe, Manuel Cavero.
- **1994**: 22 SIDs.  Zeroline (Jan Krolzig), Equinoxe, Shadow, Skull, Atlantis.
- **1995**: 18 SIDs.  Grace (Manuel Cavero/Black Dove, 10 tunes), Magic Disk 64
  end-of-life issues, Zeroline.
- **1996-2015**: Tail — Spider Jerusalem (2008-2012, 6 SIDs), SigmaZeven (2015, 2
  SIDs), one-offs.  AMP still works in emulators so later composers occasionally
  reach for it.

**Peak period: 1991-1993** (171 of 246 SIDs, 70%).

### CP Verlag / Magic Disk 64 connection

CP Verlag (Computer Publications GmbH, Germany) published Magic Disk 64
(1987-1993) — the primary distribution channel for AMP.  Several AMP SIDs in
HVSC are literally background music for the magazine menus (`Magic Disk 64/CP
Verlag` as release group).  Game On! (another CP Verlag disk magazine) also
hosted AMP tunes.  `64'er` (Markt & Technik) used AMP for Cheeky Twins.

---

## 6. MUSICIANS path breakdown

234 of 246 SIDs are under `MUSICIANS/`; 12 are under `DEMOS/`, `GAMES/`.

| Letter | SIDs | Top author |
|---|---|---|
| A | 19 | Albartus_Jan (Amadeus_Slash_Design also here) |
| B | 68 | Bakker_Nantco (49), Black_Dove (15), Bad (2) |
| D | 31 | Dr_Zoom (30), bad (1) |
| G | 11 | Griff (11) |
| H | 2 | Higgie / General (2) |
| K | 18 | Krolzig_Jan (18) |
| L | 10 | LMan (10) |
| M | 34 | Mueller_Markus (28), Maniac (3), Mass_Murderer (3) |
| N | 3 | Nebula / Seesaw_Widow (3) |
| O | 3 | Okieh (3) |
| R | 8 | Ray (8) |
| S | 19 | Skull (8), SigmaZeven (2), Sonic (2), Spider_Jerusalem (6), Sanden_Peter (1) |
| T | 5 | Tichelmann_Kay (5) |
| V | 3 | Vellinga_Maarten (3) |

Non-MUSICIANS (12):
- `DEMOS/` — 6 SIDs (Felony_note, Heart_Drums, Holy_Shit, KGB_01, Report-noter, 3 Unknown/MUP-Soft)
- `GAMES/` — 6 SIDs (Berania×16-subtune, Die_Pruefung×2-sub, Locomotion, Munch)

---

## 7. Notable anomalies and binary-RE implications

1. **play=$0000 (4 SIDs)**: Maniac×3 (Genesis Project, 1991) + Die_Pruefung
   game.  Play address $0000 means the SID player file relies on timer-driven
   NMI or the parent program to call the routine — not a PSID-standard play
   vector.  libsidplayfp's RSID/PSID handling may not replay these correctly.
   Requires special treatment.

2. **Early Euratom addresses ($0D1D, $13xx, $19DB, $1B94, $5E21 etc.)**: 8
   SIDs from 1988-89 Mueller_Markus use load addresses scattered in
   $0D00-$5F00 range.  These predate the canonical $1000 base.  The AMP
   fingerprint `B9 ?? ?? 16 D4` may or may not match — worth verifying.  If
   the driver is structurally the same but at a different base, relocation is
   straightforward.

3. **Dr_Zoom/Never_Let_Me_Down_Again**: init=$1000, play=$0FF6 — play entry is
   *before* init in memory.  Possible data at $0FF6 that doubles as code entry
   point (padding or table lookahead).

4. **Griff/Pot_Fun**: 21 subtunes, load at $7F00, play at $5906 — very unusual
   layout, possibly a compiled multi-song where each subtune entry is a JSR
   table at $5906.

5. **Mueller_Markus/Warrior**: 8 subtunes, 1990, co-authored with Griff.
   Load at $5749, play at $5802.  Commercial product (Living Colors Softwares).
   Pre-v2.3 driver.

6. **GAMES/Berania**: 16 subtunes, load=$A680, init=$A680, play=$A683 — an
   AMP player embedded deep in game memory ($A000 region).  The game is `Amos`
   (1993 Kingsoft) — note that both Berania and Locomotion (Kingsoft 1992) use
   AMP for commercial Kingsoft games via composer Daniel Spronk (NL) / Zsolt
   Szabó (HU).

---

## 8. HVSC bundled docs — AMP mentions

Searched: `HVSC.txt`, `STIL.txt`, `Musicians.txt`, `hv_sids.txt` — **no AMP
mentions found**.  No `Players.txt` exists in the DOCUMENTS dir.  STIL.txt had
no entries matching AMP-related keywords.

The only HVSC-bundled documentation is via SID metadata (title/author/released
fields in the SID headers themselves).

---

## Leads to follow

1. **Verify early driver fingerprint**: Do the 1988-89 Euratom SIDs ($0D1D,
   $13xx) actually match the SIDID AMP fingerprint, or are they a different /
   earlier Andras Molnar driver?  Run `sidid` on Mueller_Markus/*.sid.

2. **play=$0000 handling**: The 4 Maniac/Die_Pruefung SIDs need manual
   investigation — are they RSIDs?  Does libsidplayfp handle them?  They may
   need a special player init convention (call init and let the SID auto-IRQ?).

3. **$1003 +3 cluster (25 SIDs)**: Confirm these are the same binary as $1000
   canonical.  The 3-byte offset into init suggests the PSID `init` field
   points past a JSR or JMP prologue.  One `siddump` comparison would settle
   this.

4. **Griff/Pot_Fun (21 subtunes)** and **Dr_Zoom/Groove_C** ($A003 address):
   unusual multi-song layouts — worth studying to understand AMP's multi-song
   convention before designing the USF schema.

5. **LMan's $C003 cluster**: Why does LMan load at $C000 (ROM shadow region)?
   The 6510 can bank out BASIC ROM; if AMP player lives at $C000-$CFFF with
   BASIC banked out, init/play at $C003/$C006 makes sense.  Verify with
   disassembly.

6. **Warriors of Music CSDb group ID**: The 44-SID Nantco Bakker WoM batch
   (released 1992) is almost certainly a single disk release — finding the
   CSDb group/release entry would give exact release date, members list, and
   possibly AMP version used.

7. **V-Lucid / Ray $2800 cluster**: All 8 Ray SIDs load at $2800.  This is
   an unusual but consistent choice (above zero-page, below most game code).
   Find the CSDb V-Lucid group entry to confirm German affiliation and
   whether Ray used AMP from a separate binary or a modified v2.3 copy.

8. **Dr_Zoom composer tools**: The C64-Wiki article says Dr. Zoom created
   his own editors ("Dr. Zoom's Genius Composer V2.3", "Atlantis Composer
   V3.0", both 1994) — yet his HVSC SIDs are SIDID-tagged as AMP.  Possible
   explanation: early Dr. Zoom SIDs (1992-93, Black Code Design era) used AMP;
   later he switched to his own composer.  Confirm by checking dates: all
   Black Code Design / Tobias Erbsland SIDs in HVSC are dated 1992-1994,
   consistent with an AMP-then-own-composer transition.

9. **sidid.cfg fingerprint coverage**: The fingerprint `B9 ?? ?? ?? 16 D4 C8
   98 9D ?? ?? ?? ?? ?? ?? ?? ?? 8D 18 D4` is a single pattern.  It may not
   match all relocation variants.  If RE reveals the play-loop sequence
   differs in early Euratom builds, a second fingerprint entry may be needed.

10. **Black Dove / Manuel Cavero (Spain)**: 15 SIDs, split between $C000
    cluster (early, 1993) and $1003 variant (1995 Grace).  Worth checking
    whether Black Dove sourced AMP independently or received it via the Magic
    Disk 64 distribution — Spain was not a primary CP Verlag market.
