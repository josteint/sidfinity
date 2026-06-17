---
source_url: https://github.com/neumatho/NostalgicPlayer / https://nostalgicplayer.dk / https://www.exotica.org.uk/wiki/David_Whittaker_(format)
fetched_via: WebFetch 2026-06-17
fetch_date: 2026-06-17
author: Thomas Neumann (NostalgicPlayer); ExoticA editors
content_date: NostalgicPlayer ongoing; ExoticA 2000s+
reliability: primary (open-source C# implementation)
---

# David Whittaker Amiga .dw Format

**PLATFORM WARNING:** Everything in this file concerns the **Amiga version**
of the Whittaker driver (68000 assembly, `.dw` / `.dwold` file extension),
NOT the 6502/SID C64 player. The Amiga format shares the same macro-based
compositional architecture and many structural analogies with the C64 version,
but uses M68k addressing, period-register frequencies (not SID freq regs),
and optional PCM sample data.

The open-source C# implementation in NostalgicPlayer is the most detailed
public documentation of any Whittaker player format variant.

---

## Sources

- **NostalgicPlayer repo:** https://github.com/neumatho/NostalgicPlayer
- **Player source files:**
  - `Source/Agents/Players/DavidWhittaker/DavidWhittaker.cs`
  - `Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs`
  - `Source/Agents/Players/DavidWhittaker/Tables.cs`
- **NostalgicPlayer modules list:** https://nostalgicplayer.dk/modules/format/davidwhittaker/1
  (pages 1–N; 20+ modules per page; shows available .dw files for download)
- **ExoticA format page:** https://www.exotica.org.uk/wiki/David_Whittaker_(format)
  (Cloudflare-blocked 2026-06-17; try curl with User-Agent)
- **EaglePlayers plugin:** `EP_DWhittaker.lha` (6721 bytes) at
  `http://wt.exotica.org.uk/players.html` (TLS cert invalid 2026-06-17)

---

## Format Overview (ExoticA)

> ".dw files are a custom, non-tracker audio format used in a number of
> Commodore Amiga games by composer David Whittaker."

- **Not a standard tracker format.** The module file contains both the
  68000 replay code and the music data as a single binary.
- **Release year:** 1987 (earliest Amiga DW modules).
- **File extensions:** `.dw`, `.dwold`.
- **Header type:** Custom (no fixed magic bytes — identified by code patterns).
- **Instruments:** Internal (encoded in the module file, including sample data).

---

## Module Identification (from DavidWhittakerWorker.cs)

### Detection algorithm
1. Reject if file starts with SC68 magic bytes (`0x53 0x43 0x36 0x38`).
2. Search binary for init-function signature: `0x47 0xFA` followed by `0xF0`-masked check.
3. Search binary for play-function signature: `0x47 0xFA` + specific following byte pattern.
4. If both found → module identified as David Whittaker format.

(Hex `0x47 0xFA` is the M68k instruction `LEA.L (rel, PC), A7` — a common
idiom for loading a base address relative to PC. This is the fingerprint of
his initialisation and playback routines.)

### Version detection
- **Old Player (QBall):** simplified structure, different offset calculations.
  Uses `Periods1` table. Oldest known variant.
- **New Player:** enhanced features; uses `Periods2` or `Periods3`.

### Pointer width detection
- Pattern `0x20 0x70` in binary → **32-bit pointers**.
- Pattern `0x30 0x70` in binary → **16-bit pointers**.

---

## Song Data Structure (per-song entry)

| Field | Size | Notes |
|-------|------|-------|
| Speed | 8-bit (base) | If `enableDelayCounter` detected: 8-bit base speed + separate 8-bit `DelayCounterSpeed` |
| Position list offset (ch.1) | 16-bit or 32-bit | Depends on pointer-width detection |
| Position list offset (ch.2) | same | |
| Position list offset (ch.N) | same | |

Position lists reference track data blocks for each channel.

---

## Track Byte Encoding

| Byte range | Meaning |
|-----------|---------|
| `$00`–`$7F` | Note value → period table lookup |
| `$E0`–`$FF` | Wait counter: rows = `(byte - $DF) × speed` |
| `$80`–`$DF` | Effect / command bytes |

### Effect byte parameters
| Effect | Following bytes |
|--------|----------------|
| Slide | 2: speed, counter |
| StartVibrato | 2: speed, max |
| GlobalTranspose | 1: signed semitone delta |
| SetSpeed | 1: new speed value |
| Effect9 | 0 or 2 (conditional on `halfVolume` feature) |

---

## Period Tables

Three tables; selection determined by detecting instruction patterns in player binary:

### Periods1 — QBall / old player (12 entries)
Values: 256, 241, 227, 214, 202, 190, 180, 170, 160, 151, 143, 136.
(One octave; QBall format only.)

### Periods2 — first new-player version (48 entries + 3 overflow)
Range: 4096 down to 228, plus 3 extra values for arpeggio/transpose overflow.
(4 octaves.)

### Periods3 — newer extended version (68 entries)
Range: 8192 down to 135.
(~5.6 octaves; widest range.)

### EmptyTrack fallback
Single byte `$80` — returned when a channel has no track data.

---

## Optional Feature Flags (auto-detected from binary patterns)

| Feature | Binary indicator |
|---------|-----------------|
| Delay counter | `0x10 0x3A` |
| Extra counter | `0x53 0x2B` with `0x66` |
| Square waveform | `0x20 0x7A` with `0x30 0x3A` |
| Arpeggio support | `0x45 0xFA` + envelope list pointer |
| Vibrato | Jump table offset +12 bytes leads to `0x50 0xE8` |

---

## Sample Information Structure (per sample, new player)

| Offset | Size | Field |
|--------|------|-------|
| 0 | 4 | Sample pointer (skipped during parsing) |
| 4 | 4 | Loop start (big-endian INT32) |
| 8 | 2 | Length × 2 (big-endian UINT16; actual length = field/2) |
| 10 | 2 | Fine-tune period |
| 12 | 2 | Volume |
| 14 | 1 | Transpose (16-bit pointer mode) or conditional 16-bit volume/transpose |

Old player: volumes read from a separate per-channel volume table (not per-sample).

---

## Relevance to the C64 RE

The Amiga DW format is a sibling, not an identical clone, of the C64 format.
Key structural analogies:
- Same macro-based MML architecture.
- Same concept of per-channel pattern streams with terminator bytes.
- Arpeggio tables present and similarly structured.
- Effect bytes embedded in pattern stream with 1–2 parameter bytes following.
- Vibrato tables with high-bit-set termination.

Key differences:
- Amiga uses period registers (Amiga hardware period = 3546895 / freq);
  C64 uses 16-bit SID frequency registers.
- Amiga has PCM sample data; C64 does not (waveforms are synthesised by SID).
- Amiga uses 32-bit absolute M68k pointers; C64 uses 16-bit 6502 pointers.
- Amiga period tables have 3 variants; C64 has at minimum 2 (early 424 Hz,
  later retuned — exact table not yet extracted beyond Panther.asm).

---

## Archive.org DW Files

A 1988 Amiga DW module is known to exist at:
- **Collection:** https://archive.org/details/commodore-amiga-demos-music
- **Item:** "David Whittaker Music Mix (1988-05-14)(Defjam - The Young Ones)"
- **File type:** ZIP, 288.8 KB
- **Notes:** One of the earliest known standalone Amiga DW releases. The 1988
  date places it in the early new-player era (after the 1987 introduction).
  Downloading this file and comparing its binary structure against
  DavidWhittakerWorker.cs's parsing logic would yield concrete byte offsets
  for the earliest documented Amiga DW variant.

---

## Leads to Follow

- **NostalgicPlayer modules pages 1–N:** https://nostalgicplayer.dk/modules/format/davidwhittaker/1
  Each page lists 20 `.dw` files with download links. Download several from
  different years (1987–1992) to sample the full version range (QBall, 16-bit,
  32-bit pointer variants).
- **ExoticA EP_DWhittaker.lha** (6721 bytes): The Amiga EaglePlayer plugin.
  This is a replay routine in M68k assembly — disassembling it would yield
  a clean, commented player that may directly document the command byte table.
  Try fetching: `http://exotica.org.uk/files/eagleplayer/EP_DWhittaker.lha`
  or search on Aminet: https://aminet.net/search?query=DWhittaker
- **Aminet:** search `https://aminet.net/search?query=DWhittaker` for other
  Amiga player plugins or documentation.
- **DavidWhittakerWorker.cs full source** — the WebFetch summary above may
  have missed some effect byte definitions. Fetch the raw file:
  `https://raw.githubusercontent.com/neumatho/NostalgicPlayer/main/Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs`
  using `curl` from Bash to capture the complete source.
