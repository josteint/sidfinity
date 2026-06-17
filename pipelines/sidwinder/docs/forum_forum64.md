---
source_url: https://www.forum64.de/
fetched_via: direct
fetch_date: 2026-06-17
author: various
content_date: various
reliability: secondary
---

# SidWinder — Forum64.de Search Results + Supplementary Sources

## Forum64.de Search Results

The Forum64.de search endpoint (`/index.php?page=Search&q=sidwinder&action=results` and variants)
returned **HTTP 403 Forbidden** for all attempts. The forum requires authentication for search.
A Google `site:forum64.de sidwinder` query returned no matching threads — either the topic has
not been discussed there, or the content is behind login. One thread found obliquely
(`thread/134627-enhanced-sid-collection/`) also returned 403.

**Conclusion: Forum64.de has no accessible public discussion of SidWinder as of 2026-06-17.**

---

## c64-wiki.de Search Results

`https://www.c64-wiki.de/wiki/SidWinder` → **HTTP 404** (page does not exist).
`https://www.c64-wiki.com/wiki/SIDwinder` → **HTTP 404** (page does not exist).

No German or English c64-wiki entry for SidWinder.

---

## CSDb (C64 Scene Database) — Release Records

Source: https://csdb.dk/

### SIDwinder V01.22 (1999)
- CSDb release ID: **66494**
- Type: C64 Tool
- Group: Natural Beat
- Code: Taki (Balázs Takács, Hungary)
- Downloads: 391 recorded
- Notes: No detailed user comments with format discussion in the CSDb entry.

### SIDwinder V01.23 (2000-03-15)
- CSDb release ID: **101758**
- Type: C64 Tool
- Group: Natural Beat
- Code: Taki
- Music (bundled): Taki (13 tracks: Classical, Draxish, Drummer, Glorious, Lost Love,
  Memories, Precisely, Radiation, Realbeat, Southern, Speed Up!, Uncertain, + one more)
  + Luca/FIRE (2 tracks: Status Quo, Sweet Lullaby)
- Testing: Luca (Fantastic Italian Research Enterprise / FIRE)
- Production notes on CSDb: "Includes a packer and an ASCII file reader."
- Downloads: 534 recorded
- Known bug: Luca notes "a bug in that version's packer" in the CSDb V1.23 Enhanced thread.

### SIDwinder V1.23 Enhanced!! (2011-04-17)
- CSDb release ID: **99574**
- Type: C64 Tool
- Author: PCH
- Based on: SIDwinder V01.23 by Taki/Natural Beat
- Enhancement: Added **live piano feature**; PCH states: "I improved stay function and add
  many new functions .. as live piano and other next function in menu."
- PCH note: "I found this excellent music editor on my harddisk from 2001 year"
- Packer: PCH acknowledges limited familiarity with the packing mechanism.

---

## Zimmers.net FTP Archive

Source: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/

Two SIDwinder files archived (dated 2009-08-18):

| Filename | Size | Description |
|---|---|---|
| `SIDwinder_V0123_C64.d64.gz` | 73,918 bytes | C64 disk image (bootable) |
| `SIDwinder_V0123_src.zip` | 341,456 bytes | **Source code of SIDwinder v1.23** |

The source code archive is large (341 KB) — indicative of a full assembler project.
It has not been read in this session (binary download would be needed).

---

## Plus/4 World — Most Detailed Technical Documentation Found

Source: https://plus4world.powweb.com/software/SIDwinder_V01_23

This is the most technically detailed public documentation found. The page covers the Plus/4 port
(by Levente Hársfalvi / TLC) of Taki's original C64 editor — the data format and player
architecture are shared, with only hardware-address and clock differences.

### Basic Specifications
- Up to **32 subtunes** per music file
- Up to **96 sectors** ($00–$5F), 256 instructions per sector
- Up to **64 instruments** ($00–$3F)
- Up to **16× music speed** (speed multiplier, editor-supported)
- Machine code, PAL only
- Freeware; English/Hungarian language

### Song Hierarchy

```
Song → Tracks (one per voice) → Sectors (pattern-like blocks) → Note commands
```

**Tracks** reference sectors by number and may apply transposition and volume control per sector
reference. Track structure is an ordered sequence:

| Command type | Encoding | Notes |
|---|---|---|
| Sector playback | `...XX` ($00–$5F) | plays sector XX |
| Transpose up | `Tr+XX` (up $00–$3F semitones) | optional, before sector |
| Transpose down | `Tr-XX` (down $00–$3F semitones) | optional, before sector |
| Volume constant | `VolXX` ($00–$0F) | constant volume |
| Volume decrement | `DecXX` (speed $01–$07) | fades down |
| Volume increment | `IncXX` (speed $01–$07) | fades up |
| Volume halt | `HltVS` | stop volume sweep |
| Jump | `JmpXX` | jump to track position XX |

Permitted ordering per track step: optional `JmpXX`, then one volume command, then one
transposition command, then sector reference.

### Sector (Pattern) Commands

Ordered commands within a sector:

| Command | Encoding | Notes |
|---|---|---|
| Instrument | `Snd.XX` ($00–$3F) | selects instrument |
| Duration | `Dur.XX` ($01–$40 frames) | note length in frames |
| Note | C-1 through A#8 | standard note |
| Glide | `Gld.XX` ($01–$0F = down, $11–$1F = up) | frequency slide |
| Delay | `------` | rest/delay |
| Sustain | `+++` | sustain/tie previous note |
| Terminator | `Finish` | end of sector |

### Instrument / Sound Format

Each instrument has seven parameters:

| Field | Range | Meaning |
|---|---|---|
| Attack/Decay | byte | SID ADSR A/D nibbles |
| Sustain/Release | byte | SID ADSR S/R nibbles |
| Gateoff counter | byte | frames until gate bit cleared (0 = instant off) |
| Wave/arp table pos | byte | $00 = none; points into wave/arpeggio table |
| Filter table pos | byte | $00 = none; points into filter table |
| Pulse width table pos | byte | $00 = none; points into PW table |
| Slide table pos | byte | $00 = none; $FF = inherit/continue |

Value $00 disables an effect; $FF means "continue current effect unchanged."

### Effect Tables

**Wave/Arpeggio table** (`WF` + `AR` byte pairs):
- `WF` = $00–$8F: waveform byte (SID $D404/$D40B/$D412 control) + arpeggio offset
- `AR` = arpeggio semitone offset or jump target
- Jump marker: `$FF` in `WF` = jump to `AR` position

**Filter table** (`RP`, `FH`, `RL` byte triples):
- `RP` = $00–$FD: repeated frequency addition amount
- `RP` = $FE: filter type select entry
- `RP` = $FF: jump
- `FH` = filter cutoff high byte / type / jump target
- `RL` = resonance + filter cutoff low byte

**Pulse Width table** (`RP`, `PH`, `PL` byte triples):
- `RP` = $00–$FE: PW addition value
- `RP` = $FF: jump
- `PH` = PW high byte / jump target
- `PL` = PW low byte

**Slide/Vibrato table** (`RP`, `FH`, `FL` byte triples):
- `RP` = $00–$FD: frequency addition value (relative mode)
- `RP` = $FE: absolute mode flag
- `RP` = $FF: jump
- `FH`/`FL` = frequency high/low bytes
- Note: "absolute frequency values for glide/slide instructions"

### Player / Runtime Details

- **SID base address**: $D400 (C64) / $FD40 (Plus/4 SID card) — configurable via packer
- **Frequency table**: PAL C64 at $1040–$10FF (256 bytes = 128 notes × 2 bytes hi/lo)
- **Volume registers monitored**: $1673 and $165D (internal player state)
- **Three independent voice channels** with gate bit masking
- **Multispeed**: up to 16× speed via multiplier field
- **Packer parameters**: start address (hex), zeropage word (default $FB–$FC), SID base,
  frequency table selection, identification text field

### Clock/Frequency Note (C64 vs Plus/4)

- C64: 1.022727 MHz (phi2, PAL) → SID freq divisor 18
- Plus/4 SID card: 885 kHz (approximately) → SID freq divisor 20
- Result: music composed on C64 plays approximately one semitone lower on Plus/4 SID card
- Glide/slide speeds: multiply by 10/9 when porting C64→Plus/4

### Song Identity Field

The packed song data includes an identity field containing version string `V01.23`. This is
likely used as a detection signature in the player init code.

---

## Name Disambiguation

**WARNING**: There is a modern tool (2020s) also called "SIDwinder" — a C64 SID Music Linker
at https://sidwinder.netlify.app/ and a "SIDwinder V0.2 Preview" (2025) by Genesis Project on CSDb.
These are completely unrelated to Taki's 1999 C64 music editor/tracker. Do not confuse them.

---

## Leads to Follow

### Thread URLs / Pages to Chase
- **CSDb: SIDwinder V01.22** — https://csdb.dk/release/?id=66494 (check comments tab for any
  user discussion about format details)
- **CSDb: SIDwinder V01.23** — https://csdb.dk/release/?id=101758 (check comments tab)
- **CSDb: SIDwinder V1.23 Enhanced** — https://csdb.dk/release/?id=99574 (PCH's enhancement
  notes; packer bug discussion by Luca)
- **Zimmers.net source code** — https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip
  (341 KB; contains the full assembler source — highest-value next step for format RE)
- **Plus/4 World full page** — https://plus4world.powweb.com/software/SIDwinder_V01_23
  (already partially mined; may have more detail on the full manual text)
- **Planet Emulation** — https://www.planetemu.net/rom/commodore-c64-applications-d64/sidwinder-v01-23-1994-natural-beat
  (has the D64 image for download)

### Usernames to Track
- **Taki** (Balázs Takács, Hungary, Natural Beat) — CSDb scener; author of V01.22 and V01.23
- **Luca** (Fantastic Italian Research Enterprise / FIRE) — tested V01.23, bundled music,
  knows about the packer bug
- **PCH** — made the 2011 Enhanced version; has the live piano feature; Polish scene
- **TLC** (Levente Hársfalvi) — made the Plus/4 port of V01.23

### Key Next Steps
1. **Download and read the Zimmers source** (`SIDwinder_V0123_src.zip`) — will reveal
   exact data layout, player load address, table offsets, and packer format
2. **HVSC Musicians.txt** already confirmed: Taki = Takács, Balázs / Natural Beat / HUNGARY
3. **sidid signatures** — check `tools/sidid` for Natural Beat player fingerprint if present;
   otherwise derive from source code
4. **HVSC STIL.txt** — search for Natural Beat or SidWinder entries that may include
   per-tune technical comments
