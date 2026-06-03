---
source_url: synthesis of all CSDb/sidid evidence above
fetched_via: derived from primary sources
fetch_date: 2026-06-03
author: jtr (synthesis); upstream sources cited per claim
content_date: 1988-1990 era binaries
reliability: secondary (synthesis — but every claim traces to a primary in the cited file)
---

# What the CSDb evidence tells us about the FC V3.x format

This file does not duplicate `research.md`. It captures specifics
extracted *only* from primary CSDb material and the bytes inside
the released editor disks — claims here are testable against the
real binaries.

## Driver entry layout (confirmed by V4 player disasm)

```
load + 0    init     — A = subtune number (0-based), runs init code
load + 3    (next instruction in init, on Hawkeye-MoN1988 driver
             this is also the play entry)
load + 6    play     — on FC V3 editor output (Union 1990), the
             play entry is here
```

The `+3` vs `+6` divergence (see `csdb_hawkeye_provenance.md`) is
the single highest-value finding for our pipeline. The MoN/FC
signature `MoN/FutureComposer` matches *both* layouts; the
`FC_V3.x`-specific signature only fires on Union-era output.

## Wave-table command parser structure (from sidid `FC_V3.x` signature)

The verbatim bytes:

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90 0B 29 3F 9D
```

translate to a two-level dispatch:

```
loop:
    LDA  $wave_table_ptr_zp_or_abs   ; current wave-table byte
    CMP  #$60
    BCC  L1                          ; below $60 → not an AD command
    AND  #$0F                        ; opcode arg = low nibble
    STA  $D405,X                     ; voice X attack/decay register
    INC  $wave_table_ptr             ; advance
    JMP  loop
L1:
    LDA  $wave_table_ptr
    CMP  #$40
    BCC  L2                          ; below $40 → not this command
    AND  #$3F                        ; opcode arg = low 6 bits
    STA  (next dispatch — register or jump target)
    ...
```

So the V3 wave table has **three opcode tiers** by simple
threshold dispatch:

| Byte range  | Meaning                       |
|-------------|-------------------------------|
| `$00..$3F`  | Literal SID waveform/control byte (writes to $D404,X) |
| `$40..$5F`  | Command class A (6-bit arg) — likely a per-voice control byte ($D405/D406 SR? pulse width LSB?) |
| `$60..$6F`  | Set ADSR-AD nibble (writes low nibble to $D405,X) |
| `$70..$FE`  | Further commands (jump, loop, delay, end) — known to exist from research.md but exact thresholds need confirmation from binary |
| `$FF`       | End/loop marker (research.md) |

**This is the most actionable piece of byte-level info recovered.**
For our extractor, when we walk a V3 wave-table, we dispatch on
these ranges. The exact handler for the `$40..$5F` range and the
`$70..` range needs the disassembly of the actual V3.0 player to
confirm — see "Leads to follow".

## Filter-table fetch (from generic MoN/FC signature)

The verbatim signature bytes show:

```
FE ?? ??           INC  abs,X          ; advance filter-table ptr
BC ?? ??           LDY  abs,X          ; fetch filter-table value into Y
B1 ??              LDA  ($zp),Y        ; index a table by Y
C9 FF              CMP  #$FF
D0 ??              BNE  +              ; if not end marker...
A9 00              LDA  #$00
9D ?? ??           STA  abs,X          ; ...store-or-reset something
BD ?? ??           LDA  abs,X
F0 05              BEQ  +5
DE ?? ??           DEC  abs,X
10 03              BPL  +3
8D 17 D4           STA  $D417          ; *** filter resonance + voice-route ***
A0 06              LDY  #$06
88 ×6              DEY×6
B1 F9              LDA  ($F9),Y
```

This gives us:

- **`$D417` (FC + Reso + filt-voice) write path** — driven by a
  filter table indexed by `X` (voice or per-tune?), with **`$FF`
  as an end/repeat marker**.
- **Zero-page `$F9/$FA` holds an instrument-pointer used to walk
  6 bytes back into the instrument record** to fetch a related
  value. So FC instruments are **packed with their associated
  pointer data at +6 offsets**.
- **A separate counter at `abs,X` is decremented when the value
  in `abs,X` is non-zero**, with a `BPL +3` skip — classic
  "duration countdown with sustain hold" pattern.

The `$D417` write is **not** routed through the per-voice
$D404-$D406 logic. So FC's filter table is **global**, not
per-voice, and runs in a fourth pass after the three voice
loops. This matches research.md's "Global: execute filter table"
claim and bounds the schema.

## Three-voice update loop indexing convention

Multiple signatures show `STA abs,X` writes followed by `INC abs,X`
with `X` taking on `0, 7, 14` (or `0, 1, 2` scaled by 7). The
standard SID register layout is `$D400 + 7*voice`, so the FC
driver consistently uses **`X = 7 * voice_number`** as its loop
index. This means per-voice state arrays in FC are also strided
by 7, not by 1 — a useful discriminator when extracting.

## V3 vs V4 binary differentiator

`FC_V4_Packed` signature `EE 99 ?? EE 9A ?? EE 9B ?? A9` =
three consecutive `INC abs` (low, mid, high) for a **24-bit
counter or a 24-bit packed-stream offset**. V3 has only 16-bit
counters. So at the bit level:

- V3 sequences and patterns use **16-bit absolute addresses**
  (load address baked in).
- V4 introduces a **packed format** with a 24-bit pointer/offset,
  enabling a relocatable-ish layout — but it's still not runtime
  relocatable.

## Frame-counter / tempo (from FC_V1.0 signature)

`EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60`:

- Two consecutive `INC abs` = 16-bit frame counter.
- `CMP #$32` = compare against **50 ($32)** — V1.0 has the
  PAL 50 Hz wrap hard-coded.
- `LDA #$01 ; STA abs ; RTS` = reset frame counter and set a
  "second elapsed" flag.

V3/V4 likely **moved this to a tempo-parametrised counter**,
which is why their signatures don't include the `#$32` literal.
The tempo for V3 tunes is in the per-tune data block, not in
the driver.

## What we still don't know from CSDb alone

1. The exact byte for "end of pattern" vs "end of sequence" in V3
   (research.md says `$FF` for pattern end — need to confirm against
   the V3.0 driver binary).
2. The instrument record layout *exact byte order* (research.md
   gives the fields but not the byte offsets).
3. Whether V3 has a portamento opcode in the pattern stream
   (claimed by research.md but no signature confirms it).
4. The wave-table opcode set above `$70` (jump, delay, end).
5. Whether the filter-table is per-instrument-referenced or
   global-only.

All five can be resolved by hand-disassembling the V3.0 editor's
**driver-only block**, which is identifiable by finding the
`FC_V3.x` signature inside `artifacts/MoN_FC_V3.0.prg` and
following xrefs. See "Leads to follow" in the parent provenance
log.
