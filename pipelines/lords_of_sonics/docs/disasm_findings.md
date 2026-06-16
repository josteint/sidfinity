---
source_url: local: multiple (see per-section citations)
fetched_via: direct
fetch_date: 2026-06-16
author: research session (Claude Sonnet 4.6)
content_date: 2026-06-16
reliability: secondary
---

# LordsOfSonics/MS Engine — Research Findings

Research conducted 2026-06-16. Sources: CSDb, HVSC local files (STIL.txt, BUGlist.txt,
hvsc84.csv), sidid.cfg (cadaver/sidid on GitHub), VGMPF Wiki, Remix64 interview,
direct binary inspection of local HVSC SID files.

---

## 1. Engine Identity and Lineage

**sidid name:** `LordsOfSonics/MS`

**Sub-variants identified by sidid.cfg:**
- `LordsOfSonics/MS` (base player)
- `(Parsec)` — sub-variant, The Parsec Music Editor V5.1
- `(Compotech_V2.x)` — later X-Ample Architectures evolution
- `(Sonic/SDS)` — another X-Ample variant (separate sidid signature)

**Authors:**
- Markus Schneider (MS) — engine author (coder/composer); aliases: **Diflex** (1988–??),
  **Synth-Man** (1987–1988); founded Lords of Sonics (LOS) in 1988; joined X-Ample
  Architectures March 1989.
- Jens Blidon — co-founder LOS, musician; the player was originally written *for* Blidon.
- Helge Kozielek — additional code (see Move.sid version history; also in Compotech).
- Geir Tjelta — Version 2.3 upgrade (credited in Move.sid version block).
- Joachim Multermann — editor surface (see Move.sid version history; also in Compotech).

**Group:** Lords of Sonics (LOS), Cologne, Germany, 1988–1989.
Later: X-Ample Architectures (XAP), Germany, 1989–present.

**HVSC STIL comment (from /MUSICIANS/S/Schneider_Markus/):**
> "Markus Schneider composed under the alias 'Diflex' in his early years and then later
> under his own name. In addition, he also composed under the name 'Lords of Sonics',
> which was a music team consisting of Schneider and Jens Blidon."

---

## 2. Version History (recovered from binary strings in SID files)

The `Move.sid` (load $1000) contains an embedded development history block at
approximately offset $1058 (PETSCII-encoded):

```
COMPOSER: MARKUS SCHNEIDER
VERSION 2.0 PLAYER BY MARKUS SCHNEIDER, ADDITIONAL CODE BY HELGE KOZIELEK,
  EDITOR BY JOACHIM MULTERMANN
VERSION 2.2 UPGRADE PLAYER BY MARKUS SCHNEIDER
VERSION 2.3 UPGRADE PLAYER AND EDITOR BY GEIR TJELTA
VERSION 2.4 UPGRADE PLAYER AND EDITOR BY MARKUS SCHNEIDER
```

Additional versions found by scanning all 123 HVSC `LordsOfSonics/MS` SIDs:

| Version string in binary | Representative SID | Notes |
|---|---|---|
| `PLAYER 2.3 (SHORTENED)` | `Vectormania.sid` | "MUSIC DONE FOR MDG BY THE LORDS OF SONICS. PLAYER 2.3 (SHORTENED) - HI IVO H., BWB, MWS, MDG, WK, X-AMPLE ETC..." |
| `PLAYER 4.1` | `Lingo.sid` | "MUSIC BY LOS ... PLAYER 4.1" |
| `PLAYER V05.1` | `Babyface/Babes_Boogie.sid` | Parsec Music Editor V5.1 (matches CSDb release #10744 title exactly) |
| `MUSIC AND PLAYER (C) BY MARKUS SCHNEIDER/X-AMPLE ARCHITECTURES` | `Elite_Squad.sid` | X-Ample era |
| No embedded string (majority) | 99/123 SIDs | Player binary present but no version ASCII |

The **99 unlabelled SIDs** likely use versions 2.x–4.x with the same player binary
but without the embedded version annotation.

**Note from STIL for `Crystal_Fever.sid`:**
> "The drums, inspired from a jazz lp, used my new sound player for the first time." (MS)
This places the debut of the LOS player at the `Crystal_Fever.sid` composition (circa 1988–1989).

---

## 3. Tool Releases

### 3.1 The Parsec Music Editor V5.1 (1989)
- **CSDb release:** #10744
- **Group:** Mnemonic Designs (Sweden)
- **Credits:** Code: ADT, Markus Schneider (Lords of Sonics / X-Ample Architectures), Nic
- **Music (demo):** Jeroen Tel (Maniacs of Noise) — "Tomcat"
- **Bug-Fix & Documentation:** SMC (Pretzel Logic)
- **Format:** D64 disk image + T64 (without intro, from Ruthless Music Disk)
- **sidid sub-variant name:** `(Parsec)`

### 3.2 Compotech (1992) and Compotech V2.1 (1995)
- **CSDb releases:** #130599 (1992) and #122614 (1995)
- **Group:** X-Ample Architectures (XAP)
- **Code:** Chap Bizarre, Joachim Fräder, Markus Schneider
- **Music (demo in Compotech 1992):** Thomas Detert ("Magic Disk 64 1992/06")
- **sidid sub-variant name:** `(Compotech_V2.x)`
- **Docs 2 Compotech:** CSDb #253740 (documentation release by Astral / Mister Giga)
- **Compotech cracked:** CSDb #82103 (The Force, 1992) and #170243 (Extacy, 1995)

### 3.3 Lords of Sonics Music Editor / LOS Player Leo Tune Editor V1.0 (2023)
- **CSDb release:** #230753
- **Creator:** Bansai
- **Key fact from user comment:** "basically it's another editor using the same player
  code as The Parsec Music Editor V5.1"
- **Contents:** ~140 pre-loaded SID tracks including works by Jens Blidon, A-Man, Markus
  Schneider
- **Recovery instruction:** `sys 20995` to restart after crash
- **User interface:** reportedly resembles Future Composer

---

## 4. sidid Detection Signatures (from cadaver/sidid sidid.cfg + sidid.nfo)

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg

```
LordsOfSonics/MS
79 ?? ?? 48 D0 06 A4 ?? C0 04 90 02 END
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4 END

(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06 END

(Compotech_V2.x)   [under X-Ample]
A9 ?? 8D ?? ?? CE ?? ?? 10 ?? A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 90 ?? 20 ?? ?? ?? ?? 69 07 AA ?? 15 90 ?? A9 ?? 09 ?? 8D END

(Sonic/SDS)
BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 A9 00 F0 12 CE ?? ?? 10 END
```

**Binary verification (Parsec sig confirmed in Babes_Boogie.sid at offset $1132):**
```
9D 21 10 9D 83 10 9D 24 10 CA 10 E5 A9 1F 8D 54 11 A9 01 8D 06 10
A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 1F 8D 18 D4 A2 02 ...
```
(Absolute addresses depend on load address; this example: load=$1000)

---

## 5. HVSC Corpus Statistics

From `hvsc84.csv` (sidid engine column = `LordsOfSonics/MS`):

- **Total SIDs:** 123
- **Games:** 7 (Arcade_Pilot, Mean_Car, Peter_Pilot, Shoot_Out, Xytris-The_Game_preview + 2 more)
- **Demo/unknown:** 2

**Musicians who used the LordsOfSonics/MS engine (by SID count):**

| Musician | SIDs |
|---|---|
| Blidon_Jens | 34 |
| Schneider_Markus | 23 |
| Babyface | 17 |
| A-Man | 8 |
| Spang_Jesper | 8 |
| Ice | 6 |
| Mc_Olly | 6 |
| SMC | 4 |
| Kleinert_Tim | 2 |
| Wilson_Mark | 2 |
| Sphere_Success | 2 |
| Devilock | 1 |
| Doussis_Stello | 1 |
| Palmonari_Stefano | 1 |
| Stoeten_Johann | 1 |

**Note:** The X-Ample variant (`engine='X-Ample'`) is a SEPARATE sidid classification
with **380 SIDs** — it is NOT included in the 123 above. The X-Ample engine shares
Compotech lineage but is classified distinctly by sidid.

**Also note:** `VandaliSID.sid` (Schneider_Markus) is classified as
`Geir_Tjelta/Comptech-X` — yet another branch.

---

## 6. Binary Structure (V05.1 / Parsec, from Babyface/Babes_Boogie.sid)

All examined V05.1 SIDs share the same layout:

```
$1000: JMP  $10D8       ; 4C D8 10  — jump to INIT routine
$1003: JMP  $10E6       ; 4C E6 10  — jump to PLAY routine

$1006–$10D7  (D2 bytes = 210 bytes): SONG DATA BLOCK
$10D8–$10E5  (0E bytes): INIT routine (calls PLAY after zeroing state)
$10E6–end:               PLAY routine (main music engine)
```

**The data block ($1006–$10D7) layout (preliminary, from 5 SIDs):**

Byte offsets relative to $1006:
- `+00` = $01 always in single-song SIDs (song count? or version flag)
- `+01–+05` = zeroed init / playback state counters
- `+06–+0B` = something (varies per song; looks like speed / instrument indices)
- `+0C–+0D` = $FF $D7 in some SIDs (could be sentinel or tempo)
- The data block holds per-voice state and song-position pointers

**Player code structure (from hex dump at $10D8):**

The PLAY entry at $10E6 (`init=false` path):
1. Reads byte at `$10xx` (a voice-select / dispatch counter)
2. Dispatches to per-voice processing (3 voices)
3. For each voice: decrements note counter, looks up note/instrument from song data,
   writes freq lo/hi, waveform, ADSR, pulse width to $D400–$D418

The init routine at $10D8:
- Loads song number into a slot
- Zeros voice state (9 STA absolute,X instructions matching sidid Parsec sig)
- Clears SID registers ($D400–$D418, i.e. `A2 18 A9 00 9D 00 D4 CA 10 FA 60`)
- Sets master volume (`A9 1F 8D 18 D4` = $D418 := $0F)
- Calls into PLAY

**Key instruction at INIT:**
```asm
LDX #$18
LDA #$00
STA $D400,X  ; zero SID regs $D418 down to $D400
DEX
BPL *-3
RTS
```

**Version string location:** Embedded as text near the end of the song data block.
Example from Babes_Boogie:
```
"BABE'S BOOGIE" COMPOSED BY BABYFACE IN PLAYER V05.1! ...
```
Located at approximately offset $095F within the SID code region (absolute address
varies by load address).

**Typical SID file size:** 2500–3900 bytes total (player is ~600–1100 bytes of
machine code; data block is ~200–400 bytes; song data follows).

---

## 7. Memory Layout Variability

The engine is **relocatable**: load addresses observed in HVSC corpus:

| Load addr | Examples | Notes |
|---|---|---|
| $1000 | Most Babyface, A-Man, Spang_Jesper | Most common |
| $3000 | Beatbassie_2, Timezone (partial) | |
| $4000 | Mean_Car, some others | |
| $9400 | Peter_Pilot | |
| $A000 | Slot_Mashine, Lingo | |
| $F000 | Life_Goes_On | |

Multi-subtune SIDs exist (e.g. Timezone: 13 songs, Arcade_Pilot: 4 songs,
No_Mercy: 13 songs). No_Mercy is large (32KB) and likely uses a different song-dispatch
structure than the single-song variants.

Init addr is typically load+$03 (for the JMP play at +$00 and JMP init at +$03 layout).

---

## 8. Known Users and Games

Games using LordsOfSonics/MS (from HVSC):
- **Arcade Pilot** (GAMES/A-F/)
- **Mean Car** (GAMES/M-R/)
- **Peter Pilot** (GAMES/M-R/)
- **Shoot Out** (GAMES/S-Z/)
- **Xytris – The Game preview** (GAMES/S-Z/)

Commercial game soundtracks composed by Schneider (may use X-Ample successor engine):
- Rolling Ronny (Virgin/Starbyte, 1991)
- No Mercy (Golden Disk 64/CP Verlag, 1989) — sidid says LordsOfSonics/MS, large SID
- Lethal Zone (1991)
- Xiphoids (CP-Verlag)
- Django
- Crown
- Dick Tracy
- Crystal Fever (first use of new player, per composer's STIL comment)

---

## 9. Related / Successor Engines

1. **X-Ample** (380 SIDs in HVSC) — the Compotech-era engine; same authors but
   different sidid signature. Represents the post-1989 X-Ample Architectures era.
2. **Geir_Tjelta/Comptech-X** — one SID (`VandaliSID.sid`) classified separately;
   suggests Geir Tjelta (who did v2.3 upgrade) created his own branch.
3. **XTracker_V4.1x** — listed under the LordsOfSonics/MS sidid.nfo entry; by Tufan
   Uysal / The Art Project Studios (1996). This appears to be a later tool that shared
   some code or was inspired by the LOS player.

**From Remix64 interview (Markus Schneider on Compotech):**
> "The last soundplayer based on my old player. Helge Kozielek and Mario van Zeist did
> some corrections to optimise the speed [of the X-Ample player]. Joachim Fraeder
> handled the interface programming."

---

## 10. Parsec Music Editor Context

### CSDb Entry (release #10744)

- Released 1989 by Mnemonic Designs (Sweden — note: Swedish group, not German)
- The editor was distributed as an intro-bearing D64 and a plain T64 from Ruthless Music Disk
- Includes a demo tune by Jeroen Tel ("Tomcat")
- The "V5.1" version number implies earlier versions existed (v1–v5.0 not in HVSC/CSDb record)

### Parsec V5.1 vs earlier versions
From binary analysis of HVSC SIDs:
- V05.1 tagged SIDs: 12 (Babyface, Sphere_Success, Wilson_Mark + some SMC)
- Player 4.1: 1 SID (Lingo — early Schneider composition)
- Player 2.3: 1 SID (Vectormania — early LOS demo)
- "2.4 / 2.3 / 2.2 / 2.0" history: embedded in Move.sid
- Earliest versions (v2.0 and before): attributed to 1988 development period

### Format interface
From the 2023 Bansai release (CSDb #230753) user comments: the editor UI resembles
Future Composer. The `sys 20995` ($520B) restart address suggests the editor loads
at a standard C64 location.

---

## 10b. Move.sid Special Note (MODERN Comptech composition)

`Move.sid` (MUSICIANS/S/Schneider_Markus/Move.sid) is classified as `LordsOfSonics/MS`
by sidid but contains an embedded header string:

```
COMPTECH MUSIC PLAYER BY XAP - TRACKNAME: MOVE, LENGTH: 05:13, YEAR: 2020,
COMPOSER: MARKUS SCHNEIDER
```

This is a **2020 composition** using the Comptech player by X-Ample (XAP). The binary
layout differs from V05.1: the entry point uses `JSR $1B11` (init) + `JMP $1208` (play)
rather than the double-JMP table. The version history block embedded in this SID (2.0→2.4)
suggests it uses the v2.4 player and was composed with the Comptech editor.

This confirms the engine lineage is still alive as of 2020 and that Markus Schneider
continues to use the Comptech/X-Ample player for new compositions.

---

## 11. Gaps / Unknowns

- **Instrument format**: not yet decoded. The data block ($1006–$10D7) in V05.1 SIDs is
  ~210 bytes; structure within it (instrument table, wavetable, sequence/orderlist pointers)
  is not yet mapped. The block's content varies between SIDs (it is musical data, not
  player code).
- **Sequence/pattern format**: not yet extracted. Player code suggests pointer-based
  access to song data that comes *after* the 210-byte header block.
- **Disassembly**: no publicly available hand-annotated disassembly found. The cadaver/sidid
  sig is the only public RE artifact beyond our own binary inspection here.
- **Version 1.x**: no HVSC SID found with a "PLAYER 1.x" string. Earliest confirmed is 2.0.
- **Editor disk image**: the Parsec V5.1 D64 is available on CSDb (#10744) but the disk
  image has not been loaded into this research session. The actual editor binary on disk
  would contain the full player + editor interface code.
- **Documentation**: "Docs 2 Compotech" (CSDb #253740) exists but the content is on
  the actual disk image; not retrieved in this session.
- **No_Mercy.sid structure**: 32KB, 13 songs, play=$0000 — this may be a different
  variant or extended multi-song structure; needs separate investigation.
- **X-Ample engine (380 SIDs)**: a distinct sidid classification from LordsOfSonics/MS;
  not researched in depth here.
- **Geir Tjelta/Comptech-X**: only 1 SID in HVSC; engine details unknown.

---

## 12. Chronology

| Year | Event |
|---|---|
| 1987–1988 | Markus Schneider active as "Synth-Man" then "Diflex" |
| 1988 | Schneider spends 2 months writing the first LOS sound player for Jens Blidon |
| 1988 | Player v2.0 released (with "additional code by Helge Kozielek, editor by Joachim Multermann") |
| 1988–1989 | LOS group active; Vectormania uses Player 2.3 (shortened); Move.sid uses 2.4 |
| ~1988 | Crystal_Fever.sid — first use of "new sound player" (composer's own note in STIL) |
| 1989 | Parsec Music Editor V5.1 released by Mnemonic Designs (CSDb #10744) |
| 1989 | Lingo.sid — "PLAYER 4.1" version |
| 1989 Mar | Schneider joins X-Ample Architectures |
| ~1989 | Jens Blidon leaves for military service; Schneider merges LOS player with X-Ample's |
| 1989+ | X-Ample variant engine used for game work (Rolling Ronny, Lethal Zone, etc.) |
| 1992 | Compotech released (CSDb #130599) |
| 1995 | Compotech V2.1 released (CSDb #122614) |
| 2023 | Bansai releases "Lords of Sonics Music Editor / LOS Player Leo Tune Editor V1.0" (CSDb #230753) using same Parsec V5.1 player code |

---

## 13. Source URLs

Primary sources:
- CSDb Parsec V5.1: https://csdb.dk/release/?id=10744
- CSDb Compotech 1992: https://csdb.dk/release/?id=130599
- CSDb Compotech V2.1: https://csdb.dk/release/?id=122614
- CSDb LOS Music Editor 2023: https://csdb.dk/release/?id=230753
- CSDb LOS group: https://csdb.dk/group/?id=757
- CSDb X-Ample group: https://csdb.dk/group/?id=245
- CSDb Markus Schneider: https://csdb.dk/scener/?id=6003
- CSDb Jens Blidon: https://csdb.dk/scener/?id=2205
- sidid.cfg (signatures): https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
- sidid.nfo: https://github.com/cadaver/sidid/blob/master/sidid.nfo
- VGMPF Markus Schneider: https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider
- Remix64 interview: https://remix64.com/interviews/interview-markus-schneider.html
- HVSC STIL.txt: local: /home/jtr/sidfinity/hvsc84/DOCUMENTS/STIL.txt
  (section: ### /MUSICIANS/S/Schneider_Markus, offset 2869141)

---

## Leads to Follow

1. **Download and inspect the Parsec V5.1 D64** (CSDb #10744) — the editor binary
   will contain the full player + instrument editor; this is the primary target for a
   full disassembly.

2. **Download the Compotech D64** (CSDb #130599 or #122614) — to understand the X-Ample
   evolution and whether it's the same binary as the X-Ample sidid variant.

3. **Inspect "Docs 2 Compotech"** (CSDb #253740, disk `d2ct.d64`) — likely contains
   format documentation.

4. **Decode the 210-byte data block** (offsets $1006–$10D7 in V05.1 SIDs) — use
   multiple V05.1 SIDs to cross-reference; instrument table, wavetable, orderlist
   pointers should be recoverable by correlation.

5. **No_Mercy.sid** — 32KB, 13 songs, play=$0000 — may be a special multi-song variant
   or an extended engine. Needs dedicated investigation.

6. **Jesper Spang SIDs** — 8 SIDs, composer name "Mer_Parsec" (Danish: "more Parsec")
   suggests he used the Parsec editor; might have documentation.

7. **Bansai's 2023 editor** (CSDb #230753) — the disk image `disk_los_leo.d64` is
   available (284 downloads); loading it may reveal the editor UI and data format
   interactively, since it "uses the same player code as Parsec V5.1".

8. **X-Ample variant (380 SIDs)** — separate research needed; this is a much larger
   corpus and likely represents the "professional era" engine used for commercial games.

9. **Vectormania.sid text**: "HI IVO H., BWB, MWS, MDG, WK, X-AMPLE ETC." — these are
   scene-era acknowledgements; MDG = "Magic Disk Group" (CP Verlag magazine). Could
   trace more users.

10. **Geir Tjelta** — did v2.3 upgrade; also credited as author of `Geir_Tjelta/Comptech-X`.
    Check his CSDb profile for more engine context.
