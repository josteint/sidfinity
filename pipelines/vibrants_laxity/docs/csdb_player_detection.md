---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg; https://github.com/cadaver/sidid/blob/master/sidid.nfo; https://github.com/WilfredC64/player-id
fetched_via: direct
fetch_date: 2026-06-15
author: Cadaver (Lasse Öörni), HVSC contributors
content_date: ongoing
reliability: primary
---

# Vibrants/Laxity — SID Player Detection Data

## Source: sidid.cfg (cadaver/sidid GitHub)

SIDId is the HVSC playroutine identity scanner. Signatures use hex bytes, `??` for
wildcard (any byte), `END` to terminate, multiple lines = all must match (AND logic).

### `Vibrants/Laxity` (5 signature lines — all must match)

```
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4 END
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4 END
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D END
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29 END
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90 END
```

### Annotation of Vibrants/Laxity Signatures

**Signature line 1:** `18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4`
- CLC; ADC abs,Y → shift left (×2); TAY; LDA abs,Y → PHA; LDA abs,Y; LDY abs; STA $D401,Y; PLA; STA $D400,Y
- This is the frequency write pattern for a voice: loads hi+lo freq from a table, writes to SID
  regs $D400 (freq lo) and $D401 (freq hi) indexed by Y (voice offset).

**Signature line 2:** `FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4`
- INC abs,X; LDA abs,X; STA $D404,Y; JMP abs; LDA abs,X; AND #imm; BEQ; LDA #imm; STA $D404,Y
- Gate/waveform write ($D404 = control register for a SID voice). Conditional waveform load.

**Signature line 3:** `A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D`
- LDA #imm; STA abs; RTS; LDX #imm; DEC abs; BPL; DEC abs; DEC abs; DEC abs; DEC abs; LDA abs; STA
- Counter-based section: multiple DEC abs / BPL chains. Likely the tempo/frame counter or
  multi-voice advance counter. LDX # then DEC/BPL pattern = Hubbard-style nested speed counters.

**Signature line 4:** `C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29`
- CMP #imm; BCS; AND #imm; PHA; LDA #imm; STA abs,X; PLA; ASL; ASL; STA abs,X; JMP; AND
- Instrument/note decode: AND mask, push to stack, load instrument base, store, pop, shift ×4,
  store again. The ×4 shift (ASL;ASL) means instrument index is a 2-bit field stored in the
  upper part of a byte; the ×4 converts it to an instrument table offset (4 bytes/entry or
  similar). JMP to dispatch.

**Signature line 5:** `AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90`
- LDA abs; CLC; ADC abs,Y; STA abs; STA $D416; BIT abs; BVS; CMP abs,Y; BCC
- Filter cutoff write to $D416 (SID filter cutoff frequency). The `BIT`/`BVS` is a flag-test
  branch (BVS = branch if overflow set, which BIT sets from bit 6 of the memory operand).
  `CMP abs,Y; BCC` = frequency sweep comparison.

**Key observations from signatures:**
- Player writes $D400/$D401 (freq lo/hi), $D404 (control/gate), $D416 (filter cutoff)
- Uses Y as voice offset (0, 7, 14 for voices 1-3, or similar stride)
- Instrument indexing via AND + ASL×2 (4-byte instrument entries or nibble-packed)
- Filter is actively updated per-frame (line 5)
- Counter chains (line 3) consistent with multi-speed / nested tempo

---

### `Laxity_NewPlayer_V21` (1 signature line)

```
99 04 D4 BD ?? ?? C9 FF F0 ?? 4C ?? ?? DE ?? ?? BD ?? ?? D0 ?? 4C END
```

- STA $D404,Y; LDA abs,X; CMP #$FF; BEQ; JMP; DEC abs,X; LDA abs,X; BNE; JMP
- Gate write ($D404), then load/compare to $FF (end-of-data sentinel), loop or advance.
- `DEC abs,X` = decrement note-duration counter; `BNE` = still counting down → `JMP` (stay).
- This is a 2006 player (JCH Music Editor player, but coded by Laxity). Separate from the
  classic Vibrants/Laxity player above.

---

### `SidFactory/Laxity` (1 signature line)

```
A9 ?? 4C ?? ?? A9 ?? 9D ?? ?? A9 ?? 9D ?? ?? BD ?? ?? A8 29 02 D0 ?? 4C ?? ?? 98 29 FD 9D END
```

- LDA #imm; JMP; LDA #imm; STA abs,X; LDA #imm; STA abs,X; LDA abs,X; TAY; AND #$02; BNE; JMP; TYA; AND #$FD; STA abs,X
- 2005-era SID Factory player. AND #$02/$FD = bit-2 flag test (likely gate on/off control).

---

### `SidFactory_II/Laxity` (1 signature line)

```
C8 B1 ?? C9 FF D0 04 C8 B1 ?? A8 98 AND C9 7E F0 ?? 18 END
```

- INY; LDA (zp),Y; CMP #$FF; BNE 4; INY; LDA (zp),Y; TAY; TXA; AND; CMP #$7E; BEQ; CLC
- Indirect zp-indexed reads (sequence/orderlist traversal). $FF = end-sentinel. #$7E likely
  a note value or marker. Modern SID Factory II driver.

---

### `256bytes/Laxity` (1 signature line)

```
4A 4A A8 88 88 30 07 46 FC 66 FB END
```

- LSR; LSR; TAY; DEY; DEY; DEY; BMI 7; LSR $FC; ROR $FB
- Very compact routine (fits 256 bytes). Uses ZP $FB/$FC for data. Likely a mini-player.

---

### `Vibrants/JO` (10 signature lines — different engine, same group)

JO (Jesper Olsen) of Vibrants used a completely different engine. Detection patterns are
separate in sidid.cfg and are NOT part of the Vibrants/Laxity family. 130 HVSC SIDs.

---

## SIDId Tool Reference

- **Tool:** SIDId by Cadaver (Lasse Öörni / Covert Bitops)
- **GitHub:** https://github.com/cadaver/sidid
- **Config:** sidid.cfg (signatures), sidid.nfo (author info)
- **NFO reference for Vibrants/Laxity:** `https://csdb.dk/release/?id=122333`
- **NFO reference for Laxity_NewPlayer_V21:** `https://csdb.dk/release/?id=26563`

Alternative tool: player-id by WilfredC64 (Rust, multi-core BNDM algorithm)
- https://github.com/WilfredC64/player-id

---

## Memory Map Clues from Signatures

From TFA Editor v3.24 trivia (ground truth for early layout):
- Music data: $0F00 – $2000 (+ $80 per additional pattern)
- Instrument table: **$1700**
- Init/restart: SYS 2304 = **$0900**

From 3x-player variant:
- Music loads at **$4000** (not standard $0F00 area)

From sidid.cfg signature line 1:
- SID writes use Y as stride (Y-indexed into $D400 region → standard 7-byte/voice stride implied)

From sidid.cfg signature line 3:
- Multiple DEC/BPL chains → nested frame counters (Hubbard-style tempo nesting)

From signature line 4 (ASL;ASL = ×4):
- Instrument entries are likely 4-byte multiples in the instrument table

From signature line 5 (STA $D416):
- Filter cutoff is actively driven by the player per-frame

**SID registers written by Vibrants/Laxity player (confirmed from signatures):**
- $D400 (V1 freq lo), $D401 (V1 freq hi) — and equivalents $D407/$D408, $D40E/$D40F
- $D404 (V1 control/gate) — and $D40B, $D412
- $D416 (filter cutoff lo — or hi, depending on which register at +$16)
