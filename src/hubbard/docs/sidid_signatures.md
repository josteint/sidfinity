---
source_url: local: /home/jtr/sidfinity/tools/sidid.cfg
fetched_via: local read
fetch_date: 2026-04-11
author: Cadaver (Lasse Oorni)
content_date: unknown
reliability: primary
---
# Rob Hubbard SIDID Signatures

Extracted from `/home/jtr/sidfinity/tools/sidid.cfg`.

SIDID uses byte pattern matching where `??` is a wildcard byte and `AND` skips
to the next matching position. `END` terminates a signature line.

## Rob_Hubbard (main player)

Six signature patterns — any match identifies the main Hubbard player:

```
BD ?? ?? 99 ?? ?? 48 BD ?? ?? 99 ?? ?? 48 BD ?? ?? 48 BD ?? ?? 99 ?? ?? BD ?? ?? 99 END
```
Context: Instrument setup — loads instrument bytes from tables indexed by X,
stores to voice-indexed (Y) workspace, pushes values for later SID writes.

```
2C ?? ?? 30 ?? 70 ?? B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 98 38 END
```
Context: Frequency write — BIT test on status, then writes freq_lo ($D400)
and freq_hi ($D401) from Y-indexed table. `98 38` = TYA; SEC for voice offset calc.

```
AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 ?? 9D ?? ?? FE END
```
Context: Pattern/track sequencer — loads track pointer, fetches next pattern
number, checks for $FF end-of-track marker.

```
99 04 D4 BD ?? ?? 99 02 D4 48 BD ?? ?? 99 03 D4 48 BD ?? ?? 99 05 D4 END
```
Context: SID register writes — control ($D404), pulse_lo ($D402), pulse_hi
($D403), and ADSR ($D405) via voice-offset Y indexing.

```
2C ?? ?? 70 ?? FE ?? ?? AD ?? ?? 10 ?? C8 B1 ?? 10 ?? 9D ?? ?? 4C END
```
Context: Effect processing — BIT/BVS check, increment counter, indirect
load for effect table data, branch on positive/negative for command dispatch.

```
0A 0A 0A AA BD ?? ?? 8D ?? ?? BD ?? ?? 2D ?? ?? 99 04 D4 END
```
Context: Waveform/gate control — ASL x3 (multiply instrument index by 8),
load control byte, AND with gate mask, write to control register ($D404).

## Rob_Hubbard_Digi (sample playback variant)

Sub-signature of Rob_Hubbard — identifies Hubbard player with 4-bit PCM
digi playback (volume register trick):

```
4C ?? ?? 28 F0 AND 4A 4A 4A 4A 4C ?? ?? 29 0F EE ?? ?? D0 03 EE AND 8D 18 D4 AD 0D DD END
```
Context: Digi playback IRQ — PLP, BEQ branch, LSR x4 (high nybble),
AND #$0F (low nybble), write to $D418 (volume/filter), acknowledge CIA IRQ.

## Giulio_Zicchi variant

Sub-signature — Giulio Zicchi's modifications to the Hubbard player:

```
CA 30 03 4C ?? ?? 60 A2 00 8E ?? ?? E8 8E ?? ?? 60 A0 00 END
```

## Bjerregaard variant

Sub-signature — Johannes Bjerregaard's version of the Hubbard player:

```
99 03 D4 AE ?? ?? 9D ?? ?? 68 9D ?? ?? A9 01 9D END
```
Context: Writes freq_hi ($D403 offset), then stores pulled values to
workspace with gate-on flag ($01).

## Paradroid/HubbardEd

Scene editor built on the Hubbard player architecture (by Paradroid):

```
B1 FC 10 1B C9 FF F0 12 C9 FE F0 0A END
```
Context: Note fetch — LDA ($FC),Y; BPL (positive = note); CMP #$FF
(end-of-pattern); CMP #$FE (end-of-track). Uses fixed ZP pointer at $FC.

## Paradroid/Lameplayer

Simplified Paradroid player variant:

```
90 2D C9 E0 B0 09 0A 0A 0A 9D END
```

## Detection Statistics

### Hubbard_Rob/ directory (96 SIDs)
- 82 detect as `Rob_Hubbard` (the core engine, including Digi variant)
- 6 detect as `Jason_Page/RobTracker` (modern RobTracker conversions by Jason Page)
- 5 detect as `SidTracker64` (modern recreations: Casio_Extended, Dont_Step_on_My_Wire, Era_of_Eidolon, Robs_Life, Task_Force)
- 2 detect as `Companion` (early pre-driver works: Commodore_64_Music_Examples, Up_up_and_Away)

### Full HVSC scan (56,032 MUSICIANS + 4,540 GAMES/DEMOS)
- `Bjerregaard` — 65 SIDs (61 in Bjerregaard_Johannes/, 4 elsewhere)
- `Paradroid/Lameplayer` — 21 SIDs (all in Paradroid/)
- `Giulio_Zicchi` — 0 directly (7 SIDs report as Rob_Hubbard, sub-match only)
- `Paradroid/HubbardEd` — 0 SIDs (editor-specific ZP pointer, not in ripped SIDs)

Songs using Hubbard's engine also appear outside his HVSC directory. Confirmed
Hubbard-driver users: Laxity (31 SIDs), Geir Tjelta (~15 SIDs), Giulio Zicchi
(7 SIDs), Adam Gilmore (1), David Green (1). The STIL notes: "People have often
stolen Hubbard's routine causing some tunes to be falsely credited to him."

See `hvsc_variant_survey.md` for the complete breakdown.

## See Also

- `sidid_signatures.txt` — same signatures with detailed 6502 instruction decode comments
- `github_siddecompiler_hubbard_ripper.md` — data detection via 6502 pattern matching (complementary to sidid)
