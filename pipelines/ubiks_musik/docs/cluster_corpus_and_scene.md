# Ubik's Musik — Corpus Characterisation, Address Clusters, and Scene Context

## Provenance

| field | value |
|---|---|
| source_urls | hvsc84.db (local), csdb.dk, vgmpf.com, mancunian1001.wordpress.com, everygamegoing.com, lemon64.com, youtube.com |
| fetched_via | hvsc84.db READ-ONLY python3 queries + WebFetch/WebSearch |
| fetch_date | 2026-06-14 |
| author | sidfinity research agent (cluster_corpus_and_scene) |
| content_date | 2026-06-14 |
| reliability | HIGH for DB-derived facts (primary source); MEDIUM for scene/history (secondary web sources) |

---

## 1. Tool Overview

**Ubik's Musik** is a Commodore 64 music sequencer created by Dave Korn
("Ubik"), published by Firebird Software in October 1987 at £2.99.  Reviewed
at 81% in Zzap! #31 (November 1987).

Key capabilities (from manual + reviews):
- Three voice channels as vertical columns, each a sequence-of-sequences (sequence
  number + repeat count)
- 26 songs and 32 instruments per compiled file
- First editor to support logarithmic vibratos, waveform swaps, and wavetable
  drums (8 fixed drum sounds)
- Possibly first to support echoes via sustain-level changes on every note
- Pulse width modulation + portamento (note slide) + band-pass/high-pass/low-pass
  filter options
- "Compiler" output: a self-contained PRG (~7 KB) with the player at $C600 by default
- Game integration: programmers could call the driver to play a song on two voices
  with a sound effect on voice 3
- Drawback: high raster-time usage (noted in scene)
- Remained popular "almost exclusively in the UK" through the early 1990s

The tool was sold commercially; no source code has been published.  It was
cracked and distributed widely in the PD scene — at least 5 scene-cracked
copies are listed on CSDb (groups: Hotline, Teesside Cracking Service, RCS,
FBR/Trianon, Trianon; dates 1987–1989).

The SID files in HVSC were converted from PRG using tools such as PRG2SID
(by iAN CooG).  No SID player wraps the original Firebird PRG format directly
— the compiled PRG is essentially a self-contained player+data binary.

---

## 2. HVSC Corpus Shape (hvsc84.db, engine = `Ubik's_Musik`)

### 2.1 Totals

| metric | value |
|---|---|
| Total SIDs | **288** |
| PSID version | all v2 |
| All load_addr | $0000 (all; HVSC norm: PSID header carries the actual load address inside the binary) |
| Released range | 1987 – 2018 |
| Multi-subtune (n_subtunes > 1) | 118 / 288 (41%) |
| Single-subtune | 170 / 288 (59%) |
| CIA-timed (speed != 0) | 0 (all are VBI / vblank-timed) |

### 2.2 Release Year Distribution

| year | count | notes |
|---|---|---|
| 1987 | 54 | release year; Firebird, Players, John Stormont, Chris Abbott |
| 1987–89 | 30 | Kent Valdén (Noise of SID) — bulk date-range entries |
| 198? | 16 | Jinx Cracking Crew, Tonal Teapot, etc. — undated |
| 1988 | 41 | commercial peak |
| 1989 | 31 | Legend (Lyon_Legend / Patrick Ceuppens); drew Rodger |
| 1990 | 15 | Hi-Tec, Alternative Software |
| 1991 | 22 | Zaw Productions begins; Hi-Tec; CDU |
| 1992 | 38 | Zaw Productions peak (31) |
| 1993 | 9 | Point X, Zaw Productions |
| 1994 | 6 | Point X, Zaw Productions |
| 1995 | 10 | Ozone (9), John Stormont |
| 1996–1998 | 5 | Cosine Systems, Point X |
| 2018 | 1 | M. Hardy (modern revival) |

Primary commercial use: **1987–1991**.  Scene/demo use persists into the mid-1990s via
Zaw Productions (Warren Pilkington), Ozone, and Point X.

### 2.3 Songlength Distribution

| bucket | count | range |
|---|---|---|
| < 30 s | 9 | 6–29 s |
| 30–60 s | 19 | 31–59 s |
| 1–2 min | 38 | 63–116 s |
| 2–5 min | 114 | 121–298 s |
| 5–10 min | 63 | 300–599 s |
| > 10 min | 45 | 600–4055 s |

Most tunes fall in the 2–10 min range, consistent with looping game-score material
played at HVSC's standard "play until end or loop" songlength.

### 2.4 Subtune Count Distribution

| n_subtunes | count |
|---|---|
| 1 | 170 |
| 2 | 31 |
| 3 | 24 |
| 4 | 6 |
| 5 | 13 |
| 6 | 15 |
| 7 | 4 |
| 8 | 3 |
| 9 | 3 |
| 10 | 3 |
| 11 | 5 |
| 12 | 6 |
| 13 | 1 |
| 14 | 1 |
| 18 | 2 |
| 23 | 1 |

The 23-subtune file is `MUSICIANS/L/Lees_Anthony/Incredible_Shrinking_Sphere.sid`
(1989 Electric Dreams).  The two 18-subtune files are `GAMES/A-F/Die_Alien_Slime.sid`
and `MUSICIANS/D/Deadman/Ubik-Musik_Collection_I.sid`.

---

## 3. Address Cluster Analysis

All 288 SIDs have `load_addr = $0000` (PSID v2 norm; actual binary load is
embedded in the data).  The meaningful addresses are `init_addr` and `play_addr`.

### 3.1 Cluster Table

| Cluster | init_addr | play_addr | Count | % | Notes |
|---|---|---|---|---|---|
| **A — Canonical** | $C600 | $C603 | 120 | 41.7% | Standard compiled PRG; init at $C600 selects song# from A-reg; play entry at init+3 |
| **B — Multi-song C666** | $C600 | $C666 | 19 | 6.6% | init loads song# via X; separate fixed play entry at $C666 |
| **C — C601 patch** | $C601 | $C64E or $C666 | 13 | 4.5% | Eeben Aleksi (5) + Tonal Teapot (7) + Knatter (1); init shifted +1 byte |
| **D — CE-range extended** | $CE02–$CE60 | $C666 | 20 | 6.9% | Data extends past $C600 to $CE00+; player still at $C666; Lyon_Legend (14), Bellamy (3), Japmaster (3) |
| **E — B-range data + C666** | $B000–$BFFF | $C666 | 31 | 10.8% | Large data pre-$C600, player at $C666; Noise_of_SID (29 of 30 tunes) |
| **F — Fully relocated** | varies | varies (non-C6xx) | 62 | 21.5% | Complete relocation; Japmaster (14), Deadman collections (7), scattered |
| **G — C64E variant** | $Bxxx–$Cxxx | $C64E | 11 | 3.8% | Marc François / Sonix Systems; alternate play entry $C64E |
| **Oddity — play=0** | $C0D0 or $C600 | $0000 | 3 | 1.0% | Smith_Michael (2 × Boxing/BSL), Rodger (Certain_Drug); no vectored play |
| **Misc** | scattered | scattered | 9 | 3.1% | One-offs: $E000, $F600, $1xxx, etc. |

**Total: 288**

### 3.2 Cluster Interpretation

**Cluster A (canonical, 120 SIDs):**  The tool's standard compiled output.
Player binary loads at $C600; `init` at $C600 accepts subtune index in A-reg;
the immediately following `play` entry at $C603 is a bare IRQ handler.  This
is what a "normal" Ubik's Musik PRG2SID conversion produces.

**Cluster B ($C666 play, 19 SIDs):**  A multi-song variant where the data
block begins at $C600 and the actual player code starts at $C666.  Init still
at $C600 but uses X-reg or an alternative protocol to select the song.  Chris
Abbott's 11 MUSICIANS tunes are the main population; a few games.

**Cluster C (C601 patch, 13 SIDs):**  Init off-by-one at $C601.  Predominantly
Aleksi Eeben (Jinx Cracking Crew, 5 tunes, all play=$C64E) and Tonal Teapot
(7 tunes, play=$C666).  Suggests a local patch to the compiled PRG that shifts
the init vector by one byte; the play entry diverges by sub-group.  These are
PERIOD tunes (released 198?/late-1980s scene context).

**Cluster D (CE-range init, 20 SIDs):**  Music data grows past $C600 into the
$CE00–$CE60 range; init vector points into that data region; play remains at
$C666.  Dominant composer: Patrick Ceuppens / Lyon_Legend (14 × $CE60),
Paul Bellamy (3 × $CE50), Julian Potts/Japmaster (3 × $CE50/$CE4D).

**Cluster E (B-range init + C666, 31 SIDs):**  Very large data files; the
init_addr is somewhere in $B000–$BFFF (data only, not player code); player
lives at $C666 as in B/D.  29 of Kent Valdén's 30 Noise_of_SID tunes fall
here — each has a unique init address corresponding to where that tune's data
starts.

**Cluster F (fully relocated, 62 SIDs):**  Player relocated entirely away from
$C600.  Subgroups:
  - $7A00/$7C00/$7F00 — Deadman (Dennis Lindroos) collection SIDs: multiple
    tunes merged into one SID at a low address
  - $F600/$F660/$EA00 — Japmaster high-memory variants (Hi-Tec era, 1990–91)
  - $6600 — 6 SIDs (clone of canonical at alternate address)
  - Scattered $1xxx–$5xxx — one-off conversions from in-game PRGs

**Cluster G ($C64E play, 11 SIDs):**  Marc François (Skywave) Sonix Systems
tunes and a handful of others use play=$C64E as the IRQ entry; init is in the
$BC–$BE range pointing at data.  May be a specific version of the compiler or
a manual post-hoc fix.

**play=0 Oddities (3 SIDs):**  `Michael_Smith/Boxing_Manager.sid`,
`Smith_Michael/British_Super_League.sid` (both $C0D0 init), and
`Rodger_Andrew/Certain_Drug.sid` ($C600 init).  No vectored play — either
these are polled by BASIC or the PRG2SID conversion was incomplete.

### 3.3 init == play−3 relationship

The canonical pattern is `play = init + 3`.  Of the 288 SIDs, **120 follow
this exactly** (all cluster A).  The remaining 168 deviate — most are the
data-init variants (B/C/D/E/G) where init points into music data and play
is a fixed offset in the player.  A handful of the fully-relocated SIDs also
satisfy `play = init + 3` at their relocated address (e.g., Deadman's
$7A00/$7C00 collections, the $6600 cluster, the $4B00/$BD00 one-offs).

---

## 4. MUSICIANS Folder Distribution (29 distinct folders)

| Count | Folder | Composer | Notes |
|---|---|---|---|
| 56 | MUSICIANS/W/Waz | Warren Pilkington | Zaw Productions 1991–94; largest corpus |
| 45 | MUSICIANS/S/Stormont_John | John Stormont | 1987 (43) + 1995 (1); likely the earliest large batch |
| 30 | MUSICIANS/N/Noise_of_SID | Kent Valdén | Swedish; 1987–89 batch; cluster E dominant |
| 23 | (various DEMOS + GAMES) | — | 17 GAMES + 6 DEMOS + misc |
| 18 | MUSICIANS/L/Lyon_Legend | Patrick Ceuppens | Belgian; 1989 Legend label; cluster D |
| 14 | MUSICIANS/J/Japmaster | Julian Potts | Hi-Tec era 1989–91; heavy relocation |
| 12 | MUSICIANS/M/Mixer | Jouni Ikonen (Wild Finn) | Finnish; 1988 Albion/Byterapers |
| 11 | MUSICIANS/A/Abbott_Chris | Chris Abbott | 1987–88 Superior Software |
| 11 | MUSICIANS/D/Deadman | Dennis Lindroos | Finnish; collection SIDs at $7x00 |
| 10 | MUSICIANS/M/Merman | Andrew Fisher | 1990–93 Ozone/Zaw |
| 9 | MUSICIANS/R/Rodger_Andrew | Andrew Rodger (Drew) | 1989–91 |
| 9 | MUSICIANS/T/Tonal_Teapot | G. Davies & A. DeLucia | UK duo; 198? undated; cluster C |
| 6 | MUSICIANS/B/Bellamy_Paul | Paul Bellamy | 1990–91 Alternative Software |
| 6 | MUSICIANS/F/Francois_Marc | Marc François (Skywave) | 1988 Sonix Systems; cluster G |
| 5 | MUSICIANS/E/Eeben_Aleksi | Aleksi Eeben | Finnish; 198? Jinx Cracking Crew; cluster C |
| 4 | MUSICIANS/S/Sonic_Graffiti | Ben Hayes (Nutt) | 1988–89 Piracy Shed; low-address |
| 3 | MUSICIANS/H/Higgins_Neil | Neil Higgins | 1989 CDU |
| 2 | MUSICIANS/L/Lees_Anthony | Anthony Lees | 1988–89 Silverbird/Electric Dreams |
| 2 | MUSICIANS/K/Knatter | Björn Fogelberg | 1988 Xakk Cracking; cluster C |
| 2 | MUSICIANS/P/Perdita | Sandra Park | 1988 |
| 2 | MUSICIANS/S/Smith_Michael | Michael Smith & Jonathan Wells | 1990 Cult Games; play=0 |
| 1 each | MUSICIANS/W/Williams_Nick, Wilson_Mark, D/Dr_Code, J/Joseph_Richard, J/Jervis_Andy, J/Jade_Tiger, J/Stone_James, S/SMC | various | single-SID composers |

---

## 5. HVSC DOCUMENTS — Ubik's Musik Mentions

Searched `hvsc85/DOCUMENTS/STIL.txt` and `Musicians.txt` for "ubik" — **no
matches found**.  The STIL.txt file (Sub-Tune Information List) does not
contain any entries referencing Ubik or Ubik's Musik.  This is consistent
with STIL being per-SID commentary rather than engine-level docs.

The `SID_file_format.txt` and other DOCUMENTS files are format-spec docs with
no player-specific content.  No HVSC-bundled documentation covers Ubik's Musik
specifically.

---

## 6. Scene and Historical Context

### 6.1 Dave Korn ("Ubik") Background

David Korn adopted the handle "Ubik" from Philip K. Dick's 1969 novel while
on Compunet.  He was a professional programmer at Firebird Software (a budget
label of British Telecom / MicroProse UK), working on titles including *Arcade
Classics* and *Thrust II* (1988), for which he co-wrote music alongside Rob
Hubbard.  He wrote Ubik's Musik as a commercial tool sold by Firebird, reviewed
in Zzap! #31 (November 1987) by the author himself (unusual — the review
byline is Dave Korn).

### 6.2 Commercial Game Use (HVSC-confirmed)

From the HVSC GAMES/ directory (17 confirmed SIDs):

| Game | Publisher | Year | Composer | init pattern |
|---|---|---|---|---|
| Brainstorm | Firebird | 1987 | David Kirby | $6E50 / $6E25 (relocated) |
| Deviants | Players | 1987 | Mike Brown | $89C1 / $8A27 (relocated) |
| Protium | Polysoft/Alternative | 1987 | unknown | $A8B8 / $A8A0 |
| Thrust II | Firebird | 1988 | Dave Korn (Ubik) | $9000 / $A666 |
| Atlantis | Commodore Disk User | 1988 | B.N. Lewis | $A4B6 / $9B01 |
| Blip-Video Classics | Silverbird | 1988 | Tom Lanigan | $CE4D / $C666 |
| Joe Blade 2 | Players | 1988 | Mike Brown | $A6FA / $B666 |
| Jungle Raid | Imagez | 1988 | unknown | $48B9 / $491F |
| Lethal | Alternative Software | 1988 | Chris Mossop | $A3BE / $A424 |
| Space Warrior | Magic Disk 64/CP Verlag | 1988 | Christian Bruns | $C600 / $C666 |
| Die Alien Slime | Mastertronic Plus | 1989 | Tom Lanigan | $C600 / $C666 (18 subtunes) |
| Quadrant 4 | Clockwize | 1989 | Budgie | $C600 / $C603 |
| Cowboy Kidz | Byte Back/MC Lothlorien | 1990 | Andrew Carter | $C650 / $B3DD |
| Fire Breath | (Erik Hooijmeijer) | 1990 | Erik Hooijmeijer | $C600 / $C603 |
| Globetrotter | Coolsoft | 1990 | unknown | $7DE5 / $75FE |
| Madix | Commodore Disk User | 1991 | unknown | $7DC0 / $7417 |
| Zilch | Incubus | 1992 | unknown | $C600 / $C603 |

Additional confirmed commercial uses (from MUSICIANS/ entries):
- **Chess / Chess II / Galaforce 2 / Magnetic Fields** (Superior Software, 1988) — Chris Abbott
- **Street Warriors** (Silverbird, 1988) — Anthony Lees
- **Incredible Shrinking Sphere** (Electric Dreams, 1989) — Anthony Lees (23 subtunes)
- **Bangers and Mash / Fireman Sam / Popeye 2 / Double Dare / Huxley Pig** (Alternative Software, 1990–91) — Paul Bellamy
- **Bomb Fusion / Blazing Thunder / Speed Zone** (Mastertronic, 1989–90) — Julian Potts (Japmaster)
- **Yogis Great Escape / Top Cat / Futurebike / Space Rider / Chevy Chase / Road Runner** (Hi-Tec, 1990–91) — Julian Potts
- **To Hell and Back** (CRL, 1988) — Andy Jervis
- **International 3D Tennis** (Sensible Software/Palace, 1990) — Richard Joseph

Also confirmed from web sources: Tim Follin used it for **Agent X II: The Mad Prof's Back**
(Mikrogen, 1987, Stage 1 arrangement).

### 6.3 PD / Demo Scene Use

A substantial portion of the HVSC corpus is PD demo/intro music rather than
commercial games:

- **Warren Pilkington / Waz** (56 SIDs, Zaw Productions 1991–94): largest
  single-composer corpus; entirely PD/demo.
- **Kent Valdén / Noise of SID** (30 SIDs, 1987–89): Swedish scene; all in
  cluster E (large data files, player at $C666).
- **John Stormont** (45 SIDs, 1987 + 1995): the 43 SIDs from 1987 appear to
  be the bulk of his output, possibly a single-session music dump; 1 from 1995.
- **Tonal Teapot** (G. Davies & A. DeLucia, 9 SIDs, 198? undated): small UK
  PD duo; cluster C variant.
- **Aleksi Eeben** (5 SIDs, 198? Jinx Cracking Crew): Finnish; used in
  cracktros; cluster C, play=$C64E.
- **Jouni Ikonen / Wild Finn / Mixer** (12 SIDs, 1988 Albion/Byterapers):
  Finnish; fully relocated tunes.
- **Dennis Lindroos / Deadman** (11 SIDs, 1988–96 Finnish Code Masters + Point X):
  Created 7 collection SIDs (`Ubik-Musik_Collection_I` through `_VII`) packing
  multiple tunes at relocated addresses ($7A00/$7C00/$7F00/$7B00).
- **Julian Potts / Japmaster** (14 SIDs): dual use — commercial Hi-Tec work
  (1990–91) and PD/demo; heavy relocation into high memory ($F600/$EA00).
- **Andrew Fisher / Merman** (10 SIDs, 1990–93 Ozone/Zaw): PD scene.

### 6.4 Legal Episode

The Ubik's Musik demo tunes were used in a PD game called "Lunar Jailbreak"
(an abandoned Hewson title originally named "Breakout").  Future Publishing
republished it via *Commodore Format* magazine.  This led to a copyright case
at Manchester Magistrates Court; the court ruled in favour of the original
coders (Korn), with Future Publishing paying damages.

### 6.5 Tool Successor / Legacy

No direct successor tool from Dave Korn is known.  The tool's popularity was
UK-centric and waned after ~1992 as GoatTracker, SID-Wizard, and other trackers
emerged.  Composer Anthony Lees (who switched to Ubik's Musik in 1988) used it
for several Silverbird/Electric Dreams titles.  By contrast, Tim Follin used it
only once (Agent X II Stage 1) before developing his own drivers.

---

## 7. Migration Implications

### 7.1 Distinct Build Variants

The 288 SIDs resolve to **at least 7 distinct structural classes** for the
migration, summarised as:

| Class | Count | Core pattern |
|---|---|---|
| A — canonical $C600/$C603 | 120 | init=$C600, play=$C603; song# in A |
| B — $C600/$C666 multi-song | 19 | init=$C600, play=$C666; larger data footprint |
| C — $C601 patch | 13 | init offset +1; two sub-groups by play ($C64E / $C666) |
| D — CE-range data + $C666 | 20 | init in $CE00–$CE60; player at $C666 |
| E — B-range data + $C666 | 31 | init in $B000–$BFFF; player at $C666 |
| F — fully relocated | 62 | diverse; addr varies per file |
| G — $C64E alternate play | 11 | play=$C64E; init in data before $C600 |
| Oddity / play=0 | 3 | no play vector; likely JSR-only or incomplete PSID |
| Misc | 9 | one-off layouts |

The **highest-leverage target** for phase 1 is Class A (120 SIDs, 41.7%) —
the canonical compiled output from the Firebird tool.

For classes B/D/E (70 SIDs together), the player is always at $C666.  These
are likely the same engine binary but with data that overruns $C600; the
init/play split is different because `init` points into the music data, not
the player preamble.

Class F (62 SIDs) is the most complex — full relocation means the player
binary is at an arbitrary address.  The Deadman collections (7 SIDs at $7A00–
$7C00) are a particularly self-contained sub-group: the same player relocated
to make room for batched tunes.

### 7.2 Key Unknowns for RE

- **Exact init protocol**: does Class A pass song# in A-reg (jsr $C600 with A=N)
  or something else?  The Lemon64 forum (iAN CooG) says "many tunes start from
  index 4, not 0" — init indexing may not be zero-based.
- **Class B vs A**: is the player binary identical and only the data layout
  differs, or is $C666 a genuinely different player version?
- **Class C (+1 offset)**: is the $C601 init a one-byte NOP inserted before
  the real init, or does the player start at $C601?
- **Class G ($C64E)**: what is at $C64E?  Possibly an older version of the
  player where the IRQ entry point is at a different offset.
- **Relocation mechanism**: Deadman's collections suggest the tool OR the
  PRG2SID conversion supports a relocator.  Are there address tables that need
  fixing up, or is the player fully position-independent (PIC)?
- **SFX protocol**: the manual says "play song on 2 voices + SFX on voice 3"
  — this needs RE to understand the SFX call convention.
- **Speed**: all 288 SIDs have `speed = 0` (VBI).  No CIA-timed Ubik's Musik
  in HVSC.

### 7.3 Notable Individual SIDs

- `MUSICIANS/L/Lees_Anthony/Incredible_Shrinking_Sphere.sid` — 23 subtunes;
  Electric Dreams 1989; largest Ubik's Musik subtune count.
- `MUSICIANS/D/Deadman/Ubik-Musik_Collection_I.sid` — 18 subtunes at $C600;
  1988 Finnish Code Masters; 24-minute runtime (1459 s).
- `GAMES/S-Z/Thrust_II.sid` — Dave Korn himself; unusual layout ($9000/$A666);
  Firebird 1988.
- `GAMES/A-F/Die_Alien_Slime.sid` — 18 subtunes (Tom Lanigan); Mastertronic
  Plus 1989; 11-minute runtime.
- `MUSICIANS/R/Rodger_Andrew/Certain_Drug.sid` — play=$0000; 1989; may be
  incomplete PSID conversion.
- `MUSICIANS/S/Smith_Michael/Boxing_Manager.sid` + `British_Super_League.sid`
  — $C0D0 init, play=$0000; Cult Games 1990.

---

## 8. Leads to Follow

1. **Disassemble Class A canonical binary** ($C600 base): seed disassembly from
   any of the 120 Class-A SIDs to map the player structure.  The `Software_House_Demo`
   by Chris Abbott (5 subtunes, 1987 Chris Abbott, $C600/$C666 — actually Class B)
   or `Brainstorm.sid` (David Kirby, 1987, relocated but known Firebird title)
   are historically early candidates; however any canonical Class-A SID will do.

2. **Confirm init protocol** — instrument `siddump --pc-trace` on a multi-subtune
   Class-A SID to verify A-reg convention and zero-based vs 1-based indexing.

3. **Understand $C666 vs $C603** — diff the binary bytes at those offsets across
   3–4 Class-A SIDs and 3–4 Class-B SIDs.  If the player binary is identical
   and only the data layout differs, Classes A and B can share an extractor.

4. **Class D / E RE** — the CE60 tunes (Lyon_Legend cluster) and Noise_of_SID's
   30 tunes are a large block.  If the player at $C666 is identical to Class-B,
   this is a pure data-layout variant.

5. **Class G ($C64E)** — the Sonix Systems / Marc François tunes all use the same
   play address.  Inspect 2–3 of them to determine if $C64E is a fixed offset
   from the player load base or a genuinely different entry point.

6. **Relocation** — examine Deadman `Ubik-Musik_Collection_II` ($7F00) vs Class-A
   to verify whether the player binary is PIC or has embedded address tables that
   need patching.

7. **SFX convention** — none of the HVSC SIDs exercise the SFX protocol (they're
   all standalone music), but it will matter for completeness.  Check the Zzap!
   review manual excerpt (Zzap #31, 1987) for documented calling convention.

8. **CSDb disassembly search** — search CSDb for "Ubik" + "disassembly" or "source"
   to find any scene RE work.  The cracker releases (TCS, Hotline) sometimes include
   analysis notes.

9. **iAN CooG's PRG2SID tool** — the Lemon64 thread mentions `p2s` at
   `iancoog.altervista.org`.  If the tool source is available, it documents the
   init/play patching logic, confirming which part of the PRG binary is the player
   vs data.
