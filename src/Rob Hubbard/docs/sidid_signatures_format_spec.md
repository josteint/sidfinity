---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-04-21
author: Cadaver (Lasse Öörni), various contributors
content_date: ongoing
reliability: primary
---

# SIDId Signatures for Rob Hubbard Driver Variants

**Repo:** https://github.com/cadaver/sidid
**File:** sidid.cfg

SIDId uses hex byte patterns where `??` = wildcard byte.

---

## Main Rob_Hubbard Signature

```
BD ?? ?? 99 ?? ?? 48 BD ?? ?? 99 ?? ?? 48 BD ?? ?? 48 BD ?? ?? 99 ?? ?? BD ?? ?? 99
2C ?? ?? 30 ?? 70 ?? B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 98 38
AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 ?? 9D ?? ?? FE
99 04 D4 BD ?? ?? 99 02 D4 48 BD ?? ?? 99 03 D4 48 BD ?? ?? 99 05 D4
2C ?? ?? 70 ?? FE ?? ?? AD ?? ?? 10 ?? C8 B1 ?? 10 ?? 9D ?? ?? 4C
0A 0A 0A AA BD ?? ?? 8D ?? ?? BD ?? ?? 2D ?? ?? 99 04 D4
```

### Pattern Analysis

Line 1: `BD ?? ?? 99 ?? ?? 48` = `LDA table,X / STA (ptr),Y / PHA` (×2 variants)
This is the song table loading pattern, writing channel track pointers.

Line 2: `2C ?? ?? 30 ?? 70 ??` = `BIT addr / BMI / BVC` — music status check
`B9 ?? ?? 8D 00 D4` = `LDA table,Y / STA $D400` — SID register write (freq lo)
`B9 ?? ?? 8D 01 D4` = `LDA table,Y / STA $D401` — SID register write (freq hi)

Line 3: `AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ??` — load/store with register
`BC ?? ?? B1 ?? C9 FF D0 ??` = `LDY table,X / LDA (ptr),Y / CMP #$FF / BNE` — pattern fetch + $FF check
`A9 ?? 9D ?? ?? FE` — store with INX pattern

Line 4: `99 04 D4` = `STA $D404,Y` (SID control reg)
`BD ?? ?? 99 02 D4` = `LDA table,X / STA $D402,Y` (voice freq lo)
`48` = PHA
`BD ?? ?? 99 03 D4` = `LDA table,X / STA $D403,Y` (voice freq hi)
`48` = PHA
`BD ?? ?? 99 05 D4` = `LDA table,X / STA $D405,Y` (attack/decay)

Line 5: `2C ?? ?? 70 ??` = `BIT addr / BVS` — test bit for effects
`FE ?? ??` = `INC abs,X` — increment something indexed
`AD ?? ?? 10 ??` = `LDA abs / BPL` — **this is the speed counter**
`C8` = `INY`
`B1 ??` = `LDA (ptr),Y` — indirect load from pattern
`10 ??` = `BPL` — branch if positive (new instrument vs portamento)
`9D ?? ?? 4C` = `STA abs,X / JMP`

Line 6: `0A 0A 0A AA` = `ASL / ASL / ASL / TAX` — multiply by 8 (instrument index × 8)
`BD ?? ?? 8D ?? ??` = `LDA instrs,X / STA addr` — instrument byte load

**The speed counter is in Line 5**: `AD ?? ?? 10 ??` = `LDA abs / BPL` (not DEC!).
Wait — this could be `LDA speed / BPL` — but BPL would branch on positive, which contradicts
the typical pattern. Let me re-read: in the classic driver, `dec speed / bpl mainloop`.
The signature shows `AD (LDA abs) ... 10 (BPL)`, which might be `LDA mstatus / BPL` (status check),
not the speed counter per se. The speed counter DEC is likely earlier in the routine.

---

## Sub-variant: Rob_Hubbard_Digi

```
4C ?? ?? 28 F0 AND 4A 4A 4A 4A 4C ?? ?? 29 0F EE ?? ?? D0 03 EE AND 8D 18 D4
```

`4C` = JMP
`28` = PLP (pull processor status)
`F0` = BEQ
`4A 4A 4A 4A` = `LSR / LSR / LSR / LSR` — shift right 4 (extract high nibble)
`29 0F` = `AND #$0F` — mask to 4 bits
`EE ?? ?? D0 03 EE` = `INC abs / BNE / INC` — increment with carry
`8D 18 D4` = `STA $D418` — write to SID volume register (unsigned 4-bit PCM via volume register)

This confirms the digi variant uses the volume register for 4-bit PCM sample playback.

---

## Sub-variant: Paradroid/HubbardEd

```
B1 FC 10 1B C9 FF F0 12 C9 FE F0 0A
```

`B1 FC` = `LDA ($FC),Y` — load from zero-page indirect at $FC
`10 1B` = `BPL +$1B` — branch if positive (bit 7 clear = note byte, not control)
`C9 FF` = `CMP #$FF` — check for pattern end ($FF)
`F0 12` = `BEQ +$12` — branch if end
`C9 FE` = `CMP #$FE` — check for track end ($FE)
`F0 0A` = `BEQ +$0A` — branch if track end

**This is the core note-fetch loop!** The pattern shows:
1. Load byte from pattern via ($FC),Y
2. Check if negative (bit 7 set = control byte, not pitch/length)
3. Check for $FF (end of pattern)
4. Check for $FE (end of track)

The $FC zero page pointer is the pattern pointer in this variant (differs from standard $04/$05).
The "HubbardEd" name suggests this is from an editor variant.

---

## Sub-variant: Giulio_Zicchi

```
CA 30 03 4C ?? ?? 60 A2 00 8E ?? ?? E8 8E ?? ?? 60 A0 00
```

`CA` = `DEX`
`30 03` = `BMI +$03` — branch minus (when X wraps below 0, done)
`4C ?? ??` = `JMP` — jump back to channel loop
`60` = `RTS`
`A2 00` = `LDX #0`
`8E ?? ??` = `STX abs`
`E8` = `INX`
`8E ?? ??` = `STX abs`
`60` = `RTS`
`A0 00` = `LDY #0`

This is the channel loop structure, iterating X from 2 down to 0 (3 channels).
Giulio Zicchi's variant uses the same 3-channel structure as Hubbard's original.

---

## Sub-variant: Bjerregaard

```
99 03 D4 AE ?? ?? 9D ?? ?? 68 9D ?? ?? A9 01 9D
```

`99 03 D4` = `STA $D403,Y` (voice freq hi via Y-indexed)
`AE ?? ??` = `LDX abs`
`9D ?? ??` = `STA abs,X`
`68` = `PLA`
`9D ?? ??` = `STA abs,X`
`A9 01` = `LDA #$01`
`9D` = `STA abs,X`

The `PLA` (pull from stack) after writing freq hi suggests values were pushed to stack
during song table loading. Bjerregaard's variant uses stack-based temporary storage.

---

## Implications for Our rh_decompile.py

1. **Main Rob_Hubbard**: Our find_speed() scans for DEC/BPL pattern — this is NOT in the
   SIDId signature because it's earlier in the routine. The signature hits the note-work
   section. Our approach is correct.

2. **Paradroid/HubbardEd**: Different ZP address for pattern pointer ($FC instead of $04).
   Also potentially different note byte order — the BPL branch on byte 1 suggests a
   different flag layout where the sign bit means something different.

3. **Bjerregaard**: Stack-based register write. The audio output registers are the same
   ($D4xx) but the write pattern is different. Speed counter likely identical.

4. **Giulio_Zicchi**: Standard 3-channel loop, very close to Hubbard original.

5. **Rob_Hubbard_Digi**: Contains PCM via volume register. This is a LATE driver feature
   (1987+). Not all songs with the main signature have digi — it's a separate detection.
