---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip
fetched_via: WebFetch direct (ZIP cached at tmp/sidwinder_research/src_docs/)
fetch_date: 2026-06-17
author: Balázs Takács (Taki / Natural Beat) + Levente Hársfalvi (TLC / Coroners)
content_date: 1994–2000 (source dated 2000-03-12 in ZIP)
reliability: primary (official source code + bundled documentation)
---

# SidWinder V01.22/V01.23 — Format & Engine Technical Notes

Extracted from the official V01.23 source archive (README, HISTORY, GENERAL,
SUMMARY, SIDW0122, PROGRAMM; SRC/PLAYER.ASM, SRC/ED.ASM, SRC/PACKER.ASM).

## Authorship & version history

- **Balázs Takács (Taki / Natural Beat)** — original author, Hungary.
  Contact c.2000: takinb@sch.bme.hu; Thokoly str. 26, 9300 Csorna, Hungary.
  Natural Beat homepage (defunct): http://www.sch.bme.hu/~takinb
- **Levente Hársfalvi (TLC / Coroners)** — Plus/4 port + GPL release, Hungary.
  Contact c.2000: levente@terrasoft.hu; Gorkij 33, 7200 Dombóvár, Hungary.
- **Luca Carrafiello (Luca / Fire)** — beta tester, contributed "Status Quo"
  and "Sweet Lullaby" as first Plus/4 edition demo songs.

### Editor version lineage

| Version | Author | Status | Notes |
|---|---|---|---|
| V01.14 | Taki | Never released | First working editor; bugs |
| V01.20 | Taki | Never released | Major improvement; missing absolute freq issue |
| V01.21 | Taki | Never released | Minor patch; glitchy slide |
| V01.22 | Taki | 1994 coded; **1999 first public release** | CSDb #66494; binaries + player source only |
| V01.23 | TLC  | 2000-03-12; **GPL** | C64 + Plus/4; full source; fixes + new packer |

**Note:** The "(1994)" date in the PlanetEmu / filename `SIDWinder v01.23
(1994)(Natural Beat).d64` refers to when the *player* was originally coded,
not the public release year. The editor+player were coded 1994, not released
publicly until 1999.

## High-level features (V01.22/V01.23)

- Up to **32 subtunes** per music file ($00–$1F)
- Up to **96 sectors** ($00–$5F), 256 instructions per sector
- Up to **64 instruments** ($00–$3F)
- Music speed up to **16x** (V01.22 supports up to 10x; V01.23 extended to 16x)
- **PAL only** (frq tables for PAL clock; NTSC port would require frq table swap)
- 3-voice SID only; no digi channel support (flagged as "possible improvement")
- **Hard restart** is hardwired (always on), fires at end of each sector
- Two player entry points (V01.22): $1003 for first call/frame; $1006 for
  subsequent calls within a multispeed frame
- Player is **relocatable** in V01.23 (all addresses relative to `pstart` label)
- Default load address: $1000; identity field at pstart+$20 (i.e. $1020 default)
- Zero-page pointer pair: $FB/$FC (configurable by packer)
- SID base address: $D400 for C64; $FD40 for Plus/4 SID card (configurable)

## Track commands

Each track has a table of single-byte (or double-byte for JmpXX) commands.
Commands must appear in this strict order (player relies on it for rastertime):

```
  one JmpXX         (double-byte; optional)
  one of: IncXX, DecXX, HltVS, VolXX   (optional)
  one of: Tr+XX, Tr-XX                  (optional)
  ...XX  (sector replay — mandatory to trigger a sector)
```

| Command | Encoding | Description |
|---|---|---|
| ...XX  | 1 byte | Play sector number $00..$5F |
| Tr+XX  | 1 byte | Transpose up $00..$3F semitones |
| Tr-XX  | 1 byte | Transpose down $00..$3F semitones |
| VolXX  | 1 byte | Set constant global volume $00..$0F |
| DecXX  | 1 byte | Decremental volume slide at speed $01..$07 |
| IncXX  | 1 byte | Incremental volume slide at speed $01..$07 |
| HltVS  | 1 byte | Halt volume slide, keep current volume |
| JmpXX  | 2 bytes | Jump to position $XX in the track table |

## Sector commands

Each sector holds up to 256 instructions in this strict order:

```
  one Snd.XX        (optional)
  one Dur.XX        (optional)
  one of: Gld.XX, ------, +++, or a single note   (mandatory)
  one Finish        (mandatory — marks end of sector)
```

| Command | Description |
|---|---|
| Snd.XX | Select instrument $00..$3F |
| Dur.XX | Set note duration to $01..$40 frames |
| C-1 – A#8 | Play note (uses selected instrument + duration) |
| Gld.0X | Glide: play note 1, glide toward note 2; X = glide table index |
| Gld.1X | Slide: keep current note, slide toward specified note; X = glide table index |
| ------ | Delay unit + release current note (gate off) |
| +++ | Hold current note, stay in sustain stage |
| Finish | End of sector |

- Sector $5E: reserved for channel 2/3 silence during sector/liveplay mode (V01.22)
- Sector $5F: reserved for liveplay (SFX) mode (V01.22); freed in V01.23

## Instrument (sound) parameters

7 parameters per instrument:

1. **Attack, Decay** — SID ADSR
2. **Sustain, Release** — SID ADSR
3. **Gateoff counter** — counts down frames; clears gate bit when 0
4. **Wave/arpeggio table position** — pointer into wave/arp table ($00 = off)
5. **Filter table position** — pointer ($00 = switch off filter effect; $FF = keep running)
6. **Pulse width table position** — pointer ($00 = switch off; $FF = keep running)
7. **Slide table position** — pointer

## Effect tables

### Wave/Arpeggio table (2 bytes per row: WF, AR)
```
WF $00..$8F  → current waveform = WF, arpeggio offset = AR
WF $90..$FE  → repeat last waveform with new arpeggio offset AR
WF $FF       → jump to position AR
AR           → arpeggio offset (semitones) OR jump position
```

### Filter table (3 bytes per row: RP, FH, RL)
```
RP $00..$FD → add to cutoff freq + resonance each frame
RP $FE      → select filtertype (bits 6..4 of FH)
RP $FF      → jump to position FH
FH          → addition to cutoff hi byte OR filtertype OR jump position
RL          → addition to resonance (bits 7..4) + freq lo (bits 2..0)
```
Filter init: all filter parameters reset to 0 on instrument start (must be
"added" to from 0 by the filter program on first tick). $D418 written as
`current_volume OR filtertype` — keep low nibble of filtertype = 0.

### Pulse width table (3 bytes per row: RP, PH, PL)
```
RP $00..$FE → add to pulse width each frame
RP $FF      → jump to position PH
PH          → addition to PW hi byte OR jump position
PL          → addition to PW lo byte
```
Pulse init: PW registers reset to 0 on instrument start (same add-from-zero
pattern as filter).

### Slide/Vibrato table (3 bytes per row: RP, FH, FL)
```
RP $00..$FD → add to actual frequency each frame
RP $FE      → set absolute frequency FH/FL (drum mode)
RP $FF      → jump to position FH
FH          → addition to freq hi OR absolute freq hi OR jump position
FL          → addition to freq lo OR absolute freq lo
```
Glide/slide suspends the vibrato during execution but keeps it in sync.

**Known limitation (flagged in docs):** Glide/slide uses absolute (non-adaptive)
frequency parameters. The glide table contains 16-bit absolute speed values;
glide speed therefore depends on the note being played (not normalized to
semitones). Flagged as "bad idea" by Taki; listed as a target for future
improvement that was never implemented.

### Glide table
Indexed by the low nibble of Gld.XX. Contains 16-bit absolute glide/slide
speed values (little-endian). Up to 16 entries ($0–$F / $10–$1F, shared).

## Subtune/track layout (multisong)

- 32 subtunes ($00..$1F); 8 track tables, each shared by 4 subtunes
- Subtunes $00,$08,$10,$18 share track table 0; subtunes $01,$09,$11,$19
  share table 1; etc.
- Each subtune has **track start pointers** indicating where its arrangement
  begins in the shared table (offset within the table, not an absolute address).
- This "start pointer" scheme is flagged by TLC as awkward; he explicitly lists
  "Reorganized code for subsongs (because I hate 'start pointers')" as a
  planned improvement.

## Music speed / multispeed

- V01.22: up to 10x player speed (10 play() calls per frame)
- V01.23: up to 16x player speed; player calls spread equally over the frame
  using CIA timer 1 (C64) / TED timer 1 (Plus/4)
- Editor supports tracing at ≤6x speed

## Hard restart

- Automatic hard restart (test-bit mechanism) at the start of every new note
  AND at the end of every sector (sector boundary always issues a hard restart)
- Cannot be disabled
- Minimum useful note duration: $04 frames (below this, hard restart routine
  behaviour is undefined)
- For notes shorter than 4 frames, use the arpeggio table instead

## Player structure (from PLAYER.ASM / signature analysis)

The sidid signature covers the inner loop of the play routine:

```
; Speed counter check (fires once per N frames)
LDA  <speed_counter>    ; AD ?? ??
BEQ  <do_tick>         ; F0 ??
DEC  <speed_counter>    ; CE ?? ??
; Voice loop
DEY                     ; 88  (Y = voice index, counts down 0,1,2)
JMP  <voice_loop_top>  ; 4C ?? ??
; Track/sector instruction dispatch
LDA  <track_table>,Y   ; B9 ?? ??
CMP  #<opcode>         ; C9 ??
BCC  <below>           ; 90 ??
BEQ  <equal>           ; F0 ??
LDA  <sector_table>,Y  ; B9 ?? ??
STA  <state_byte>      ; 8D ?? ??
TAY                    ; A8
```

Zeropage usage: one word at $FB/$FC (configurable by packer).

## Packer output format

The packer (V01.23 new implementation by TLC) produces a self-contained
relocatable binary:

- Start address: user-selected (default $1000)
- Layout: `[player_code][identity_field_32bytes][music_data]`
- Identity field at pstart+$20: 32 bytes of screencode text (composer ID)
- Relocatable: all internal pointers adjusted to the selected start address
- Selectable SID base address and frq table (C64 vs Plus/4 variants)

## Source file inventory (SIDwinder_V0123_src.zip, 2000-03-12)

```
SRC/ED.ASM      138,832 bytes  — editor main (keyboard handler, IRQ, I/O)
SRC/PACKER.ASM   65,209 bytes  — packer
SRC/PLAYER.ASM   30,137 bytes  — play routine (the core; relocatable)
SRC/SIDR.ASM      2,195 bytes  — SID reader component
SRC/VIEWER.ASM   18,819 bytes  — ASCII viewer
SRC/CHARS.BIN     1,024 bytes  — character set
SRC/MASKS.BIN     2,047 bytes  — graphics masks
SRC/SECTORS.BIN  24,576 bytes  — sector data (demo songs)
SRC/TRACKS.BIN    6,144 bytes  — track data (demo songs)
SRC/VCHARS.BIN      768 bytes  — extended character set
PRE_0123/0120/  — V01.20 sources (ED1.ASM, ED2.ASM, ED3.ASM, PACK0120.ASM,
                  PLAY0120.ASM; split because of Turbo Assembler source limits)
PRE_0123/0122/  — V01.22 player (PLAY0122.ASM, 20,180 bytes)
PRE_0123/REANIM/ — intermediate "reanimated" sources (reverse-engineered from
                  V01.22 binary + V01.20 source)
TOOLS/          — Pascal + C utilities (STRIPCR, FREQ, DIFF, D2, CLC_RS, ABS)
```

**Key insight:** Taki lost the V01.22 editor sources. TLC re-derived them by
diff-matching the V01.20 SEQ files against the disassembled V01.22 binary using
the Recomment reassembler + custom Pascal diff tools. This means the V01.23
editor source is a reconstruction, not the original.

The V01.22 *player* source was preserved (`PRE_0123/0122/PLAY0122.ASM`).
The V01.23 player (`SRC/PLAYER.ASM`) is a minor modification of V01.22.

## Toolchain

- Assembler: Table Driven Assembler (TASM 3.0.1 or above), DOS
- Linker: ComLink V0.98 (DOS)
- Build: `tasm -65 -dc64 ed.asm` + `comlink -thx ed.obj`
- Plus/4 build: `-dp4` instead of `-dc64`

## Leads to follow

- Read `SRC/PLAYER.ASM` directly from the ZIP for exact memory map, label
  addresses, and instruction encoding (30 KB of TASM source). This is the
  definitive reference for the USF extractor's binary parsing.
- Read `PRE_0123/0122/PLAY0122.ASM` to confirm V01.22 vs V01.23 player diffs
  (the NFO says "just a few minor modifications").
- The packer's "thorough data examination" algorithm (PACKER.ASM) shows exactly
  which bytes are music-data vs player-bookkeeping — essential for USF separation.
- Factor6 adopted SidWinder despite being Czech: likely downloaded via
  `ftp://ftp.funet.fi/pub/cbm/c64/audio/editors/` (Funet FTP) or the c64.rulez.org
  mirror listed in GENERAL as the primary distribution points.
- Eclipse's 2025 SIDs may use an unmodified V01.23 player — verify with sidid
  binary + PLAYER.ASM comparison.
