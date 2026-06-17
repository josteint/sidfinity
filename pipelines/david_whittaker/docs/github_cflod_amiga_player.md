---
source_url: https://github.com/rofl0r/c-flod/tree/master/neoart/flod/whittaker
fetched_via: direct
fetch_date: 2026-06-17
author: Christian Corti (original Flod 4.1 ActionScript); rofl0r (C conversion)
content_date: 2012 (copyright date in source headers)
reliability: primary (Amiga format; NOT the C64 player, but closely related)
---

# c-flod — Amiga David Whittaker Player (DWPlayer)

## Repository

- Repo: https://github.com/rofl0r/c-flod
- Whittaker dir: https://github.com/rofl0r/c-flod/tree/master/neoart/flod/whittaker
- License: Creative Commons Attribution-Noncommercial-Share Alike 3.0

## IMPORTANT CAVEAT

This implements the **Amiga** version of the Whittaker player (Paula sound chip,
.dw modules with PCM samples), NOT the C64 SID chip version. The two engines
share command encoding conventions and the same composer's design idioms but are
distinct binaries targeting different hardware.

## Files

```
DWPlayer.c / DWPlayer.h   — main play routine, effect dispatcher
DWSample.c / DWSample.h   — sample (instrument) record
DWSong.c   / DWSong.h     — song-level structure (speed, delay, tracks array)
DWVoice.c  / DWVoice.h    — per-voice state block
```

## Song structure (DWSong.h)

```c
typedef struct {
    int     speed;              // global playback speed
    int     delay;              // global delay counter
    int     tracks[16];         // DWSONG_MAXTRACKS = 16
    unsigned int vector_count_tracks;  // actual track count
} DWSong;
```

## Voice state (DWVoice.h fields)

| Field | Purpose |
|---|---|
| `index`, `bitFlag`, `next` | channel identity / linked-list |
| `channel`, `sample` | Paula channel + current sample ptr |
| `trackPtr`, `trackPos` | track sequence position |
| `patternPos` | pattern byte read cursor |
| `frqseqPtr`, `frqseqPos` | frequency-sequence position |
| `volseqPtr`, `volseqPos`, `volseqSpeed`, `volseqCounter` | envelope/volume sequence |
| `halve`, `speed`, `tick` | timing / tempo |
| `busy`, `flags` | state booleans |
| `note`, `period`, `transpose` | pitch state |
| `portaDelay`, `portaDelta`, `portaSpeed` | portamento/glide |
| `vibrato`, `vibratoDelta`, `vibratoSpeed`, `vibratoDepth` | vibrato |

## Command/effect encoding (DWPlayer.c)

Byte values in pattern data:

| Range | Meaning |
|---|---|
| 0x00–0x7F | Note value (bit 7 clear) |
| 0x80 | Track loop / end-of-song marker |
| 0x81 (`-127`) | Portamento — sets slide speed + delay |
| 0x82 (`-126`) | Note end (mute) |
| 0x83 (`-125`) | Note restart (variant 0+) |
| 0x84 (`-124`) | Song end |
| 0x85 (`-123`) | Global transpose |
| 0x86 (`-122`) | Vibrato on (speed + depth bytes follow) |
| 0x87 (`-121`) | Vibrato off |
| 0x88–0x8C (`-120` to `-116`) | Variant-specific: fade speed, volume, delay, other |

**Effect byte counts** (bytes consumed after the command byte):
- End-of-track, stop: −1 (terminates parsing)
- Mute, wait, vibrato-off: 0 additional bytes
- Global transpose, speed, volume fade: 1 additional byte
- Slide, vibrato-on: 2 additional bytes
- Effect 0x09 (half-volume toggle): 0 or 2 conditional bytes

## Period tables (Amiga)

Two period tables exist; one is annotated "old QBall-only player":
- `Periods1` — 12 entries, 256 down to 136 (extremely limited octave range)
- `Periods2` — 48 entries, 4096 down to 228 ("first version of player")
- `Periods3` — 60 entries, 8192 down to 135 ("newer version of player")
- `EmptyTrack` — single byte `0x80` fallback

The 48-entry table has a comment "additional periods were added beyond the
original player to handle arpeggio or transpose operations that exceeded normal
ranges" — meaning the player itself has no out-of-bounds guard for these.

## Mapping to C64 engine

The Amiga player's effect hierarchy maps directly to what is seen in the Panther
disassembly for C64:

| Amiga command | C64 equivalent (Panther) |
|---|---|
| Portamento | $89 modulation setup / VD slide field |
| Vibrato on/off | $89 modulation (freq mod) |
| Note end | $91 stop / $84–$87 flag ops |
| Global transpose | implicit via track sequence |
| Arpeggio | ArpTable (separate mechanism, C64-specific) |
| Note value 0–127 | Note value + octave base |

Key difference: Amiga uses PCM sample numbers embedded in the note byte
(`note = trackByte`; older QBall-style: `sample = trackByte / 12; note = trackByte % 12`).
C64 uses waveform selection via explicit command bytes ($8A–$8D).

## Source file raw URLs

- DWPlayer.c: https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.c
- DWPlayer.h: https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.h
- DWSong.c:   https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSong.c
- DWSong.h:   https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSong.h
- DWVoice.c:  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWVoice.c
- DWVoice.h:  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWVoice.h
- DWSample.c: https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSample.c
- DWSample.h: https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSample.h

## Leads to follow

- Original Flod 4.1 ActionScript by Christian Corti (neoart.eu) — may have
  more complete format comments; site may be down
- rofl0r's c-flod README for any format notes: https://github.com/rofl0r/c-flod/blob/master/README
- UADE Amiga emulator's EP_DWhittaker eagleplayer plugin (binary, 6721 bytes);
  was in UADE v2.13 (released 2000-11-11); source unknown
- EaglePlayers player page (TLS cert broken as of 2026-06-17):
  http://wt.exotica.org.uk/players.html
- exotica.org.uk David Whittaker format page (Cloudflare-gated):
  https://www.exotica.org.uk/wiki/David_Whittaker_(format)
