---
source_url: derived from c4_basic_floatingpoint_core.md
fetch_date: 2026-06-22
author: SIDfinity research agent (C4 cluster)
reliability: derived/secondary
---

# C4 Quick Reference: C64 BASIC Floating Point

## 5-byte packed float (RAM storage)

```
Byte 0: exponent  (excess-128; $00 = zero)
Byte 1: sign:mantissa[1] (MSB=sign; 0=+, 1=−; mantissa bits [1:7] follow)
Byte 2: mantissa byte 2
Byte 3: mantissa byte 3
Byte 4: mantissa byte 4 (LSB)
```
Mantissa is always normalised to [0.5, 1.0); the implicit leading 1 is
represented by the sign bit in RAM and restored to bit 7 of byte 1 in the
6-byte unpacked form used internally.

## FAC zero-page unpacked layout

```
$61  exponent
$62  mantissa 1 (MSB, bit 7 = implied leading 1 restored)
$63  mantissa 2
$64  mantissa 3
$65  mantissa 4 (LSB)
$66  sign  ($00=positive, $FF=negative)
$70  overflow/rounding byte
```

ARG register: same layout at $69–$6E.
RND seed: 5-byte packed float at $008B–$008F.

## Key routine addresses

```
$B867  FADD    FAC2 + FAC1 → FAC1
$B850  FSUB    (AY ptr) − FAC1 → FAC1
$BA28  FMUL    FAC2 × FAC1 → FAC1   [has multiply bug at $BA59]
$BB0F  FDIV    (AY ptr) ÷ FAC1 → FAC1  [no bug]
$BC9B  QINT    FAC1 → 32-bit integer, floor toward −∞, stored in $62–$65
$BCCC  INT()   calls QINT, returns floor result in FAC1
$B849  round   FAC1 + 0.5 (OUTPUT/PRINT path only, not POKE)
$E043  POLY1   polynomial evaluator (odd-power Horner)
$E097  RND()   LCG: seed×C1+C2, byte-swap, normalise
$E26B  SIN()   6-term polynomial via POLY1, argument reduced
$E264  COS()   shares SIN infrastructure
$E2B4  TAN()
$E30E  ATN()   12-term polynomial
```

## POKE call chain (value argument)

```
B824 POKE → B7EB → [evaluate expr] → B7F7 → BC9B (QINT/floor) → return
```

**POKE byte conversion = FLOOR (INT), not round-to-nearest.**
`POKE x, 9.9`  writes byte 9.
`POKE x, -0.1` → ILLEGAL QUANTITY ERROR (negative rejected at B7F9).

## FDIV + FLOOR: `PEEK(M)/28` example

Given `PEEK(M) = N` (integer 0–255):
1. N converted to FAC float
2. FDIV: FAC := N / 28.0  (5-byte precision)
3. QINT (via POKE path): result = floor(N/28)

Key values:  0/28=0, 28/28=1, 56/28=2, ..., 252/28=9, 255/28=9.

## RND algorithm (positive argument)

LCG in 5-byte floating point:
```
new_seed = (old_seed × 11879546 + 3.927677739E-8)
mantissa bytes of new_seed byte-swapped: [b1,b2,b3,b4]→[b4,b3,b2,b1]
exponent set to $80, normalise → output in [0, 1)
```
Constants: C1=11879546 at ROM $E08D; C2≈3.927677739E-8 at $E092.
Seed at ZP $008B–$008F (5-byte packed).

## RND determinism

- `RND(n>0)`: deterministic from known seed state.
- `RND(0)`: reads CIA1 $DC04/$DC05 (Timer A) + $DC08/$DC09 (TOD).
  **NONDETERMINISTIC** — live hardware timer values.
- `RND(-k)` literal: deterministic.
- `RND(-TI)`: nondeterministic — TI = jiffy count (50/60 Hz IRQ-driven).

## The FMUL multiply bug ($BA59)

Affects: all FMUL operations where a mantissa byte = 0.
Effect: ADC without ensuring carry=0 → shifts 9 instead of 8 bits.
Wrong but DETERMINISTIC — same inputs → same wrong output.
Present in all C64 BASIC V2; fixed in BASIC 7.0 (C128) only.
Software reimplementation must reproduce to be bit-exact.

## PEEK of unmapped I/O

Address $DF78 (= 57272 decimal, used in Two Lines of Code 1):
- Expansion port I/O Area 2 ($DF00–$DFFF).
- No C64-internal chip active; data bus is open.
- Empirically usually returns $FF (255) when no cartridge present.
- **Not guaranteed** — depends on board revision and VIC-II bus state.
- Makes full software reproduction impossible without hardware modelling.
