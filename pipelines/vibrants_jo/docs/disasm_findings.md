---
source_url: local: /home/jtr/sidfinity/hvsc84/MUSICIANS/J/JO/ + web searches
fetched_via: direct
fetch_date: 2026-06-16
author: research session (Claude + HVSC binary analysis)
content_date: 2026-06-16
reliability: primary (binary inspection) + secondary (web)
---

# Vibrants/JO SID Player Engine — Research Findings

## Identity

- **Real name:** Poul-Jesper Olsen
- **Handles:** JO (primary), Technic (Genesis Project era), Rock (another alias per Demozoo)
- **Groups:** AMOK Sound Department (1988–89) → Genesis Project ("Technic") → Vibrants (~1992+)
- **CSDb scener page:** https://csdb.dk/scener/?id=1926
- **Demozoo:** https://demozoo.org/sceners/6764/
- **HVSC count:** 105 SIDs (+ 2 sidfinity files already present), all classified as engine `Vibrants/JO`
- **Active years:** 1988–1990 most prolific; still active 2026 (Rasta Grid 2026)

## Key Biographical Finding

JO **wrote his own C64 music player in 6502 assembler** — confirmed by text strings embedded in the SID binaries:

| SID file | Embedded string |
|---|---|
| `Stormlord_2_Demo.sid` | `- NEW PLAYER V22.6-7 BY JESPER OLSEN. MUSIC BY HJE/JO. (M) BY VOLKER SCRAP WAS HERE` |
| `Col.sid`, `Dos.sid` | `- PLAYER BY JO. -` |
| `Airwolf.sid` | `- CODED AND IMITATED BY J.O. OF AMOK SOUND DEPARTMENT 1988 -` |
| `Psycho.sid` | `PLAYER AND MUSIC (C) J.O. OF AMOK MUSIC DEPARTMENT 1988` |
| `Soundtrack_1.sid` | `PLAYER AND MUSIC (C) JESPER OLSEN OF AMOK SOUND DEPARTMENT 05-07TH OF NOVEMBER 1988` |
| `Megabad.sid` | `MUSIC + PLAYER (C) JO 1988 REMEMBER ME IF YOU USE IT!! ,ELSE DIE` |
| `Hit_It.sid` | `MUSIC AND PLAYER BY JESPER OLSEN` |
| `A_Way_to_be_Cool_for_W_S.sid` | `MUSIC + ROUTINE BY -=*>JESPER O.<*=-` |
| `Jaws_Imitation.sid` | `MUSIC + ROUTINE BY JO OF AMOK MUSIC DEPARTMENT` |
| `Destiny_v3.sid` | `MUSIC BY JO/AMOK LEVETOFTEVEJ 1A. 4690 HASLEV DENMARK PHONE:(+45)56316459` |
| `Behind_the_Wheel.sid` | `PLAYER & MUSIC (C) BY ROCK/G * P  YOU MAY USE IT!.... CALL (03) 31 63 67....JESPER` |

**No external RE writeups, disassemblies, or format documentation found online.** No GitHub repository contains a JO/Vibrants disassembly. The player is not in `sidid.cfg` (WilfredC64/player-id) nor in `realdmx/c64_6581_sid_players`. This is an undocumented format requiring original RE.

## Player Lineage — NOT JCH

JCH (Jens-Christian Huus) is a *different* Vibrants member who made his own widely-used editor (JCH Editor V3.04, 1991). JO's player is entirely independent — custom 6502 assembler compositions, not JCH-format. The Chordian.net blog confirms: "Jesper Olsen also wrote his very own AdLib player and composed tunes for it in an assembler listing" (the same approach on C64).

## Corpus Statistics (HVSC inspection)

- **105 SID files** in `hvsc84/MUSICIANS/J/JO/`
- **All VBL-timed** (`speed = $00000000`) — no CIA-timed tunes found
- **Typical load addresses:** $1000, $2000, $3000, $4000, $E000, $F000 (relocated per tune)
- **PSID version:** v2 throughout

## Player Version Families (Binary Analysis)

JO clearly **iterated his player continuously** — each tune often has a slightly updated engine. From binary clustering of first 200 bytes of play routine (>80% match threshold):

| Cluster | Files | Notes |
|---|---|---|
| A | `Cool_Intro_Music`, `Creep_Mix`, `My_Best_Tune` | 84–97% match; same architecture, only data addresses differ |
| B | `Beat`, `Genesist_Muzak_for_the_demo` | 97% match |
| C | `Col`, `Dos` | 92% match; self-labelled "PLAYER BY JO." |
| D | `Gamlere`, `Gamlest` | 88% match; $42xx-load family |
| E | `Hi-Score`, `Impressive` | 88% match |
| F | `Amok_Title`, `Jaws_Imitation` | 91% match |
| G | `Bat-Crap`, `Pice_of_Mind` | 80% match |
| Unique | ~90 files | Each tune has individually-evolved code |

At 65% threshold, ~15 additional cross-family links appear (e.g. `A_Way_to_be_Cool_for_W_S` ↔ Cluster A at 70%).

The version string `V22.6-7` in `Stormlord_2_Demo` (play=$1006, ~1990) suggests JO was internally versioning his player through at least 22+ major iterations.

## Format Reverse-Engineering (from binary inspection of Cool_Intro_Music + Cool_Intro_Music family)

**This is original RE from binary inspection — not from any published source.**

### Memory Layout (example: Cool_Intro_Music, load=$1003...$1C1F)

```
$1003:  JMP init_routine    ; init entry (subtune# in A)
$1006:  [play routine]      ; play entry (called every frame)
$1006-$12B5: play engine
$12B6-$12FF: (varies) — data used by engine
$1300-$17FF: (varies) — instrument/wave program tables + state
$1800-$19E9: (varies) — state / per-voice work areas + instrument tables
$19EA-$1A09: voice orderlist pointer table (3 pointers, one per voice)
$1A0A-$1A74: voice 1 pattern stream data
$1A56-...:   voice 2 pattern stream data
$1A69-...:   voice 3 pattern stream data
$1A7B-$1B32: pattern data (sequences of [note, duration] pairs with special commands)
$1B00-$1B33: instrument/wave table data
$1B38-$1B57: song configuration table (key player pointers + per-subtune config)
$1B94-$1C1F: SID frequency table (24 entries × 2 bytes, PAL)
```

### Frequency Table

24-entry PAL frequency table (little-endian SID freq values). Printable ASCII
signature in data: `" "$')+.147:>AEINRW\bhnu|` (31 files) or
`!#%'*,/258;?CGKOTY^djpw~` (12 files, alternate tuning).

Low bytes: `20 22 24 27 29 2B 2E 31 34 37 3A 3E 41 45 49 4E 52 57 5C 62 68 6E 75 7C`

### Voice Stream Format (note/pattern data)

Each voice has a **flat byte stream** (not a pointer-based orderlist of separate patterns). The stream contains interleaved note+duration pairs and command bytes:

```
[note_byte] [duration_byte]   ; play note for duration frames
[command_byte] [param_byte]   ; special command
...
$FF                            ; end-of-stream / loop
```

**Special command bytes observed** (in voice streams):
- `$FB xx` — likely repeat / loop marker
- `$FD xx` — command (possibly transpose or speed change)
- `$FE xx` — command (possibly end-of-section / loop-back)
- `$FF` — stream end
- `$80 xx` — set volume / filter / control
- `$81 xx` — related command
- `$82 xx`, `$83 xx`, `$84 xx`, `$85 xx`, `$86 xx` — effect/control commands
- Values `$00`–`$7F` (below $FB) are note indices into the frequency table

The play routine dispatches on the stream byte value:
```
B1 $F8   ; load byte from (F8)+Y  (F8/F9 = current stream pointer)
C9 $FF   ; == $FF → end/loop
C9 $FE   ; == $FE → handle $FE command
C9 $FD   ; == $FD → handle $FD command
C9 $FC   ; == $FC → ...
C9 $FB   ; == $FB → handle $FB command
; else: value is a note index
STA $24,18  ; store note for this voice
FE $13,18   ; advance stream position (×2 for note+duration)
```

### Per-Voice State (inferred from 6502 code)

The player maintains 3-voice state in page-$17/$18 regions (per-voice arrays accessed via `X` register = voice 0/1/2):

- `$1618,X` — stream position (current byte index into voice stream)
- `$1918,X` — current note position (secondary counter?)
- `$3202,X` — some voice flag / gate control
- `$3602,X` — voice status
- `$BD17,X` — instrument number / program index
- `$BA17,X` — gate/waveform control byte
- `$AB17,X` — note frequency adjustment

SID register writes use absolute indexed: `STA $D400,X` style with X striding through voice offset.

### Init Behavior

Init routine sets:
- Master volume: `A9 1F 8D 18 D4` (LDA #$1F, STA $D418 — master vol $0F + filter enabled)
- All SID registers zeroed for 3 voices
- Voice stream pointers reset to song start
- Per-subtune config loaded from song table

### Song/Subtune Table Structure

For multi-subtune SIDs, a table indexed by subtune number holds pointers to the per-voice
stream data. In the Cool_Intro_Music family, the table lives at ~$1B45 with 4 bytes per subtune.

For larger multi-subtune SIDs (e.g. `A_r_cade_Sprint`, 7 subtunes, load=$3000), the song table
is at $3084 with a different (larger) format. This is a distinct player version.

## Notable Non-Standard Cases

- `First_Digi.sid` — play address $0000 (no play routine? or digi?); init=$2300
- `Grid.sid` — non-JMP entry byte ($A2 = LDX); starts with `A2 02 C6 75`
- `Destiny_v2.sid` — very large player region ($980..$1A7C, 4348 bytes); different layout
- `Battle_Pac.sid` — `$0ABF` init, `$0AFF` play, load=$09D0; complex multi-section SID
- `Behind_the_Wheel.sid`, `Intro_Music.sid`, `Jans_Tune.sid`, `Soundtrack_1.sid` — "PLAYER & MUSIC BY ROCK/G * P" — JO using alias "Rock" in Genesis Project

## Existing Partial Migration

`Multi_Move.sid` already has:
- `hvsc84/MUSICIANS/J/JO/Multi_Move.usf` — a USF file exists
- `hvsc84/MUSICIANS/J/JO/Multi_Move.sidfinity.sid` — a rebuilt SID exists

The USF uses the Hubbard-style USF schema (freq_table, pulse_programs, filter_programs, wave_programs, instrument blocks). This suggests an earlier migration attempt was started. The `.usf` file should be read carefully before starting fresh RE — it encodes the freq table and some instrument data already decoded.

## External Resources Found

### Useful but non-technical
- **CSDb scener page:** https://csdb.dk/scener/?id=1926 (503 during research — try later)
- **Demozoo:** https://demozoo.org/sceners/6764/ — 82 productions listed
- **MobyGames:** https://www.mobygames.com/person/53900/jesper-olsen/
- **Mirsoft:** http://www.mirsoft.info/gmb/musician_info.php?id_ele=MjQzMQ== (blocked)
- **Chordian.net (AdLib article):** https://blog.chordian.net/2017/12/03/the-later-adlib-music-by-vibrants/
  — confirms JO "wrote his very own AdLib player and composed tunes for it in an assembler listing"
  (parallel to C64 approach)
- **Retroworld Vibrants page:** https://retroworld.canell.dk/music/group/vibrants-c64.html
  — confirms all Vibrants members were musicians; JCH's editor is separate from JO's player

### Absent (confirmed not found)
- No published disassembly of the JO C64 player anywhere online
- Not in sidid.cfg player identification database
- Not in realdmx/c64_6581_sid_players
- No CSDb technical articles about the format
- No scene magazine (C=Hacking, Vandalism News) coverage of JO's player
- No GitHub repository with JO player source or RE

## Leads to Follow

1. **CSDb scener page** (https://csdb.dk/scener/?id=1926) — was returning 503 during this session. Fetch when available: look for download links to any releases, source code, or music packs JO released.

2. **CSDb group page — Vibrants** (https://csdb.dk/group/?id=328) — also 503'd. May have releases listing music tools or source packs.

3. **Hotshot 3 (August 1990) interview** — Demozoo notes JO was "interviewed in Hotshot 3". Search CSDb for "Hotshot" magazine releases; this interview may contain technical details about his player.

4. **Internet Archive / CSDB downloads for AMOK group** — search `csdb.dk` for "Amok Sound Department" releases; JO's original work was under this label 1988–89. Any disk images may contain the source assembler listing.

5. **Demozoo productions by JO** (https://demozoo.org/sceners/6764/) — 82 productions; examine the code/music pack releases that have downloadable files. The production "Multi Move" (1988) mentioned "Code, graphics, and music" — JO coded his own player from the start.

6. **`Destiny_v2.sid` text string:** `DESTINY SOUNDTRACK ^C! BY JESPER OLSEN_AMOK DESIGNS ... GAME PRODUCED BY FUTURE VISION_ANIMATED PIXELS` — this is a game soundtrack. Search for "Destiny" C64 game by Amok/Future Vision on CSDb; the game binary might contain the player in a less-HVSC-compressed form with original labels.

7. **Phone number in text:** `(03) 31 63 67` / `(+45)56316459` appears in multiple SIDs — JO's Danish address from 1988–89. Historic context only; address is Haslev, Denmark.

8. **`Stormlord_2_Demo.sid` → "MUSIC BY HJE/JO"** — HJE is another musician. Search for HJE on CSDb; if HJE also made music for this player, more examples may have different data layouts that illuminate the format.

9. **`Le_Cool.sid`** — contains `RIPPED BY G.GOUWELOOS ON 16-OCT-95`; several other SIDs have this ripper's name. Gerrit Gouweloos may have notes on what he found during extraction.

10. **`Bad_One.sid` and `Quick_Kill.sid`** — "RECODED PLAYER BY TECHNIC" / "COMPOSED BY TECHNIC IN HIS PLAYER D 3/10 1988" — these tunes use JO's player but with "TECHNIC" alias (Genesis Project era). Search CSDb for Genesis Project and Technic/JO releases for more player examples.

11. **DeepSID** (https://deepsid.chordian.net/) — JCH's online player. Check if it has any engine metadata or comments about the Vibrants/JO engine — JCH would know JO's format from the group collaboration.

12. **HVSC Songlengths.md5** — confirm frame counts for JO SIDs; check for any unusually long/short entries that might indicate multi-speed or unusual player behavior.

## RE Priority Recommendation

The **Cool_Intro_Music family** (Cool_Intro_Music / Creep_Mix / My_Best_Tune) is the clearest starting point for full disassembly:
- Player fits entirely in $1003..$1C1F (3226 bytes including data)
- Cluster of 3 near-identical tunes allows cross-validation
- Text string "-=> DONE BY TECHNIC OF FUTURITY.. 11/9 1988" dates it to early mature era
- The `A_Way_to_be_Cool_for_W_S.sid` (70% match) extends the family further

The **Gamlere / Gamlest / Rob_Lam_Fejl** family (load=$4259, play=$425C) represents a later/larger player (~3KB of player code at $42xx) and the `A9 1F D0 01 60 A2 02 CE` signature cluster.

The 90+ "unique" SIDs are likely not truly unique — they're iteratively evolved from the same lineage. A disassembly of the Cool_Intro_Music family player + the Gamlere family player will likely cover 80%+ of the corpus patterns.
