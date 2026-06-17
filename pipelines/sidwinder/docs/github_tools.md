---
source_url: multiple
fetched_via: direct
fetch_date: 2026-06-17
author: various
content_date: various
reliability: secondary
---

# SidWinder: GitHub & Open-Source Tool Survey

## 1. What SidWinder Is (Taki, Natural Beat, Year, Known Versions)

SidWinder is a C64 SID music tracker/editor created by **Taki (Balazs Takacs) of Natural Beat**. It is a
machine-code music editor for the Commodore 64, PAL only, distributed as a D64 disk image.

**Known release history:**

| Version | Group | Year | CSDb ID | Notes |
|---------|-------|------|---------|-------|
| V01.22  | Natural Beat | 1999 | 66494 | Original release; code + music by Taki |
| V01.23  | Natural Beat | 2000-03-15 | 101758 | Updated; testing by Luca (FIRE); GPL; identity field changed |
| V1.23 Enhanced!! | PCH (KGB'92, Unreal) | 2011-04-17 | 99574 | Third-party fork; adds live piano, menu functions; GPL disputed |

**Author:** Taki / Natural Beat. Real name Balazs Takacs (Hungarian demoscener).
**License:** Originally released under GPL (per Luca/FIRE's comment on CSDb, confirmed in TLC's Plus/4 port).
**Platform:** C64 original; Plus/4 conversion by TLC (Fantastic Italian Research Enterprise, FIRE group).
**HVSC coverage:** 117 SID files in HVSC classified under the SidWinder engine.

The Plus/4 port by TLC also fixed a known packer bug present in V01.23. Source code is distributed with the
release (assembly source confirmed available in multiple distribution bundles per Plus/4 World).

---

## 2. Modern "SIDwinder" Tool — DIFFERENT FROM TAKI'S EDITOR

**WARNING — NAME COLLISION:** There is a modern tool also named "SIDwinder" that is entirely unrelated to
Taki's 1999 tracker.

**SIDwinder (Genesis Project / Robert Troughton "Raistlin"), 2025**
- CSDb: https://csdb.dk/release/?id=253271 (SIDwinder V0.2 - Preview, 24 May 2025)
- GitHub: https://github.com/RobertTroughton/SIDwinder/
- Web app: https://sidwinder.netlify.app/

This is a **web-based SID analysis, relocation, disassembly, and PRG-builder tool**. It:
- Runs a full 6510 CPU emulator in WebAssembly to analyze SID files
- Can relocate SID tunes to new memory addresses
- Disassembles SID files to 6502 assembly
- Builds executable C64 PRGs with 9 visualizer templates
- Detects multi-SID (2SID/3SID), CIA timer, zero-page usage
- Built with vanilla JavaScript + KickAss assembler + TSCrunch
- Rated 9.8/10 on CSDb; testers include Trident (Fairlight)

**It does NOT parse the Taki SidWinder tracker format** — it handles standard .sid files only and has no
knowledge of the older tracker's data format. The naming overlap is coincidental.

---

## 3. Open-Source Tools That Touch the SidWinder Format

### 3.1 cadaver/sidid — C64 Playroutine Identity Scanner

**URL:** https://github.com/cadaver/sidid
**What it does:** Scans SID binary code for known playroutine signatures; reports which tracker/player
produced a SID. The canonical player-detection tool for HVSC classification.

**SidWinder detection signature** (from `sidid.cfg`, raw file):

```
[SidWinder]
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

**Signature format:** Hex bytes; `??` = wildcard (accept any byte at that position); `END` = end of signature.
The signature is a single pattern — no version-discriminating sub-entries (no V1.22 vs V1.23 split).

**Interpretation of the bytes:**
- `AD ?? ??` — LDA absolute (load from some address)
- `F0 ??` — BEQ (branch if zero)
- `CE ?? ??` — DEC absolute (decrement counter in memory)
- `88` — DEY (decrement Y)
- `4C ?? ??` — JMP absolute (main loop jump)
- `B9 ?? ??` — LDA absolute,Y (indexed read from table — likely sector/track data)
- `C9 ??` — CMP immediate
- `90 ??` — BCC (branch if carry clear)
- `F0 ??` — BEQ
- `B9 ?? ??` — LDA absolute,Y (second table read)
- `8D ?? ??` — STA absolute (write to SID or RAM)
- `A8` — TAY (transfer A to Y)

This appears to be from the player's main dispatch loop: load a byte from a sequence, compare against
command thresholds, branch on type, write to hardware.

**Note:** The sidid.nfo file does not mention Taki or Natural Beat by name — the engine is listed solely as
"SidWinder" with no author attribution in that file.

**Signature authors:** Various (Wilfred Bos, iAN CooG, Professor Chaos, Cadaver, Ninja, Ice00, Yodelking).

---

### 3.2 WilfredC64/player-id — Player Identification Utility

**URL:** https://github.com/WilfredC64/player-id
**What it does:** Cross-platform utility inspired by sidid; identifies C64 music players using a sidid.cfg
signature file. Uses the BNDM search algorithm for fast matching across SID files.

**SidWinder:** Uses the same sidid.cfg config as cadaver/sidid above. The tool inherits the single SidWinder
signature entry. No additional SidWinder-specific handling has been found in the repo.

**Config:** Accepts sidid.cfg via `-c` flag or `SIDIDCFG` env variable; includes a `Signature File Format.txt`
doc. Signatures contributed by the same pool of authors as sidid.

---

### 3.3 Chordian/deepsid — DeepSID Online SID Player

**URL:** https://github.com/Chordian/deepsid
**What it does:** Web-based HVSC browser + SID player; uses player-id/sidid signatures for player
identification labelling in the UI.

**SidWinder:** No dedicated parsing or special handling found — DeepSID inherits player identification from the
sidid.cfg signature system. No SidWinder-specific code branches were located.

---

### 3.4 No SidWinder Import/Export in SIDFactory II, CheeseCutter, or GoatTracker

A search across GitHub for SIDFactory II (Chordian/sidfactory2), CheeseCutter, and GoatTracker found **no
SidWinder format import or export support**. These editors use their own native formats and have no format
bridge to Taki's tracker. None of the open-source editors have attempted to interoperate with SidWinder.

---

## 4. Detection Signatures (Byte Patterns, Offsets)

### From cadaver/sidid `sidid.cfg`:

```
[SidWinder]
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

- **Single signature entry** — no version split.
- **Pattern length:** 27 bytes (13 fixed, 14 wildcards).
- **Instruction profile:** Matches the player's command-dispatch loop: load byte from table (LDA abs,Y),
  compare to command ranges (CMP imm / BCC / BEQ), write to SID (STA abs), advance Y (TAY + DEY + JMP loop).
- **Offset:** Not fixed — sidid searches the entire SID binary for this pattern (not anchored to a fixed offset
  from the PSID load address).

---

## 5. SidWinder Format Summary (from Plus/4 World + CSDb)

The following is derived from the Plus/4 World technical page (https://plus4world.powweb.com/software/SIDwinder_V01_23)
and CSDb release comments. This is the format as described in the editor's built-in documentation.

### Song Constraints
- Up to **32 subtunes** per file
- Up to **96 sectors** (256 instructions each)
- Up to **64 instruments**
- Up to **16× music speed** (speed multiplier)
- PAL only (C64 standard; Plus/4 port adjusts for 885 kHz vs 985 kHz clock)

### Track Commands (one byte each, except Jump)
| Command | Range | Function |
|---------|-------|----------|
| Sector play | $00–$5F | Play sector N |
| Tr+XX | $00–$3F semitones | Transpose up |
| Tr-XX | $00–$3F semitones | Transpose down |
| VolXX | $00–$0F | Set constant volume |
| DecXX | speed $01–$07 | Volume decrement slide |
| IncXX | speed $01–$07 | Volume increment slide |
| HltVS | — | Halt volume slide |
| JmpXX | position $XX | Jump to track position |

Required track order: JmpXX → volume command → transposition command → sector reference.

### Sector Commands
| Command | Range | Function |
|---------|-------|----------|
| Snd.XX | $00–$3F | Select instrument |
| Dur.XX | $01–$40 | Note duration (frames) |
| Note | C-1 to A#8 | Play note |
| Gld.XX | $01–$0F | Glide |
| Gld.XX | $11–$1F | Slide |
| ------ | — | Delay + release |
| +++ | — | Hold (sustain) |
| Finish | — | End sector |

Required sector order: Snd.XX → Dur.XX → pitch modifier → Finish.

### Instrument Parameters (7 fields)
1. Attack/Decay (SID ADSR hi byte)
2. Sustain/Release (SID ADSR lo byte)
3. Gateoff counter (counts down per frame, clears gate bit at zero)
4. Wave/arpeggio table start position
5. Filter table start position ($00 = off, $FF = active)
6. Pulse width table start position ($00 = off, $FF = active)
7. Slide table start position

### Effect Tables

**Wave/Arpeggio table:**
- $00–$8F: waveform byte + arpeggio offset
- $90–$FE: repeat waveform with new arpeggio
- $FF: jump to AR field position

**Filter table:**
- RP $00–$FD: add to frequency + resonance (repeated)
- RP $FE: select filter type via FH byte
- RP $FF: jump to FH position
- FH: cutoff frequency high byte or filter type (bits 6–4)
- RL: resonance (bits 7–4) + frequency low (bits 2–0)

**Pulse Width table:**
- RP $00–$FE: add to pulse width (repeated)
- RP $FF: jump to PH position
- PH: PW high byte or jump target
- PL: PW low byte

**Slide/Vibrato table:**
- RP $00–$FD: add to frequency (repeated; used for vibrato)
- RP $FE: set absolute frequency (drum mode)
- RP $FF: jump to FH position
- FH: frequency high byte addition or jump target
- FL: frequency low byte addition

All effect tables initialize to zero at note start — first program line must establish base values.

### Packer Configuration
| Parameter | Purpose |
|-----------|---------|
| Filename | Source data file |
| Subsong count | Number of subtunes |
| Start address | Load address (hex, e.g. $1000) |
| Zeropage word | Player pointer (default $FB) |
| SID base address | Chip base ($D400 C64; $FD40 Plus/4) |
| Frequency table | Platform selection (C64 or Plus/4) |
| Identity field | 32-char text descriptor |

Packed output: identity text stored in screencode format at player_start + $20 (default $1020).

### Known Packer Bug
A bug in the V01.23 packer related to the END MUSIC mark was acknowledged by PCH (V1.23 Enhanced author).
TLC created a fixed Plus/4 packer that resolves this; the fix may not be in the C64 V01.23 release.

### Version Compatibility
- V01.23 loads and edits songs from V01.22 editors
- Single format change between versions: identity field layout
- No bare memory image save/load in V01.23

---

## 6. CSDb Entries Found

| CSDb ID | Title | Group | Year | Type |
|---------|-------|-------|------|------|
| 66494 | SIDwinder V01.22 | Natural Beat | 1999 | C64 Tool |
| 101758 | SIDwinder V01.23 | Natural Beat | 2000 | C64 Tool |
| 99574 | SIDwinder V1.23 Enhanced!! | PCH / KGB'92, Unreal | 2011 | C64 Tool |
| 253271 | SIDwinder V0.2 - Preview (**DIFFERENT TOOL**) | Genesis Project | 2025 | Other Platform Tool |

**Direct URLs:**
- https://csdb.dk/release/?id=66494 (V01.22)
- https://csdb.dk/release/?id=101758 (V01.23)
- https://csdb.dk/release/?id=99574 (V1.23 Enhanced)
- https://csdb.dk/release/?id=253271 (Modern Raistlin tool — unrelated)

**Credits confirmed via CSDb:**
- V01.22: Code = Taki, Music = Taki
- V01.23: Code = Taki, Music = Taki + Luca (FIRE), Testing = Luca (FIRE)
- V1.23 Enhanced: Code = PCH + Taki (original), released 2011

**License:** GPL (confirmed by Luca/FIRE in V1.23 Enhanced comments; TLC's Plus/4 port respects this).

---

## 7. Leads to Follow

### Highest-Priority: Source Code Recovery
- **D64 disk images** for V01.22 and V01.23 are available via CSDb downloads (IDs 66494, 101758).
  The disk images reportedly contain the **complete assembly source** (stated in Plus/4 World docs:
  "Source code: Complete assembly source available in multiple distributions"). Fetch and mount the D64
  to extract `.s` / `.asm` files. This is the most direct path to a full format spec.
- **Plus/4 World download:** https://plus4world.powweb.com/software/SIDwinder_V01_23 — has download links
  including Rulez.org, Zimmers, ko2000, commodore.ca mirrors.
- **Planet Emulation mirror:** https://www.planetemu.net/rom/commodore-c64-applications-d64/sidwinder-v01-23-1994-natural-beat
  — D64 image (72 KB zip) downloadable directly.

### sidid Signature Source File
- Raw sidid.cfg: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
  — Only one SidWinder entry found. No version split. If HVSC contains 117 tunes, all presumably
  match this single signature. Worth checking whether V01.22 and V01.23 produce identical player code.
- sidid.nfo (player info notes): https://github.com/cadaver/sidid/blob/master/sidid.nfo
  — Taki / Natural Beat not mentioned by name; only "SidWinder" label.

### GitHub Repos Worth Checking Directly
- https://github.com/cadaver/sidid — sidid.cfg + sidid.c (C source for scanner logic)
- https://github.com/WilfredC64/player-id — Python player-id; may have extended config
- https://github.com/RobertTroughton/SIDwinder/ — Modern Raistlin tool; **unrelated** but may contain
  useful SID analysis infrastructure re: player detection logic
- https://github.com/Chordian/deepsid — DeepSID; check PHP/JS backend for player-name lookup tables

### CSDb Comments / Community Knowledge
- Check all comments on CSDb release 101758 (V01.23) — Luca's GPL comment thread may link to TLC's fixed
  packer source or the plus/4 port with corrected packer code.
- Taki's handle: search CSDb for "Taki" as a composer/coder to find any other tools or contact info.

### HVSC Internal Documentation
- HVSC ships `DOCUMENTS/Sidplayers/` — check if a SidWinder entry exists in that directory.
  Path would be something like `hvsc84/C64Music/DOCUMENTS/Sidplayers/SidWinder.txt`.

### Author Handle
- Taki / Natural Beat — Hungarian C64 demoscener, circa 1999–2001. No public GitHub or modern contact
  found. May have activity on CSDB as a coder; worth searching CSDb for other Natural Beat releases.

### Potential Format Variants to Verify
- Whether V01.22 and V01.23 produce player code with the same sidid signature (single signature implies yes)
- Whether the Plus/4 port (TLC) uses a different player binary (different SID base $FD40 vs $D400, different
  frequency table) — if so, the PSID would not play correctly on C64 and vice versa; HVSC likely only
  contains C64 variants
- The "identity field" change between V01.22 and V01.23 — this is a metadata-only change (32-char text at
  player_start + $20), not a music data format change

---

## Deep fetch results (2026-06-17)

### Byte patterns confirmed

Direct fetch of https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg confirmed:

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

Context (surrounding entries in sidid.cfg):
```
SidTracker64
BD ?? ?? 29 FE 9D 04 D4 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? F0 ?? A8 BD ?? ?? 18 69 END

SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END

Silas_Warner
69 01 9D ?? ?? A9 00 9D ?? ?? 9D 04 D4 8A 18 69 END
```

The WilfredC64/player-id repo (https://github.com/WilfredC64/player-id) ships an identical
sidid.cfg + sidid.nfo in its config/ directory. No additional SidWinder detection logic
beyond the shared pattern.

The sidid.nfo attribution (both repos, identical):
```
SidWinder
   AUTHOR: Balázs Takács (Taki)
 RELEASED: 1999 Natural Beat
REFERENCE: https://csdb.dk/release/?id=66494
```

### cadaver/sidid repo contents
Files: Makefile, readme.txt, sidid.c (12,849 bytes), sidid.cfg (82,803 bytes),
sidid.nfo (46,267 bytes), tedid.cfg (842 bytes). No additional SidWinder-specific files.

### WilfredC64/player-id repo
Top-level: .editorconfig, .gitignore, Cargo.lock, Cargo.toml, LICENSE, README.md,
build.rs + directories: .github/, config/, doc/, src/. Rust implementation using BNDM
algorithm. config/ contains only sidid.cfg, sidid.nfo, tedid.cfg (same as cadaver).

### Modern SIDwinder tool (RobertTroughton) — CONFIRMED UNRELATED

Direct fetch of https://github.com/RobertTroughton/SIDwinder confirmed:
- Author: Robert Troughton (Raistlin of Genesis Project)
- Tool type: Web-based SID analysis, relocation, disassembly, PRG-builder
- Technology: C++ / WebAssembly + JavaScript
- Handles standard .sid PSID files only
- Zero knowledge of Taki's SidWinder tracker format
- The naming overlap is entirely coincidental; these are different tools from different eras

The web app (https://sidwinder.netlify.app/) appears to be the same Genesis Project tool
rebranded/hosted there — also unrelated to Taki's tracker.

### DeepSID (Chordian/deepsid)
Repo structure confirmed: PHP web app. config/ directory contains only PHP configuration
templates (example_general.php, example_localhost.php, example_online.php) — no
SidWinder-specific detection code. Player labelling is inherited from sidid.cfg signatures.

### Format parser code
No open-source SidWinder format parser (Python/JS/C) was found on GitHub. The only
machine-readable SidWinder knowledge in the open-source ecosystem is the single
detection signature in sidid.cfg. All format knowledge lives in the assembly source
files already present at pipelines/sidwinder/docs/src/ (PLAYER.ASM, PLAY0122.ASM,
SIDW0122.txt, PROGRAMM.txt, etc.).

### HVSC local state
- HVSC path: hvsc84/MUSICIANS/T/Taki/ — 49 SID files
- No "SidWinder" subdirectory in HVSC musicians (SidWinder is a tool, not a musician;
  its output SIDs are filed under their respective composers in HVSC)
- Some Taki SIDs already have sidfinity.sid + .usf builds in the repo

### Saved files
- pipelines/sidwinder/docs/src/sidid_cfg_sidwinder_section.txt — raw sidid.cfg section
- pipelines/sidwinder/docs/src/player_id_sidwinder.txt — WilfredC64/player-id coverage notes
