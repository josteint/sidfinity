# Electrosound — Corpus Characterisation & Scene Context

## Provenance

| Field | Value |
|---|---|
| author | Research agent (corpus characterisation task) |
| fetch_date | 2026-06-14 |
| content_date | 1985–2026 (primary sources) |
| reliability | HIGH for DB facts (hvsc84.db, read-only); MEDIUM for web sources (VGMPF, Lemon64, c64.com interviews, cadaver/sidid.nfo) |
| primary sources | hvsc84.db (local), VGMPF wiki, Lemon64 forum, c64-music.blogspot.com, c64.com interview with Barry Leitch, gamedeveloper.com interview with Barry Leitch, remix64.com interview with Peter Clarke, cadaver/sidid GitHub, nightfallcrew.com (Gubbdata 2020 results) |
| source URLs | https://www.vgmpf.com/Wiki/index.php?title=Electrosound_64 ; https://www.lemon64.com/forum/viewtopic.php?t=19807 ; https://c64-music.blogspot.com/2009/06/electrosound.html ; https://github.com/cadaver/sidid/blob/master/sidid.nfo ; https://remix64.com/interviews/an-interview-with-peter-clarke.html ; https://www.gamedeveloper.com/audio/interviewing-veteran-composer-barry-leitch-part-i-sound-chips-from-zx-81-to-the-snes- |

---

## 1. Background: What Electrosound 64 Is

Electrosound 64 (nicknamed "Leccysound" in the scene) was a commercial C64 music composition and sound editor sold by Orpheus Ltd., priced at £14.95. It appeared in 1985 and was the most widely used British music tool for the C64 through 1986–1987 before being superseded by Soundmonitor. sidid.nfo (cadaver/sidid) confirms: "RELEASED: 1985 Orpheus, REFERENCE: https://csdb.dk/release/?id=27433".

The HVSC itself carries a demo tune `DEMOS/A-F/Electrosound_64.sid` by Steve Mellin / 1985 Orpheus — the product demo that shipped with the software. The only other Steve Mellin tune in HVSC is `GAMES/S-Z/Young_Ones.sid` (1986 Orpheus), the game that appears to have been scored with the same tool.

**Key features (per VGMPF wiki + Lemon64 + c64-music.blogspot):**
- Instrument editor: up to 10 instruments with full SID register control + pitch/pulse/cutoff modulations
- Sequencer: up to 20 sequences × 240 notes (3 instruments + 24 drum sounds per sequence)
- Track layer: sequences linked into songs; up to 5 songs + 10 instrument banks per disk file
- Pattern-based (like a Roland TR-606 "but with notes instead of drumbeats" — Peter Clarke)
- Tempo is per-sequence; tempo changes mid-tune are supported but require CIA1 timer calculation on export
- The compiled output is NOT the player itself — it bundles a player routine with the data

**Technical limitations (per VGMPF):**
- "Poorly coded and the slowest known on the C64"
- Non-looping driver (PSID play() does not loop automatically)
- Tuned at 423.9 Hz (non-standard — normal SID A4 = 440 Hz)
- Single preset sound set per sequence (no mid-sequence instrument changes)
- Largely superseded by Soundmonitor in 1987

**Author testimony (Barry Leitch, gamedeveloper.com interview):** "As I couldn't program, I was left using a commercial package called Electrosound, which was very basic." — confirms the tool was the entry point for non-programming composers. He later got a programmer friend to write a custom driver.

**Peter Clarke (remix64.com interview):** Bought Electrosound 64 on Paul Hughes' recommendation; called it "the Holy Grail" at the time. Used it for his first commissioned work (Repton 3). Moved to Martin Galway's Ocean ODS system when he joined Ocean Software; later rewrote Ocean Loader III from Electrosound.

---

## 2. HVSC Corpus Shape

### 2.1 Total count and PSID metadata

| Field | Value |
|---|---|
| Total Electrosound SIDs in HVSC #84 | **297** |
| PSID version | All **v2** |
| SIDs with load_addr set | 0 (all NULL — standard PSID LOAD behaviour) |
| SIDs with play_addr = NULL | 3 (broken/non-standard rips: First_Day_Tune, On_the_Move, Peter_Shiltons_Handball_Maradona) |

### 2.2 Songlength distribution

All songlengths are real (per HVSC Songlengths.md5); no >1000s anomalies detected.

| Bucket | Count | Avg (s) |
|---|---|---|
| <30 s | 4 | 20.6 |
| 30–60 s | 11 | 48.0 |
| 1–2 min | 49 | 93.4 |
| 2–5 min | 174 | 193.4 |
| 5–10 min | 48 | 411.2 |
| >10 min | 11 | 696.9 |

Most tunes (174/297 = 59%) fall in the 2–5 minute range. The long tails are multi-subtune SIDs (e.g. Peter Clarke's Kinetik has 22 subtunes, songlength 261 s cumulative).

### 2.3 Multi-subtune distribution

| n_subtunes | Count |
|---|---|
| 1 | 256 |
| 2 | 11 |
| 3 | 3 |
| 4 | 9 |
| 5 | 11 |
| 6 | 1 |
| 8 | 2 |
| 9 | 1 |
| 11 | 1 |
| 16 | 1 |
| 22 | 1 |

41 SIDs (14%) have 2+ subtunes. High-subtune outliers are game soundtracks: Peter Clarke's Kinetik (22), Top Duck (16), Gunstar (11).

### 2.4 Year distribution

| Year | Count | Notes |
|---|---|---|
| 1985 | 3 | Steve Mellin demo + two 1985 Nige tunes |
| 1986 | 188 | Peak year — Barry Leitch, Jonathan Dunn, Matt Perry, Neil Baldwin, Peter Clarke, Stu Taylor, Matt Gray |
| 1987 | 66 | Jonathan Dunn commercial games; Peter Clarke at Ocean; The Fall Guys; Pulse Productions; Firebird titles |
| 1988 | 1 | Barry Leitch |
| 1989 | 2 | Empire, Blue Ribbon |
| 198?/19?? | 18 | Undated/uncertain |
| 1990s | 2 | 1990 + 1997 |
| 2000s+ | 17 | John Stormont (2020 revival) |

The **1986 peak (63%)** is consistent with Electrosound's commercial lifespan: it shipped in late 1985, was widely adopted in 1986 via Compunet and UK computer clubs, and began declining in 1987 as Soundmonitor spread.

### 2.5 Top composers (by SID count)

| Composer (handle) | Count | Years | Notes |
|---|---|---|---|
| Barry Leitch (The Jackal) | 68 | 1986–1988 | Largest single cohort; Scottish; prolific cover-version maker |
| Jonathan Dunn (Choroid) | 26 | 1986–1987 | Later became major Ocean composer; early ZZAP!64 competition work |
| John Stormont | 17 | 2020 | Revival: 2020 compositions in Electrosound format |
| Matthew Perry (Matt) | 15 | 1986 | |
| <?> (unknown) | 15 | 1986 | Unidentified authors |
| Peter Clarke | 12 | 1986–1987 | Later Ocean / Firebird composer |
| Stu Taylor | 11 | 1986–1987 | |
| Graphics Designs | 10+4 | 1986–1987 | Group handle (multiple sub-handles) |
| Neil Baldwin (Demon) | 8 | 1986 | |
| Matt Gray | 6 | 1986–1987 | |
| Sean Connolly | 6 | 1987 | Pulse Productions; Jarre covers |
| David Bain | 6 | 198? | Zeon Acoustics |
| Keith Tinman | 4 | — | |
| Adam Gilmore (Gizmo) | 4 | 1987 | |

### 2.6 MUSICIANS directory breakdown

| Directory letter | Count | Notable composer |
|---|---|---|
| L | 68 | Barry Leitch |
| G | 28 | Graphics Designs, Matt Gray, Adam Gilmore |
| D | 26 | Jonathan Dunn |
| C | 23 | Peter Clarke, Sean Connolly |
| M | 21 | Matthew Perry, MC (Marco Swagerman), Matt Gray |
| B | 21 | Neil Baldwin, David Bain, Wally Beben |
| T | 20 | Stu Taylor, Keith Tinman |
| S | 18 | John Stormont, Sam Roads, Stuart Taylor |
| (DEMOS) | 42 | Unknown authors |
| (GAMES) | 10 | Steve Mellin, Peter Clarke, Jonathan Dunn |

---

## 3. Player Address Clustering — Variant Analysis

### 3.1 The canonical Electrosound player signature

The Lemon64 conversion thread (waz) reveals the critical structural fact:

> "The IRQ routine [is] at load address + $0A65"
> "Call JSR to the Electrosound player at load address + $0518"

**This means: for any canonical Electrosound SID, `play_addr = load_addr + $0A65`.**

This is confirmed by the corpus: **235 of 297 SIDs (79%)** have `play_addr & 0xFF == 0x65`, i.e. the low byte of play_addr is always `$65`. These are all canonical Electrosound player rips. The player binary is the same; only the load address varies.

Derived canonical load addresses (play − $0A65):

| Derived load | play_addr | Count |
|---|---|---|
| $4000 | $4A65 | 87 |
| $1000 | $1A65 | 56 |
| $8000 | $8A65 | 13 |
| $7000 | $7A65 | 13 |
| $6500 | $6F65 | 10 |
| $6000 | $6A65 | 8 |
| $2000 | $2A65 | 8 |
| $1800 | $2265 | 8 |
| $4800 | $5265 | 4 |
| others (1–2 each) | various | 28 |

**The player binary is fully relocatable**; the two dominant positions are load=$4000 (87 SIDs, Barry Leitch cohort) and load=$1000 (56 SIDs, Jonathan Dunn + John Stormont cohort).

### 3.2 Init address variants (within canonical builds)

The init_addr points to the tune-selection stub — the code that sets the tune number, tempo, and init flag before calling the player. Four patterns emerge:

| Init style | Offset from play | Offset from load | Count | Notes |
|---|---|---|---|---|
| **A** — init stub AFTER player end | play + $9B (= load + $0B00) | load + $0B00 | 83 | Standard pack: stub at end of player |
| **B** — init stub INSIDE player | play + $2B (= load + $0A90) | load + $0A90 | 24 | Stormont's tunes; stub embedded |
| **C** — init stub BEFORE load | play − $A75 (= load − $10) | load − $0010 | 88 | Largest group; init sits 16 bytes before player load |
| **D** — init = play − $20 | play − $20 | load + $0A45 | 6 | Peter Clarke tunes at load=$8000 |
| other | varies | varies | 34 | Multi-song, unusual packings |
| non-canonical | — | — | 62 | No $65 low byte — custom re-packings or different player |

**These four init styles are SID-packing conventions, not different player versions.** The player code itself is the same relocatable binary across all canonical builds. The PSID rippers chose different strategies for where to put the tune-selection stub.

Style C (88 tunes) — init sits at load − $10 — is the most common single pattern, dominant in Barry Leitch's large collection (52 at load=$4000, init=$3FF0).

### 3.3 Non-canonical builds (62 SIDs)

These 62 SIDs have play_addr with a low byte != $65. They include:
- Custom in-game players (Renegade, Top Duck, Kinetik, Gunstar, Young_Ones) where the game programmer wrapped the Electrosound data in their own init/play shell
- Incomplete or differently-converted rips
- A few tunes where the player was loaded at an offset not aligned to make play=$x65

Notable non-canonical cases:
- `GAMES/S-Z/Young_Ones.sid`: play=$FF34, init=$E3FA — Steve Mellin / Orpheus, very high load; non-standard
- `MUSICIANS/C/Clarke_Peter/Kinetik.sid`: play=$BE10, 22 subtunes — custom Ocean-era player wrapper
- `MUSICIANS/G/Gray_Matt/Funky_Limits.sid`: play=$08A1, init=$08BD — play < init, reversed-init layout

### 3.4 Address cluster summary table

| Cluster | Canonical | Init style | Count | Representative composers |
|---|---|---|---|---|
| load=$4000, init=$3FF0 | Yes | C | 52 | Barry Leitch (bulk) |
| load=$1000, init=$1B00 | Yes | A | 29 | Jonathan Dunn, demos |
| load=$4000, init=$4B00 | Yes | A | 22 | Barry Leitch, Rodger, Mad_Donne |
| load=$1000, init=$1A90 | Yes | B | 19 | John Stormont (all 17 his + 2 demos) |
| load=$6500, init=$64EB | Yes | C | 8 | Barry Leitch, Dunn |
| load=$1800, init=$17EB | Yes | C | 7 | — |
| load=$6000, init=$6B00 | Yes | A | 7 | Graphics Designs, MC |
| load=$2000, init=$2B00 | Yes | A | 6 | Bain, Roads, Dunn |
| load=$8000, init=$8A45 | Yes | D | 6 | Peter Clarke (1986) |
| load=$7000, init=$6FD0 | Yes | C | 5 | Barry Leitch |
| load=$7000, init=$7B00 | Yes | A | 5 | Barry Leitch, Stu Taylor |
| (non-canonical, various) | No | — | 62 | Games/custom |

**Conclusion: there is ONE Electrosound player binary (fully relocatable), loaded at a composer/ripper-chosen base address. The player code is always at base + $0000 .. $0AFF; play() is always at base + $0A65. At least two distinct init conventions exist (stub at $0B00 vs. $0A90 vs. before load), but these are packing choices, not engine variants.**

---

## 4. Scene Context and Timeline

### 4.1 Release and adoption

- **1985**: Orpheus Ltd. releases Electrosound 64, sold commercially for £14.95. Demo tune by Steve Mellin ships with it. First known use in HVSC: 1985 Nige (2 tunes).
- **1985–1986**: Tool spreads through the UK C64 scene via Compunet (the pre-internet dial-up demo-sharing network) and physical computer clubs. Barry Leitch states explicitly that he used Compunet to distribute demos made with Electrosound.
- **1986**: Peak adoption. Barry Leitch (60+ tunes), Jonathan Dunn (24+ tunes), Neil Baldwin (8 tunes), Matt Gray (4 tunes), Matthew Perry (15 tunes), Peter Clarke (7+ tunes), Stu Taylor (10 tunes), plus dozens of amateur scene groups.
- **1987**: Decline begins. Soundmonitor and later Rob Hubbard-derived custom players are dominant. Electrosound still used for Firebird/Tynesoft commercial titles (Jonathan Dunn, Peter Clarke) and demo groups (Pulse Productions, The Fall Guys), but many composers transition away.
- **1988–1989**: Only isolated uses. Barry Leitch uses custom driver by this point.
- **2020**: John Stormont releases a revival collection ("John Stormont's Electrosound History Book" by Onslaught, at Gubbdata 2020 demoparty) — 17 new Electrosound compositions added to HVSC (all tagged 2020 John Stormont).

### 4.2 Main composers and their context

**Barry Leitch (The Jackal)** — The largest single cohort (68 SIDs, 23% of the entire engine corpus). Scottish, born 1970. His first professional work was I.C.U.P.S. (1986, Thor Computer Software). He used Electrosound for cover versions (Ace of Spades, When Doves Cry, Walk of Life, etc.) and originals. Moved to a custom driver built by a programmer friend after the Electrosound phase. Later became a professional game composer (Top Gear, Road Rash). Almost all his Electrosound SIDs load at $4000.

**Jonathan Dunn (Choroid)** — 26 SIDs. Entered the ZZAP!64 music competition in 1986 under "Choroid"; shared second place. Early work entirely in Electrosound; later became Ocean Software's primary composer (Total Recall, Robocop 2, Platoon, etc.). His Electrosound tunes load predominantly at $1000 (init style A).

**John Stormont** — 17 SIDs, all dated 2020. A revival composer who returned to Electrosound decades later; part of the Onslaught demoparty release. His tunes use the $1A90 init variant (style B) almost exclusively — a distinctive packing not used by the 1986 cohort.

**Peter Clarke** — 12 SIDs. Bought Electrosound on Paul Hughes' recommendation. First commercial work: Repton 3. Moved to Martin Galway's Ocean ODS system. His game titles (Kinetik, Gunstar, Top Duck) use non-canonical player wrappers. His early Peter Clarke & Paul Hughes tunes use a distinctive load=$8000 / init=$8A45 packing (style D).

**Matt Gray** — 6 SIDs. Later famous for Creatures, Enforcer, and work with Digital Reality. His Electrosound work is from his early demo scene days (1986–1987). Mixed load addresses.

**The Fall Guys** — 17 SIDs dated 1987. A German C64 cracking/demo group (formed 1985, disbanded 1987). All their Electrosound material uses load=$4000 / init=$3FF0 (same as Barry Leitch's standard packing).

**Graphics Designs** — 14 SIDs (multiple sub-handles: Graphics Designs, Graphics Design, Graphics Designs<?>). Demo group, predominantly load=$6000 / init=$6B00.

**Sean Connolly** — 6 SIDs, 1987, Pulse Productions. Cover versions of Jarre (Oxygene, Equinoxe, Rendezvous, Magnetic Fields). Uses widely varying load addresses — each tune at a different base.

### 4.3 Commercial games using Electrosound

| Game | Composer | Publisher | SID path |
|---|---|---|---|
| The Young Ones | Steve Mellin | Orpheus (1986) | GAMES/S-Z/Young_Ones.sid |
| Donkey Kong | <?> | — | GAMES/A-F/Donkey_Kong.sid |
| Renegade | <?> | — | GAMES/M-R/Renegade.sid |
| Rat Splat | <?> | — | GAMES/M-R/Rat_Splat.sid |
| Pipe Mania | <?> | — | GAMES/M-R/Pipe_Mania.sid |
| Sky Runner | <?> | — | GAMES/S-Z/Sky_Runner.sid |
| Syntax | <?> | — | GAMES/S-Z/Syntax.sid |
| Peter Shilton's Handball Maradona | <?> | — | GAMES/M-R/Peter_Shiltons_Handball_Maradona.sid |
| Jeep Command | <?> | — | GAMES/G-L/Jeep_Command.sid |
| Cloud Kingdoms | Dene Carter | — | GAMES/A-F/Cloud_Kingdoms.sid |

Peter Clarke's commercial titles (Kinetik, Gunstar, Top Duck, Mystery of the Nile, Big K.O., Scooby Doo) are listed under MUSICIANS not GAMES — they were ripped from the game binary and the player wrapper differs from the standard Electrosound init/play layout.

---

## 5. Technical Notes for Migration

### 5.1 Player structure (per Lemon64 waz post)

The compiled Electrosound PRG has this layout relative to load address:
- `load + $0000` .. `load + $0A64`: player code (including instrument/sequence/song data)
- `load + $0A65`: **play() entry point** (IRQ routine)
- `load + $0518`: init subroutine (JSR target)
- `load + $0A65 + $007B` and `+ $0084`: two `JMP $EA31` that must become `RTS` for PSID use

Init stub sets three memory locations:
- `$02AB` = tune number (zero-based)
- `$02FF` = tempo value
- `$02F9` = init flag ($01)

Variable-tempo tunes: `$02AD` stores the running tempo during playback and changes value mid-tune. Each tempo change requires a different CIA1 timer value; the Lemon64 thread describes this as "not fun" to convert.

### 5.2 What the init styles mean for the USF extractor

- **Styles A, B, D**: init_addr points inside or just after the player binary — the stub is preserved alongside the player in the PSID.
- **Style C** (the dominant Barry Leitch packing): init_addr = play_addr − $0A75 = load_addr − $0010. The init stub was placed 16 bytes *before* the player binary's load address. This means the SID file's "load" (which PSID infers from the data offset) actually starts 16 bytes early, at the init stub.

For the USF extractor, the safe approach is: **treat all canonical builds as a single player binary loaded at (play_addr − $0A65), regardless of init_addr**. The init stub's location only matters for understanding what the original ripping tool did; the player entry at play_addr is always authoritative.

### 5.3 Non-looping driver note

VGMPF says the driver is "non-looping." This means the play() routine returns when the song ends rather than cycling back to measure 1. PSID players call play() indefinitely, so end-of-song detection (if any) and the loop point must be understood to avoid playing garbage after song end.

---

## 6. HVSC Bundled Docs — Electrosound Mentions

Searched: `hvsc84/DOCUMENTS/{SID_file_format.txt, STIL.txt, BUGlist.txt, hv_sids.txt, HVSC.txt, Musicians.txt, Creators.txt, Songlengths.md5}`.

**Findings:**
- `Songlengths.md5` contains comment-header lines listing `Electrosound_64.sid`, `Strangled_Electrosound.sid`, `Lobotomy_Electrosound.sid`, `Howzat_64_Electrosound.sid` — these are the comment markers for the songlength entries, not technical documentation.
- No mention of Electrosound in STIL.txt, BUGlist.txt, SID_file_format.txt, or Musicians.txt.
- **No dedicated player documentation for Electrosound exists in the HVSC DOCUMENTS directory.** The knowledge lives in external sources only.

---

## Leads to Follow

1. **sidid.nfo byte signature** — the GitHub raw fetch returned only metadata. The actual Electrosound byte signature(s) in `cadaver/sidid.nfo` need to be extracted directly to confirm whether sidid distinguishes canonical vs. non-canonical builds. Run: `grep -A10 -i "electrosound" $(find /path/to/sidid -name "*.nfo")` if a local copy is available, or fetch the raw .nfo content via `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo` and look for the `[Electrosound]` block.

2. **The non-looping driver end condition** — VGMPF says non-looping. Need to determine: does play() simply return when the orderlist runs out (leaving a silent loop), or does it signal via a flag/register write? This affects whether extract needs to know song length or detect the end marker in the orderlist.

3. **Variable-tempo mechanics** — $02AD holds the current tempo. The Lemon64 thread confirms tempo changes during playback. The USF representation must decide: encode tempo as a per-sequence value (matching the Electrosound format's per-sequence tempo field), or capture the CIA1 timer values at each change point. The format already has per-sequence tempo in the Electrosound tool, so this is the natural representation.

4. **CSDb release page** (https://csdb.dk/release/?id=27433) — returned 503 in all fetch attempts. This is the authoritative source for version history, release date precision, and any known variants. Retry via Wayback Machine when available: `https://web.archive.org/web/*/https://csdb.dk/release/?id=27433`.

5. **CSDb release 85170** (Electrosound 64 by The Snail, 1985) — a second CSDb entry for Electrosound, possibly a crack/spread of the original. Also returned 503. May indicate a modified player variant.

6. **John Stormont's Electrosound History Book** (Onslaught, Gubbdata 2020) — John Stormont released 17 new Electrosound compositions in 2020 under a demoscene collection package. This may contain documentation, source files, or editor notes useful for understanding the format. Find it at CSDb by searching "John Stormont Electrosound History Book Onslaught 2020".

7. **Peter Clarke's non-standard wrappers** — his commercial titles (Kinetik 22-subtune, Top Duck 16-subtune, Gunstar 11-subtune) use non-canonical play addresses. These likely have a game-programmer-written wrapper around the Electrosound data that needs separate reverse-engineering if they are to be migrated.

8. **The 0x0518 init subroutine** — the Lemon64 post says JSR to load+$0518 initialises the player. Understanding what this subroutine does (beyond setting $02AB/$02FF/$02F9) is essential for the USF init.sid priming block.

9. **Drum sounds** — VGMPF says "24 drum sounds" are supported. Understanding how drum sequences differ from pitched sequences in the binary format is needed for full USF representation.

10. **Barry Leitch's Electrosound History Book or interview** — Barry Leitch has a personal website and has given multiple interviews. An interview-level question about how Electrosound's data was structured (sequence bytes, instrument records) could short-cut much of the reverse-engineering.
