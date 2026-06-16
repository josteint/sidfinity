---
source_url: https://csdb.dk/release/?id=10744 (downloads 162063=D64, 162077=T64)
fetched_via: direct (curl, via csdb.dk/storage redirect)
fetch_date: 2026-06-16
author: Markus Schneider (MS/Diflex) + Nic + ADT; docs by SMC; release by Mnemonic Designs
content_date: 1989
reliability: primary (actual editor disk image)
---

# CSDb #10744 "The Parsec Music Editor V5.1" — stashed artifacts

**This is the ground-truth source for the `lords_of_sonics` (LordsOfSonics/MS)
format.** The driver Markus Schneider wrote in 1988 for Jens Blidon was
publicly released as this editor. Disassembling its player stub + reading its
in-editor data layout is the authoritative path to a complete format spec —
that work belongs to the MIGRATION phase, not this gather sweep. The disk
images are stored here so the migration doesn't have to re-fetch them.

## `Parsec_5_1-Mnemonic_Designs.d64` (CSDb file 162063, standard 35-track D64)
Disk name `IMAGE`. Directory:
```
PRG 64 blk  (M)PARSEC V5.1     <- the editor + embedded player (~16 KB)
```
The migration target: disassemble the player routine inside this PRG and read
how the editor lays out instruments / wavetables / orderlists / sequences in
memory. Cross-check against the in-corpus sidid signatures (`src/sidid_signatures.txt`)
and the PSID-header survey in `../hvsc_findings.md`.

## `Parsec_4_info.t64` (CSDb file 162077, T64 tape image)
Tape name `IMAGETAPE`. One file:
```
PRG $0801-$23EA  PARSEC 4.0+ INFO   (7145 bytes)
```
An info/about program for Parsec v4.0+. Its text is **crunched inside the ML**
(only the static string `2071 SMC.` is recoverable without running it — SMC =
Sanke Michael Choe, the Parsec docs author). Reading the actual info text
requires running the viewer in an emulator (migration phase). Not a static
format spec, but may contain usage/version notes once displayed.

## Status
Both artifacts acquired and verified (directory parsed). NOT disassembled —
RE is deferred to the migration phase per the research-player gather scope.
