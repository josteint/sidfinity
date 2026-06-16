---
source_url: multiple (CSDb, Demozoo, zimmers.net, blog.chordian.net, last.fm, github.com/cadaver/sidid)
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: various
reliability: secondary
---

# Vibrants/JO — CSDb + Scene Database Research Findings

## Identity

- **Real name:** Poul-Jesper Olsen
- **Handle:** JO (also: Rock, Technic, Jesper Olsen)
- **Nationality:** Danish
- **Groups:** Genesis Project (early), AMOK (pre-Vibrants), Vibrants (from ~1992, current)
- **Website (defunct):** www.vibrants.dk
- **CSDb scener page:** https://csdb.dk/scener/?id=1926 (returned HTTP 503 on 2026-06-16 — CSDb was down)
- **Demozoo page:** https://demozoo.org/sceners/6764/

## Player Identity — sidid.cfg

The sidid player-identification config (https://github.com/cadaver/sidid) names this engine:

```
Vibrants/JO
```

That is the canonical engine name used across HVSC and this project's DB (102 tunes in
`MUSICIANS/J/JO/`, 3 stray-classified tunes in other dirs). Full fingerprint from
`sidid.cfg` (raw GitHub, 2026-06-16):

```
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

Key observations from the fingerprint patterns:
- `BC ?? ??` = `LDY addr,X` — indexed Y-from-table loads appear repeatedly → pointer-indexed
  data tables (instrument/note/pattern arrays accessed via X as voice index, Y as offset)
- `B1 ??` = `LDA (zp),Y` — indirect Y-indexed reads → pointer in zero page, Y walks data
- `C9 F0`, `C9 FF`, `C9 60`, `C9 80` = compare immediates used as sentinel values in data
  streams: $F0, $FF, $60, $80 are likely pattern/sequence end/command markers
- `FE ?? ??` = `INC addr,X` — per-voice counter increments using X as voice index
- `DE ?? ??` = `DEC addr,X` — per-voice counter decrements
- `9D ?? ??` = `STA addr,X` — per-voice state writes
- `18 7D ?? ??` = `CLC` + `ADC addr,X` — frequency addition (transpose or slide)
- `0A 0A 0A` = three ASL A — multiply by 8, consistent with an 8-byte instrument record stride
- `A2 02` + loop with `CA 10` = `LDX #2` ... `DEX BPL` — 3-voice init loop
- `99 05 D4 99 06 D4 A9 08 99 04 D4` = write 0 to $D405,y and $D406,y, write $08 to $D404,y
  → voice gate-off with test-bit ($08) set on release
- `30 03 4C ?? ??` = `BMI`+`JMP` — negative branch to jump → sign-bit used for direction flag
  (possibly pulse sweep direction)
- `C9 D0 90 ?? E9 D0 0A 0A 0A 9D` = compare $D0, branch, subtract $D0, shift left 3×, STA,X
  → note-to-index conversion: subtract $D0 (208?), scale by 8 → instrument table lookup stride

## HVSC Coverage

- **Engine label in hvsc84.csv:** `Vibrants/JO`
- **Count:** 102 SIDs (100% of `MUSICIANS/J/JO/` except 1 MoN/Bjerregaard + 1 MoN/FutureComposer)
- **Migration status:** None migrated except Multi_Move (USF + sidfinity.sid present in tree)
- **Pipeline:** `pipelines/vibrants_jo/` exists with stub docs only

### PSID header survey (5 sampled files)

| File | Load | Init | Play | Songs | Speed | Year |
|------|------|------|------|-------|-------|------|
| Tweetys_Tweedledeed | $F000 | $F000 | $F003 | 1 | 0 (VBL) | 1989 |
| Behind_the_Wheel | $2003 | $2003 | $2006 | 1 | 0 (VBL) | 1988 |
| A_Way_to_be_Cool | $1000 | $1E23 | $107C | 1 | 0 (VBL) | 1988 |
| Dreams | $C052 | $C052 | $C055 | 1 | 0 (VBL) | 1988 |
| Battle_Pac | $09D0 | $0ABF | $0AFF | 2 | 0 (VBL) | 1989 |

Observations:
- All sampled tunes are PAL VBL (speed=0), called once per 50 Hz frame
- init is always load_addr or load_addr+3 for single-subtune files → the player loads at
  a fixed address with no separate relocator; init and play are fixed stubs at the top
- Wide load address range ($09D0–$F000) → the player is relocatable per-tune (or different
  versions load at different locations)
- Multi-subtune tunes exist (Battle_Pac has 2) → subtune dispatch is present in init

## Technical Profile from sidid Fingerprint Analysis

Based purely on the fingerprint opcodes (no emulator/binary analysis):

### Architecture signals
- **3-voice loop, X = voice index (0-2):** The `A2 02` / `CA 10` pattern shows a canonical
  3-voice iteration loop
- **Zero-page pointer + Y-walk:** `BC`+`B1` pairs = pointer table in ZP, Y is the
  per-voice read cursor. Data is read through a ZP pointer loaded from a per-voice
  pointer table indexed by X
- **Sentinel-terminated streams:** Multiple `C9 Fh` comparisons (`$F0`, `$FF`, `$60`, `$80`)
  suggest byte sequences (note lists, pattern streams, or instrument programs) are terminated
  or command-tagged by high-byte values in the $60-$FF range
- **8-byte instrument stride:** `0A 0A 0A` (×8) suggests instrument records are 8 bytes wide
- **Per-voice counters using INC/DEC addr,X:** Duration or speed counters maintained in
  absolute arrays indexed by X

### Likely data-stream structure
- Note/sequence streams with sentinels at $60, $80, $F0, $FF (end, loop, slide-trigger, etc.)
- Instrument table with 8-byte records (ADSR, wave, pulse, effect flags)
- Pulse sweep: direction bit (BMI check), probably in a per-instrument byte; up/down via
  signed flag
- Gate-off uses test-bit ($08 to $D404,y) → standard hard-restart-capable gate-off
- Frequency delta accumulation (CLC+ADC) → glide or vibrato support
- `$D0` subtraction pattern → note numbers may be offset; raw note bytes ≥ $D0 may be
  commands, < $D0 are note indices (similar to FC/JCH convention of high-byte commands)

## External Source Statements

### blog.chordian.net (JCH of Vibrants, 2017-12-03)
Source: https://blog.chordian.net/2017/12/03/the-later-adlib-music-by-vibrants/

> "In addition to composing a few test tunes in EdLib, Jesper Olsen also wrote his very
> own AdLib player and composed tunes for it in an assembler listing."

This confirms JO's MO: he writes his own players in assembler from scratch (not from a GUI
editor), then composes directly in the assembler listing. This applies to AdLib; by analogy
likely true for his C64 player — no editor GUI, data encoded directly in asm source.

### last.fm / Vibrants bio
Source: https://www.last.fm/music/Jesper+Olsen+(JO)/Vibrants+(AdLib)

> "He made his own players on C64 and for the AdLib sound card. He had unique knowledge
> about coding players for computer formats such as the Amiga home computer and the
> Roland MT-32 on the PC."

Confirms: C64 player is custom-written, not a shared Vibrants engine. JO is distinct from
JCH, Laxity, Drax — who all use the JCH editor. JO's player and data format are his own.

### Professional game credits (MobyGames)
Source: https://www.mobygames.com/person/53900/jesper-olsen/

JO scored games for: Interactivision, Brain Bug, FunSoft (Germany), Interactive Television
Entertainment. Game titles include Harald Hårdtand (Amiga port confirmed). Game rips would
use the same player as his demo/cracktro tunes — the sidid fingerprint will match those too.

## Source / Editor Status

**No public release of JO's player source or editor has been found.** The zimmers.net
Vibrants utilities archive (https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/)
contains only JCH-related tools (Deluxe Drivers, JCH Editor, Relocate Laxity — but no
JO tools). The CSDb scener page (id=1926) was unreachable; no tool/source releases known
from prior searches.

JO composed "in an assembler listing" for his AdLib player; the C64 player is likely the
same pattern — hand-assembled binary, no separate editor distributed.

## Demozoo Production List (selected)

Full list at https://demozoo.org/sceners/6764/. Key entries:

| Year | Title | Type | Alias used |
|------|-------|------|------------|
| 1988 | Multi Move | 8K Intro (Code+Graphics+Music) | Rock |
| 1988 | Pice of Mind | Music | JO |
| 1988 | Soporific | Music | JO |
| 1988 | Behind the Wheel | Cracktro music | Rock |
| 1989 | The Batcave | Demo (Code+Music+Graphics+Text) | JO |
| 1989 | Battle Pac | Music | JO |
| 1989 | Sex'n'Crime #1-#11 | Diskmag music | Jesper Olsen |
| 1989 | Atomic News 00, 05 | Diskmag music | Jesper Olsen |
| 1990 | Various demos | Music | JO / Jesper Olsen |
| 1991 | Beermacht, Unreal, Spritemania | Demo music | JO |
| 1992 | Copper | MS-DOS: Code (player) + Music | JO |
| 1994 | Notes | C64 Demo music | JO |

The 1992 "Copper" entry is explicitly "Code (player), Music" — confirms JO wrote a custom
player for MS-DOS as well. His C64 career peaked 1988-1991 with the custom player.

## Key Negative Findings

- **No editor GUI found** — JO composes in assembler source, not a music editor like JCH's
- **No player source released** — not in zimmers.net, CSDb, or Archive.org
- **CSDb was down (503)** on 2026-06-16 — could not retrieve full release list or forum comments
- **No version history found** — no V1/V2 naming in any source; sidid has one entry "Vibrants/JO"
  (no variants), suggesting either one player version or the fingerprint covers all variants
- **No game-rip documentation found** — no public disassembly of Interactivision/FunSoft game
  music using this player

## Load Addresses and Possible Relocation

The wide spread of load addresses suggests either:
1. A simple assembler-time relocatable player (JO re-assembles for each tune's load address), or
2. A hand-relocated binary (he copies his player template and patches the absolute addresses per tune)

Multi_Move loads at $2003 with init=$2003/play=$2006 — the standard 3-byte init stub (+0=init,
+3=play). This is consistent with a simple fixed-layout player that assembles to different origins.

## Multi_Move USF (already extracted)

One tune has a complete USF: `hvsc84/MUSICIANS/J/JO/Multi_Move.usf`. Extracted fields include:
- Standard freq_table (192 entries / 96 notes)
- pulse_programs (2 programs with lo/hi, seg entries)
- filter_programs (1 program with init/onset/d418/final/end/seg chain)
- wave_programs (2 programs with ctrl[] and freq[] arrays)
- wave_arp
- instrument blocks with: waveform, loop, pwm, adsr, arp, vibrato, pulse_prog, effects

This provides a known-good reference for the USF schema used by this engine.
