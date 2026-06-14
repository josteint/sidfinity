# Provenance Log — 20CC Research

All URLs attempted during research wave 1 (2026-06-14).

| URL | Status | Notes |
|-----|--------|-------|
| https://csdb.dk/release/?id=10741 | OK | 20CC Music Editor V1 CSDb page |
| http://csdb.dk/getinternalfile.php/128749/20CC_Composer_Instructions.txt | OK (downloaded) | F7 help text; saved to docs/src/ |
| http://csdb.dk/getinternalfile.php/42798/20CC_COMPOSER_V1.T64 | OK (downloaded) | Editor T64 binary |
| http://csdb.dk/getinternalfile.php/571/Music%20User-Disk.zip | OK (downloaded) | Two D64 disk images |
| https://archive.org/details/d64_20CC_Music_Editor_V1_19xx_20th_Century_Composers | OK | D64 image; no additional docs |
| https://csdb.dk/scener/?id=2374 | OK | Falco Paul CSDb profile |
| https://8bitlegends.com/edwin-van-santen/ | OK | EVS tribute/bio page |
| https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=47 | OK | Falco Paul interview in Recollection #3 |
| https://demozoo.org/groups/7643/ | OK | 20CC Demozoo group page |
| https://demozoo.org/productions/188693/ | OK | Future Composer V3.1 by Union |
| https://demozoo.org/sceners/14666/ | OK | Falco Paul Demozoo profile |
| https://csdb.dk/release/?id=6657 | OK | 1 Year 20CC release |
| https://csdb.dk/release/?id=7709 | OK | Future Composer V3.1 CSDb |
| https://csdb.dk/release/?id=45379 | OK | 20CC Music by Manowar |
| https://csdb.dk/release/?id=171079 | OK | 20CC Rip by Fear |
| https://csdb.dk/release/?id=246043 | OK | 20CC Tune 2 by The Ancient Temple |
| https://csdb.dk/group/?id=626 | OK | 20th Century Composers group page |
| https://csdb.dk/sid/?id=32903 | OK | "The Words" SID file |
| https://csdb.dk/forums/?roomid=14&topicid=149796 | OK | Music Player Routine forum (not 20CC) |
| https://www.pouet.net/groups.php?which=5764 | OK | 20CC Pouet page |
| https://c64.ch/groups/311/20th_Century_Composers | OK | c64.ch group page |
| https://www.commodore.ca/manuals/funet/cbm/c64/demos/pal/20th%20Century%20Composers/index.html | FAIL 403 | FTP index page |
| https://www.lemon64.com/forum/viewtopic.php?t=67248 | OK | Comparison of editors (no 20CC content) |
| https://remix64.com/interviews/c64-music-scene-by-steve-drysdale.html | OK | Steve Drysdale interview; Falco mentioned |
| https://remix64.com/news/new-revolutionary-c64-music-routine-unveiled.html | OK | Different routine (not 20CC) |
| http://c64music.blogspot.com/2008/11/new-revolutionary-c64-music-routine.html | OK | Different routine (not 20CC) |
| https://deepsid.chordian.net/?file=MUSICIANS%2F0-9%2F20CC%2Fvan_Santen_Edwin%2FRoodkapje.sid | OK | DeepSID (no specific player ID text) |
| https://github.com/WilfredC64/player-id | OK | No 20CC in index.php |
| https://github.com/Chordian/deepsid/blob/master/index.php | OK | No 20CC entry |
| https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg | OK | Found 20CC signature block |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg | OK | Full 20CC signature (8 alt patterns) |
| http://20thcenturycomposers.blogspot.com/ | FAIL 404 | Blog not found; check Wayback |
| https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/Musicians.txt | OK | Falco Paul + EVS confirmed as NL |
| web.archive.org (CSDb instructions) | FAIL | Claude Code unable to fetch Wayback |

## Local binary analysis performed

| File | Source | Analysis |
|------|--------|----------|
| 20CC_COMPOSER_V1.T64 | CSDb #10741 | BASIC boot at $0801, SYS 2061, machine code $080D–$2F0C |
| Music User-Disk #1.D64 | CSDb #10741 | String extraction; found FC relocator, Beatless, Sound Machine |
| Music User-Disk #2.d64 | CSDb #10741 | String extraction; JCH/DMC, Romuzak, FC references, "6 MUSIC BY 20CC!" |
| van_Santen_Edwin/*.sid (all) | HVSC local | Header dump: load/init/play addresses for all ~80 SIDs |
| Vlindertjes.sid | HVSC local | Play routine disasm at $106C; SID writes; frequency table at $1800 |
| Enigma_Intro_Tune.sid | HVSC local | Dispatch table at $1003; copyright string embedded in binary |
| Revolution.sid | HVSC local | Different structure; $2100 load; $577D play; likely variant/special |

## Write-model + FC-link cluster (cluster_write_model_and_fc_link.md)

| File / source | Status | Notes |
|------|--------|-------|
| I_Wanna_Dance.sid (HVSC, Variant A) | analysed | full write model + state map + data hierarchy → `src/I_Wanna_Dance_hexmap.md` |
| Party_Report.sid (HVSC, Variant B) | analysed | the $0FFA/$1081 variant; instrument-in-note-pitch packing |
| `pipelines/future_composer/docs/` (local, read-only) | read | FC comparison baseline (vibrato/dispatch/filter/instrument differences) |
| cadaver/sidid + WilfredC64/player-id sidid.cfg | read | 8-line 20CC signature; author Falco Paul, no "based-on-FC" flag |

## Corpus + scene cluster (cluster_corpus_and_scene.md)

| Source | Status | Notes |
|------|--------|-------|
| `hvsc84.db` (read-only) | queried | 209-SID address-cluster table; composer/year cohorts; all PSID v2 |
| HVSC DOCUMENTS dir (local) | read | no 20CC-specific player doc (Musicians.txt confirms NL authors) |
| CSDb / Demozoo / Pouet / c64.ch | fetched | scene timeline 1988–2025; 20th Century Composers group history |

## Failures / blocked (retry later)
- web.archive.org — Claude Code cannot fetch Wayback in this environment.
- commodore.ca funet FTP index (403); 20thcenturycomposers.blogspot.com (404).
- **No public source/spec** — the auto-swing/beat-accent/glide algorithms + Variant-B
  note packing require disassembling a compiled HVSC SID (migration phase; `src/` hex map
  + the Vlindertjes $106C disasm are the head start).

## Leads to follow
- F7 in-tool feature docs — OBTAINED (`src/20CC_Composer_Instructions.txt`).
- Falco Paul interviews/pages (Recollection #3 fetched) — may hold more player internals.
- CSDb #10741 editor disk + bundled FC relocator — for instrument/effect byte semantics.
