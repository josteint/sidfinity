---
source_url: https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.c
fetched_via: direct
fetch_date: 2026-06-17
author: Christian Corti (original Flod 4.1); rofl0r (C port)
content_date: 2012
reliability: primary
---

# c-flod DWPlayer.c — Format Detection + Playback Summary

Full raw file at:
  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.c

The WebFetch tool summarized rather than returning raw content. Key facts
extracted from the summary:

## Format detection (`DWPlayer_loader`)

The loader pattern-matches Motorola 68000 assembly instructions directly in
the binary:
- `0x47FA` = `LEA pc-relative` — used to find module base address
- `0x6100` = `BSR.W` — used to locate init/play function entry points
- Detects "variant versions 0–41" through instruction patterns
- Determines sample data width: 2 bytes (16-bit) or 4 bytes (32-bit)
- Detects channel count and whether waveform modification is enabled

This is the same 68000-opcode-scan approach documented in the NostalgicPlayer
C# worker (see `github_nostalgicplayer_csharp.md`).

## Playback (`DWPlayer_process`)

- Negative command values: -128 to -116 → effects (portamento, vibrato, transpose, etc.)
- Positive values → note trigger; reads from sample data
- Sample playback via Amiga hardware channel structs

## Effects list (from DWPlayer.c)

| Command | Value | Effect |
|---|---|---|
| Track loop | -128 (0x80) | end-of-track or jump |
| Portamento | -127 (0x81) | slide: speed + delay params |
| Note end | -126 (0x82) | mute |
| Note restart | -125 (0x83) | resume (variant >= 0) |
| Song end | -124 (0x84) | mark song complete |
| Transpose | -123 (0x85) | global pitch offset (1 byte) |
| Vibrato on | -122 (0x86) | speed + depth (2 bytes) |
| Vibrato off | -121 (0x87) | disable |
| Variant-specific | -120 to -116 | fade speed, volume, delay |

Positive note values trigger sample playback directly (Amiga: period table
lookup → Paula period register).

## Raw URLs for all DW source files

```
DWPlayer.c  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.c
DWPlayer.h  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWPlayer.h
DWSample.c  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSample.c
DWSample.h  https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSample.h
DWSong.c    https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSong.c
DWSong.h    https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWSong.h
DWVoice.c   https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWVoice.c
DWVoice.h   https://raw.githubusercontent.com/rofl0r/c-flod/master/neoart/flod/whittaker/DWVoice.h
```

## Leads to follow

- Download the raw .c/.h files above for full implementation detail
- The variant-index (0–41) is key: maps to the Amiga player revision history
  and potentially correlates with C64 engine releases (1984–1991)
- Locate the original Flod 4.1 ActionScript source (neoart.eu, may be archived)
  for more complete comments
