---
source_url: multiple (see individual docs/ files)
fetched_via: direct + local
fetch_date: 2026-06-17
author: research synthesis (Jostein Trondal session)
content_date: 2026-06-17
reliability: primary (based on official source archive + HVSC local data)
---

# SidWinder Research — Final Synthesis

## Overview

SidWinder is a C64 SID music editor and player written by **Balázs Takács (Taki)**
of the Hungarian demoscene group **Natural Beat**, originally coded in 1994 and
first released publicly in 1999 as V01.22.  A Plus/4 port with GPL source release
(V01.23) followed in March 2000 by Levente Hársfalvi (TLC / Coroners).

- **HVSC count:** 117 SID files (engine = "SidWinder" per sidid classification)
- **Musicians using SidWinder in HVSC:** Factor6 (38), Luca (25), Taki (21),
  Eclipse (19), PCH (5), Zapac (4), Puterman (4), Phobos (1)
- **Format doc state:** OK — full source archive recovered; complete format spec written.

---

## What We Know About the Format

### Complete byte-layout spec is available

The V01.23 source archive (`SIDwinder_V0123_src.zip`, zimmers.net/funet) contains:
- `SIDW0122` — Taki's original, detailed V01.22 user+programmer documentation
- `SUMMARY` — complete command/key reference
- `SRC/PLAYER.ASM` — full 6502 player source (1167 lines, TASM syntax)
- `SRC/ED.ASM` — full editor source (138 KB)
- `SRC/PACKER.ASM` — full packer source (65 KB)
- `HISTORY`, `GENERAL`, `PROGRAMM` — version history + architecture notes

A complete format specification is in `format_spec.md` (derived from primary source).
Key points:

**Capacity:** 32 subtunes, 96 sectors (256 instructions each), 64 instruments,
up to 16× speed (V01.23), 3 SID voices, PAL only.

**Track commands** (orderlist, strict ordering enforced by player dispatch):
- `$00–$3F` Tr+ (transpose up), `$40–$7F` Tr- (transpose down)
- `$80–$DF` sector-play, `$E0–$EF` VolXX, `$F0` HltVS
- `$F1–$F7` DecXX (volume slide down), `$F8–$FE` IncXX (volume slide up)
- `$FF + byte` JmpXX (2-byte, jump to track position)

**Sector commands** (strict ordering):
- `$00–$5E` note (semitone index), `$5F` `------` (delay+release)
- `$60–$6E` glide, `$70–$7E` slide, `$6F` `+++` (hold), `$7F` Finish
- `$80–$BF` Dur.XX (duration 1–64 frames), `$C0–$FF` Snd.XX (instrument select)

**Instrument** (7 bytes): AD, SR, gate-off counter, wave/arp pointer, filter
pointer, pulse pointer, slide pointer.  $00 = effect off; $FF = don't reinitialise.

**Effect tables** (all 256-row, page-aligned):
- Wave/arpeggio (WF+AR): waveform byte + arpeggio semitone offset; $90–$FE = repeat;
  $FF = jump.
- Filter (RP+FH+RL): additive sweep of $D415/$D416/$D417; $FE = set filtertype;
  $FF = jump.  Filter only updates from voice 1 (X=0); voices 2/3 use $D417 bits
  only.
- Pulse width (RP+PH+PL): additive sweep of 12-bit PW; $FF = jump.
- Slide/vibrato (RP+FH+FL): additive freq offset + `$FE` drum-mode (absolute freq
  write); $FF = jump.

**Glide table:** 16 entries × 2 bytes (absolute 16-bit freq increment per frame).
Non-adaptive (speed not relative to note pitch).

### Player entry points (default base $1000)

| Address | Role |
|---------|------|
| `$1000` | `JMP m_init` — init (A = subtune 0–31) |
| `$1003` | `JMP irqplr` — first play() call per frame |
| `$1006` | `JMP mltspd` — multispeed extra play() calls |

ZP pointer: `$FB/$FC` (packer-selectable).  Speed table at `pstart+$1692`.
Identity field (32 chars, screen codes) at `pstart+$1020`.

### Hard restart

Automatic at every sector end and every new note (test-bit mechanism, first
frame skipped).  Minimum safe duration: 4 frames.

---

## What We Know About the Player Architecture

**Timing:** VBI-driven (raster IRQ).  Not CIA-timed.  Multispeed calls are spread
equally across the frame in V01.23 (CIA timer 1 used for call spacing within the
editor player).  PSID `speed` bit = 0 (VBI) for all known HVSC SidWinder SIDs.

**Rastertime budget:**
- First call (`$1003`): max ~$14 scan-lines
- Subsequent calls (`$1006`): max ~$10 scan-lines

**ROM mapping:** Player runs with ROMs mapped out (`$01 = $35`) except during
editor I/O.

**Volume slide:** Internal slide via Inc/Dec track commands; external fade possible
by writing target volume to `pstart+$168E` (V01.22) / `pstart+$1673` (V01.23)
and `$00` to the control register each frame to suppress the internal slider.

---

## Thomas Jansson Tool Verdict — NAME COLLISION, UNRELATED

There are TWO distinct tools named "SIDwinder" that are **completely unrelated**:

1. **Taki's SIDwinder (1994/1999)** — C64 native SID music editor/tracker.
   This is the engine we are migrating.  CSDb #66494.

2. **Raistlin's SIDwinder (Genesis Project, 2025)** — A modern web/CLI tool
   (`https://sidwinder.netlify.app/`, `https://github.com/RobertTroughton/SIDwinder/`)
   for analyzing, relocating, disassembling, and packaging SID files as C64 PRGs.
   CSDb release #253271 (preview, May 2025), rated 9.8/10.
   It runs a 6510 CPU emulator in WebAssembly, accepts standard .sid files, and
   has **no knowledge of Taki's tracker format**.  The name overlap is coincidental.

**Thomas Jansson** (GitHub: `tjansson60`) has no connection to either tool.
He contributed to SID Factory II (a different tracker).  There is no evidence of
a "SIDwinder by Thomas Jansson" tool; the prompt may have conflated two different
people or searched the wrong name.  The modern tool's author is Robert Troughton
("Raistlin" of Genesis Project), not Thomas Jansson.

---

## CSDb Releases Found

| CSDb ID | Title | Group | Year | Notes |
|---------|-------|-------|------|-------|
| 66494 | SIDwinder V01.22 | Natural Beat | 1999 | First public release |
| 101758 | SIDwinder V01.23 | Natural Beat | 2000 | GPL; Plus/4 port by TLC |
| 99574 | SIDwinder V1.23 Enhanced!! | PCH / KGB'92, Unreal | 2011 | Third-party fork; live piano |
| 8708 | Cubic Player (The Third Album) | Natural Beat | 1998 | Taki's SID player demo, 13 tracks |
| 253271 | SIDwinder V0.2 Preview | Genesis Project | 2025 | DIFFERENT TOOL (Raistlin) |

---

## sidid Detection Signature

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

Single pattern — no version split between V01.22 and V01.23.  Covers the
player's core voice-dispatch loop (speed-counter check + DEY + JMP across voices
+ sector-instruction comparison).

---

## Sources Found

| Source | URL | Quality |
|--------|-----|---------|
| Official V01.23 source archive (Zimmers) | `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip` | Primary |
| Plus/4 World page (full keyboard + format doc) | `https://plus4world.powweb.com/software/SIDwinder_V01_23` | Primary |
| CSDb release V01.22 | `https://csdb.dk/release/?id=66494` | Primary |
| CSDb release V01.23 | `https://csdb.dk/release/?id=101758` | Primary |
| CSDb SIDwinder Enhanced!! | `https://csdb.dk/release/?id=99574` | Secondary |
| Planet Emulation D64 | `https://www.planetemu.net/rom/commodore-c64-applications-d64/sidwinder-v01-23-1994-natural-beat` | Secondary |
| sidid.cfg signature | `https://github.com/cadaver/sidid/blob/master/sidid.cfg` | Primary |
| HVSC Musicians.txt | local `hvsc84/DOCUMENTS/Musicians.txt` | Primary |
| Modern Raistlin tool | `https://sidwinder.netlify.app/` | Not relevant to Taki's engine |

---

## Gaps Remaining

1. **Disassembly of a packed binary** — we have the source but no annotated
   disassembly of an actual HVSC binary.  A packed binary at a concrete load
   address would let us verify address offsets precisely.  Suggestion: run `py65`
   or `siddump --pc-trace` against a Taki or Factor6 SID to confirm dispatch.

2. **SIDwinder Enhanced!! (PCH, 2011, CSDb #99574)** — a third-party fork with
   a live-piano keyboard mode.  The player may be a compatible superset (same
   data format?) or may diverge.  HVSC classifies 5 PCH SIDs as SidWinder; if
   those are Enhanced!! variants, the format should be identical.  Confirm by
   running sidid on the PCH SIDs.

3. **Factor6 / Eclipse adoption path** — Factor6 (Czech) has the most SidWinder
   SIDs (38); Eclipse's most recent SidWinder SIDs are dated 2025.  Neither is
   Hungarian.  Worth confirming no regional variant or extended version was
   distributed outside Hungary.

4. **Scene magazine coverage** — No coverage of SidWinder was found in Vandalism
   News, C=Hacking, Domination, or Recoil scene magazines.  Taki's package was
   small-circulation and primarily Hungarian/Central-European; the tool did not
   receive wide scene-press coverage.

5. **`PLAY0122.ASM` vs `PLAYER.ASM` differences** — the archive includes the
   original V01.22 player source (`PRE_0123/0122/PLAY0122.ASM`) alongside the
   V01.23 version.  A diff would confirm whether the packed format changed
   between versions (the SUMMARY says the data format was not changed, only the
   identity field — but worth verifying against the ASM).

---

## Leads to Follow

- Fetch and mount CSDb D64 download #66494 for V01.22 binary + any included docs.
- Diff `PRE_0123/0122/PLAY0122.ASM` against `SRC/PLAYER.ASM` to enumerate V01.23
  player changes precisely.
- Run `sidid` on all 117 HVSC SidWinder SIDs to confirm all match the single
  pattern (no version split or variant).
- Fetch CSDb #99574 (Enhanced!! by PCH) and check if the player binary matches
  the same sidid signature.
- Check `c64.rulez.org/pub/c64/Tools/Music/Editor/` for any additional SIDwinder
  releases not on Zimmers.
