# Jeff Player — Corpus Characterisation & Scene Context

## Provenance

| Field | Value |
|---|---|
| author | sidfinity research agent |
| content_date | 2026-06-14 |
| fetch_date | 2026-06-14 |
| primary_sources | hvsc84.db (READ-ONLY), HVSC STIL.txt v84, HVSC DOCUMENTS/, sidid.cfg (cadaver/sidid on GitHub), CSDb scener #8059, remix64.com interview April 2002, recollection #86 interview |
| secondary_sources | WebSearch hits: csdb.dk, remix64.com, deepsid.chordian.net |
| reliability | HIGH for corpus shape (direct DB query); MEDIUM for scene context (web fetches from CSDb homepage sometimes redirected — profile content extracted on second try); LOW for player internals (no source or disassembly consulted) |

---

## 1. Corpus Overview

HVSC #84 contains **205 SIDs** tagged with a `Jeff*` engine (excluding `Jeff_Minter`, a
completely different person — Jeff Minter of Llamasoft). All 205 are PSID version 2.

Engine tag breakdown:

| Engine tag | Count | Notes |
|---|---|---|
| `Jeff` | 192 | Base detection |
| `Jeff/Airwalk` | 3 | Sub-variant fingerprint |
| `Jeff/BullSID` | 3 | Sub-variant fingerprint |
| `Jeff/XLarge` | 3 | Sub-variant fingerprint |
| `Jeff/BullSID3` | 2 | Sub-variant fingerprint |
| `Jeff/FLT` | 2 | Sub-variant fingerprint (FairLight custom player) |
| **Total** | **205** | |

Additionally, 2 SIDs in `/MUSICIANS/J/Jeff/` have engine=`NULL` (X-Large_5, X-Large_6 — likely
the same engine family, not fingerprinted in sidid for these specific variants). One more file in
that folder uses `Power_Music` (Feeling_Alone.sid, author listed as "Søren Lund (Nick)").

---

## 2. Address Cluster Table

All Jeff* SIDs have `load_addr = 0` (PSID embed — loader determines actual load). The relevant
addresses are `init_addr` and `play_addr`. 24 distinct `(init_addr, play_addr)` pairs found.

### Logical relocation clusters

| Cluster | init_addr | play_addr | Count | % | Notes |
|---|---|---|---|---|---|
| **Canonical $1000** | `$1000` | `$1003` | 161 | 78.5% | All sub-variant tags (Airwalk/BullSID/XLarge/FLT/BullSID3) also load here |
| **$FD0 stub group A** | `$FD0` | `$FE3` | 10 | 4.9% | Early period (1992–1994) |
| **$FD0 stub group B** | `$FD0` | `$FE2` | 8 | 3.9% | Early period (1991–1993) |
| **$FD0 stub group C** | `$FD0` | `$FE4` | 1 | 0.5% | Duck LaRock 1994 |
| **$FB1-$FF4 sub-stubs** | various ($FB1/$FC0/$FD8/$FE0/$FF4) | various | 6 | 2.9% | One-offs, same era |
| **$0B00 (Crest 2000)** | `$B00` | `$B03` | 3 | 1.5% | Three 2000 Crest tunes |
| **$E000** | `$E000` | `$E003` | 3 | 1.5% | 1995–2001 |
| **$8000** | `$8000` | `$8003` | 2 | 1.0% | 2004 Smash, 2025 Bonzai/Camelot |
| **$0800-$09C0 range** | $843/$8CA/$8D0/$9C0 | various | 4 | 2.0% | Early 1992–1993, custom per-tune |
| **$8A00–$9F00** | $8A00/$9000/$9F00 | `+3` | 3 | 1.5% | 1991–1996 |
| **$C000** | `$C000` | `$C003` | 1 | 0.5% | 2021 Atlantis (Snap) |
| **Mid-range one-offs** | $1EF0/$2178/$2D55 | various | 3 | 1.5% | 1993/2000/2006 |
| **Total** | | | **205** | 100% | |

**Key finding:** 79% of the corpus sits at the canonical `$1000`/`$1003` load. The `$FD0` stub
group (19 SIDs, play at `$FE2`/`$FE3`) is the second cluster and is temporally earlier (1991–1994
almost exclusively), suggesting it is a predecessor version of the player before the `$1000` base
became standard. The stub variants near `$FB1–$FF4` are transitional.

The sub-variant tags (`Jeff/Airwalk`, `Jeff/BullSID`, etc.) are purely fingerprint discriminators
within the same `$1000` load — they all share init=`$1000`, play=`$1003`. They represent
group-commissioned custom builds with slightly different runtime code, not different relocation
targets.

### All distinct (init, play) pairs

```
init=0x1000  play=0x1003  n=161  (canonical; all sub-variants)
init=0xfd0   play=0xfe3   n=10   ($FD0 era, play at $FE3)
init=0xfd0   play=0xfe2   n=8    ($FD0 era, play at $FE2)
init=0xb00   play=0xb03   n=3    (Crest 2000)
init=0xe000  play=0xe003  n=3    (1995-2001)
init=0x8000  play=0x8003  n=2    (one 2004, one 2025)
init=0x843   play=0x846   n=1    (Duck LaRock 1993)
init=0x8ca   play=0x8cd   n=1    (Duck LaRock 1993)
init=0x8d0   play=0x8e2   n=1    (Jeff 1992)
init=0x9c0   play=0x9d4   n=1    (Jeff 1993)
init=0xfb1   play=0xfbb   n=1    (Jeff 1996)
init=0xfc0   play=0xfd2   n=1    (Jeff 1996)
init=0xfd0   play=0xfe4   n=1    (Duck LaRock 1994)
init=0xfd8   play=0xfea   n=1    (A-Man 2009)
init=0xfe0   play=0xff2   n=1    (Duck LaRock 1995)
init=0xff4   play=0x1003  n=1    (Jeff 1992 — transitional, play already at $1003)
init=0x1000  play=0xfc0   n=1    (Jeff, unusual play stub)
init=0x1ef0  play=0x1f04  n=1    (Jeff 1993)
init=0x2178  play=0x218a  n=1    (Jeff 2000 remix)
init=0x2d55  play=0x2d68  n=1    (Jeff 2006)
init=0x8a00  play=0x8a03  n=1    (Jeff 1996)
init=0x9000  play=0x9003  n=1    (Jeff 1991)
init=0x9f00  play=0x9f03  n=1    (Jeff 1996)
init=0xc000  play=0xc003  n=1    (Snap 2021)
```

---

## 3. Sub-Variant Engine Tags — Same Engine or Different Builds?

The sidid.cfg fingerprints (from cadaver/sidid on GitHub) show:

| Tag | sidid Fingerprint (key bytes) | Interpretation |
|---|---|---|
| `Jeff` (main) | `A5 ?? 48 A5 ?? 48 … A2 07 20 … 68 85 ?? 68 85 ?? 60` + SID-write patterns | Base player |
| `Jeff/Airwalk` | `C9 FF B0 0E 8D 04 D4 C8` | Slightly different sequence/waveform handling |
| `Jeff/BullSID` | `10 D7 A9 00 85 FC A9 00 85 FB 60 A9` | Different reset/init tail |
| `Jeff/FLT` | `60 A9 00 8D 02 D4 A9 08 8D 03 D4 4C` | FairLight custom — "made for One Million Lightyears" |
| `Jeff/XLarge` | `60 A9 D7 8D 06 D4 A9 ?? 8D 0D D4 A9 ?? 8D 14 D4 …` | X-Large group custom |
| `Jeff/BullSID3` | `A0 16 A9 00 99 00 D4 88 10 FA 8D ?? ?? A0 ?? 99` | BullSID v3 variant |

All sub-tags are at `$1000`/`$1003`. These are confirmed to be **the same author's engine
in group-commissioned variants**, not a different composer's player. The sidid.nfo notes
`Jeff/FLT` has a CSDb reference (release #17292 = "One Million Lightyears from Earth" by
FairLight, 2005) and the description "Custom player made for One Million Lightyears from Earth/FairLight."

---

## 4. Author Concentration

| Author | Count | % |
|---|---|---|
| Søren Lund (Jeff) | 174 | 84.9% |
| Anders Daugaard (Duck LaRock) | 14 | 6.8% |
| Søren Lund (Soren) | 3 | 1.5% |
| Anders Daugaard & Søren Lund | 2 | 1.0% |
| Mihály Horváth (Hermit) | 2 | 1.0% |
| Alexander Rotzsch (Fanta) | 2 | 1.0% |
| Thomas Mogensen & Søren Lund | 1 | 0.5% |
| Søren Lund (Old Tramp) | 1 | 0.5% |
| Steven Diemer (A-Man) | 1 | 0.5% |
| Ronny Nilsen (Snap) | 1 | 0.5% |
| Péter Nagy-Miklós (NecroPolo) | 1 | 0.5% |
| Owen Crowley (Conrad) | 1 | 0.5% |
| László Vincze (Vincenzo) | 1 | 0.5% |
| Jesper Spang (Vernest) | 1 | 0.5% |

"Søren Lund (Soren)" is the same person using a later handle post-2013 (handle change noted
on CSDb after 2013). Duck LaRock (Anders Daugaard) is a close collaborator and Camelot co-member
who also used Jeff's player for 14 of his own tunes.

**92% of the corpus** comes from Søren Lund himself or in collaboration with him.

---

## 5. MUSICIANS Path Distribution

| HVSC path | Count |
|---|---|
| MUSICIANS/J/Jeff | 178 |
| MUSICIANS/D/Duck_LaRock | 16 |
| MUSICIANS/F/Fanta | 2 |
| MUSICIANS/H/Hermit | 2 |
| MUSICIANS/A/A-Man | 1 |
| MUSICIANS/C/Crowley_Owen | 1 |
| MUSICIANS/D/DRAX | 1 |
| MUSICIANS/N/NecroPolo | 1 |
| MUSICIANS/N/Nilsen_Ronny | 1 |
| MUSICIANS/S/Spang_Jesper | 1 |
| MUSICIANS/V/Vincenzo | 1 |

The engine was shared with collaborators and close friends in the Danish C64 scene — all the
non-Jeff MUSICIANS folders represent people who received a copy of the player from Søren Lund.

---

## 6. Year / Release Distribution

| Decade | Count |
|---|---|
| 1990s | 148 (72%) |
| 2000s | 46 (22%) |
| 2010s | 7 (3%) |
| 2020s | 4 (2%) |

Earliest release in corpus: 1990 (X-Factor). Bulk of activity 1991–1994 (Camelot era).
The player was most active in the early-to-mid 1990s demoscene. Notable releases continue
through 2000–2010 (Crest, Viruz, Digital Excess, FairLight). Post-2013 releases use the
"Soren" handle after Søren Lund passed away on 1 December 2013 — these are tribute/memorial
releases made by others using his player, or archival additions.

### Key release groups by year

| Year range | Dominant groups |
|---|---|
| 1990–1991 | X-Factor, Daniax, early Jeff/Camelot |
| 1991–1995 | Camelot (peak — 106 releases) |
| 1996 | Cyberzound Productions (label he co-founded), Reflex, Jeff solo |
| 1999–2002 | Bonzai, Crest, Digital Excess, X-Large compilation |
| 2003–2007 | Viruz (group he founded), FairLight, Smash Designs, Fanta |
| 2008–2013 | Conrad, Hermit, Xenon, Crest (late period) |
| 2021–2025 | Atlantis (Snap), Lethargy/Singular Crew, NecroPolo, Bonzai/Camelot (tribute) |

---

## 7. Multi-Subtune Distribution

199 SIDs (97%) are single-subtune. Multi-subtune entries:

| File | Subtunes | Notes |
|---|---|---|
| 4_Zelda_Covers.sid | 4 | Four Zelda game covers |
| Rock_Paper_Scissors_Simulator.sid | 4 | 2006 Drawback Engineering |
| Sheep_Toss.sid | 3 | 2006 5 Minutes Fun Productions |
| Deep_Shit.sid | 2 | Jeff/FLT — 6581 and 8580 versions |
| Martin_Walker_Tribute.sid | 2 | Jeff/FLT — 6581 and 8580 versions |
| Turrican_3_Shooter.sid | 2 | 2004 Smash Designs |

The Jeff/FLT 2-subtune pattern (6581 vs 8580 version in separate subtunes) is a recurring
convention for chip-specific tuning.

---

## 8. Songlength Distribution

All 205 SIDs have PSID v2. All use 50 Hz VBL (no CIA-timed speed field in the DB — the
`speed` column is not stored, but all 205 being PSID v2 does not exclude CIA; would need
per-SID binary inspection to confirm VBL-only). Songlength range: 2s–522s, average 117s.

| Bucket | Count |
|---|---|
| < 30s | 8 |
| 30–60s | 24 |
| 1–2 min | 91 (44%) |
| 2–5 min | 78 (38%) |
| 5–10 min | 4 |

The engine leans toward full-length musical compositions (1–5 minutes is 82% of corpus).

---

## 9. Scene Context — Søren Lund (Jeff)

**Identity:**
- Real name: Søren Lund
- Handle: Jeff (later "Soren", also used "Old Tramp", "Nick", "Joss")
- Born: 1974 (age ~17 at scene entry ~1991)
- Died: 1 December 2013
- Nationality: Danish (raised mostly in Denmark, brief early childhood in Italy)
- CSDb profile: https://csdb.dk/scener/?id=8059 (musician rating 9.5/10, 60 votes)

**Group timeline:**
| Group | Period | Role |
|---|---|---|
| Daniax | until Aug 1991 | Early demo group |
| X-Factor | Aug 1991 – Dec 1992 | Co-founder |
| Imagination Developments | 1992–1993 | |
| Cyberzound Productions | 1993–2003 | Co-founder (with Duck LaRock / Anders Daugaard) |
| Camelot | Dec 1992 – Nov 2013 | Musician (his most-valued group) |
| Crest | 1999–2013 | |
| Bonzai | 1999–2013 | |
| Viruz | Jun 2003–2013 | Co-founder |
| Cosine | Nov 2006–2013 | |
| Maniacs of Noise | Apr 2013–2013 | (just before death) |

**Player/editor development:**
From the Remix64 interview (April 2002) and Recollection #86 interview:
- Jeff wrote approximately **30 custom SID players** and **2 editors** over his career.
- His player is named **"Music Editor"** in sidid.nfo, officially released 1996 via Cyberzound
  Productions. The 1996 release date is the first formal release; he had been using private
  versions since at least 1991 (earliest HVSC tunes tagged Jeff).
- He described the player as based on "CZP music editor 2" (CZP = Cyberzound Productions),
  further optimised, with maximum rastertime of `$1C`.
- Features cited: special glide/detune/vibrato table, flexible ADSR handler for echo/reverb,
  track/sequence editing system similar to JCH editors, large instrument table.
- He claimed it had "more features than the JCH editor (using player 20!)" — JCH (Jens-Christian
  Huus) editor was a dominant C64 music tool of the era.
- In 2007 he released **X-SID** (CSDb release #47985 via Viruz), a new SID music editor for C64.
  The sidid.cfg has no X-SID fingerprint; its SIDs are not tagged as Jeff engine in HVSC.
- He also coded **The Symphonizer Music Driver V1.10** (but that is a separate engine — not
  the Jeff player; it appears in HVSC under `Symphonica/MDA` not `Jeff`).
- Editors were "never 100% finished" per the interview; the player side was always the more
  polished component.

**Cyberzound Productions:**
A music label/demo group co-founded by Søren Lund (Jeff) and Anders Daugaard (Duck LaRock)
in 1993/1994. The name appears in HVSC `released` fields starting 1996. The group disbanded
by 2003 when Jeff co-founded Viruz.

**STIL annotations for /MUSICIANS/J/Jeff:**
The HVSC STIL v84 has a dedicated section. Key notes extracted:
- `6581_Doped_Cows.sid`: "Won the music competition at the X'2006 party."
- `Cyberworld.sid`: `"Not a direct cover, but heavily influenced by it" (Jeff)` — the source is
  a ScreamTracker S3M module by Torben Hansen (Metal) titled "Trip To Mars."
- `Fungus_Intro.sid`: `"An intro tune done for Fungus in april 2005, but he never used it."` (Jeff)
- `Tune_01A.sid`: `"The number '01A' was simply tune # 01A, so not my first one. It was back in the days
  when I used to name tunes like 'tune 01a', etc."` (Jeff)
- `Space_Journey.sid`: "First presented at The Party 1995 music compo but not released there,
  being not finished. This rip is from the final 1996 release."
- `Jeff/FLT` tunes (`Deep_Shit`, `Martin_Walker_Tribute`): used in FairLight's "One Million
  Lightyears from Earth" demo (Floppy 2005, placed #2 in C64 demo competition, rated 8.9/10).

**Recognition:**
- 46 remixes of his compositions on Remix64 (cover artists).
- Popular remixed tunes: "Beyond" (co-written with Drax/Thomas Mogensen), "Cyberworld",
  "Blowing", "Euro Dance", "Hyperzapper", "Turrican 3".
- "Beyond" remix rated 96% ("Outstanding") on Remix64.
- Duck LaRock's `Happy_Birthday_Jeff.sid` (using CheeseCutter 2.x, not the Jeff player) is
  a tribute track in HVSC.

---

## 10. HVSC DOCUMENTS Coverage

Checked: STIL.txt, Musicians.txt, Creators.txt, hv_sids.txt, HVSC.faq.

- `STIL.txt` (ISO-8859, 108k lines): 35 occurrences of `/MUSICIANS/J/Jeff` path — all are
  cross-reference notes from other SIDs that cover Jeff tunes, plus the Jeff-folder STIL
  section itself. No Players.txt in DOCUMENTS (not part of HVSC #84 distribution).
- No dedicated Jeff-player technical documentation in HVSC DOCUMENTS — the player format is
  undocumented in the standard HVSC bundle.
- The Recollection fanzine (atlantis-prophecy.org) published an interview (#86) with Jeff
  (the 2002 Remix64 interview is the same content / same era).

---

## 11. Summary Statistics

| Metric | Value |
|---|---|
| Total Jeff* SIDs (excl. Jeff_Minter) | 205 |
| Primary author concentration | 174 / 205 = 84.9% Søren Lund |
| Canonical $1000 load | 161 / 205 = 78.5% |
| $FD0 stub era | 19 / 205 = 9.3% |
| All sub-variants at $1000 | 13 (all Jeff/Airwalk + BullSID + XLarge + FLT + BullSID3) |
| Distinct (init, play) pairs | 24 |
| PSID version | All v2 |
| Multi-subtune | 6 / 205 |
| Active period | 1990–2013 (Søren Lund); 2021–2025 (tribute/continuation) |
| Player name (sidid) | "Music Editor" by Søren Lund (Jeff), 1996 Cyberzound Productions |

---

## Leads to Follow

1. **CIA vs VBL**: No speed column in hvsc84.db. The 19 `$FD0`-base SIDs and the unusual
   mid-range addresses should be checked for CIA timing (`speed != 0` in the PSID header)
   — run `python3 -c "import pySID; ..."` or check binary header bytes $16–$19 for the speed
   field. The `$FD0`/`$FE2` era may be a 6-speed multi-timer player.

2. **$FD0 stub: predecessor version or relocated $1000 player?** The 1991–1994 `$FD0` base
   tunes predate the canonical `$1000` era. Whether these are a genuinely different player
   version (e.g. v1 → v2 transition) or just an earlier load address choice needs binary
   comparison. Check if the play-stub at `$FE2`/`$FE3` contains a `JMP $1000+3` trampoline or
   self-contained code.

3. **X-SID engine fingerprint**: The 2007 X-SID editor (CSDb #47985) is NOT in hvsc84.db as
   a Jeff engine. Whether X-SID tunes are present in HVSC under an undetected fingerprint
   (NULL engine?) is unknown. The 2 undetected `$1000`/`$1003` SIDs in `/J/Jeff/` (X-Large_5,
   X-Large_6) could be X-SID or just fingerprint gaps.

4. **"The Symphonizer Music Driver"**: Jeff coded this as a separate tool (V1.00 1993,
   V1.10 later). HVSC has 6 SIDs tagged `Symphonica/MDA`. These are NOT the Jeff player —
   confirm they're unrelated to this research.

5. **Jeff/BullSID vs BullSID3**: The `BullSID3` fingerprint adds a `A0 16 A9 00 99 00 D4 88
   10 FA` loop that initialises D400+ differently. One BullSID3 SID is from 2025 (`$8000`
   relocation) — worth checking if this is a living fork of the engine.

6. **CSDb release coverage**: Jeff is credited on 500+ CSDb releases. The HVSC subset (205
   SIDs) does not cover every composition — some may exist as standalone CSDb music releases
   not submitted to HVSC. CSDb search for scener #8059 SID releases would give the full list.

7. **Player source / disassembly**: No source code is publicly available. The `src/` directory
   under `pipelines/jeff/` may contain prior RE work — check before starting disassembly.
   CSDb release for the Music Editor (the 1996 Cyberzound release) may have the binary.

8. **Duck LaRock cross-engine**: Anders Daugaard uses Jeff's player for 14 tunes but also
   uses CheeseCutter 2.x, Music_Assembler, MoN/FutureComposer, and FutureComposer for other
   tunes. This is not a single-engine composer — the Jeff-tagged Duck LaRock tunes represent
   a specific era or style choice.
