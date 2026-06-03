---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-03
author: Lasse Oorni (Cadaver) — sidid project
content_date: ongoing (sidid.cfg in master)
reliability: primary
---

# SIDId signature blocks for the FC family

Verbatim from the live `sidid.cfg`. These are the canonical byte-pattern
fingerprints HVSC uses to classify FC-family players. They double as
**precise pinpoint anchors** inside any FC SID body — every signature
below identifies a specific subroutine in the driver, so once you load a
Hawkeye SID you can grep for these patterns to land directly on the
relevant code.

## `MoN/FutureComposer` (generic catch-all)

```
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03
8D 17 D4 A0 06 88 88 88 88 88 88 B1 F9
```

Decoded:

- `INC abs,X` / `LDY abs,X` / `LDA (zp),Y` / `CMP #$FF` / `BNE *+..` /
  `LDA #$00` / `STA abs,X` / `LDA abs,X` / `BEQ +5` / `DEC abs,X` /
  `BPL +3` / `STA $D417` — that is the **filter-table fetch /
  $D417 (FC1/FC2/Resonance/Filt-Voice control) write** sequence.
- The trailing `LDY #$06 / DEY×6 / LDA ($F9),Y` is the **6-byte
  back-step into a packed table entry** — the per-voice instrument
  pointer arithmetic.

## `FutureComposer_V1.0`

```
EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60
```

Two consecutive `INC abs` (16-bit counter increment), then load /
compare-against-50 / branch / store-1 / RTS. This is the **50 Hz frame
counter wrap** specific to V1.0 — V1's tempo was hardwired to 50/sec.

## `FC_V3.x` (this is the Hawkeye-era driver)

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90 0B 29 3F 9D
```

Decoded as 6502:

```
   JMP    *  ; the wave-table command dispatcher
L: LDA    abs       ; fetch next wave-table byte
   CMP    #$60      ; >= $60 ?
   BCC    +0B       ; no → fall-through to normal waveform write
   AND    #$0F      ; yes → mask low nibble = ADSR-attack/decay opcode
   STA    abs,X     ; write to $D405,X (AD register)
   INC    abs,X     ; advance wave-table pointer
   JMP    *         ; loop
   LDA    abs       ; (next branch — different opcode range)
   CMP    #$40      ; >= $40 ?
   BCC    +0B       ; no
   AND    #$3F      ; yes → 6-bit-mask = something else
   STA    abs,X
```

This is the **wave-table command parser**. Two distinct command
ranges:
- `$60–$6F` → masked to low nibble, written to AD (attack/decay).
  16 possible AD values from a single byte.
- `$40–$5F` (6-bit range) → masked to `$3F` → another register write.

**Key implication for byte-exact rebuild:** the wave-table command
encoding has at least two threshold-dispatched opcode ranges. The
binary structure of a V3 wave table is a stream where each byte's
high-nibble selects between "literal waveform byte" and "command
type N", and the parser is a cascade of `CMP #threshold / BCC`.

## `FC_V4_Packed`

```
EE 99 ?? EE 9A ?? EE 9B ?? A9
```

Three consecutive `INC abs` (probably $xx99 / $xx9A / $xx9B as a
24-bit pointer or three byte-counters), then `LDA #`. The V4 packer
adds a three-byte unpacker entry — that's how the V4 packed format
differs from V3.x at the binary level (V3 has at most a 2-byte
sequence counter; V4 adds a third for the packed-stream offset).

## `MoN/Cyb2` (sister driver — same FC family)

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C
```

Identical structure to FC_V3.x but without the `AD/CMP #$40/BCC`
intermediate stage — Cyb2 collapses two of FC_V3's command ranges
into one. Useful diff to confirm FC_V3 has a distinct extra branch.

## Why these signatures matter for our rebuild

The signatures *are* the dispatch table of the wave-table command
parser. To rebuild byte-exact V3 SIDs we need to faithfully reproduce
this exact instruction sequence (the trick branches at `$60` and
`$40` thresholds are part of the parser's *control flow*, not just
its data). When we extract a V3 SID, locate the FC_V3.x signature
inside the binary — the offset gives us the wave-table parser's
fixed address, which in turn anchors all the other tables.
