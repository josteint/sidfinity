# John Player — Corpus Characterisation & Scene Context

<!-- provenance header -->
<!-- source_url: hvsc84.db (local), csdb.dk/release/?id=18767, csdb.dk/scener/?id=13210,
     demozoo.org/sceners/627/, demozoo.org/productions/134378/, en.wikipedia.org/wiki/Aleksi_Eeben,
     pouet.net/prod.php?which=13860, github.com/cadaver/sidid (sidid.cfg signatures),
     pipelines/john_player/docs/src/johnhelp_v16.txt (local), tmp/john_player_research/ (local)  -->
<!-- fetched_via: WebFetch + WebSearch + local DB query + local file read -->
<!-- fetch_date: 2026-06-14 -->
<!-- author: corpus+scene sub-agent -->
<!-- content_date: 2026-06-14 (DB snapshot = HVSC #84); scene sources retrieved 2026-06-14 -->
<!-- reliability: DB queries exact; web sources moderate (CSDb may be cached) -->

---

## 1. Tool Identity

**Full name:** John Player  
**Author:** Aleksi Eeben (demoscene alias: Heatbeat)  
**Groups:** Carillon (formed by Eeben) → merged with Cyberiad → CNCD; also listed under MVT.  
**Country:** Finland (born 2 July 1976, born Antti Aleksi Mikkonen)  
**First release:** V1.0 ca. September 2001  
**Final known release:** V2.0 beta (2002); V1.6 corrected frequency table uploaded 2024  
**CSDb tool release:** [#18767](https://csdb.dk/release/?id=18767)  
**CSDb scener:** [#13210](https://csdb.dk/scener/?id=13210)  
**Pouet:** [#13860](https://www.pouet.net/prod.php?which=13860)  
**Demozoo:** [productions/134378](https://demozoo.org/productions/134378/)  
**Motivation (Aleksi's own words):** Created John Player because he found existing C64 music tools
unintuitive. Community described it as "by far the most efficient C64 editor combining
user-friendliness and straightforwardness" (Pouet) and "far easier to learn [than other music
utilities] and still contains a good deal of functionality" (CSDb / Overthink, 2013).

---

## 2. Version History

| Version | Date       | Notes |
|---------|------------|-------|
| V1.0    | 2001-09    | First release; sidid V1.0 fingerprint distinct from later |
| V1.4    | 2001       | sidid fingerprint variant; slide command apparently absent |
| V1.5    | 2001–2002  | "Note trig rewritten from scratch; added slide command; optimised 1 rasterline" (help text) |
| V1.6    | 2002       | Paste track key changed; help screen; music relocator included |
| V2.0b   | 2002       | Beta only; never finalised (packer for this version was not released) |
| V1.6 "intune" | 2024 | Aleksi corrected frequency table: original assumed exactly 1 MHz CPU clock; corrected to 985248 Hz PAL / 1022727 Hz NTSC. Distributed as john16intune.prg (66 downloads as of 2026-06-14) |

The V1.6 release package (johnplayer.zip, 1 723 downloads) includes both V1.6 and V2.0 beta
alongside two demo SIDs: "Rock'n'Roll Butterfly" and "The Radio Challenge".

**sidid.cfg fingerprints** (github.com/cadaver/sidid — version-discriminating signatures):
```
John_Player      A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 END          (generic)
John_Player_V1.0 A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A9 END
John_Player_V1.4 8D 06 D4 A9 AND A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 A9 END
John_Player_V1.6 8D 06 D4 B9 AND A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 A9 END
John_Player_V2.0b A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 AD END
```
The generic + V1.0 patterns differ only in the byte after the main init loop; V1.4 vs V1.6 differ
in the byte immediately after `8D 06 D4` (A9 vs B9 = LDA immediate vs LDA absolute,Y — suggests a
filter or pulse routine tweak); V2.0b introduces `AD` (LDA absolute) in place of `A8` (TAY).

---

## 3. HVSC Corpus Shape (hvsc84.db, engine='John_Player')

**Total SIDs: 183**  
(The research.md stub says 184 — off by one; 183 is the exact DB count.)

All 183 SIDs are PSID version 2. All have `load_addr = $0000` (PSID embedded load address).

### 3.1 Address Cluster Table

The player is relocatable. init_addr = base; play_addr = base + 3 (always, except two play=$0000
anomalies). Clusters are defined purely by `init_addr`:

| init_addr | play_addr | Count | % | Notes |
|-----------|-----------|-------|---|-------|
| $1000     | $1003     | 164   | 89.6 % | Canonical / default reloc |
| $0500     | $0503     |   2   |  1.1 % | Reed (Boogie Factor 1 + 2) |
| $5000     | $5003     |   2   |  1.1 % | TDS + The Bellows |
| $E000     | $E003     |   2   |  1.1 % | Reed (We Control 6581 + 8580) |
| $C000     | $C003     |   1   |  0.5 % | DEMOS / Big Fucking Scroller 2000 |
| $9000     | $9003     |   1   |  0.5 % | GAMES / Wyverns |
| $7000     | $7003     |   1   |  0.5 % | Dalezy / halloween |
| $A000     | $A003     |   1   |  0.5 % | Mermaid / Ghostship |
| $B000     | $B003     |   1   |  0.5 % | Eeben / Cello Suite No. 1 |
| $B200     | $B203     |   1   |  0.5 % | TDS / Black Oak |
| $6000     | $6003     |   1   |  0.5 % | TDS / No Time |
| $4000     | $4003     |   1   |  0.5 % | Eeben / The Burger Ninja (2022 game) |
| $4E00     | $0000     |   1   |  0.5 % | Eeben / Greenrunner (11 subtunes — unusual) |
| $0900     | $0000     |   1   |  0.5 % | Eeben / One for Reed (play=$0000 anomaly) |
| $2D90     | $2D93     |   1   |  0.5 % | Eeben / Aquarius (4 subtunes; non-page-aligned) |
| $99E6     | $99F4     |   1   |  0.5 % | Duck-hunter / The Face Lift (non-page-aligned) |
| $0FFF     | $1003     |   1   |  0.5 % | TDS / Shortcut (init $0FFF, play $1003 — 1-byte offset) |

**Key observations:**
- Canonical $1000 covers 164/183 (89.6%) — the toolchain's default, matching player.asm `.DEFINE reloc $1000`.
- 17 relocations (10.4%): most are clean page boundaries, two are non-page-aligned ($2D90, $99E6).
- Two SIDs have play_addr = $0000 — these likely use a different dispatch mechanism or
  play-via-init loop; both are by Aleksi Eeben himself (Greenrunner 2006, One for Reed 2006).
- $0FFF init is a 1-byte negative shift (TDS / Shortcut 2000) — sidid likely still matches the
  generic fingerprint since the sequence is unchanged.
- Total distinct relocation addresses: 17 (including the two $0000 play anomalies).

### 3.2 Subtune Counts

| n_subtunes | SID count |
|------------|-----------|
| 1          | 180       |
| 2          | 1 (Reed / Boogie Factor 1) |
| 4          | 1 (Eeben / Aquarius) |
| 11         | 1 (Eeben / Greenrunner) |

John Player is primarily single-subtune; the multi-subtune outliers are all either Eeben himself
or use the relocator.

### 3.3 Songlength Distribution

| Range    | Count |
|----------|-------|
| < 30 s   |   5   |
| 30–60 s  |  22   |
| 60–120 s |  71   |
| 120–300 s|  76   |
| > 300 s  |   9   |

Median: 115 s. Mean: 140 s. Longest: 1095 s (Eeben / Water Music 2004).
No missing songlengths (all 183 have HVSC Songlengths.md5 entries).

---

## 4. Year / Release Distribution

| Year    | SIDs | Top contributor(s) |
|---------|------|--------------------|
| 2001    |   8  | Aleksi Eeben (4), AlwyzStnd (2) |
| 2002    |  41  | Aleksi Eeben (26), dalezy (3), TDS (3) |
| 2003    |  27  | Mortimer Twang (8), Mr. Death (3), Crome (3) |
| 2004    |  26  | Aleksi Eeben (11), The Bellows (4), Reed (3) |
| 2005    |  13  | Reed (4), Duck-hunter (2), Crome (2) |
| 2006    |  23  | Xiny6581 (14), Aleksi Eeben (3), SCouT (3) |
| 2007    |   8  | Player One (3), Pezac (2), Xiny6581 (1) |
| 2008    |   3  | Xiny6581 (1), SCouT (1), Muhmi (1) |
| 2009    |   4  | Player One (1), Codehead (1), Muhmi (1) |
| 2010    |   2  | Player One (1), Davizion (1) |
| 2011    |   2  | TomoAlien (1) |
| 2012    |   5  | various |
| 2014–2019|  5  | scattered (Alwyz, Sos, iLKke, Linde, Sos/Ylesradio) |
| 2020    |   4  | Isocosa (4) |
| 2021    |   1  | Aleksi Eeben |
| 2022    |   1  | Aleksi Eeben (Burger Ninja game) |
| 2023    |   2  | psc64 (2) |
| 2024    |   2  | Aleksi Eeben (Aquarius, Extended Ambience V3) |
| 2025    |   5  | Aleksi Eeben (3), Fade+Cyberstorm64 (1) |

**Activity profile:** Peak 2001–2006 (138/183 = 75%); steady trickle 2007–present. Tool remains
in use in 2025 — Aleksi himself returned to it (Equinoxe Part 5, Cello Suite No. 1, Fairlight in
Major, Tuhannen Markan Seteli). Small modern revival: Isocosa (2020), psc64 (2023).

---

## 5. Author Concentration (full list)

| Author (HVSC tag)                         | Count |
|-------------------------------------------|-------|
| Aleksi Eeben                              |  53   |
| Cris (Xiny6581)                           |  17   |
| Lukas Nystrand (Mortimer Twang)           |  10   |
| Jaakko Kaitaniemi (Reed)                  |   9   |
| Sam Behm (Player One)                     |   8   |
| Siegfried Rudzynski (Crome)               |   7   |
| Roland van Oorschot (SCouT)               |   6   |
| Trond Jensen (TDS)                        |   6   |
| Ronny Engmann (dalezy)                    |   5   |
| Hai Nguyen Dinh (Duck-hunter)             |   5   |
| Andreas Samuelsson (Mr. Death)            |   5   |
| Isocosa                                   |   4   |
| Vanja Utne (Mermaid)                      |   4   |
| Roope Kangas (Muhmi)                      |   4   |
| Ragnar Aambø (The Bellows)               |   4   |
| TomoAlien                                 |   2   |
| Philip Linde (Linde)                      |   2   |
| Lukas Nystrand (LuKiss)                   |   2   |
| AlwyzStnd / Alwyz                         |   2   |
| psc64                                     |   2   |
| Peter Mattson (Pezac)                     |   2   |
| Ilija Melentijevic (iLKke)                |   1   |
| Christian Siege (Wyverns game)            |   1   |
| Sos Sosowski (Chest Bump game)            |   1   |
| Mikolaj Kaminski (Sos)                    |   1   |
| Nick Vivid (3 SIDs but listed as 3 separately) | 3 |
| Vincenzo (2 SIDs)                         |   2   |
| David Sullivan (Davizion)                 |   1   |
| and others (Samuli Piela / Codehead, Øyvind P. Noste / Zixaq, Matthew Kuebrich, Fade, etc.) | ~10 total |

**Eeben himself = 29% of the corpus (53/183).** The top 5 composers (Eeben + Xiny6581 +
Mortimer Twang + Reed + Player One) account for 97/183 = 53%.

---

## 6. MUSICIANS Folder Distribution

| HVSC subfolder                       | Count |
|--------------------------------------|-------|
| MUSICIANS/E/Eeben_Aleksi             |  54   |
| MUSICIANS/X/Xiny6581                 |  17   |
| MUSICIANS/M/Mortimer_Twang           |  12   |
| DEMOS (all)                          |  10   |
| MUSICIANS/R/Reed                     |   9   |
| MUSICIANS/P/Player_One               |   8   |
| MUSICIANS/C/Crome                    |   7   |
| MUSICIANS/D/Duck-hunter              |   6   |
| MUSICIANS/S/Scout                    |   6   |
| MUSICIANS/T/TDS                      |   6   |
| MUSICIANS/D/Dalezy                   |   5   |
| MUSICIANS/M/Mr_Death                 |   5   |
| MUSICIANS/I/Isocosa                  |   4   |
| MUSICIANS/M/Mermaid                  |   4   |
| MUSICIANS/M/Muhmi                    |   4   |
| MUSICIANS/T/The_Bellows              |   4   |
| MUSICIANS/N/Nick_Vivid               |   3   |
| GAMES (all)                          |   2   |
| MUSICIANS/L/Linde                    |   2   |
| MUSICIANS/P/PSC64                    |   2   |
| MUSICIANS/P/Pezac                    |   2   |
| MUSICIANS/S/Slumgud                  |   2   |
| MUSICIANS/V/Vincenzo                 |   2   |
| MUSICIANS/A/Aegis                    |   1   |
| MUSICIANS/C/Codehead                 |   1   |
| MUSICIANS/F/Fade                     |   1   |
| MUSICIANS/I/Ilkke                    |   1   |
| MUSICIANS/L/LordNikon                |   1   |
| MUSICIANS/O/Odo                      |   1   |
| MUSICIANS/S/SounDemoN                |   1   |

Note: Eeben_Aleksi folder has 69 total SIDs in HVSC; 54/69 = 78% of his work uses John Player
(the other 15 use other engines or different tools).

---

## 7. GAMES and DEMOS SIDs

**GAMES (2 SIDs):**
- `GAMES/A-F/Chest_Bump.sid` — Sos Sosowski, 2015, init=$1000 (canonical)
- `GAMES/S-Z/Wyverns.sid` — Christian Siege / Colorclash Software, 2012, init=$9000 (relocated)

**DEMOS (10 SIDs):** Various authors 2002–2019. All single-subtune. Examples: Øyvind P. Noste
"83" (Creators 2004), David Sullivan "One More Time" (Edge of Panic 2010), Mikolaj Kaminski
"Big Fucking Scroller 2000" (2019, relocated to $C000).

---

## 8. HVSC DOCUMENTS — John Player Mentions

Searched: STIL.txt (108 101 lines), Musicians.txt, Creators.txt, hv_sids.txt, SID_file_format.txt,
all .faq files. **Result: zero hits** for "John Player", "Aleksi Eeben", "Heatbeat", "CNCD",
or "Cyberiad" in any HVSC DOCUMENTS file. The STIL file has no per-SID comment entries for the
Eeben_Aleksi folder. The HVSC documents do not document individual music players/editors; they
document the archive and file format only.

The help text (V1.6) is preserved locally at:
`pipelines/john_player/docs/src/johnhelp_v16.txt` (352 lines, from the tool download).

---

## 9. Tool Architecture (from help text + source)

From `johnhelp_v16.txt` (built into the tool binary, recovered from the download zip) and
`player.asm` (WLA-6510 source, also in the zip):

**Screens:** Block Edit (pattern), Sound Edit (instrument), Sequencer, Disk/Options.  
**Sequencer model:** Positions contain block references; one global loop position.  
**Block commands (in pattern data):**
- `Brk` — block break (early exit)
- `End` — block end (player-internal)
- `Tmp xx` — set tempo (06–FF, default $0C)
- `Flt xx` — set filter cutoff base
- `Ini xx` — init modulation (vibrato width 00–02)
- `Mod xx` — select channel for modulation (01–03)
- `Off xx` — stop modulating channel (01–03)
- `Vib xx` — set vibrato rate (01–04) or stop slide (00)
- `Sli xx` — start pitch slide (00–7F = up, FF–80 = down)

**Single modulator:** Vibrato and slide share one engine modulator. Multiple channels can be
modulated simultaneously but all use the same rate/settings. Vibrato uses a sine table.

**Sound (instrument) table:** 64 steps, shared across all sounds. Per-instrument: waveform,
ADSR, Sound Trig/End/Loop positions, PWM Init/Rate/Top/Bottom limits, Filter Reso+Chan Sel,
Filter Type+Volume. Filter is global (channel 1 only reads filter params).

**Memory layout (reloc-relative, from player.asm):**
```
reloc+$0358  FreqTab   (note frequency table)
reloc+$0400  VibTab    (vibrato sine table)
reloc+$0420  SoundTab  (64 × ? bytes sound definitions)
reloc+$0500  FilTab    (filter table)
reloc+$0540  WaveTab   (waveform table)
reloc+$0580  ArpTab    (arpeggio table)
reloc+$05C0  Sequencer (song order)
reloc+$0600  BlockData (pattern data)
```

**Zero-page layout (base $40):** cmdtick, fbase, c1hold–c3hold, count, speed, seqpos, step,
block, vibpos, mod, modh.

**Compile-time modes:** `COMPILE_PLAYER=0` (editor), `=1` (standalone player), `=2` (packed
block data player). The "packed" mode (V2.0b adds this) packs block data.

**Known quirk from help text:** "Packed music might not sound right if restarted: channel
modulation and some sounds are not reset." Restart is sys2061 or sys16384 ($1000 + editor
entry, when at default reloc).

**Frequency table bug (V1.0–V1.6):** Original assumed 1 MHz CPU clock. Correct values are
985248 Hz PAL / 1022727 Hz NTSC. Corrected in john16intune.prg (2024). This means ALL
183 HVSC SIDs composed with the original tool have slightly detuned frequency tables —
the SID data encodes the original (incorrect) freq table bytes and playback with the
matching player produces the composer's intended pitch relationships. The corrected version
is a *different sonic outcome*.

---

## 10. Scene Context

**Is it a beginner-friendly tool?** Yes, explicitly. Aleksi Eeben created it because he found
existing C64 music editors unintuitive. Community reception confirms: Pouet commenters called it
"by far the most efficient c64 editor combining user-friendliness and straightforwardness";
Overthink on CSDb said it is "far easier to learn [than] other music utilities for the 64."
One Pouet commenter noted it is "user friendly, but limited" — the limitation being primarily
composition length (no "packed" packer for V2.0b was ever released).

**Community reach:** The 183 HVSC SIDs span ~30 distinct composers across 10 countries
(Finland, Sweden, Norway, Netherlands, Germany, Vietnam, Poland, US, UK, others). This is a
broader geographic spread than most scene-specific tools. The tool attracted non-Finnish and
non-demoscene authors (GAMES entries, standalone composers).

**Peak use 2001–2006:** 138 SIDs in this window. Aleksi himself drove 53 (mostly 2002–2004 with
Carillon & Cyberiad). After 2007, use drops sharply except for Xiny6581's 2006 burst (14 SIDs)
and Player One's late use (2007–2010). A small modern revival (Isocosa 2020, psc64 2023, Aleksi
himself 2021–2025) shows it remains viable 20+ years later.

**Still actively used (2025):** Aleksi himself released 5 John Player SIDs in 2025
(Equinoxe Part 5, Cello Suite No. 1, Fairlight in Major, Tuhannen Markan Seteli, plus one
with Fade/Cyberstorm64). This is the highest single-year Eeben output since 2004.

**Aleksi Eeben's broader output:** Nokia/Microsoft Mobile principal sound designer 2002–2015.
C64 composer and coder since 1988–1990 (Rebels). Also developed Polly Tracker (2005),
Retroskoi (2005), Polyanna (2017), Spinning Jenny (2021), Bunny Basic (2019), Basil PET
Emulator (2022), and Quantum Soundtracker (2024). John Player remains his primary C64 music
composition tool.

**CSDb download count:** 1 723 downloads for the main johnplayer.zip as of 2026-06-14.
The relocated (john16reloc.prg) and corrected (john16intune.prg) variants have far fewer
downloads (73 and 66 respectively).

**No sidid classification in HVSC update notes.** The sidid fingerprints are in the Cadaver
sidid.cfg community file, not HVSC's own documentation. The HVSC STIL has no entries for this
engine family.

---

## 11. Notable Individual SIDs

| SID | Init | Subs | Len | Note |
|-----|------|------|-----|------|
| Eeben / Water Music (2004) | $1000 | 1 | 1095 s | Longest JP SID in corpus |
| Eeben / Greenrunner (2006) | $4E00 | 11 | 480 s | Most subtunes; unusual play=$0000 |
| Eeben / Aquarius (2024) | $2D90 | 4 | 752 s | Non-page-aligned reloc; multi-subtune |
| Reed / Boogie Factor 1 (2005) | $0500 | 2 | 370 s | 2 subtunes; $0500 reloc |
| Eeben / Cello Suite No. 1 (2025) | $B000 | 1 | — | $B000 reloc: bank danger zone |
| Eeben / One for Reed (2006) | $0900 | 1 | — | play=$0000 anomaly |
| Duck-hunter / The Face Lift | $99E6 | 1 | 158 s | Non-page-aligned; unusual |
| TDS / Shortcut | $0FFF | 1 | 100 s | 1-byte negative shift from $1000 |

---

## Leads to Follow

1. **Version breakdown in corpus:** sidid can classify V1.0/V1.4/V1.6/V2.0b per-SID; the
   four patterns in sidid.cfg differ at V1.4 (filter table read change: B9=absolute,Y vs A9=imm).
   Run `sidid` on the 183 SIDs to get a version-distribution table — this directly drives
   whether extract/compose needs version branching. Open question: do all canonical $1000 SIDs
   share one version, or is there a mix of V1.0–V2.0b in the wild?

2. **play=$0000 anomaly:** Greenrunner (11 subtunes, $4E00) and One for Reed ($0900) have
   play_addr=0. The PSID standard treats play=$0000 as "use CIA interrupt." These may actually
   be CIA-timed SIDs — check PSID speed byte. If so, they are the only two CIA-mode JP tunes
   and need the per-irq writelog path.

3. **$B000 reloc (Cello Suite No. 1, 2025):** $B000–$BFFF is the C64 BASIC ROM bank. If the
   player runs there with KERNAL/BASIC mapped, fetches will hit ROM, not RAM. Check whether
   this SID sets $01 to disable BASIC before play, or whether it relies on PSID's memory model.
   See feedback_c64_banking_relocation.md.

4. **Non-page-aligned relocs ($2D90, $99E6):** These break the pattern init=base,
   play=base+3. The $2D90 case (Aquarius, 4 subtunes) is Aleksi himself — likely a deliberate
   custom layout. The $99E6 case (Duck-hunter / The Face Lift) with play=$99F4 (= init+$0E)
   is anomalous — play is 14 bytes after init, not 3. This may indicate a non-standard init
   wrapper that ends at $99F4, or a corrupt/hand-edited PSID header. Worth binary inspection.

5. **V2.0b changes:** The iLKke-uploaded pastebin (http://pastebin.com/80TaWPMz, 2014) lists
   changes from V1.6 to V2.0b. That URL may be stale after 12 years but is worth fetching.
   The tool agent (sibling sub-agent) should have this; if not, it's a priority fetch.

6. **Frequency table variant in USF:** The 2024 "intune" correction means there are two
   distinct freq table variants in the wild. All 183 HVSC SIDs use the *original* (detuned)
   table — the correction is only for new compositions with john16intune.prg. USF should carry
   the freq table as data (it already does in the Hubbard pipeline), so this is not a schema
   issue, just an extraction note: use the detuned original table, not the 2024 correction.

7. **Xiny6581 burst (14 SIDs, 2006):** Cris / Xiny6581 is the second-largest user (17 total,
   14 in 2006 alone). His SIDs may expose instrument/effect usage that Eeben's own compositions
   don't exercise. Worth sampling during the write-model phase.

8. **Source code authenticity:** The player.asm / mem.inc / editor.asm etc. in
   `pipelines/john_player/docs/src/` and `tmp/john_player_research/source_extracted/` are
   from the johnplayer.zip distribution (V1.6/V2.0b). The source targets WLA-6510 assembler.
   Confirm which version these sources represent before using as ground truth for disassembly —
   V1.6 and V2.0b may have differed in the player routine.
