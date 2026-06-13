# X-Ample / Compotech — CSDb Release History

<!-- provenance:
  source_url: https://csdb.dk/ (multiple pages)
  fetched_via: WebFetch + direct urllib fetch + D64 disk image download
  fetch_date: 2026-06-13
  author: various CSDb contributors
  content_date: 1989-2025
  reliability: HIGH (primary database; D64 files are original releases)
-->

## Group: X-Ample Architectures (XAP)

- **CSDb group ID:** 245
- **Founded:** July 1988 by Stephen Taylor, Takashi, General X, Chap Bizarre
- **Motto:** "Bit For Bit A Hit"
- **Country:** Germany
- **Website:** http://www.xap64.de (currently offline)
- **Group types:** Demo Group, Game Development Group
- **Trivia:** "X-ample" stands for "Example" (stated in their 1988 demo _Blade Runner_).
  "Double Density" was NOT their publishing label — it was a separate label by Walter Konrad
  at CP Verlag.
- **CSDb rating:** 8.8/10 (22 votes)

### All Members

| Handle | Real name (where known) | Period | Role |
|--------|------------------------|--------|------|
| Markus Schneider | Markus Schneider | March 1989 → | Coder, Musician |
| Thomas Detert | Thomas Detert | July 1988 → | Musician |
| Michael Detert | Michael Detert | July 1988 → | Graphician |
| Thomas Heinrich | Thomas Heinrich | July 1988 → | Graphician |
| Helge Kozielek | Helge Kozielek | July 1988 → (inactive) | Coder |
| Mr. Cursor | — | March 1989 → (inactive) | Coder |
| Joachim Multermann | — | 1989 → | Coder |
| Joachim Fräder | — | 1989 → 2005 | Coder |
| Chap Bizarre | — | July 1988 → | Coder (ex) |
| Stephen Taylor | — | July 1988 → | Musician (ex) |
| Takashi | — | July 1988 → | Graphician, Musician (ex) |
| General X | — | July 1988 → | Graphician (ex) |
| The Viking | — | 1988 → 1989 | Coder (ex) |
| Plasticman | — | 1988 | Coder, Swapper (ex) |
| Cameron, ME, Tomcat, TPA | — | 1988 | various (ex) |

---

## Tool Releases: Compotech / Parsec Music Editor

### 1. The Parsec Music Editor V5.1

- **CSDb ID:** 10744
- **Year:** 1989
- **Group:** Mnemonic Designs (MCD)
- **Credits:** Code: ADT, Markus Schneider (Lords of Sonics / X-Ample Architectures), Nic;
  Music: Jeroen Tel (Maniacs of Noise); Graphics: Kee; Bug-fix + Docs: SMC (Pretzel Logic)
- **Download:** http://csdb.dk/getinternalfile.php/129717/Parsec_5_1-Mnemonic_Designs.d64 (389 downloads)
- **Also:** http://csdb.dk/getinternalfile.php/129729/Parsec_4_info.t64 (137 downloads) — Parsec V4 info file
- **Notes:** This is the Mnemonic Designs release of V5.1, with intro. A separate release from the
  same version on Ruthless Music Disk omits the intro. Cracked versions were released by Topaz
  Beerline, Raiders of the Lost Empire, X-Plicit, and Genesis Project in 1991.
- **D64 contents:** SEQ file `(M)PARSEC V5.1` (64 blocks = ~16 KB) — the editor binary (compressed).

### 2. Compotech (1992 release)

- **CSDb ID:** 130599
- **Year:** July 1992
- **Group:** X-Ample Architectures (XAP)
- **Credits:** Code: Chap Bizarre, Joachim Fräder, Markus Schneider (Lords of Sonics / X-Ample);
  Music: Thomas Detert
- **SID used in release:** Magic_Disk_64_1992_06.sid (Thomas Detert)
- **Download:** http://csdb.dk/getinternalfile.php/129662/Compotech-X-Ample.d64 (430 downloads)
- **D64 contents:**
  - SEQ `compotech   /xap` (45 blocks = ~11 KB) — editor binary containing player version 3.2 source
  - SEQ `ed>demo sfx` (4 blocks = ~807 bytes) — demo SFX data block
  - SEQ `ed>demo song` (11 blocks = ~2668 bytes) — demo song data

### 3. Compotech V2.1 (final release)

- **CSDb ID:** 122614
- **Year:** August 1995
- **AKA:** Comptech V2.1
- **Group:** X-Ample Architectures (XAP)
- **Credits:** Code: Chap Bizarre, Joachim Fräder, Markus Schneider (Lords of Sonics / X-Ample)
- **Download:** http://csdb.dk/getinternalfile.php/121250/Comptech_2.1.d64 (451 downloads)
- **D64 contents:**
  - SEQ `comptech 2.1 [x]` (50 blocks) — editor binary
  - SEQ `.player-routine` (65 blocks = ~16.5 KB) — full annotated TurboAss player source (Version 3.2)

### 4. Docs 2 Compotech

- **CSDb ID:** 253740
- **Group:** Astral
- **Credits:** Music: Xayne (Beat Machine / Crest); Docs: Mister Giga
- **Downloads:**
  - https://csdb.dk/getinternalfile.php/270228/Compotech%20The%20Force%20full%20release.d64 (93 downloads)
    — The Force full release with D2CT docs + cracked editor
  - https://csdb.dk/getinternalfile.php/270227/d2ct.d64 (41 downloads)
    — standalone docs viewer
- **D64 contents (The Force full release):**
  - SEQ `COMPOTECH/FORCE` (70 blocks) — cracked/compressed editor binary
  - SEQ `1.SFX DEMO` (4 blocks) — demo SFX data
  - SEQ `2.MUSIC DEMO` (11 blocks) — demo song data
  - SEQ `DOCS2COMPOTECH!` (21 blocks) — C64 viewer program for documentation
- **Notes:** The DOCS2COMPOTECH file is a crunched C64 viewer. Text content could not be
  extracted in plaintext — requires runtime decrunching on real hardware or emulator.
  The viewer displays text with title "Docs 2 Compotech" and music by Xayne/Beat Machine.

---

## Version History (reconstructed from player sources)

| Version | Year | Evidence |
|---------|------|---------|
| Parsec Music Editor V4.x | ~1988 | T64 info file: "PARSEC 4.0+ INFO" |
| Parsec Music Editor V5.1 | 1989 | CSDb release 10744 (Mnemonic Designs) |
| Compotech (first release) | 1992 | CSDb release 130599; player binary contains V3.2 string |
| Compotech V2.1 | August 1995 | CSDb release 122614; player-routine SEQ says "VERSION 3.2" |
| XTracker V4.1x / V4.2x | ~1993+ | SIDId classification (not in CSDb) |

Note: The "VERSION 3.2" string is found in BOTH the 1992 and 1995 player-routine files —
suggesting the player core did not change major version between the 1992 release and V2.1.
The editor UI (Compotech) is versioned separately from the player.

---

## Related/Cracked Releases on CSDb

| CSDb ID | Title | Year | Group |
|---------|-------|------|-------|
| 82103 | Compotech | 1992 | The Force (TF) |
| 170243 | Compotech | 1995 | Extacy (XTC) |

---

## X-Ample Architectures Full Release List (non-tool)

92 total releases 1988–2017. Notable game credits relevant to engine:
- _Blue Angel 69_ (1989) — Thomas Detert music
- _Coalminer_ (1991) — Thomas Detert music
- _Dynamoid_ (1990) — Thomas Detert music
- _Zillion_ (1993) — Thomas Detert music
- _Parsec_ game (1993) — Thomas Detert music
- _Bronx Medal_ (1994) — Thomas Detert music
- _Veterans of Style_ (2017 demo) — Evoke 2017, 8th place Mixed Demo

## Notable External Users of the Engine

Thomas Detert used the X-Ample engine for commercial C64 game soundtracks across 177+ HVSC SIDs.
Stefan Hartwig: 134 SIDs. Markus Schneider himself: 105 SIDs.
Famous game soundtracks: Turrican 3, Katakis, numerous Factor 5 / Rainbow Arts productions.

## Pouet.net

X-Ample Architectures is NOT listed in Pouet.net — they were a C64-only group and Pouet
focuses on multi-platform demo scene. No Pouet page exists.
