---
source_url: https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
fetched_via: direct
fetch_date: 2026-06-17
author: VGMPF wiki contributors; NES driver reverse-engineering: Tony Bybell
content_date: unknown (wiki, undated)
reliability: secondary
---

# David Whittaker Cross-Platform Format Notes

This file consolidates everything found about the C64 engine in the context of
its cross-platform relatives (NES, Amiga, ZX Spectrum). Understanding the
variants helps bound what is engine-invariant vs C64-specific.

## Sources consulted

1. VGMPF — David Whittaker (NES Driver):
   https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)

2. VGMPF — DW (Amiga format):
   https://vgmpf.com/Wiki/index.php?title=DW

3. Lemon64 forum — "Why wasn't David Whittaker asked to do the music for Xenon?":
   https://www.lemon64.com/forum/viewtopic.php?t=81385

4. Remix64 interview:
   https://remix64.com/interviews/interview-david-whittaker.html

5. fileformats.archiveteam.org (site unreachable 2026-06-17 — connection refused):
   http://fileformats.archiveteam.org/wiki/David_Whittaker

6. NostalgicPlayer catalog description:
   https://nostalgicplayer.dk/modules/format/davidwhittaker/4

## Song table format (from VGMPF NES driver page)

Whittaker documented his own format layout:

> Each entry: `<speed>, <v1_lo>, <v1_hi>, ..., <vN_lo>, <vN_hi>`

- C64 (3 SID voices) → 7 bytes per sub-song entry
- NES (4 voices)     → 9 bytes per sub-song entry

Each voice pair is a 16-bit pointer to the voice's first pattern. The `speed`
byte controls the play-callback rate.

Pattern data terminates with a platform-defined end byte:
- NES:  `$FF`
- C64:  appears to be `$88` (pattern jump) or special command; Panther uses
  the command table ($80–$93) with $91 = stop music

Pointers are **absolute** addresses — the format is NOT relocatable.
Re-entering a pattern list loops from beginning (NES: `0,0` pointer signal;
C64: track sequence structure with 56-entry fixed arrays per voice).

## NES driver technical details (Tony Bybell reverse-engineering)

- "NES is loosely based on the Jason Brooke rewrite for C64" (Bybell's note)
- NES uses only 4 main APU channels; DPCM used exactly once (Krusty's Fun House)
- NES contains "soundparameters" tables similar to Future Composer on C64,
  encoding vibrato and tremolo. High bit set in final table entry marks end.
- Whittaker converted C64 driver to NES: "not too difficult since both use
  6502-based CPU, but had to account for difference between SID and 2A03"
- "All the heavy lifting for effects [is] done by the player, not the PSG
  in the 2A03" — software-driven effects architecture identical to C64 model

## C64 → Amiga delta (from c-flod / NostalgicPlayer analysis)

| Aspect | C64 SID | Amiga .dw |
|---|---|---|
| Audio hardware | SID chip ($D400–$D418) | Paula (DMA channels) |
| Waveform | SID control reg commands ($8A–$8D) | PCM sample numbers in note byte |
| Frequency | SID freq table (96 entries) | Amiga period table (48 or 60 entries) |
| Arpeggio | Dedicated ArpTable (13 patterns) | ArpeggioList byte sequences |
| Envelope | ADSR via SID registers | EnvelopeList byte sequences (software) |
| Vibrato | Freq-mod via SoundUpdate | DWVoice vibrato fields (software) |
| Portamento | Slide via VD_ state | portaDelta/portaSpeed/portaDelay |
| Sub-songs | Single song (Panther); multi suspected | SongInfo.PositionLists[] |
| Pointer size | 16-bit absolute | 32-bit (old) or 16-bit (new) Amiga |

## C64 → ZX Spectrum delta (Lemon64 forum)

A developer performed automatic C64→ZX128 Whittaker conversion:
- "Spectrum missing commands here and there for the additional SID waveforms"
  (Spectrum has no triangle/sawtooth/ring/sync — commands $8C/$8D/$92/$93
  are absent or silently ignored)
- "All the usual Whittaker arpeggios tables and such are there in the
  Spectrum data" — arpeggio format is preserved across ports
- "Nothing that is a dealbreaker with getting a reasonable conversion"
- NES player derived from C64 player; NES implements all effects in software

## Evolution of the C64 engine (timeline inferred)

| Era | Notes |
|---|---|
| ~1983 (very early) | "Minimalist, tuned at 424 Hz" — pre-SID or early SID |
| 1984 | Lazy Jones ($30405), Red Max — first recognisable Whittaker engine |
| 1985–1986 | Panther, Glider Rider — mature engine with 20 commands |
| 1987–1991 | Used "without real updates until 1991" (Whittaker's own words) |

## Key RE insight from NostalgicPlayer (applies to C64)

The Amiga player has two variants detectable by opcode scan:
- **Old (QBall)**: very limited 12-note period table, 32-bit abs pointers
- **New**: 48–60-note range, 16-bit or 32-bit pointers, extended effects

The C64 player likely has analogous early/late variants (Lazy Jones = old,
Panther = mature) distinguished by frequency table size and command range.
The sidid signatures do not distinguish them, suggesting the core play loop
is structurally identical.

## Leads to follow

- VGMPF NES driver page (detailed format + "soundparameters" tables):
  https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
- VGMPF DW Amiga page:
  https://vgmpf.com/Wiki/index.php?title=DW
- fileformats.archiveteam.org (unreachable; try Wayback Machine):
  https://web.archive.org/web/*/http://fileformats.archiveteam.org/wiki/David_Whittaker
- Lemon64 "Xenon" thread (cross-platform conversion discussion):
  https://www.lemon64.com/forum/viewtopic.php?t=81385
- exotica.org.uk Amiga format wiki (Cloudflare-gated as of 2026-06-17):
  https://www.exotica.org.uk/wiki/David_Whittaker_(format)
- UADE v2.13 source (EP_DWhittaker eagleplayer binary + format detection):
  https://github.com/dv1/uade (or search for v2.13 tarball on aminet)
- Aminet EP_DWhittaker.lha (6721 bytes, binary eagleplayer plugin):
  search aminet.net for "EP_DWhittaker"
- Tony Bybell's NES driver reverse-engineering notes (cited by VGMPF,
  original source unknown — try to locate)
