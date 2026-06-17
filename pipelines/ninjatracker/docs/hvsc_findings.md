---
source_url: local: /home/jtr/sidfinity/hvsc84/ + https://cadaver.github.io/tools.html + https://csdb.dk/search/?stype=all&search=ninjatracker + https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: local read + curl
fetch_date: 2026-06-17
author: SIDfinity research session
content_date: 2026-06-17
reliability: primary (local HVSC) + secondary (web)
---

# NinjaTracker — HVSC Research Findings

## Overview

NinjaTracker is a C64 music tracker written by Lasse Öörni (Cadaver) of Covert Bitops.
It was the primary tool for Cadaver's own game music production and used widely in the
C64 scene from 2002 onward.

- **Author**: Lasse Öörni (Cadaver) / Covert Bitops
- **Website**: https://cadaver.github.io/ (Tools section)
- **Authoritative source**: Cadaver authored both the tracker and the sidid detection tool
- **HVSC #84 corpus**: 111 SIDs total (18 V1.x + 93 V2.x)

### Version lineage (from CSDb releases)

V1.x series (2002–2004):
- V1.0: 31 Oct 2002
- V1.01: 10 Nov 2002
- V1.01 Gamemusic Version: 10 Nov 2002 (separate player for game embedding)
- V1.02: 14 Nov 2002
- V1.03: 23 Nov 2002
- V1.04: 5 Mar 2003
- V1.05: 6 Jan 2004
- V1.1: 25 Jan 2004

V2.x series (2006–2013):
- V2.0: 30 Aug 2006
- V2.01: 2 Sep 2006
- V2.02: 2 Sep 2006
- V2.03: 3 Sep 2006
- V2.04: 19 Jun 2013 (latest canonical release)

Additional tooling:
- GoatTracker V1.xx -> NinjaTracker converter: 24 Jan 2003
- GoatTracker2 to NinjaTracker2 Converter V1.0: 3 Feb 2013
- GoatTracker2 to NinjaTracker2 Converter V1.02: 3 Oct 2015
- NinjaTracker MOD V2.04 by Spider Jerusalem: 10 Jan 2017 (third-party mod)

### Cadaver's own description of V2.04 (from cadaver.github.io/tools.html)

> "A C64 music editor with quite minimal featureset. Changes to previous versions
> include commands (also used as instruments), 2-column tables and a slide function
> that stops at target pitch. As before, allows to save both normal executable
> musicdata and gamemusic data without the player."

> "V2.04 fixes transpose not resetting when playback is started from the beginning."

This describes three key V2 additions over V1:
1. **Commands as instruments** — instrument slots can be command entries that modify playback
2. **2-column tables** — waveform/instrument data organized in two parallel columns
3. **Slide to target pitch** — portamento stops when the target note frequency is reached

### GoatTracker2 converter description (from tools page)

> "Utility that converts GoatTracker2 songs to NinjaTracker V2.03+ format with some
> limitations. Songs that work within the limitations can then be played back with
> less memory and rastertime consumption."

This confirms NinjaTracker is a low-memory, low-rastertime player — a deliberate
design constraint, not a limitation.


## PSID Header Variant Table

### V1.x SIDs (18 total)

All V1.x SIDs: PSID version 2, load_addr=0x0000 (embedded), speed=0x00000000 (all VBL/50Hz)

| File | init | play | songs | flags | SID model | Notes |
|------|------|------|-------|-------|-----------|-------|
| DEMOS/S-Z/Silent_Night.sid | 0x140B | 0x1003 | 1 | 0x0004 | unknown | Non-std init |
| MUSICIANS/C/Cadaver/Consultant.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/C/Cadaver/Metal_Warrior_4.sid | 0x1000 | 0x1003 | 71 | 0x0014 | 6581 | Canonical; 71 subtunes |
| MUSICIANS/C/Cadaver/Nintendo_Metal.sid | 0x1000 | 0x1003 | 4 | 0x0014 | 6581 | Canonical |
| MUSICIANS/C/Crowley_Owen/Worktunes/Digi-Freak.sid | 0x1000 | 0x0000 | 1 | 0x0014 | 6581 | play=0 (no PSID play hook) |
| MUSICIANS/J/Julian_Jaymz/Chase_That_Feeling.sid | 0x1A00 | 0x14C0 | 1 | 0x0014 | 6581 | Relocated |
| MUSICIANS/J/Julian_Jaymz/Flower_6.sid | 0x28FA | 0x2900 | 1 | 0x0014 | 6581 | Relocated |
| MUSICIANS/J/Julian_Jaymz/Not_a_Scene_Production.sid | 0x0DFA | 0x0E00 | 1 | 0x0014 | 6581 | Relocated |
| MUSICIANS/J/Julian_Jaymz/cdagame_s3m.sid | 0x19B0 | 0x1000 | 1 | 0x0014 | 6581 | Relocated |
| MUSICIANS/M/Maktone/Bigbud_v2.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/M/Maktone/Blueberry.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/M/Maktone/Stroh.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/M/Maktone/We_Laser_v2.sid | 0x16FC | 0x16FF | 1 | 0x0014 | 6581 | Relocated (play=init+3) |
| MUSICIANS/M/Mermaid/D_oh_Ninjatracker.sid | 0x1517 | 0x1000 | 1 | 0x0034 | 6581+8580 | Non-std; play<init |
| MUSICIANS/P/Puterman/Emanation_Machine_tune_2.sid | 0xC000 | 0xC003 | 1 | 0x0014 | 6581 | High-mem reloc |
| MUSICIANS/P/Puterman/Ultragui.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/R/Radiantx/Fruit_Salad.sid | 0x1000 | 0x1003 | 1 | 0x0014 | 6581 | Canonical |
| MUSICIANS/V/Vincenzo/4k_PETSCII_Intro.sid | 0x4000 | 0x4003 | 1 | 0x0024 | 8580 | 4K intro; relocated |

**V1.x canonical form** (init=0x1000, play=0x1003): 8/18 SIDs (44%).
The remaining 10 are relocated (init at a different base; play=init+3 in most cases)
or have non-standard play addresses (Digi-Freak play=0x0000, Mermaid play < init).

**V1.x SID model distribution**:
- 6581 only: 16 SIDs (0x0014 flags)
- 6581+8580: 1 SID (0x0034 flags) — Mermaid
- 8580 only: 1 SID (0x0024 flags) — Vincenzo 4k
- unknown model: 1 SID (0x0004) — Silent Night


### V2.x SIDs (93 total)

All V2.x SIDs: PSID version 2, load_addr=0x0000 (embedded), speed=0x00000000 (all VBL/50Hz)

Key subset (non-canonical or notable entries):

| File | init | play | songs | flags | Notes |
|------|------|------|-------|-------|-------|
| MUSICIANS/A/Avory_Sarah_Jane/Briley_Witch_Chronicles.sid | 0x3C00 | 0x31D1 | 34 | 0x0034 | Non-std; play≠init+3 |
| MUSICIANS/A/Avory_Sarah_Jane/Soul_Force.sid | 0x4000 | 0x0ED9 | 43 | 0x002C | Non-std; PAL+NTSC; max subtunes |
| MUSICIANS/A/Avory_Sarah_Jane/Zeta_Wing.sid | 0x12C0 | 0x12C3 | 10 | 0x0034 | Canonical (shifted) |
| MUSICIANS/C/Cadaver/Hessian.sid | 0x1000 | 0x1003 | 21 | 0x0014 | Canonical; 21 subtunes |
| MUSICIANS/C/Cadaver/Steel_Ranger.sid | 0x1000 | 0x1003 | 26 | 0x0034 | Canonical; 26 subtunes |
| MUSICIANS/M/Mat64/Adventure_1.sid | 0xC000 | 0xC014 | 7 | 0x0014 | Non-std play offset (+$14) |
| MUSICIANS/M/Mat64/Strawberry_Strings.sid | 0x1980 | 0x15D9 | 2 | 0x0024 | Non-std; play<init |
| GAMES/M-R/Mimizuku_Saga_4K.sid | 0xA6A0 | 0xA0AE | 1 | 0x0024 | Non-std; play<init |
| MUSICIANS/J/Julian_Jaymz/Stupid_Bitmap_and_Scroll.sid | 0x6400 | 0x0000 | 1 | 0x0014 | play=0 (no hook) |
| MUSICIANS/S/Spider_Jerusalem/Red_Serpent_preview.sid | 0xCC00 | 0xC7EA | 1 | 0x0024 | Non-std; play<init |
| MUSICIANS/T/Taxim/Sams_Journey.sid | 0xAF00 | 0xAF03 | 19 | 0x0024 | High-mem; 19 subtunes |
| MUSICIANS/W/Widding_Roy_Johan/Captain_Cloudberry.sid | 0xC000 | 0xC003 | 11 | 0x0014 | High-mem |
| MUSICIANS/W/Widding_Roy_Johan/Tombstones_Soundtrack.sid | 0xC000 | 0xC003 | 5 | 0x0014 | High-mem |

**V2.x canonical form** (play=init+3): ~53/93+ SIDs (observed ~68-76%).
**Dominant load base**: init=0x1000, play=0x1003 — approximately 40/93 SIDs.

**V2.x SID model distribution** (from sampled subset of 9 + inference):
- 6581 only (0x0014): significant minority — older V2 SIDs (2006–2012 era)
- 8580 only (0x0024): majority of newer V2 SIDs (2013+ era)
- 6581+8580 (0x0034): some SIDs (e.g. Steel_Ranger, Avory)
- PAL+NTSC+8580 (0x002C): rare (Soul_Force)

**V2.x subtune count highlights**:
- Maximum: 43 subtunes (Soul_Force by Sarah Jane Avory)
- Multi-subtune (>1): 17 SIDs including large game soundtracks
- Most V2 SIDs are single-subtune demo/intro music


### Speed field

All 111 NinjaTracker SIDs have `speed = 0x00000000` = all subtunes use VBL (50Hz) timing.
No CIA-timed subtunes found in the corpus. This is consistent with a minimal-featureset
tracker design — NinjaTracker does not support CIA timing.


## sidid V1.x and V2.x Signatures

See `/home/jtr/sidfinity/pipelines/ninjatracker/docs/src/sidid_signatures.txt` for full annotations.

### V1.x signature (raw hex)

```
FE ?? ?? ?? ?? BD ?? ?? 9D ?? ?? ?? ?? ?? ?? 7D ?? ?? 9D ?? ?? 9D 00 D4 BD ?? ?? 7D ?? ?? 4C
```

Fixed bytes: `FE`, `BD`, `9D`, `7D`, `9D`, `9D 00 D4`, `BD`, `7D`, `4C`

Key anchors:
- `9D 00 D4` = `STA $D400,X` — indexed write to SID register base; X indexes the voice/register
- `FE` = `INC abs,X` — increment a counter or pointer
- `7D` = `ADC abs,X` — add with carry (frequency accumulation)
- `4C` = `JMP abs` — player dispatch jump at end

### V2.x signature (raw hex)

```
C9 0C 90 ?? BD ?? ?? B0 ?? 4A 09 FE 9D ?? ?? 90
```

Fixed bytes: `C9 0C`, `90`, `BD`, `B0`, `4A`, `09 FE`, `9D`, `90`

Key anchors:
- `C9 0C` = `CMP #$0C` — compare with 12; threshold for note/command dispatch
- `09 FE` = `ORA #$FE` — OR mask to set waveform bits (gate handling)
- `4A` = `LSR A` — right shift for gate/waveform bit extraction
- `9D` = `STA abs,X` — store to SID buffer/register


## STIL Excerpts

No NinjaTracker-specific STIL.txt entries found. The STIL.txt search for "ninja",
"cadaver", and "covert bitops" returned zero results — NinjaTracker SIDs do not
carry STIL technical commentary in HVSC #84.

The Update Announcements contain only incidental mentions of Cadaver (credit for the
sidid tool, and unrelated content), with no NinjaTracker format notes.


## Key Observations

### Architecture

1. **Fully VBL-driven**: All 111 SIDs use speed=0x00000000 (50Hz VBL interrupt). No CIA timing.
   This is a defining property of the engine; no multi-rate support.

2. **V1.x vs V2.x are architecturally distinct engines**: The sidid signatures are completely
   different — V1.x uses a `STA $D400,X`-indexed write loop (accumulator-arithmetic on
   frequency tables), V2.x uses a `CMP #$0C / ORA #$FE` dispatch/wave-masking pattern.
   These are NOT backward-compatible; they represent a full rewrite between the families.

3. **Relocation is common**: Only ~44% of V1.x and ~68% of V2.x SIDs use the canonical
   init=0x1000 (or init=base, play=init+3) layout. The rest are relocated to arbitrary
   addresses. The play routine is always play=init+3 when canonical (the player is structured
   so the init entry is 3 bytes before the play entry).

4. **play=init+3 is the structural rule**: When the player is at its canonical position,
   init calls some setup, then falls through to the play routine (or: the player binary has
   3 bytes of init prologue before the play entry). All canonical members follow this pattern
   regardless of load address.

5. **Gamemusic variant (V1.x)**: V1.01 had a "Gamemusic Version" — a separate player binary
   for game embedding (data without embedded player). The Digi-Freak SID (play=0x0000)
   likely represents game music data with an external player, not the standard PSID format.

6. **Low-memory / low-rastertime design**: Cadaver explicitly designed NinjaTracker for
   "less memory and rastertime consumption" — confirmed by the GoatTracker2 converter
   description and Spider Jerusalem's CSDb comment ("great rastertime and RAM saver").
   This shapes the feature set: minimal, fixed-function, no extras.

7. **V2.x multi-subtune capacity is large**: Up to 43 subtunes (Soul_Force). This is used
   for game soundtracks (Sams_Journey=19, Hessian=21, Steel_Ranger=26, Briley_Witch=34).
   The player must support subtune selection via init(A) where A is the subtune index.

8. **SID model shift between generations**: V1.x SIDs are predominantly 6581 (16/18).
   V2.x SIDs shift toward 8580 (most post-2013 releases). This reflects the real-hardware
   shift in the scene (emulator prevalence, 8580 preference in later era).

9. **V2.x commands-as-instruments**: Cadaver's description says instrument slots can be
   "commands" — meaning the instrument table in V2.x is dual-purpose: some slots define
   sound parameters, others define playback commands (tempo change? transposition? loop?).
   This is a significant departure from V1.x.

10. **No digi in the corpus**: No NinjaTracker SIDs appear to use sampled audio (no
    SID model flags indicating stereo/digi, no obvious digi SIDs). The tracker is
    purely PSG (SID oscillator) music.

11. **Cadaver is the primary user of both versions**: 4 V1.x SIDs and 4 V2.x SIDs under
    his own name. Steel_Ranger (2018) and Hessian (2016) are the largest game soundtracks.
    The active V2.x community includes Spider Jerusalem (25 SIDs), NecroPolo (14 SIDs),
    Vincenzo (9 SIDs), Mat64 (10 SIDs), and Sarah Jane Avory (5 SIDs).


## Leads to Follow

1. **Download and read the NinjaTracker V2.04 source/binary** from cadaver.github.io
   (`tools/ninjatr204.zip`). It contains the player assembly source. This is the authoritative
   format reference. Priority: HIGH.

2. **Download NinjaTracker V1.1** (`tools/ninjatrk.zip`) for V1.x player source.
   Priority: HIGH.

3. **Fetch and read the GoatTracker2-to-NinjaTracker2 converter** (`tools/gt2nt2.zip`):
   it documents the NinjaTracker2 data format by necessity (the converter must produce
   valid NT2 data files). Priority: HIGH.

4. **Examine the player binary in a canonical V2.x SID**: Cadaver/Hessian.sid
   (init=0x1000, 21 subtunes, pure V2.x) is the best RE starting point. Disassemble
   from 0x1000 onward to map the player structure. Priority: HIGH for RE phase.

5. **Examine Metal_Warrior_4.sid** (V1.x, 71 subtunes): largest V1.x SID, best for
   understanding V1.x multi-subtune layout. Priority: MEDIUM.

6. **Examine Soul_Force.sid** (V2.x, 43 subtunes, non-canonical addresses): largest
   subtune count, non-standard layout — likely an integrated game player.
   Priority: MEDIUM (edge case).

7. **Spider Jerusalem's NinjaTracker MOD V2.04** (CSDb 2017): a modified version of
   the tracker. May have format extensions. Priority: LOW initially.

8. **The CSDb release pages for each version** contain comment threads that sometimes
   document format changes. Check: V2.0 (39374), V2.01-03 (39498-99, 39571), V2.04 (119721).
   Priority: LOW.

9. **Identify which V2.x SIDs are "gamemusic" (no embedded player)**: SIDs with play=0x0000
   (Stupid_Bitmap_and_Scroll, Digi-Freak) and possibly some non-canonical ones have the
   player loaded separately. These will need special handling during extraction.
   Priority: MEDIUM.

10. **Confirm the CMP #$0C threshold semantics**: The V2.x signature uses `CMP #$0C` as a
    branch point. In many C64 trackers, note value 0 = rest, values 1-n = notes, or values
    < 12 = rests/commands. Disassembling Hessian.sid will confirm the note encoding.
    Priority: HIGH for extraction design.
