---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: WebFetch
fetch_date: 2026-06-13
author/handle: cadaver (Lasse Öörni) — sidid tool; signatures contributed by community
content_date: ongoing; entry dates not shown in cfg
reliability: secondary — detection patterns are empirically derived from real SID binaries; highly reliable for player identification
---

# sidid Detection Signatures — SoedeSoft / Soundmaster

Repository: https://github.com/cadaver/sidid

The sidid tool identifies C64 music player routines by matching byte sequences against known signatures. `sidid.cfg` uses `??` as a wildcard byte. The following four entries cover the SoedeSoft/Soundmaster family.

## Umbrella Entry: SoedeSoft

```
SoedeSoft
D0 03 BD ?? ?? 9D ?? ?? 60 END
B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9 END
```

**Annotation in sidid.nfo:**
> "Authors: Jeroen Soede & Michiel Soede. Released: 1988 Soedesoft. The editor is also known as Soundmaster or SoedeSound Editor."

RE-NOTES on the SoedeSoft umbrella signature:

Sequence 1: `D0 03 BD ?? ?? 9D ?? ?? 60`
- `D0 03` = BNE +3 (branch if not zero — skip 3 bytes)
- `BD ?? ??` = LDA abs,X (load from table indexed by X)
- `9D ?? ??` = STA abs,X (store to SID register indexed by X)
- `60` = RTS

This short 9-byte signature captures the BNE-skip + table-LDA + STA-indexed + RTS idiom. Consistent with a voice-loop: X register cycles through voice offsets (0, 7, 14 for three SID voices), and the BNE skips the write for a muted/inactive voice.

Sequence 2: `B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9`
- `B9 ?? ??` = LDA abs,Y (load from table indexed by Y)
- `4A 4A 4A 4A` = LSR A × 4 (shift right 4 — extract high nibble)
- `9D ?? ??` = STA abs,X (store high nibble to SID)
- `B9 ?? ??` = LDA abs,Y again
- `0A 0A 0A 0A` = ASL A × 4 (shift left 4 — extract low nibble)
- `9D ?? ??` = STA abs,X (store low nibble to SID)
- `B9` = start of next LDA

This 20-byte signature is highly distinctive: **nibble-splitting of a packed byte into two separate SID writes.** Two SID parameters are packed into one data byte (high nibble → one register, low nibble → another register). This is very likely the envelope pack: ATTACK/DECAY in one byte ($D405,X) and SUSTAIN/RELEASE in another ($D406,X), or alternatively the oscillator frequency split. The 4×LSR / 4×ASL pattern is unmistakable.

---

## Soundmaster_V1.0 Signature

```
(Soundmaster_V1.0)
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4 B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C END
```

RE-NOTES:

- `9D ?? ??` = STA abs,X
- `BD ?? ??` = LDA abs,X
- `D0 ??` = BNE rel (conditional skip)
- `18` = CLC (clear carry before ADC)
- `B9 ?? ??` = LDA abs,Y (from note/freq table)
- `7D ?? ??` = ADC abs,X (add voice-specific offset)
- `99 ?? ??` = STA abs,Y (store to internal buffer)
- `99 00 D4` = STA $D400,Y — **write to SID voice frequency lo** ($D400 = SID base; Y = 0/7/14 for voices)
- `B9 ?? ??` = LDA abs,Y again (hi byte)
- `69 ??` = ADC #imm (add immediate)
- `99 ?? ??` = STA abs,Y (store hi byte to buffer)
- `99 01 D4` = STA $D401,Y — **write to SID voice frequency hi**
- `4C` = JMP

This 31-byte signature is the **frequency calculation and write routine for V1.0.** Key observations:
1. Y register is used for voice offset (Y = 0, 7, 14) — different from V3.x which may use X.
2. Frequency is computed as: `freq_hi = table[Y] + constant` and `freq_lo = table[Y] + voice_offset` (ADC abs,X with voice-specific accumulator). This is classic "base frequency from note table + per-voice transposition" — each voice has a transposition/pitch offset.
3. The `CLC` before the first `7D` (ADC abs,X) indicates the freq_lo calculation uses carry-clear addition. The second `69 ??` (ADC #imm) is carry-propagation from the lo byte to the hi byte (standard 16-bit add).
4. Direct STA to $D400,Y and $D401,Y (not via an `X`-indexed `STA $D400,X`). This confirms V1.0 uses **Y as the voice index register** for SID writes, not X.

---

## Soundmaster_V3.1 Signature

```
(Soundmaster_V3.1)
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60 END
```

RE-NOTES:

- `A9 ??` = LDA #imm (load immediate constant)
- `9D ?? ??` = STA abs,X (store to voice work area)
- `4C ?? ??` = JMP (unconditional jump)
- `BD ?? ??` = LDA abs,X (load freq lo from table/buffer, X-indexed)
- `9D 00 D4` = STA $D400,X — **SID freq lo via X-indexed write** ($D400,X means X=0,7,14)
- `BD ?? ??` = LDA abs,X (load freq hi)
- `9D 01 D4` = STA $D401,X — **SID freq hi via X-indexed write**
- `60` = RTS

This 20-byte V3.1 signature shows the **frequency write path has been restructured** relative to V1.0:
1. Now uses **X register** for voice indexing (STA $D400,X), not Y as in V1.0.
2. No addition — the frequency values are loaded directly from a table/buffer (already computed). The calculation was likely moved to an earlier stage.
3. `A9 ?? / 9D ?? ??` = writes an immediate constant to a per-voice work location before jumping — may be a note/status initialisation step.
4. The `4C` (JMP) between the init store and the freq writes suggests V3.1 reorganised the routine into sub-functions called via JMP rather than inline code.

---

## Soundmaster_V3.2 Signature

```
(Soundmaster_V3.2)
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60 END
```

RE-NOTES:

This 38-byte V3.2 signature is the **longest of the three and combines features of both V1.0 and V3.1:**

- `A9 ?? / 9D ?? ?? / 4C ?? ??` — same init+jump idiom as V3.1
- `18` = CLC (same as V1.0 — freq calculation involves addition)
- `BD ?? ?? / 7D ?? ?? / 9D ?? ??` — LDA abs,X, ADC abs,X, STA abs,X (freq lo calculation with carry-clear add)
- Second `BD ?? ?? / 7D ?? ?? / 9D ?? ??` — same pattern for freq hi
- `BD ?? ?? / 9D 00 D4` — LDA abs,X, STA $D400,X (final freq lo write, X-indexed)
- `BD ?? ?? / 9D 01 D4` — LDA abs,X, STA $D401,X (final freq hi write)
- `60` = RTS

Observations:
1. V3.2 uses **X-indexed SID writes** (like V3.1), not Y-indexed (V1.0).
2. V3.2 **re-introduces the ADC calculation** that V3.1 dropped — so V3.2 has a more complete frequency computation inline (not pre-computed).
3. The double `BD ?? ?? / 7D ?? ?? / 9D ?? ??` sequences are 16-bit addition: lo byte first (CLC + ADC), hi byte second (inherits carry). This is more explicit 16-bit arithmetic than V1.0's mixed B9/7D/99 pattern.
4. Since CSDb confirms V3.2 is the **internal development version** (1988, Fire-Eagle only) and V3.1 is the **public release** (1989, Magic Disk 64), this suggests V3.2 → V3.1 was a simplification: the full frequency arithmetic was moved upstream (pre-computed into a buffer), leaving V3.1 with direct table lookup. This is a common optimisation — precalculate during note-on, fast direct copy during play loop.

---

## Summary: Version Differences from Signatures

| Feature | V1.0 | V3.1 (public) | V3.2 (internal) |
|---------|------|---------------|-----------------|
| Voice index reg (SID write) | Y | X | X |
| Freq calculation inline | Yes (ADC abs,X + ADC #imm) | No (pre-computed) | Yes (CLC + ADC abs,X ×2) |
| Init store before freq write | No | Yes (A9 imm + STA abs,X + JMP) | Yes (same) |
| SID write opcode | STA $D400,Y / STA $D401,Y | STA $D400,X / STA $D401,X | STA $D400,X / STA $D401,X |
| Nibble-split for envelope | Yes (umbrella signature) | Yes (umbrella signature) | Yes (umbrella signature) |

OPEN: Is the V3.2 inline freq calc a different song format (freq stored un-transposed in song data) vs V3.1 (freq pre-transposed)? Or is V3.2 simply an earlier stage of the same routine before the pre-calc refactor was done?
