# Provenance Log — Rob Hubbard Research Wave 1

All URLs attempted during the 2026-04-21 research session.

| URL | Status | Notes |
|-----|--------|-------|
| https://www.1xn.org/text/C64/rob_hubbards_music.txt | OK | C=Hacking #5 McSweeney article — key reference |
| https://github.com/Chordian/sidfactory2 | OK (search only) | SID Factory II — no Hubbard-specific importer found |
| https://github.com/Galfodo/SIDdecompiler | OK | STHubbardRipper.cpp — key source, see sidfactory_parser_notes.md |
| https://raw.githubusercontent.com/Galfodo/SIDdecompiler/master/src/SIDdisasm/STHubbardRipper.cpp | OK | Full source fetched, mostly commented-out |
| https://raw.githubusercontent.com/Galfodo/SIDdecompiler/master/src/SIDdisasm/siddisasm.cpp | OK | Usage only, no Hubbard internals |
| https://raw.githubusercontent.com/Galfodo/SIDdecompiler/master/test/monty.asm | OK | Annotated assembly output |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg | OK | Signatures for Rob_Hubbard, Paradroid/HubbardEd, Rob_Hubbard_Digi, Giulio_Zicchi, Bjerregaard |
| https://github.com/katkoviiva/BE6502_SidPlayer | OK | MontyOnTheRun_BE6502.asm — adapted for breadboard 6502 |
| https://raw.githubusercontent.com/katkoviiva/BE6502_SidPlayer/main/MontyOnTheRun_BE6502.asm | 404 | URL wrong; accessed via WebFetch of github page instead |
| http://csbruce.com/cbm/hacking/ | OK | Issue index — confirmed Issue 5 has Hubbard disassembly |
| http://csbruce.com/cbm/hacking/hacking05.txt | OK | C=Hacking Issue 5 — main McSweeney disassembly |
| https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/ | 403 | Blocked |
| https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/page/2/ | 403 | Blocked |
| https://csdb.dk/search/?stype=all&search=rob+hubbard+player+source | OK | No results |
| https://csdb.dk/search/?stype=all&search=hubbard+music+editor | OK | Found 2 editors: csdb id 66495, 222633 |
| https://csdb.dk/release/?id=66495 | OK | "Robb Hubbard Music Editor V1.5" by BHT (1989), based on Zoolook |
| https://csdb.dk/release/?id=222633 | OK | "Rob Hubbard Music Editor" by Mirror (1988) |
| https://csdb.dk/release/?id=75124 | OK | ACE 2 player editor by Moz(IC)art / Predator (1989) |
| https://csdb.dk/scener/?id=8131 | OK | Rob Hubbard's CSDb profile — no tech releases |
| https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver) | OK | Historical overview only, no tech detail |
| https://www.lemon64.com/forum/viewtopic.php?t=8111 | OK | OLD Rob Hubbard editor — confirms Zoolook base, no speed detail |
| https://www.lemon64.com/forum/viewtopic.php?t=7920 | OK | WAR Hidden SID — confirms Wizball uses 4x speed (200Hz) |
| https://www.lemon64.com/forum/viewtopic.php?t=39774 | OK | No tech detail |
| https://codebase64.net/doku.php?id=base:sid_programming | OK | Links to chacking5 disassembly |
| https://codebase64.net/doku.php?id=magazines:chacking5 | OK | Rob Hubbard section confirmed present |
| https://cadaver.github.io/rants/music.html | OK | General C64 music routine architecture |
| https://codetapper.com/c64/diary-of-a-game/paradroid/birth-of-a-paradroid-part-3/ | OK | Paradroid diary — no music tech detail |
| https://web.archive.org/web/2020/https://www.1xn.org/... | FAIL | Claude Code cannot fetch web.archive.org |
| https://chiptunesak.readthedocs.io/en/stable/sid.html | 403 | Blocked |

## Leads NOT yet followed

- Archive.org Zoolook demo — disk image may contain README or source
- Archive.org Rob Hubbard SIDs collection (phsideffects) — may have annotations
- Lemon64 forum t=39774 comment about "ACE 2 player" and speed control
- csdb.dk release 75124 comments section (7 comments about the ACE 2 editor)
- The "fourth channel for effects/filter/tempo/speed table" — needs actual SID binary inspection
- Johannes Bjerregaard's driver variant — sidid signature is different, may have different speed handling
- Giulio Zicchi variant — sidid signature present but behavior undocumented
- SID Factory II source code — check if it imports Hubbard format anywhere
- ChiptuneSAK source — check if it has Hubbard-specific parsing
