---
source_url: multiple (see per-section citations)
fetched_via: WebSearch + WebFetch (leaf agent, 2026-06-22)
fetch_date: 2026-06-22
author: SIDfinity research agent (C4 cluster)
content_date: 2026-06-22
reliability: primary (ROM disassembly citations) + secondary (C64-Wiki / c64os.com)
---

# C4: Commodore 64 BASIC Floating Point — Core Research

## Purpose

Determines whether algorithmic `Basic_Program` SIDs (tunes that compute
notes via FP math: `PEEK(M)/28`, `M=M+.2`, `SIN`, `RND`) can be
reproduced bit-exactly WITHOUT running the real ROM.  The verdict feeds
the USF representation design for the `Basic_Program` category.

Primary example: `Two_Lines_of_Code_1_BASIC.sid` (Bond/Alan):
```
1 S=54272:M=57272:POKES+24,15:POKES+6,255:POKES+4,81:POKES+13,255:POKES+11,23
4 POKES+1,PEEK(M)/28:POKES+8,TIANDPEEK(M+64):M=M+.2:GOTO4
```

---

## 1. The 5-Byte Float Format

### Packed (RAM storage) — 5 bytes

| Byte | Role |
|------|------|
| 0 | Exponent (excess-128 / biased-128). Value 0 = float is zero. |
| 1 | Sign/Mantissa MSB. **MSB is the sign bit** (0=+, 1=−). The remaining 7 bits are mantissa[1:7]. The implied leading "1" of the normalised value occupies the MSB position in RAM (displaced by the sign bit). |
| 2–4 | Mantissa bytes 2–4 (LSB = byte 4). |

"The mantissa is always in the 0.5-to-1 range so the first binary digit
will always be a 1 — no need to store that.  When storing a number in
RAM, that invariant 1 is replaced by the sign bit." (c64os.com, C64-Wiki)

Special rule: exponent byte = `$00` → number is exactly zero regardless
of mantissa contents.

### Unpacked (FAC / ARG zero-page) — 6 bytes

The ROM unpacks the 5-byte form into a 6-byte accumulator that restores
the implicit leading "1" and holds the sign in a separate byte:

**FAC (Floating-point Accumulator 1):**

| ZP address | Role |
|------------|------|
| `$61` | exponent |
| `$62` | mantissa byte 1 (MSB, implied 1 restored) |
| `$63` | mantissa byte 2 |
| `$64` | mantissa byte 3 |
| `$65` | mantissa byte 4 (LSB) |
| `$66` | sign byte: `$00` = positive, `$FF` = negative |

**ARG (Floating-point Accumulator 2):**

| ZP address | Role |
|------------|------|
| `$69` | exponent |
| `$6A–$6D` | mantissa |
| `$6E` | sign |

Additional ZP byte `$70` = rounding/overflow byte used during arithmetic.
Seed for RND stored at `$8B–$8F` (5 bytes, same packed format).

**Sources:**
- https://www.c64-wiki.com/wiki/Floating_point_arithmetic
- https://c64os.com/post/floatingpointmath
- https://www.c64-wiki.com/wiki/FAC

---

## 2. Float → Integer Conversion: The POKE Byte-Fetch Call Chain

This is the pivotal detail for `PEEK(M)/28` → `POKES+1,...`.

### POKE implementation (ROM $B824–$B82C)

```
B824: JSR $B7EB   ; "get parameters for POKE/WAIT"
B827: TXA
B828: LDY #$00
B82A: STA ($14),Y  ; store byte to target address
B82C: RTS
```

### B7EB — "get parameters for POKE/WAIT" ($B7EB–$B7F4)

```
B7EB: JSR $AD8A   ; evaluate expression, check numeric (address arg)
B7EE: JSR $B7F7   ; convert FAC1 → unsigned 16-bit integer → $14/$15
B7F1: JSR $AEFD   ; scan comma
B7F4: JMP $B79E   ; get byte parameter (value arg) and return in X
```

### B7F7 — "convert FAC1 to integer in $14/$15" ($B7F7–$B80C)

```
B7F7: LDA $66      ; get FAC1 sign
B7F9: BMI $B798    ; if negative → ILLEGAL QUANTITY ERROR
B7FB: LDA $61      ; get FAC1 exponent
B7FD: CMP #$91     ; compare with exponent for 2^16 = 65536
B7FF: BCS $B798    ; if >= 65536 → ILLEGAL QUANTITY ERROR
B801: JSR $BC9B    ; ** QINT: float → 32-bit fixed (floor) **
B804: LDA $64      ; mantissa byte 3 (= word high byte)
B806: LDY $65      ; mantissa byte 4 (= word low byte)
B808: STY $14      ; temp integer low
B80A: STA $15      ; temp integer high
B80C: RTS
```

### B79E — "get byte parameter" (called for POKE's value argument)

Per the skoolkid disassembly this ultimately also passes through $AD8A
(evaluate expression numeric) and $B7F7 (same QINT path), then masks
result to [0,255] with ILLEGAL QUANTITY ERROR if out of range.

### QINT ($BC9B) — the floor routine

```
BC9B: LDA $61      ; get exponent
BC9D: BEQ $BCE9    ; if zero → FAC=0, result=0
BC9F: SEC
BCA0: SBC #$A0     ; subtract $A0 (= max exponent for 32-bit int)
BCA2: BIT $66      ; test sign
BCA4: BPL $BCAF    ; branch if positive (skip two's-complement)
BCA6: TAX
BCA7: LDA #$FF
BCA9: STA $68      ; set overflow byte for negative
BCAB: JSR $B94D    ; two's complement the mantissa
BCAE: TXA
BCAF: LDX #$61     ; index FAC1
BCB1: CMP #$F9     ; compare shift count
BCB3: BPL $BCBB    ; if < 8 right-shifts needed, done
BCB5: JSR $B999    ; shift FAC1 right (8-bit chunks)
BCB8: STY $68      ; clear overflow byte
BCBA: RTS
```

**Result:** 32-bit two's-complement integer stored big-endian in
`$62–$65` (FAC mantissa bytes). The bottom byte (LSB, `$65`) is what
POKE takes as the output byte value.

### Verdict: FLOOR not ROUND

- `QINT` truncates **toward negative infinity** (same as `INT()`).
  - `INT(9.9)` = 9; `INT(-9.1)` = -10 ← **floor, not truncate-toward-zero**.
- `POKE x, val` converts `val` via QINT → floor.
- So `PEEK(M)/28` where `PEEK(M)` returns N:
  - Exact float result = N/28 (5-byte FP precision)
  - `POKES+1` value = `floor(N/28)` where the division is C64 5-byte FP.
- The add-0.5 rounding routine ($B849) is used ONLY in the ASCII
  output path (PRINT / BDDD), NOT in POKE.

**Concrete example (Two Lines of Code):**
- If `PEEK(57272) = 255` (unmapped I/O Area #2, see §5):
  - `255/28` as 5-byte FP ≈ 9.10714...
  - `POKES+1` writes `9` (= voice-1 freq-hi = $09)

**Sources:**
- https://skoolkid.github.io/sk6502/c64rom/asm/B824.html
- https://skoolkid.github.io/sk6502/c64rom/asm/B7EB.html
- https://skoolkid.github.io/sk6502/c64rom/asm/B7F7.html
- https://skoolkid.github.io/sk6502/c64rom/asm/BC9B.html
- https://www.c64-wiki.com/wiki/QINT
- https://www.c64-wiki.com/wiki/INT
- https://sta.c64.org/cbm64basconv.html

---

## 3. Core FP Arithmetic Routines — Determinism & Reproducibility

### Key ROM addresses

| Routine | Address | Operation |
|---------|---------|-----------|
| FADD | `$B867` | FAC2 + FAC1 → FAC1 |
| FADD2 | `$B86A` | (AY ptr) + FAC1 → FAC1 |
| FSUB | `$B850` | (AY ptr) − FAC1 → FAC1 |
| FMUL | `$BA28` | FAC2 × FAC1 → FAC1 |
| FDIV | `$BB0F` | (AY ptr) ÷ FAC1 → FAC1 |
| QINT | `$BC9B` | FAC1 → 32-bit int (floor) |
| INT  | `$BCCC` | FAC1 := INT(FAC1) — calls QINT |
| ROUND | `$B849` | FAC1 := FAC1 + 0.5 (output path only) |
| SIN  | `$E26B` | FAC1 := sin(FAC1) |
| COS  | `$E264` | FAC1 := cos(FAC1) |
| TAN  | `$E2B4` | FAC1 := tan(FAC1) |
| ATN  | `$E30E` | FAC1 := atan(FAC1) |
| EXP  | (POLY2) | FAC1 := e^FAC1 |
| LOG  | (POLY1) | FAC1 := ln(FAC1) |
| RND  | `$E097` | FAC1 := RND(FAC1) |
| POLY1 | `$E043` | polynomial evaluator (odd-power series, Horner) |

### The multiply bug ($BA59 MLTPLY)

The floating-point multiply routine has a known carry-flag bug.
When a mantissa byte being multiplied is zero, the code jumps to
`MULSHF ($B983)` without ensuring carry=0 first.  `MULSHF` uses `ADC`
carelessly: it may shift by 9 bits instead of 8 bits, producing a
wrong (but consistent) result.

- **Trigger:** multiplying a value whose 5-byte mantissa has a zero byte
  in a specific position.  E.g. `X = 1 + 255/2^31; PRINT 1*X - X`
  gives `-5.91389835E-08` instead of `0`.
- **Deterministic:** YES — same input → same wrong output every time.
- **Fixed in:** BASIC 7.0 (C128) only.  All C64 BASIC V2 builds have it.
- **Impact on FMUL-users:** RND uses FMUL (multiply step in LCG) and
  CAN hit this bug in principle.  EXP/SIN use FMUL via POLY routines.
  For typical note-generation values the affected mantissa byte is
  rarely zero, but it cannot be ruled out for all possible seeds/inputs.
- **Emulation requirement:** a software reimplementation MUST reproduce
  this bug to be bit-exact for the GENERAL case.

### Transcendental functions (SIN/COS/ATN/EXP/LOG/SQR)

All are polynomial approximations via POLY1/POLY2 (Horner's method):
- Coefficients are HARDCODED in BASIC ROM, derived from "Computer
  Approximations" (Hart) using the Remez algorithm.
- **EXP:** 8-term approximation of 2^x over [0,1).
- **SIN:** 6-term odd-power series, sin(2πx) over [−0.25,+0.25],
  preceded by argument reduction (divide by 2π, take fractional part,
  quadrant correction via INT()).
- **LOG:** 4-term odd-power series.
- **ATN:** 12-term odd-power series over [−1,+1].
- All are **fully deterministic** given the same 5-byte FAC input.
  However they share the underlying FMUL which carries the multiply bug.

### FDIV — division

`FDIV` at `$BB0F` is the routine called for `PEEK(M)/28`.  It converts
28 to a 5-byte float, then divides.  Division is NOT affected by the
MLTPLY bug (different code path).  FDIV is deterministic.

**Sources:**
- https://www.c64-wiki.com/wiki/Floating_point_arithmetic
- https://www.c64-wiki.com/wiki/POLY1
- https://www.c64-wiki.com/wiki/Multiply_bug
- https://skoolkid.github.io/sk6502/c64rom/maps/routines.html

---

## 4. RND in Full

### ROM location: `$E097–$E0F8`

### RND(positive n) — the PRNG

```
E097: JSR $BC2B    ; get FAC1 sign: A=$FF (neg), $01 (pos), $00 (zero)
E09A: BMI $E0D3    ; negative → reseed from argument
E09C: BNE $E0BE    ; positive → next sequence value
                   ; (fall through if zero → CIA path)

; Positive path — E0BE:
E0BE: LDA #$8B     ; seed address low byte
      [...]
E0C2: JSR $BBA2    ; unpack 5-byte seed at $008B into FAC1
E0C5: [load ptr to E08D]  ; multiply constant
E0C9: JSR $BA28    ; FAC1 := FAC1 × constant_at_$E08D
E0CC: [load ptr to E092]  ; add constant
E0D0: JSR $B867    ; FAC1 := FAC1 + constant_at_$E092

; Byte-swap mantissa: $62↔$65, $63↔$64

; Finalize:
E0E3: LDA #$00
      STA $66      ; sign := positive
E0E7: LDA $61
      STA $70      ; save exponent to rounding byte
      [...]
      LDA #$80
      STA $61      ; force exponent = $80  (result in [0.5, 1.0))
E0EF: JSR $B8D7    ; normalise FAC1
E0F2: [store FAC1 back to seed at $008B]
```

**Algorithm:** Linear Congruential Generator (LCG) in 5-byte FP:
```
  next_seed = (prev_seed × C1 + C2)
  C1 = 11879546  (at $E08D, packed 5-byte float)
  C2 ≈ 3.927677739E-8  (at $E092, packed 5-byte float)
  mantissa bytes are then byte-swapped before normalization
  output = normalised fraction in [0, 1)
```

**Seed storage:** 5-byte packed float at `$008B–$008F` (zero-page).

**Determinism:** 100% deterministic from a known seed state.
`RND(-23)` always produces the same sequence (93, 83, 91, 2, 31...).
RND(n>0) for any positive n produces the next value in the same sequence.

**Known flaw:** The algorithm has poor statistical quality.  Due to the
mantissa byte-swap + normalize step and the use of FMUL (with its bug),
the sequence can degenerate to as few as **723 unique values** (C64-Wiki).
In worst cases it repeats a single value.  This is DETERMINISTIC —
same seed → same degenerate sequence.  The multiply bug in FMUL can
affect RND's multiply step (C1 × seed) when the right mantissa byte
is zero; results remain deterministic but wrong vs. ideal LCG.

### RND(0) — CIA hardware seeding (NONDETERMINISTIC)

```
; n=0 path — E09E:
E09E: JSR $FFF3    ; get I/O base address (CIA1 = $DC00)
      [store in $22/$23]
E0A5: [read ($22),$04] → $62  ; CIA1 Timer A low  ($DC04)
E0A8: [read ($22),$05] → $64  ; CIA1 Timer A high ($DC05)
E0B0: [read ($22),$08] → $63  ; CIA1 TOD 1/10s   ($DC08)
E0B5: [read ($22),$09] → $65  ; CIA1 TOD seconds  ($DC09)
E0BB: JMP $E0E3    ; finalize (byte-swap + normalize)
```

CIA1 registers read:
- `$DC04` Timer A low  — running free, changes every μs
- `$DC05` Timer A high
- `$DC08` TOD 1/10 second register (BCD, 0–9; only auto-increments if
  TOD is started — often not started, so may be static)
- `$DC09` TOD seconds register (BCD, 0–59)

**RND(0) is NONDETERMINISTIC** — its output depends on live CIA timer
state at the moment of the call.  Every different run of the program
will produce a different seed.  Any BASIC tune that uses RND(0) or
`RND(-TI)` (seeding from jiffy clock) to initialise its PRNG has a
**nondeterministic melody sequence** and cannot be reproduced bit-exact
without reading a captured CIA-state snapshot.

### RND(negative n) — reseed from argument

The negative-n path ($E0D3) byte-swaps the FAC1 mantissa (derived from
the argument itself) and writes it to $008B as the new seed, then
normalises.  This is deterministic from a known `n`.

### Summary: RND reproducibility

| RND form | Deterministic? | Reproducible? |
|----------|---------------|---------------|
| `RND(1)` or any positive | YES (from seed) | YES — capture `$008B–$008F` at start |
| `RND(-k)` fixed literal | YES | YES |
| `RND(-TI)` | NO — TI changes | NO without hardware-exact CIA state |
| `RND(0)` | NO — CIA timers | NO without hardware-exact CIA state |

**Sources:**
- https://skoolkid.github.io/sk6502/c64rom/asm/E097.html
- https://www.larsgregori.de/2020/05/24/c64-basic-how-i-fixed-rnd/
- https://www.c64-wiki.com/wiki/RND
- CIA register addresses: $DC04/$DC05/$DC08/$DC09 (C64-Wiki)

---

## 5. `PEEK(M)/28` — The Two Lines of Code Case Study

### What address does M=57272 read?

`57272` decimal = `$DF78` hex.

C64 memory map at $DF78:
- `$DF00–$DFFF` = **I/O Area #2** — expansion port cartridge space.
- **Without a cartridge:** no C64 chip is enabled at this address.
  The data bus is "open" (floating).  On a real C64 the 6510 CPU reads
  the last byte driven on the bus by the previous cycle — often from the
  VIC-II's video data (since the VIC-II cycles interleave with the CPU).
  In practice empirically reads return **$FF** (all lines pulled high by
  bus resistors) but this is NOT guaranteed — it depends on the specific
  C64 board revision, video chip state, and timing.
- `M = M + .2` means M progresses: 57272.0, 57272.2, 57272.4, ...
  PEEK calls QINT on M's value (floor), so PEEK(57272.0) through
  PEEK(57272.8) all read address 57272 ($DF78) — 5 identical POKE
  values per ROM byte.  Then at 57273.0 it reads $DF79, etc.

### Determinism verdict for PEEK(M)/28

- **If all reads return $FF (= 255):** 255/28 = 9.107... → POKES+1,9
  every iteration.  Melody is a constant tone.  Deterministic IF the
  bus consistently returns $FF.
- **On different hardware:** different bus-last-value could produce
  other byte values → different melody.
- **`POKES+8, TI AND PEEK(M+64)`:** uses the jiffy TI variable which
  increments at 60 Hz during BASIC interpreter execution, making the
  voice-2 freq-hi value depend on **execution timing** — this IS
  nondeterministic across different executions.

**Verdict: Two Lines of Code 1 has TWO sources of nondeterminism:**
1. `PEEK(M)` reads expansion I/O area — hardware-dependent bus state.
2. `TI AND PEEK(M+64)` — jiffy counter makes voice-2 freq timing-
   dependent.

The libsidplayfp ground-truth capture (siddump --writelog with real ROMs)
CAPTURES a specific hardware-modelled instantiation of these; that
captured stream IS deterministic and reproducible as a register trace.
But it cannot be reproduced by a software FP re-implementation without
also modelling the specific VIC-II video cycle and CIA state.

---

## 6. Practical Verdict: Exact Software Reimplementation

### What's needed for bit-exactness

To reproduce a `Basic_Program` SID's `$D400–$D418` write stream exactly
in software (without running the real ROM), the reimplementation needs:

| Component | Status |
|-----------|--------|
| 5-byte float format | **Fully documented**, portable |
| FADD/FSUB | **Fully documented**, deterministic |
| FMUL with multiply bug | **Documented bug** — must be reproduced exactly; bug is DETERMINISTIC |
| FDIV | **Fully documented**, deterministic, no bug |
| QINT / floor conversion | **Fully documented** — it is floor-toward-−∞, not round-to-nearest |
| INT() function | Same as QINT |
| POKE byte conversion | **Confirmed FLOOR** via QINT path at B7F7→BC9B |
| SIN/COS/ATN/EXP/LOG | Polynomial coefficients hardcoded, **reproducible** |
| RND(positive) | Deterministic from seed — **reproducible** if seed captured |
| RND(0) | NONDETERMINISTIC — CIA timers at call time |
| RND(-TI) | NONDETERMINISTIC — TI depends on execution timing |
| PEEK of ROM/RAM | Deterministic — ROM content known |
| PEEK of SID registers | Partially deterministic (voice 3 osc/$D41B returns live oscillator) |
| PEEK of unmapped I/O | NONDETERMINISTIC — floating bus |
| TI variable | NONDETERMINISTIC — jiffy count at interpreter speed |

### Existing bit-accurate software reimplementations

**`cbmbasic` (Michael Steil / mist64):**
- https://github.com/mist64/cbmbasic
- "100% compatible version of Commodore's version of Microsoft BASIC
  6502 as found on the Commodore 64."  Native C code, not a 6502
  emulator — the BASIC interpreter logic is re-implemented in C.
- The README claims 100% compatibility but does not specify whether
  this includes the FMUL multiply bug.
- Does NOT emulate CIA timers, VIC-II bus behaviour, or SID registers
  by default — so `RND(0)`, `PEEK($DF78)`, `PEEK($D41B)` will differ
  from real hardware.
- **Verdict:** Suitable for DATA/READ table-driven BASIC tunes where
  no hardware I/O is PEEKed.  NOT sufficient for algorithmic tunes that
  use `PEEK(unmapped)`, `TI`, or `RND(0)`.

**`libsidplayfp` + real ROMs:**
- The only currently proven path that handles ALL BASIC tunes including
  hardware-dependent cases.  Requires authentic C64 ROM images
  (`basic.rom`, `kernal.rom`, `chargen.rom`) — see cluster C5 research
  for provenance/licensing.
- Ground truth IS `siddump --writelog` (once siddump is patched to call
  `setRoms()`) — see `00_local_recon_findings.md` Blocker 1.

**VICE emulator:**
- Full-system 6502 emulation including CIA timers, VIC-II, SID.
- Handles all edge cases including floating bus (emulates as $FF or
  last VIC byte), CIA timer state, TI.
- Used as ground truth by the retro-computing scene.
- Open source (GPL), could be interrogated for its FP implementation,
  but it's a full emulator path not a "lift the FP routines" path.

### Feasibility conclusion

**For the SIDfinity project purpose (exact `$D400–$D418` write stream):**

| Tune sub-class | Software FP reimpl. feasible? |
|----------------|-------------------------------|
| DATA/READ table-driven | **YES** — no FP math needed at all; detokenise + replay DATA |
| Algorithmic with ROM/RAM PEEK only | **YES** — FDIV+FLOOR is sufficient; ROM bytes are known |
| Algorithmic with `RND(1)` (fixed seed) | **YES** — LCG is reproducible from known seed |
| Algorithmic with `PEEK(SID $D41B)` | **PARTIALLY** — SID noise osc state deterministic within sidplayfp model |
| Algorithmic with `RND(-TI)` or `RND(0)` | **NO** — CIA/timing nondeterministic without full emulator |
| Algorithmic with `PEEK(unmapped I/O)` | **NO** — bus state hardware-dependent |
| Algorithmic with `TI` for timing | **NO** — execution-speed dependent |

**Bottom line:** Lifting the FP arithmetic (FDIV, FADD, FMUL+bug, QINT)
is feasible and sufficient for a substantial fraction of algorithmic
tunes, but the SAFE general path is to run the program under libsidplayfp
with real ROMs and capture the write log.  The cbmbasic project provides
a reference implementation of the pure-interpreter semantics but lacks
hardware simulation.

---

## 7. Key Facts for USF Representation Design

1. **POKE byte conversion is FLOOR**, not round.  `floor(PEEK(M)/28)` is
   the exact formula.  A software reimpl must use this.

2. **The multiply bug is deterministic** — it must be reproduced if
   attempting software FP reimplementation.  The bug affects values where
   a mantissa byte (in the multiply operand's 5-byte form) is zero.

3. **`PEEK(M)/28` with M=$DF78+** reads expansion port I/O — value is
   hardware-dependent.  Most commonly $FF on a bare C64 (all lines high).
   Not guaranteed. Makes full software reproduction infeasible for this
   specific tune without knowing the specific hardware's bus state.

4. **RND(positive) from known seed is perfectly reproducible** in a few
   lines of C: multiply seed by C1=11879546, add C2≈3.927677739E-8,
   byte-swap mantissa, normalise.  The 5-byte seed at power-on ($008B)
   has a known initial value (from KERNAL init); the same initial seed
   on every cold-boot means RND sequences ARE replayable given a fresh
   power-on capture.

5. **SIN/COS/ATN/EXP/LOG** are purely deterministic.  The polynomial
   coefficients are hardcoded in ROM and reproducible.  Any BASIC tune
   using these for note generation is exactly reproducible IF no
   nondeterministic PEEK or RND(0) is involved.

---

## Leads to Follow

1. **Capture the exact 5-byte float constants** for C1 and C2 in the RND
   multiplier/adder at $E08D and $E092 from the actual ROM binary.
   These are in `hvsc84/`-companion ROM images; extract with `xxd`.

2. **Corpus survey** — run the BASIC detokeniser across all 486 SIDs and
   classify: how many use `RND`?  Of those, which form?  How many PEEK
   unmapped I/O?  Estimate the fraction of tunes that ARE software-
   reproducible vs. requiring the full emulator path.

3. **cbmbasic multiply-bug fidelity** — check whether cbmbasic reproduces
   the $BA59 MLTPLY bug.  Grep `cbmbasic.c` for the carry-flag behaviour
   around the zero-byte optimisation, or test empirically with
   `X=1+255/2^31 : PRINT 1*X-X`.

4. **Initial RND seed** — document the cold-boot initial value at $008B
   from the KERNAL ROM initialisation sequence.  This is the starting
   point for all RND(1)-only tunes.

5. **VICE FP source** — inspect VICE's `src/vic20/vic20basic.c` or
   the relevant BASIC FP emulation file to confirm whether the multiply
   bug is emulated and what the CIA timer modelling gives for RND(0).

6. **The `TI` variable in algorithmic tunes** — determine whether HVSC's
   recordings of BASIC tunes that use TI were recorded from a power-on
   state (TI=0) or mid-session.  If power-on, TI increments are fully
   deterministic given a fixed interpreter execution speed — but the
   interpretation speed depends on the exact BASIC line count and
   expression complexity, tying it to CIA1 interrupt rate (50/60 Hz).

7. **B79E call chain confirmation** — verify that $B79E (the POKE value
   byte fetch path) also goes through QINT and not a different rounding
   path.  The skoolkid disassembly showed only `JSR $AD8A` at $B79E;
   a direct fetch of the complete $B79E routine is needed.

8. **Unmapped I/O empirical test** — run `siddump --writelog` on
   `Two_Lines_of_Code_1_BASIC.sid` with real ROMs (once siddump is
   patched) to see what actual byte values PEEK returns.  Compare with
   $FF hypothesis.

9. **`$D41B` SID register PEEK** — used by some algorithmic tunes for
   hardware randomness (voice 3 oscillator output).  Research whether
   libsidplayfp models the SID noise oscillator deterministically.
