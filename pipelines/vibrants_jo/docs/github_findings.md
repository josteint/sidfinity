---
source_url: multiple (see inline citations)
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: various
reliability: primary
---

# Vibrants/JO Player — GitHub & Open-Source Tool Findings

## 1. Author Identity

**Poul-Jesper Olsen** ("JO"), Danish demoscene composer/coder.
- Scene aliases: JO, Jesper Olsen, Rock, Technic
- Groups (in order): Genesis Project → AMOK → Vibrants (joined ~1992)
- Personal website: www.vibrants.dk (defunct; archived copies exist)
- CSDb scener page: https://csdb.dk/scener/?id=1926
- Demozoo profile: https://demozoo.org/sceners/6764/
- MobyGames: https://www.mobygames.com/person/53900/jesper-olsen/

Key biographical note (from Demozoo / CSDb):
> "JO joined Vibrants around 1992, at that time already well known as a C64 composer
> for Amok. He had unique knowledge about coding players for computer formats such as
> the Amiga home computer and the Roland MT-32 on the PC. He also made his own players
> on C64 and for the AdLib sound card."

This confirms JO wrote his own custom C64 music player (not JCH's editor), which is
the "Vibrants/JO" engine detected by sidid.

Demozoo production list credits JO with "code player creation for 'Copper' (1992,
Surprise! Productions)" — evidence he shipped the player in at least one external demo.

DRAX has a worktune explicitly titled "Worktune in JO's player" (HVSC:
MUSICIANS/D/DRAX/Worktunes/Worktune_in_JOs_player.sid), confirming other Vibrants
members used JO's engine.

## 2. HVSC Corpus

Engine label in hvsc84.csv: **`Vibrants/JO`**

Total SIDs with this engine classification: **130** across:
- MUSICIANS/J/JO/ — 106 files (JO's own compositions)
- MUSICIANS/D/DRAX/Worktunes/ — 1 file (DRAX worktune in JO's player)
- MUSICIANS/H/HJE/ — ~23 files (Hans Jürgen Ehrentraut compositions)

The HJE files confirm JO's player was exported to at least one other composer.
HJE (Hans Jürgen Ehrentraut) is a German composer who released SIDs using this engine.

Songlength range: 12 s – 460 s (avg ~150 s).

## 3. sidid Signature Database (cadaver/sidid)

Source: https://github.com/cadaver/sidid
File: `sidid.cfg` (also mirrored in WilfredC64/player-id)

### [Vibrants/JO] signature block

Ten separate hex-pattern signatures identify this engine. Each line is one
independent pattern; the tool matches any one of them as sufficient for identification.
`??` = wildcard (any byte); `END` = pattern terminator.

```
[Vibrants/JO]
C9 80 D0 ?? BC ?? ?? C8 B1 END
29 7F DD ?? ?? D0 ?? A9 ?? 9D ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 F0 D0 ?? C8 B1 ?? 18 7D ?? ?? 9D ?? ?? C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? DE ?? ?? D0 ?? A9 01 9D ?? ?? FE END
BC ?? ?? B1 ?? C9 60 90 ?? 38 E9 60 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? D0 ?? 9D ?? ?? FE END
B9 ?? ?? 85 ?? DE ?? ?? ?? ?? BC ?? ?? B1 ?? C9 END
A2 ?? CE ?? ?? 10 ?? AD ?? ?? 8D ?? ?? EE ?? ?? EE ?? ?? EE END
C9 D0 90 ?? E9 D0 0A 0A 0A 9D END
A2 02 BC ?? ?? A9 00 99 05 D4 99 06 D4 A9 08 99 04 D4 CA 10 ?? 60 END
30 03 4C ?? ?? A9 00 9D ?? ?? A9 08 99 04 D4 98 48 A0 00 BD END
```

### [Vibrants/Laxity] signature block (for comparison)

Five signatures identify Laxity's player (CSDb ref: https://csdb.dk/release/?id=122333):

```
[Vibrants/Laxity]
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4 END
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4 END
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D END
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29 END
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90 END
```

### sidid.cfg Format

- File parsed by `readconfig()` in sidid.c; matched by `identifybytes()`.
- `??` = ANY (matches any single byte).
- `AND` = skip ahead to find next byte (discontinuous match).
- `END` = pattern terminates; match succeeds.
- Matching scans the **entire file buffer from offset 0** (no restriction to code section).
- Multiple signatures per player = OR logic (any one match is sufficient).
- No addresses in good signatures (code is often relocated).

Source: https://github.com/cadaver/sidid/blob/master/sidid.c

## 4. sidid.nfo — Player Metadata

Source: https://github.com/cadaver/sidid/blob/master/sidid.nfo (45.2 KB text file)

The Vibrants/JO entry has:
- AUTHOR: Poul-Jesper Olsen (JO)
- CSDB: entry not directly listed in JO block (the CSDB id=122333 belongs to Laxity)
- No explicit RELEASED date found in the visible portion

The sidid.nfo is a human-readable catalog of C64 music players with AUTHOR / RELEASED /
CSDB fields. It documents 787+ engines including Vibrants/JO.

## 5. Related Open-Source Tools

### cadaver/sidid
- URL: https://github.com/cadaver/sidid
- Written by Cadaver (Lasse Oorni)
- C language, uses BNDM-like scanning
- The canonical sidid.cfg signature database; all other tools derive from it.

### WilfredC64/player-id
- URL: https://github.com/WilfredC64/player-id
- Cross-platform C64 player identifier, inspired by sidid
- Ships its own copy of sidid.cfg in `config/sidid.cfg`
- Signature contributors: Wilfred Bos, iAN CooG, Professor Chaos, Cadaver, Ninja, Ice00, Yodelking
- Vibrants/JO signatures are included (confirmed by direct fetch of raw config)

### realdmx/c64_6581_sid_players
- URL: https://github.com/realdmx/c64_6581_sid_players
- Contains original/reverse-engineered player source code for selected composers
- Does NOT include Vibrants/JO (covers: Hubbard, Tel, Dunn, Galway, Gray, Kimmel,
  Ouwehand, Bjerregaard, Deenen, Whittaker, Bulka, Gray-Matt, Audial_Arts, Kimmel)

### Chordian/deepsid
- URL: https://github.com/Chordian/deepsid
- Created by JCH of Vibrants (NOT JO — JCH is Jens-Christian Huus, a different Vibrants member)
- PHP+JS web player; no special JO player detection code visible

### Chordian/sidfactory2
- URL: https://github.com/Chordian/sidfactory2
- SID Factory II (cross-platform C64 music editor, uses JCH's player engine)
- Not related to JO's player

## 6. Binary Structure Observations (from local HVSC files)

All observations are from HVSC binaries — NOT disassembly work, just header/layout survey.

### PSID Header Pattern
- PSID version 2 throughout
- Author field examples: "Jesper Olsen (JO)", "Hans Jürgen Ehrentraut (HJE)"
- Released field examples: "1988-89 Amok Sound Dept.", "1988 Amok Sound Dept."

### Load Address Distribution (106 JO/ SIDs)
The player is NOT fixed-address — it relocates freely across the address space.
Observed load addresses include: $0800, $0810, $0814, $0900, $0980, $0A00, $0FFF,
$1000, $1800, $2000, $2003, $2300, $2FFF, $3000, $3400, $3FFF, $4000, $4A03,
$5000, $5003, $6000, $A900, $C000, $E000, $F000 and many more.
This wide relocation range is consistent with the sidid signatures avoiding absolute addresses.

### Init/Play Offset Pattern
Common observed offset between load and init: 0 or 3 bytes.
Common play = init + 3 bytes (a JMP dispatch table at the very beginning).

Representative example (Airwolf_Theme, 2769 code bytes):
- Load=$1000, Init=$1003, Play=$1009
- $1000: 00 00 00  (3-byte pad / unused)
- $1003: 4C 1B 1A  JMP $1A1B  (init vector)
- $1006: 00 00     (2 byte pad)
- $1009: 4C 77 12  JMP $1277  (play vector)
- Signature hit: `30 03 4C` confirmed at offset $06FB in this file.

Representative example (Grid, 635 code bytes — minimal):
- Load=$1000, Init=$1169, Play=$1000
- Play entry at $1000: `A2 02 C6 75` — starts with LDX #2 then DEC zpg (frame counter dec)
- Init at $1169: `A2 3A A9 00 95 40 9D 00 D4 CA 10 F6 A9 1F 8D 18 D4 60` — clear all voice registers + set master vol $1F, RTS

Amok_Title (3864 code bytes, multi-subtune):
- Load=$1000, Init=$1000, Play=$1003
- $1000: 4C 0A 18  JMP $180A  (init jumps into data section — player code is at high end)
- $1003: 4C 15 10  JMP $1015  (play dispatches into play routine)
- $1006–$1014: data bytes (song parameter table)
- Play at $1015: reads a state byte to determine which subtune is active

### Code Size Range
- Minimum: 635 bytes (Grid — likely a minimal stripped version)
- Maximum: 6705 bytes (large multi-subtune tunes)
- Average: ~2966 bytes
- Typical: 2000-3500 bytes

### Relocation Behavior
The player body is at different offsets from load address in different tunes.
Some tunes place the player routine at the END of the binary (Amok_Title: JMP to $180A
while code loads at $1000), putting data before code.

## 7. Vibrants Group Context

Source: https://demozoo.org/groups/769/, https://retroworld.canell.dk/music/group/vibrants-c64.html

Vibrants was founded October 1989 by JCH, DRAX, and Link. All members were musicians.
Members: DRAX, JCH/Chordian, Joss, Laxity, Link, Metal, MSK, JO (joined ~1992), Deek (Scotland, ex-member).

Each member used their own editor/player:
- JCH: JCH Editor v1/v2.53/v3.04 (the popular one, released on CSDb)
- Laxity: his own player (sidid: Vibrants/Laxity, CSDB id=122333)
- JO: his own player (sidid: Vibrants/JO, this engine)
- DRAX: used multiple players including JO's (see "Worktune in JO's player")

## 9. Leads to Follow

### High priority (most likely to yield format knowledge)

1. **sidid.nfo full text for Vibrants/JO entry** — the NFO was too large to read fully.
   URL: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
   The JO entry may have AUTHOR/RELEASED/CSDB fields that link to an actual player release.

2. **CSDb scener page for JO** (id=1926) — CSDb was returning 503 during this session.
   URL: https://csdb.dk/scener/?id=1926
   When accessible: get full release list; look for "player" or "music system" releases
   (distinct from his music compositions). JO had 600+ credits but his tooling may be listed too.

3. **CSDb Vibrants group page** (id=328) — similarly inaccessible.
   URL: https://csdb.dk/group/?id=328
   Lists all Vibrants tools releases; cross-reference JO's standalone player if it exists.

4. **vibrants.dk archive** — the group's website is defunct but likely archived.
   URL: https://web.archive.org/web/*/vibrants.dk
   JO's AdLib MP3 files were known to be hosted there; C64 player source may also exist.

5. **"Delux Driver V2.0 by Vibrants (1989)"** — CSDb id=39845
   URL: https://csdb.dk/release/?id=39845
   Unknown if JO-related but is a 1989 Vibrants tool release worth investigating.

6. **Archive.org search for JO's music collection** — JCH's collection is on archive.org;
   check if a similar JO C64 collection exists:
   https://archive.org/search?query=JO+vibrants+c64

7. **"Copper" demo (1992, Surprise! Productions)** — Demozoo credits JO with "code player creation"
   on this demo. The demo binary may contain a clean copy of the JO player.
   Search CSDb: https://csdb.dk/search/?search=Copper+1992

8. **HJE (Hans Jürgen Ehrentraut)** — used JO's player for ~23 SIDs. His CSDb page may
   have notes about obtaining the player or format documentation.
   CSDb search: https://csdb.dk/search/?search=HJE

### Medium priority

9. **pouet.net search for Vibrants/JO** — demoscene releases sometimes have inline comments
   about player formats.

10. **The JCH complete C64 music collection (archive.org)** — contains JCH's works in JCH
    player format, not JO's; but the download may include a README describing the Vibrants
    player ecosystem.
    URL: https://archive.org/details/jch_c64_zip

11. **Smack My SID Up — Best of Vibrants** (archive.org id=mtk056)
    URL: https://archive.org/details/mtk056
    May contain player binaries alongside SID rips.

12. **WilfredC64/player-id config/sidid.cfg** — verify their version has same JO signatures
    and check for any additional comments.
    URL: https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg

## 8. No Existing Disassembly or Source Found

Extensive search found NO existing:
- Source code for the JO player (no GitHub / CSDb / archive.org upload found)
- Hand-annotated disassembly
- Format documentation
- Instrument/table layout description

The sidid signatures are the only machine-readable format knowledge in open-source tools.
The engine is identified but not documented beyond "exists and matches these patterns."
