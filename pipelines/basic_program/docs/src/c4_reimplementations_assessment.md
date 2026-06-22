---
source_url: https://github.com/mist64/cbmbasic + https://vice-emu.sourceforge.io + research 2026-06-22
fetch_date: 2026-06-22
author: SIDfinity research agent (C4 cluster)
reliability: secondary (README read; source code not fully audited)
---

# C4: Existing C64 BASIC Reimplementations — Bit-Exactness Assessment

## cbmbasic (Michael Steil / mist64)

**URL:** https://github.com/mist64/cbmbasic
**License:** BSD 2-clause
**Nature:** Native C code reimplementation of C64 BASIC V2.  NOT a 6502
emulator — the BASIC interpreter logic is in C.  The C code is
LLVM-generated from the 6502 machine code and then hand-cleaned.
**Compatibility claim:** "100% compatible version of Commodore's version
of Microsoft BASIC 6502."

### What it handles

- All BASIC V2 arithmetic (FADD/FSUB/FMUL/FDIV reimplemented in C)
- The full floating-point interpreter pipeline
- PRINT, POKE, PEEK (for RAM/ROM addresses)
- SIN, COS, ATN, EXP, LOG, SQR, RND

### What it does NOT handle (critical for SIDfinity)

- **CIA timers**: TI variable returns 0 or synthetic values; RND(0) fails
  unless patched (see Lars Gregori's "how I fixed RND" blog post — the
  fix returns `time()` bits for the CIA addresses).
- **SID registers**: PEEK($D400+) returns 0 or undefined.
- **Unmapped I/O**: PEEK($DF78) behaviour is undefined / returns 0 rather
  than the real floating-bus value.
- **VIC-II bus state**: no video chip simulation.

### Multiply bug fidelity

UNCONFIRMED from README alone.  Because cbmbasic is described as
LLVM-translated from actual 6502 ROM code, it may inherit the bug
through the translation.  Requires source-code audit of the multiply
path (search for `mltply` or the equivalent C translation of $BA59).

### Verdict for SIDfinity

Suitable for DATA/READ table-driven BASIC tunes (no FP math, no hardware
PEEK).  NOT sufficient for:
- Tunes using RND(0) or RND(-TI)
- Tunes PEEKing SID registers or unmapped I/O
- Tunes with timing-sensitive TI usage

---

## VICE (Versatile Commodore Emulator)

**URL:** https://vice-emu.sourceforge.io
**License:** GPL
**Nature:** Full-system emulator — 6502 CPU + CIA + VIC-II + SID + all
memory banking.  Runs the original C64 ROM directly; does NOT
reimplement BASIC V2 in a higher-level language.

### Bit-exactness

VICE emulates the CIA timers, TOD clock, VIC-II bus arbitration, and
SID chip.  For BASIC tunes:
- RND(0): reads emulated CIA timer registers → same sequence on every
  run IF the timing model is deterministic (depends on cycle-exact
  emulation mode).
- PEEK($DF78): returns emulated open-bus value (implementation-specific;
  typically last VIC fetch byte).
- TI: updated on emulated 50/60 Hz IRQ cycle.

VICE is the de facto standard for "what the C64 really does" and is the
basis for most HVSC recording captures.

### Verdict for SIDfinity ground truth

VICE (or libsidplayfp with ROMs) is the safest ground-truth source.
siddump already uses libsidplayfp; adding `setRoms()` and `--force-rsid`
would give correct captures.

---

## The "lift the FP routines" approach

For tunes where the only FP operations are deterministic (FDIV, FADD,
RND(positive), SIN/COS), a portable C reimplementation of the 5-byte FP
format is feasible and already partially exists in:

1. **cbmbasic** — for pure-interpreter semantics
2. **The ROMs themselves** — can be included verbatim as a C byte array
   and executed under a simple 6502 emulator (minimal subset: just
   the math routines)
3. **py65 / perfect6502** — 6502 emulators that could run JUST the FP
   routines with stubbed I/O (suitable for unit-testing the FP math)

The key challenge is the MLTPLY bug: the carry-flag state at the point of
the bug depends on the exact execution history within that multiply call.
A C reimplementation must match it, which means either:
- Translating the bug faithfully from 6502 to C (as cbmbasic presumably
  does), OR
- Running the actual ROM bytes in a 6502 emulator

For the SIDfinity use case (exact register write log), the simplest and
most reliable approach remains: patch siddump to call setRoms(), run the
BASIC program under libsidplayfp, capture the write log.
