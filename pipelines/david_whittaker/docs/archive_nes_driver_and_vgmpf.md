---
source_url: https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
fetched_via: WebFetch 2026-06-17
fetch_date: 2026-06-17
author: Tony Bybell (RE analysis); Jeroen Tel (lineage); VGMPF editors
content_date: undated (article added post-2005)
reliability: primary (RE-derived; author credited)
---

# David Whittaker NES Driver — VGMPF Technical Analysis

This file preserves the technical content from the VGMPF's NES driver page,
which is the single most comprehensive publicly available analysis of
Whittaker's macro-based driver architecture. Its relevance to the C64 RE is
high because (a) the NES driver is a direct port of the C64 driver and (b)
Tony Bybell's analysis explicitly compares C64, NES, and Spectrum.

---

## Contributor Attribution

- **Tony Bybell** — primary reverse-engineering analysis of the NES driver.
  His key contributions: the macro-expansion observation, the platform
  comparison, and the vibrato table structure.
- **Jeroen Tel** — confirmed that Whittaker "converted his NES sound driver
  from his Commodore 64 sound driver."
- **Manfred Trenz** — modified the NES driver for Super Turrican (different
  frequency mapping).

---

## Macro-Based Architecture (Bybell's Observation)

Bybell's key observation is worth preserving verbatim:

> "It appears to me that he had an excellent, macro-based system in place
> that at the source level was largely compatible from platform to platform
> and ensured he could quickly port work across platforms."

> "Command vary from platform to platform but C64 vs Spectrum tells me he
> used macro expansion in an assembler. Again, these are not true assembled
> tunes per se, but music data is macro expanded and uses absolute pointers."

**What this means for the SIDfinity RE:**

1. The `.sid` binary (and the original game binary before ripping) is the
   OUTPUT of a macro assembler — not the source. The source was a platform-
   neutral MML-style text that used macros for waveform commands, note
   sequences, arpeggio references, etc.

2. Absolute pointers appear in the binary as concrete load-address-dependent
   values. This is why the player has no fixed load address across games (each
   binary is a separate assembler pass at a different load address).

3. The command set varies slightly per platform (Spectrum lacks SID waveform
   commands; NES lacks some C64 filter commands) but the underlying NOTE and
   DURATION encoding is the same.

4. Arpeggio tables and vibrato tables are present in ALL versions (C64,
   Spectrum, NES) — confirmed by Bansai's cross-platform porting work.

---

## Song Table — Exact Byte Layout

### C64 (7 bytes per entry)
```
Offset  Size  Field
  0      1    Speed (tempo counter initial value)
  1      1    Voice 1 pattern pointer — low byte
  2      1    Voice 1 pattern pointer — high byte
  3      1    Voice 2 pattern pointer — low byte
  4      1    Voice 2 pattern pointer — high byte
  5      1    Voice 3 pattern pointer — low byte
  6      1    Voice 3 pattern pointer — high byte
```

### NES (9 bytes per entry)
Same as C64 but with two extra bytes for voice 4:
```
  7      1    Voice 4 pattern pointer — low byte
  8      1    Voice 4 pattern pointer — high byte
```

Pattern pointers are absolute addresses (load-address-relative).
A pointer value of `$0000` signals repeat from pattern start.

---

## Pattern Byte Encoding

### C64 / Spectrum / NES common structure

- Bytes `$00`–`$7F`: Note index (lookup in platform's frequency table).
- Pattern terminator:
  - C64: `$88`
  - Spectrum: `$87`
  - NES: `$FF`
- Special commands (embedded in pattern stream): repeat from new address
  (skipping intro on loop), or force song stop.

### C64-specific note range

From `Panther.asm` (`NoteFreqsL`/`NoteFreqsH`): C-1 through B-8 (12 octaves
× 12 semitones = 96 notes, indices $00–$5F, plus pattern-terminator $88 and
effect bytes $80–$87, $89–$FF).

---

## Vibrato Table Structure

- Tables encode vibrato depth and tremolo information.
- **Final byte of each table entry has its high bit set** (`$80`-OR'd).
- C64 version: vibrato depth **scales per octave** (higher octaves get
  smaller ± adjustments).
- NES version: vibrato does NOT scale per octave — at the highest NES octave
  +/-1 period step jumps to the adjacent note, so vibrato is effectively
  disabled there.
- This is a KEY C64 vs. NES behavioural difference.

---

## Frequency Table Comparison (NES)

### Whittaker's own NES mapping (hex period values)
| Note | Period |
|------|--------|
| G-7  | $0011  |
| ...  | ...    |
| A-1  | $03E7  |

### Manfred Trenz's modified mapping (Super Turrican NES)
| Note | Period |
|------|--------|
| C-6  | $0032  |
| ...  | ...    |
| A-1  | $03D5  |

The two mappings differ at the high end — Trenz's version extends coverage
down to C-6 whereas Whittaker's starts at G-7. The low-note (high-period)
end is similar.

---

## NES-Only Features

- Uses only 4 main NES APU channels (pulse1, pulse2, triangle, noise).
- DPCM channel used **once only**: Krusty's Fun House title screen SFX.
  Not part of the regular music playback pipeline.
- PAL/NTSC tempo difference: not handled in the first two NES releases;
  corrected in later releases.

---

## Driver Lineage Timeline

| Year | Platform | Event |
|------|----------|-------|
| ~1984 | C64 | Original driver — *"minimalist, tuned at 424 Hz"* |
| 1986 | CPC | Jason Brooke rewrites driver — richer chords, envelopes, pitch bends |
| 1986 | C64 | Brooke/Whittaker converts CPC rewrite back to C64 — this becomes the "mature" driver used by most HVSC tunes |
| ~1987 | NES | Whittaker converts C64 driver to NES |
| 1987 | NES | First two NES releases — PAL/NTSC tempo not handled |
| 1988+ | NES | PAL/NTSC corrected; later NES releases (Krusty's uses DPCM once) |
| ~1988 | Amiga | .dw format (68000); samples from Korg M1 |
| 1991 | C64 | Driver frozen — Whittaker stops updating the C64 driver |
| various | Spectrum, Atari ST, Game Boy, GG/SMS | Conversions of the same driver |

---

## C64 vs. NES: Effect Residency

From Bansai's porting observation (Lemon64 t=81385):
*"His player does all the heavy lifting for effects, not the PSG in the 2A03,
so it seems reasonable that it can be emulated without any conversion
necessary."*

This confirms: all effects (arpeggio, vibrato, portamento, pulse sweep) are
computed in the **player software** and written as concrete `(freq_lo, freq_hi,
ctrl, pw_lo, pw_hi)` values to the chip. The chip carries no autonomous effect
state. From a USF modelling perspective: every effect visible in the SID
write-log is a direct write from the player, not a chip self-modifying value.

---

## Leads to Follow

- Full VGMPF NES driver page: `https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)`
  Fetch with `curl -s` to capture the complete frequency table (both Whittaker
  and Trenz mappings, all 48+ entries). The WebFetch tool only got the first
  and last row.
- NES `.nes` ROM binaries with Whittaker's music: Super Turrican (Manfred
  Trenz modification), Krusty's Fun House (DPCM SFX), Double Dragon, Gauntlet.
  Disassemble NES ROM music data to see macro expansions in their raw form —
  the NES patterns should structurally mirror C64 patterns.
- Tony Bybell direct contact via VGMPF — his full analysis notes (beyond the
  wiki page) may describe the exact C64 command byte table.
