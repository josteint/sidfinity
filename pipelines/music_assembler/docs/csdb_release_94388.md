---
source_url: https://csdb.dk/release/?id=94388
fetched_via: curl 2026-06-13 (Firefox UA + --compressed; plain WebFetch got HTTP 503)
fetch_date: 2026-06-13
author: page maintained by CSDb; release by Dutch USA-Team
content_date: release 1989-02 (CSDb), uploaded files 2006 / 2010
reliability: primary (the canonical release record + bundled binaries)
---

# CSDb release #94388 — "Music-Assembler V1.0" by Dutch USA-Team (1989)

Scrape of https://csdb.dk/release/?id=94388. (CSDb blocks the markdown
WebFetch proxy with HTTP 503; fetched the raw HTML with
`curl -sL --compressed -A "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) ..."`.)

## Release record

- **Name:** Music-Assembler V1.0
- **Released by:** Dutch USA-Team (1989; CSDb "Type: Music Assembler")
- **Credits:** Code / Music / Design all = **MC** + **OPM** of Dutch USA-Team
  (Marco Swagerman + Oscar Giesen).
- **Release date note (from a user comment):** *"This can't be in anyway
  released on 1st Jan 1987. Even the intro scroller says it was developed from
  Nov 1987 to Feb 1989. Hence the release date can't be anything less than
  Feb 89."* → development window **Nov 1987 – Feb 1989**.

## Downloads on the release page (ALL vendored locally)

| CSDb internal file | what it is | local file |
|---|---|---|
| getinternalfile.php/92052/`MusicAssemblerDUSAT.zip` (843 dls) | DUSAT editor disk | `MusicAssemblerDUSAT.zip` → `Music Assembler DUSAT.d64` |
| getinternalfile.php/137191/`masm_manual_0_01b.pdf` (351 dls) | the manual | `csdb_manual_0_01b.pdf` (+ `.txt`) |
| getinternalfile.php/178876/`ma.d64` (134 dls) | earliest editor disk | `ma.d64` |
| getinternalfile.php/38875/`music assembler.zip` (132 dls) | older editor disk | `music_assembler.zip` → `music assembler.d64` |

## Disk-image contents (parsed locally — no c1541 needed; Python D64 walker)

All three D64s are standard 35-track 174,848-byte images. Editor PRG is always
the first entry, named with a leading shift-space so it sorts first.

### `ma.d64` (md5 b4eceefb…) — smallest editor (likely the earliest)
```
PRG 57  "_MUSIC ASSEMBLER"   load $0801  (14264 bytes)   <- editor
PRG  8  "S.DUTCH USA SONG"   load $6800  ( 1938 bytes)   <- demo song
```

### `Music Assembler DUSAT.d64` (md5 7b6aa928…) — the 2010 DUSAT disk, 84-block editor
```
PRG 84  "_MUSIC-ASSEMBLER"   load $0801  (21193 bytes)   <- editor (bigger build)
+ 31 "S.<name>" demo songs: ACTION BIKER, AMIGATUNE 1/2, BLUE MONDAY,
  CONFUZION, EYEBALL, FANTJES BEAT, FLASH GORDON, GAME KILLER,
  GHOSTBUSTERS, GOLDRUNNER, HELLO MONTY, HOUSE BEAT, KALASHNIKOV,
  KARATE II, LAST V8, LETS TEL, MEGA APOCALYPS, NEMESIS THE WA,
  NINJA MIX, ONE MAN AND HI, PARALLAX, ROCK DA HOUSE, SABOTEUR II,
  SHIFTING GEAR, SLOW BASS, SID SLAM, SYNC SOLO, THANATOS,
  TUBULAR BALLS, UNTOUCHED
```
(These are MA renditions of famous game tunes — good cross-check fixtures: an
MA "S.CONFUZION" vs the real Hubbard Confuzion already migrated in this repo.)

### `music assembler.d64` (md5 441d77a5…) — 2006 disk, same 84-block editor
```
PRG 84  "_MUSIC-ASSEMBLER"   load $0801                  <- editor
PRG 12  "MUSIC"              load $2900  ( 2946 bytes)   <- STANDALONE player
PRG  4  "P."                 load $4300  (  770 bytes)   <- bare presets file
+ many S.* songs (NATO TUNE, FALCON DUMP, SPEEDZAX II, M1..M4, MUSIX 01..06, ...)
PRG 12  "S.NEI"  ;  *PRG 0 "P.2900" (unclosed/splat — corrupt dir entry)
```
The `MUSIC` (load $2900) is a **standalone packaged player** (JMP-table entry
instead of the in-editor IRQ installer — see packed-format doc). `P.` is the
**presets-only file format** (`p.<name>`), 770 bytes.

## User comments (6 total; only the technical/dating one is load-bearing)

- *"it is today I am going to download this editor for the first time. Real time
  machine for me :)"* — no technical content.
- The dating comment quoted above (development Nov 87 – Feb 89).
- (Other comments are greetings / nostalgia — skipped per quality bar.)

## Linked sceners on the page

`/scener/?id=` 823, 1498, 4074, 6662, 6746, 7485 (CSDb member references —
MC = scener 6151, see version-lineage doc). Discussion thread:
`forums/?csdbentrytype=release&csdbentry=94388&entrytopic=1`.

## Naming caveat (CRITICAL — two unrelated "Music Assembler"s)

CSDb / sidid record **a different product also called "Music Assembler V3.1"
by Harald Rosenfeldt, 1989 64'er/Markt+Technik**. Markt+Technik published
both. Do NOT conflate: this DUSAT release is the Swagerman/Giesen editor whose
player carries the `Music_Assembler` sidid signature documented in the sidid
docs. The Rosenfeldt "V3.1" is a separate engine. The ~6,351 HVSC tunes
attributed to "Music_Assembler" are the DUSAT lineage (its signature), not the
Rosenfeldt one.
