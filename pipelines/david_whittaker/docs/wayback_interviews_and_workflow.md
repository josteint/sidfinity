---
source_url: multiple (see per-section headers)
fetched_via: WebFetch + WebSearch 2026-06-17
fetch_date: 2026-06-17
author: research synthesis (Archive.org + Wayback cluster)
content_date: interviews 2001–2019; tech analysis by Tony Bybell (undated)
reliability: secondary (interview summaries); primary (VGMPF tech analysis)
---

# David Whittaker — Interviews, Workflow, and Cross-Platform Driver Documentation

This file covers the Archive.org / Wayback / interview cluster. It focuses
on (1) Whittaker's composing workflow and tools as described in his own words,
(2) Tony Bybell's reverse-engineering analysis of the macro-based driver
architecture (VGMPF), and (3) NostalgicPlayer Amiga-DW format technical data
(a sibling of the C64 format).

---

## 1. Interview Sources

### 1a. Remix64 interview (2001)
- **URL:** https://remix64.com/interviews/interview-david-whittaker.html
- **Key quotes (technical):**
  - *"Just a synth (Yamaha CX5 and Jupiter 6, mostly) and an assembler – no
    MIDI whatsoever."*
  - *"I like its similarity to analogue synths – especially the pulse-width
    flexibility – instead of the usual square/sine wave chips - but I was still
    disappointed that it only had 3 voices."*  (on the SID chip)
  - On perceived polyphony: *"Just the old method of playing quick/short notes
    of a chord, in quick succession – giving the feeling of more notes sounding
    than there really were."*
- **Technical detail level:** Low. Biographical. No data-structure content.

### 1b. c64.com interview (Stefan Posthuma, summer 1989)
- **URL:** https://www.c64.com/interviews/whittaker.html  (TLS cert error on
  direct fetch 2026-06-17; use HTTP or Wayback)
- **Wayback canonical:** https://web.archive.org/web/*/http://www.c64.com/interviews/whittaker.html
  (enumerate snapshots for earliest capture date)
- **Key content (from secondary sources):**
  - Confirms Supersoft + Commodore tools for assembly programming.
  - States he and Rob Hubbard *"used to swap/borrow each others sound drivers"* —
    implication: driver code was fluid between the two composers in ~1985–1986.
  - Driver used (without real updates) until 1991.
  - Jason Brooke rewrote the CPC driver in June 1986, enabling *"much more
    flexible chords, envelopes, and combining pitch bends with chords"*; one of
    them (Brooke or Whittaker) converted it back to C64 — this CPC-derived
    version is what HVSC calls the "standard" Whittaker C64 driver.
- **Technical detail level:** Low-medium. Confirms the Jason Brooke rewrite
  timeline.

### 1c. karsmakers.nl / Metal E-zine interview (1989)
- **URL:** https://www.karsmakers.nl/metal-e-zine/david.htm
- **Key quote (composing method):**
  - *"I either doodle around on a keyboard - or if I'm in a hurry, just get
    ideas from (i.e. rip-off) another style of music."*
- **Technical detail level:** Negligible. No driver content.

### 1d. VGMPF biographical page
- **URL:** https://www.vgmpf.com/Wiki/index.php/David_Whittaker
- **Technical content (synthesised from multiple secondary sources):**
  - Earliest C64 drivers: *"minimalist and tuned at 424 Hz."*
    Spectrum 128K driver *"was almost always tuned at 390 Hz (two semitones
    too low)"* — probably a porting simplification.
  - SID filter: used inconsistently; *"sounding best with a bias of at least
    -300."*  After 1991 he abandoned it except on engine sounds.
  - By 1998 he called the SID his favourite chip, citing *"similarity to
    analogue synthesizers, specifically the pulse width modulation which makes
    him recognizable."*
  - Tools: Yamaha CX5M, Casio CZ-230S, Roland Jupiter-6.
  - Cross-platform methodology: *"he had an excellent, macro-based system in
    place that at the source level was largely compatible from platform to
    platform."* (Tony Bybell's observation — see §2.)

---

## 2. Tony Bybell's Reverse-Engineering Analysis (VGMPF NES Driver page)

- **URL:** https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
- **Contributor:** Tony Bybell (reverse-engineered and wrote the analysis;
  Jeroen Tel confirmed the C64→NES conversion history)
- **reliability:** primary — produced from direct binary disassembly

### 2a. The macro-based architecture insight

> *"It appears to me that he had an excellent, macro-based system in place
> that at the source level was largely compatible from platform to platform
> and ensured he could quickly port work across platforms."*

> *"Command vary from platform to platform but C64 vs Spectrum tells me he
> used macro expansion in an assembler. Again, these are not true assembled
> tunes per se, but music data is macro expanded and uses absolute pointers."*

Implication for the migration: the C64 `.sid` binary is **not** the
canonical representation — it is the output of a macro assembler pass over
a platform-neutral source. The underlying musical content (notes, durations,
effect assignments) is recoverable; the binary form is a derived artefact.

### 2b. Song table layout (C64 vs. NES)

| Platform | Bytes/entry | Fields |
|----------|-------------|--------|
| C64      | 7           | `<speed>, <v1_lo>, <v1_hi>, <v2_lo>, <v2_hi>, <v3_lo>, <v3_hi>` |
| NES      | 9           | `<speed>, <v1_lo>, <v1_hi>, <v2_lo>, <v2_hi>, <v3_lo>, <v3_hi>, <v4_lo>, <v4_hi>` |
| Spectrum | 7 (assumed) | same as C64 but Spectrum-specific command set |

Voice pointers reference individual patterns for each channel. A `0,0`
pointer value signals repetition from pattern start. Special commands allow
restart from a **new** pointer address (skipping intro material on loop).

### 2c. Pattern byte encoding (C64)

- Bytes `$00`–`$7F`: note values (index into frequency table).
- Termination byte: `$88` on C64; `$87` on Spectrum; `$FF` on NES.
- Special pattern commands:
  - Restart with new voice pointers (for intro-skip on loop).
  - Force immediate song termination.

### 2d. Vibrato / tremolo tables

- Tables encode vibrato and tremolo information.
- The **final byte of each table entry always has its high bit set** (i.e.,
  the table is `$80`-terminated at each entry).
- NES limitation: vibrato tables do NOT scale by octave. At the highest NES
  octave, a +/-1 vibrato step jumps to an adjacent note; vibrato is
  effectively disabled there.
- C64 side: scales properly by octave (this is a key C64 vs. NES difference).

### 2e. Frequency tables (NES — hexadecimal period values)

David Whittaker's mapping: G-7 → `$11`  through  A-1 → `$3E7`

Manfred Trenz's modified mapping (Super Turrican): C-6 → `$32`  through  A-1 → `$3D5`

(C64 mapping not reproduced here — read from `NoteFreqsL`/`NoteFreqsH` in
`docs/src/Whittaker_David_Panther.asm`.)

### 2f. Cross-platform driver lineage (Jeroen Tel's account)

- Original driver: C64, ~1985.
- CPC rewrite: Jason Brooke, June 1986 — richer chords, envelopes, pitch
  bends. Subsequently converted back to C64 (this is the mature Whittaker C64
  driver used by most HVSC tunes).
- NES conversion: Whittaker converted his C64 driver to NES.
  The NES driver was licensed to Manfred Trenz (Super Turrican) and Enigma
  Variations (The Lion King).
- DPCM on NES: used once, for Krusty's Fun House title screen SFX only.
  Not part of the music channel pipeline.
- PAL/NTSC tempo: addressed after the first two NES releases.

### 2g. Key implication for C64 RE

Bansai (Lemon64 forum, thread t=81385) confirms from practical porting work:
*"His player does all the heavy lifting for effects, not the PSG in the 2A03,
so it seems reasonable that it can be emulated without any conversion
necessary."*  — i.e. the player is predominantly **software-side effect
logic**, not hardware-dependent. All effects (arpeggio, vibrato, portamento)
are computed in the driver and written as concrete frequency values to the
chip; the chip itself carries no effect state.

---

## 3. NostalgicPlayer Amiga DW Format (C# open-source implementation)

**IMPORTANT PLATFORM NOTE:** NostalgicPlayer's "David Whittaker" format is the
**Amiga version** of his player (68000 assembly, `.dw` file extension,
period tables in M68k addressing). It is NOT the 6502 C64 player. However,
it shares the same **macro-based compositional architecture** and the format
structure is closely analogous to the C64 variant.

- **NostalgicPlayer repo:** https://github.com/neumatho/NostalgicPlayer
- **DW player source:**
  `Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs`
  `Source/Agents/Players/DavidWhittaker/Tables.cs`

### 3a. Amiga DW format detection (from DavidWhittakerWorker.cs)

The player identifies modules by binary fingerprinting:
1. Rejects SC68 files (magic bytes `0x53 0x43 0x36 0x38`).
2. Searches for init-function signature: byte pattern `0x47 0xfa` followed
   by `0xf0` mask.
3. Searches for play-function signature: `0x47 0xfa` with specific
   following byte patterns.
4. File extensions: `.dw` and `.dwold`.

Two version families:
- **Old Player** ("QBall" format): simplified structure, different offsets.
- **New Player**: enhanced features.

Pointer width detection: `0x20 0x70` = 32-bit pointers; `0x30 0x70` = 16-bit.

### 3b. Amiga DW song/track data structure

**Per-song entry:**
- Speed: 8-bit or 16-bit depending on `enableDelayCounter` feature.
- `DelayCounterSpeed`: 8-bit if delay enabled.
- Position list offsets: one per channel, 16-bit or 32-bit.

**Track byte encoding:**
- `0x00`–`0x7F`: Note values → period table lookup.
- `0xE0`–`0xFF`: Wait counter (rows = `trackByte - 0xDF × speed`).
- `0x80`–`0xDF`: Effect/command bytes.

**Effect encoding (byte following the command byte):**
| Effect | Following bytes |
|--------|----------------|
| Slide | 2 bytes: speed, counter |
| StartVibrato | 2 bytes: speed, max value |
| GlobalTranspose | 1 byte |
| SetSpeed | 1 byte |
| Effect9 | 0 or 2 bytes (conditional on `halfVolume` feature) |

### 3c. Amiga DW period (frequency) tables

Three period tables used depending on player version:
- `Periods1` (12 entries, 256–136): QBall / old player only.
- `Periods2` (48 entries, 4096–228 + 3 extra): first new-player version.
- `Periods3` (68 entries, 8192–135): newer extended version.
- `EmptyTrack`: single byte `0x80`, fallback when no track data.

Period table selection: detected from instruction patterns in the binary:
- `0x10 0x00` instruction → `Periods2`.
- `0x20 0x00` instruction → `Periods3`.
- Old player → `Periods1`.

### 3d. Amiga DW optional feature flags

Detected by scanning for specific instruction byte patterns in the player binary:
| Feature | Indicator pattern |
|---------|------------------|
| Delay counter | `0x10 0x3a` |
| Extra counter | `0x53 0x2b` with `0x66` |
| Square waveform | `0x20 0x7a` with `0x30 0x3a` |
| Arpeggio | `0x45 0xfa` + envelope list |
| Vibrato | Jump table +12 bytes → `0x50 0xe8` |

### 3e. Amiga DW sample information structure

**New player format (per sample):**
- 4 bytes: pointer (skipped).
- 4 bytes: loop start (big-endian INT32).
- 2 bytes: length × 2 (big-endian UINT16).
- 2 bytes: fine-tune period.
- 2 bytes: volume.
- 1 byte: transpose (16-bit pointer mode) or conditional 16-bit volume/transpose.

**Old player:** Volumes read from a separate per-channel volume table.

---

## 4. Archived Amiga DW File Presence (archive.org)

Searching archive.org for downloadable David Whittaker Amiga music:
- **"David Whittaker Music Mix (1988-05-14)(Defjam - The Young Ones)"**
  appears in the Commodore Amiga Demos Music collection:
  https://archive.org/details/commodore-amiga-demos-music
  File is a `.zip`, 288.8 KB. Contains Amiga DW format music from 1988.

No C64-specific David Whittaker rip disk was found as a standalone archive.org
item. The HVSC-format SIDs remain the primary C64 archive.

---

## 5. Panther.asm — C64 Player Architecture (from the recovered disassembly)

`docs/src/Whittaker_David_Panther.asm` (reversed by dmx87) reveals the
C64 player internals more concretely. Key findings not duplicated in
`README.md`:

**Memory layout:**  Code loads at `$9000`. Voice data structures (`v1data`,
`v2data`, `v3data`) are 36 bytes each. Pattern sequencing uses track
pointers + pattern tables. Three independent track sequences
(`Track1Seq`, `Track2Seq`, `Track3Seq`) reference pattern data blocks.

**Command dispatch table ($8093):**
Effect codes `$80`–`$93` map to routines:
- Waveform selection: noise, pulse, sawtooth, triangle.
- Portamento (glide).
- Arpeggio.
- Filter control.
- Music stop.

**Arpeggio tables:** 13 predefined arpeggio sequences stored as byte tables,
each terminated with `$88`.

**Frequency tables:** `NoteFreqsL` / `NoteFreqsH` — 12-octave lookup
(C-1 through B-8). Confirmed $88 as pattern terminator (same byte as
arpeggio table terminator).

**Tempo system:** `TempoCnt` countdown with per-song `SongTempo` values.

**Voice state per voice (36 bytes):** flags, pattern pointers, track data,
note counter/duration, ADSR envelope values, frequency/pulse-width storage,
effect state (arpeggio, vibrato, portamento).

**Vibrato/portamento:** state-driven with direction tracking (`VD_B1D` flags).

**Waveform effects:** pulse-width modulation, sync square, ring modulation.

**Pattern format (inline):** note values 0–127, duration codes, ADSR
parameters, special effect commands. Terminator: `$88`.

**PSID metadata:** v2, single song, data offset `$007c`, init = play = `$9000`,
play = `$9151` (offset `$151` = 337 bytes into the binary = end of player code).

---

## 6. Bansai Cross-Platform Porting Work (Lemon64 thread t=81385)

Source: https://www.lemon64.com/forum/viewtopic.php?t=81385

Key technical findings from Bansai (CSDb scener 38332, coder/cracker):
- Performed **automatic conversion** of Whittaker's ZX128 player to C64
  format — the players are "quite compatible"; Spectrum is missing only
  SID-specific waveform commands and a few other things.
- Arpeggio tables confirmed present in the Spectrum player data with the
  same structure.
- Has "the full player source/song data for Xenon" (C64 format).
- Converted Platoon and Xenon Spectrum music to C64; result *"sounds like
  native C64 tunes"*.
- Working on running Whittaker's NES player directly on C64 backed by a
  2A03→2SID translation layer — possible because *"his player does all the
  heavy lifting for effects, not the PSG in the 2A03."*
- Implication: the Whittaker C64/NES/Spectrum engines are the **same player
  source compiled with different macros** — a fact directly relevant to
  identifying which effects the C64 version supports.

---

## Leads to Follow

- **Wayback snapshots of c64.com interview** — earliest capture may have more
  technical content than later versions. URL:
  `https://web.archive.org/web/*/http://www.c64.com/interviews/whittaker.html`
  (Wayback Machine fetch was blocked by the tool; try with `curl` via Bash).
- **NostalgicPlayer Amiga DW modules list** — 20+ `.dw` files playable by
  NostalgicPlayer:
  https://nostalgicplayer.dk/modules/format/davidwhittaker/1
  (pages 1–N). Download one `.dw` file and disassemble to compare with the
  C64 command set — likely reveals additional Amiga-only commands.
- **ExoticA `EP_DWhittaker.lha`** (Amiga EaglePlayers plugin):
  `http://wt.exotica.org.uk/players.html` (TLS cert invalid 2026-06-17).
  Try: `http://exotica.org.uk/files/eagleplayer/EP_DWhittaker.lha`
  This EaglePlayer source may document the `.dw` format from the Amiga side.
- **Bansai's Xenon player source/song data** — contact via CSDb PM (scener
  38332) or Lemon64 forum. This is likely the C64 source for the full Xenon
  Spectrum-to-C64 conversion, and would reveal the command set in text form.
- **Tony Bybell's full VGMPF NES driver analysis** — the page at
  `https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)` contains
  frequency tables not fully captured here. Fetch with `curl -s <url>` and
  save the full HTML.
- **ftp.funet.fi C64 archive** — Wayback snapshot:
  `https://web.archive.org/web/*/ftp://ftp.funet.fi/pub/cbm/c64/music/`
  Look for any `whittaker.*` or `david_whittaker.*` files in the music tree.
  The funet FTP was a major early SID distribution point.
- **Remix64 "Hitting the High Notes" article** — at
  `https://remix64.com/articles/featured-merman-whittaker.html`
  The fetch produced only musical-appreciation content; a Wayback snapshot
  from an earlier date may have had different technical content.
- **David Whittaker Amiga music mix (1988, Defjam)**:
  https://archive.org/details/commodore-amiga-demos-music
  The 1988-05-14 Defjam release contains Amiga DW format files — download
  and examine the binary to understand the oldest Amiga DW variant.
- **Wikipedia citations** — the Wikipedia article on Whittaker cites
  several sources; check whether any are magazine scans on archive.org
  (e.g., Commodore Force, ACE, Zzap!64).
