---
source_url: https://github.com/ice00/jc64
         + https://raw.githubusercontent.com/ice00/jc64/master/src/sw_emulator/software/SidId.java
         + https://raw.githubusercontent.com/ice00/jc64/master/src/sw_emulator/software/machine/C64SidDasm.java
         + https://www.lemon64.com/forum/viewtopic.php?t=83673  (JC64dis 2.8 release)
fetched_via: WebFetch
fetch_date: 2026-05-25
author: Ice Team (ice00); Italian C64 community
content_date: 2003 — present (active, latest release v3.x)
reliability: primary (source code)
---

# JC64dis as a Companion reverse-engineering tool

## What JC64dis is

Java GUI disassembler for PRG/SID/MUS/CRT/VSF/MPR/PRG files across C64, VIC-20,
C128, Plus4, and Atari (6502 family). Iterative — you label, it improves the
disassembly. Built-in SID emulator (own implementation under
`src/sw_emulator/software/sidid/` — confusingly named, this is the SID *chip
emulator*, not the player-id scanner). Player identification lives in
`src/sw_emulator/software/SidId.java`.

## How it identifies Companion

Per inspection of `SidId.java`:
- Loads an external `sidid.cfg` at runtime — uses the EXACT same config file
  format as cadaver/sidid (same `ANY (??) / AND / END` tokens).
- `readConfig()` tokenises each line into `SidIdRecord(name, pattern[])`.
- `identifyBuffer()` scans the full file buffer for every loaded pattern.
- No hardcoded Companion knowledge — it inherits whatever signatures the
  shipped `sidid.cfg` contains. Forum demonstrations show JC64dis
  successfully identifies a SID as Companion and then proceeds to
  generic-label disassembly.

## Disassembly side: NOT Companion-aware

`C64SidDasm.java` has special-case labelling only for SID extended-register
addresses ($D41D-$D47F). No Companion-specific labels, no orderlist/freq-table
recognition, no engine-aware comments. The disassembly you get out of JC64dis
for a Companion SID is **player-agnostic 6502 with SID-register comments**
— useful as a starting point but no better than what `da65` or our
`gt2_decompile.py` would give.

## Forum evidence (Lemon64, JC64dis 2.8 thread)

The release threads mention "Rob Hubbard's Companion player" with the sample
file "Synth Sample III" by Rob Hubbard © 1985 Rob Hubbard. The tool ships with
that .sid as a test/demo case showing the Companion ID firing. There's also a
YouTube video titled "JC64Dis (Next Generation Disassembler): get Chris Murray
player" — same workflow applied to Murray's Henry's House.

## Verdict for our pipeline

- JC64dis **is the best off-the-shelf disassembler for a Companion SID**.
  Equivalent quality to our own seed disassembly at
  `docs/hubbard_up_up_and_away_disassembly.s`.
- It does NOT provide a Companion-format parser, byte-layout doc, or codegen
  template. We still have to write those ourselves.
- The Java sources are MIT-equivalent / freely browsable on GitHub for ideas
  about iterative-disassembly UX, but we won't need to translate them.
