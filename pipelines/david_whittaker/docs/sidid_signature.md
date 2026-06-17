---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg; https://raw.githubusercontent.com/WilfredC64/player-id/main/config/sidid.cfg; local: hvsc84/MUSICIANS/W/Whittaker_David/ (binary analysis)
fetched_via: direct (cadaver/WilfredC64 fetched 2026-06-17); local read (binary analysis)
fetch_date: 2026-06-17
author: Cadaver (Lasse Öörni); Wilfred Bos; iAN CooG; local analysis by this session
content_date: cadaver/sidid config as of 2026-06-17; WilfredC64/player-id as of 2026-06-17
reliability: primary
---

# SIDId Signatures — David Whittaker

## Summary

The `David_Whittaker` player is identified by a **single block of 5 alternative
patterns** in all major sidid databases (cadaver/sidid, WilfredC64/player-id,
DeepSID bundled sidid). There is NO sub-entry (no `David_Whittaker_v2` /
`David_Whittaker_early` etc.) — all variants are folded into one label.

This is consistent with Prg2Sid 1.20 (HVSC Update 81, June 2024) adding
"Whittaker (2 variants)" — the two variants share enough code structure to be
identified by the same pattern set, but differ in their PSID header layout (init/play
addresses, init-code structure) enough that Prg2Sid needs two identification paths.

## Canonical Signature Block

Identical across cadaver/sidid and WilfredC64/player-id (as of 2026-06-17):

```
David_Whittaker
CE ?? ?? 8E 04 D4 E8 8E 04 D4
8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4
AD ?? ?? 85 ?? AD ?? ?? 85 ?? A0 00 B1 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? 60
B1 ?? F0 AND C8 B1 AND A9 ?? 8D 04 D4 A9 ?? 8D 04 D4 AND 69 02 85
8D 08 D4 B9 ?? ?? 8D 0E D4 B9 ?? ?? 8D 0F D4 A9 ?? 8D 04 D4
```

Format: `??` = wildcard byte; `AND`/`&&` = logical-AND mask (cadaver uses `AND`,
WilfredC64 uses `&&`); `END` terminates each pattern in cadaver's format
(absent in WilfredC64's newer format which uses blank-line separation).

### Pattern P1 — dominant variant (DEC+STX gate-toggle)
```
CE ?? ?? 8E 04 D4 E8 8E 04 D4
```
Decoded: `DEC abs` (decrement a duration/tempo counter) followed by
`STX $D404; INX; STX $D404` — the gate-off / gate-on double-write via X register.
This is the **most common pattern** — present in 79 of the 103 Whittaker_David
folder SIDs plus the cross-folder detections. The `DEC` operates on a per-voice
note-duration countdown byte.

### Pattern P2 — alternate variant (STA SR + LDX gate-toggle)
```
8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4
```
Decoded: `STA $D406` (write V1 sustain/release) then `LDX abs; STX $D404; INX;
STX $D404` — same INX double-write gate toggle but anchored to the SR write
preceding it. Present in **10 SIDs** (see list below). Both P1 and P2 end in the
same `8E 04 D4 E8 8E 04 D4` idiom — they describe the same gate-toggle mechanism
in two different calling contexts.

### Pattern P3 — early / init-copy variant
```
AD ?? ?? 85 ?? AD ?? ?? 85 ?? A0 00 B1 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? 60
```
Decoded: Two `LDA abs / STA zp` pairs (loading voice data pointers into zero page),
then `LDY #$00; LDA (zp),Y; STA abs; INY; LDA (zp),Y; STA abs; RTS`.
This is the **voice-pointer loader subroutine** (init path). Present in 4 SIDs:
`David_Music_Demo_2`, `David_Music_Demo_3`, `Max_Headroom_preview`, `Elektra_Glide`.
The first two are Whittaker's own demo tunes (1984-1986 era) — this pattern
characterises the earliest known driver version.

### Pattern P4 — high false-positive risk
```
B1 ?? F0 AND C8 B1 AND A9 ?? 8D 04 D4 A9 ?? 8D 04 D4 AND 69 02 85
```
The `AND` masks make this an overlapping multi-condition check: `LDA (zp),Y;
BEQ ...; INY; LDA (zp),Y; [conditional]; LDA #imm; STA $D404; LDA #imm;
STA $D404; [conditional]; ADC #$02; STA zp`. This is the **pattern-data reader
with immediate gate-toggle** path, present in 26 SIDs (many overlapping with P1).
P4 is broad — the 3-byte `B1 ?? F0` anchor is common in many 6502 routines.
Use P1/P2/P3/P5 for primary identification; treat P4 as a corroborating signal
only.

### Pattern P5 — tiny/special player variant
```
8D 08 D4 B9 ?? ?? 8D 0E D4 B9 ?? ?? 8D 0F D4 A9 ?? 8D 04 D4
```
Decoded: `STA $D408` (V2 freq hi), `LDA abs,Y` (freq table), `STA $D40E`
(V3 freq lo), `LDA abs,Y`, `STA $D40F` (V3 freq hi), `LDA #imm; STA $D404`
(V1 ctrl). This is the **3-voice frequency update loop**. Present in only
3 SIDs: `Humphrey`, `Mayhem`, `Pandoras_Box`. These are all small SIDs
(484, 394, 508 bytes respectively) — likely stripped-down versions of the
Whittaker engine, possibly by a different programmer using the same data format.

## Corpus hit counts (Whittaker_David folder, 103 SIDs)

| Pattern | Whittaker_David hits | Notes |
|---------|---------------------|-------|
| P1 (DEC+STX) | 86 | 79 from original count + 7 false-negatives in DB |
| P2 (STX+STX) | 10 | distinct sub-variant |
| P3 (early) | 4 | early demo era |
| P5 (tiny) | 3 | stripped-down variant |
| P4 (gate-imm) | ~26 | broad overlap with P1; high false-positive risk |
| NONE | 1 | Exorcist.sid only |

Note: 7 of the 8 "NULL engine" SIDs in hvsc84.csv match P1 in direct binary search —
they are false-negatives from the DB's sidid run, not genuine detection failures.
The DB should be refreshed with the current sidid binary.

## P2 variant SIDs (10 SIDs)

SIDs where P2 is the primary (only or first) match:

| SID | Notes |
|-----|-------|
| `BMX_Simulator.sid` | load $E000, play $E0AA |
| `Chicken_Farm.sid` | load $603C |
| `Knight_Games.sid` | load $6FF0, 9 subtunes — large multi-song |
| `Max_Headroom.sid` | load $1F00, 18 subtunes — large multi-song |
| `Max_Headroom_preview_v2.sid` | load $8000 |
| `Miami_Dice.sid` | load $14B4 |
| `Model.sid` | load $0846 — dmx87 has a CSDb release for this |
| `Red_Max.sid` | load $E000, 3 subtunes |
| `Split_Personalities.sid` | load $07FC |
| `Elektra_Glide.sid` | load $C000, also matches P3 |

The P2 variant's write sequence is:
`STA $D401 (V1 freq hi) → STA temp → STA $D402 (V1 pw lo) → STA $D403 (V1 pw hi) →
STA $D405 (V1 AD) → STA $D406 (V1 SR) → LDX abs → STX $D404 → INX → STX $D404`

This is a full 6-register voice-update block. The P1 variant uses `DEC abs` +
`STX $D404` gate-toggle in a shorter context. Both are architectural variants of
the same Whittaker engine — the data format is likely compatible.

## P3 (early) variant SIDs (4 SIDs)

| SID | Notes |
|-----|-------|
| `David_Music_Demo_2.sid` | load $081B — Whittaker's own demo, 1984 era |
| `David_Music_Demo_3.sid` | load $0F00 — Whittaker's own demo |
| `Max_Headroom_preview.sid` | load $081B — early Max Headroom demo |
| `Elektra_Glide.sid` | load $C000, also matches P2 |

`David_Music_Demo_2` and `David_Music_Demo_3` are the smallest non-P5 SIDs
(1594 and 1593 bytes respectively) and represent the earliest known version
of the Whittaker driver. The init-path sub (P3) is a shared utility subroutine
for loading voice pointers — it may be present in other variants too but only
becomes the identifying pattern when P1/P2 are absent.

## P5 (tiny) variant SIDs (3 SIDs)

| SID | Size | Notes |
|-----|------|-------|
| `Humphrey.sid` | 484 bytes | 1 subtune, load $3F00 |
| `Mayhem.sid` | 394 bytes | 1 subtune, load $5B20 |
| `Pandoras_Box.sid` | 508 bytes | 1 subtune, load $0E00 |

These are extremely small SIDs with only 1 subtune each. They likely use a
stripped-down version of the Whittaker data format with a minimal player.
The P5 pattern `STA $D408; LDA abs,Y; STA $D40E; LDA abs,Y; STA $D40F;
LDA #imm; STA $D404` is the 3-voice frequency update core. These may be
from a different programmer using Whittaker's data encoding.

## True detection miss — Exorcist.sid

**Exorcist.sid** (load $4F00, init $5408, play $5448, 1471 bytes) does NOT match
any of the 5 sidid patterns. Binary analysis:

- The first $5×8 = 1288 bytes are **song data** (frequency-pair arrays, two
  bytes per note), not code — the data starts at $4F00.
- The player code begins at $5408 (offset 1288 in the file).
- The player writes only to V2 ($D40B gate: `A9 20 8D 0B D4 / A9 21 8D 0B D4`)
  and V3 ($D412 gate: `A9 20 8D 12 D4 / A9 21 8D 12 D4`).
- **No $D404 writes at all** — V1 is silent or handled elsewhere.
- The init routine uses `LDA (zp),Y` indexed reads but in a different structural
  context than P3.

Conclusion: Exorcist.sid is a **special-purpose player** for the Exorcist game —
possibly written by a different programmer, or an extremely early Whittaker engine
predating the P1/P2/P3 idioms. It uses a V2+V3 only architecture (V1 either
unused or driven by NMI/interrupts not captured in this rip).

## DeepSID jsSID workaround for Whittaker

DeepSID's JavaScript SID emulator (`js/handlers/jsSID-modified.js`) has a
**named workaround specifically for the Whittaker player**:

```javascript
// Line 709 (jsSID-modified.js):
if(addr==0xD404 && !(memory[0xD404]&1)) ADSRstate[0]&=0x3E;
if(addr==0xD40B && !(memory[0xD40B]&1)) ADSRstate[1]&=0x3E;
if(addr==0xD412 && !(memory[0xD412]&1)) ADSRstate[2]&=0x3E;
//Whittaker player workaround
```

This fires when any voice control register ($D404, $D40B, $D412) is written with
**gate bit = 0** (gate-off). It clears the ADSR state's attack/decay-sustain bits
(`0x3E` = clear bits 1-5). The comment on line 922:
```javascript
//falling edge (with Whittaker workaround this never happens, but should be here)
```
confirms this suppresses the normal "falling edge" ADSR handling. The effect:
Whittaker's gate-off writes are treated as ADSR-state clears rather than
triggering normal release. This is needed because Whittaker writes
waveform=$20 (gate-off, pulse) immediately before waveform=$21 (gate-on, pulse)
— the intended behaviour is crisp note re-trigger, not a full ADSR release.

**For the USF extractor and composer:** this means Whittaker's note trigger
sequence is intentionally avoiding the SID's ADSR release phase. The gate-off
write is a "reset" not a "release" — this is important for the instrument model.

## Variant taxonomy summary

From binary analysis, there are effectively **3-4 structural variants** within
the single `David_Whittaker` label:

| Variant | Identifying pattern | SID count | Era/notes |
|---------|--------------------|-----------|----|
| Main (P1) | `CE ?? ?? 8E 04 D4 E8 8E 04 D4` | ~86 | 1985–1990+, dominant form |
| Alt-reg (P2) | `8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4` | 10 | Different register-write ordering |
| Early (P3) | init-path loader subroutine | 4 | 1984–1986 demos |
| Tiny (P5) | freq-update loop, 3-voice | 3 | <500 bytes, stripped |
| Unknown | none | 1 (Exorcist) | V2/V3 only, different architecture |

The P1 and P2 variants share the same `INX; STX $D404` gate-toggle idiom —
their musical data format is likely the same; only the play() register-write
ordering differs. P3 (early demos) likely shares the same data format but
may have a simpler effect set. P5 (tiny) is ambiguous.

## Cross-family detections

Beyond the `Whittaker_David` folder, 15 SIDs in other folders are tagged
`David_Whittaker` in the DB:

| Path | Notes |
|------|-------|
| `GAMES/A-F/Baal.sid` | |
| `GAMES/M-R/Plaque_Man.sid` | |
| `GAMES/S-Z/Track_and_Field_1987.sid` | |
| `MUSICIANS/B/Beben_Wally/Come_What_May.sid` | Wally Beben used Whittaker's driver |
| `MUSICIANS/B/Beben_Wally/Passing_Phases.sid` | |
| `MUSICIANS/B/Beben_Wally/Skindeep.sid` | |
| `MUSICIANS/B/Beben_Wally/Tigers_Eye.sid` | |
| `MUSICIANS/B/Bjerregaard_Johannes/Vikings_loader.sid` | |
| `MUSICIANS/B/Brooke_Jason/Tiger_Road.sid` | Jason Brooke (original driver author?) used Whittaker format |
| `MUSICIANS/F/Foreman_Gary/Pluto.sid` | Gary Foreman used Whittaker's driver |
| `MUSICIANS/F/Foreman_Gary/Run_the_World.sid` | |
| `MUSICIANS/M/Mahoney/Lazy_Jones_remix.sid` | |
| `MUSICIANS/N/Scales_Neil/NWCUG_Demo.sid` | |
| `MUSICIANS/W/Williams_Tony/Sector_90.sid` | Tony Williams used Whittaker's driver |
| `MUSICIANS/W/Williams_Tony/Star_Wars_Droids.sid` | |

**Notable:** `MUSICIANS/B/Brooke_Jason/Tiger_Road.sid` — Jason Brooke is
mentioned in `research.md` as the person whose code Whittaker's driver was
"based on". Tiger_Road uses the P1 variant, suggesting the two composers shared
the driver code (or Brooke used Whittaker's driver for his own tunes).

## Leads to follow

- **Refresh hvsc84.csv** with current sidid binary — 7 false-negatives present
  (`python3 tools/build_sid_db.py` after verifying sidid binary is current)
- **cadaver/sidid GitHub** — check if any Whittaker sub-variant was ever discussed
  in issues/commits: https://github.com/cadaver/sidid/issues
- **WilfredC64/player-id** — check for any Whittaker-specific test cases in
  `src/tests/`: https://github.com/WilfredC64/player-id/tree/main/src/tests
- **Exorcist.sid** driver source — needs a separate disassembly; it may be a
  completely different player that HVSC has mis-attributed to Whittaker, OR
  it may be an ultra-early Whittaker variant predating the P1/P2 family
- **Tiger_Road / Jason Brooke connection** — confirms driver was shared between
  Whittaker and Brooke; re-read `research.md`'s "driver based on code by Jason
  Brooke" note and trace which one wrote the original
- **Prg2Sid 1.20 source** (CSDb 238521) — download and read to understand exactly
  what the 2 "variants" are that Prg2Sid identifies and patches
