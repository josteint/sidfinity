---
source_url: local: /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg
fetched_via: local read (opcode analysis = this session, not prior work)
fetch_date: 2026-06-15
author: opcode analysis by Claude claude-sonnet-4-6 (Anthropic) based on 6502 ISA + SID register map
content_date: 2026-06-15
reliability: secondary (derived — not confirmed against running player)
---

# SIDId Signature Opcode Analysis — Vibrants/Laxity Family

This document decodes what each SIDId signature fragment reveals about the per-frame
SID-register-write model for each engine family.

## Notation

`$Dxxx` = SID register write addresses ($D400–$D418).
`abs,X` = absolute indexed by X (voice loop counter).
`abs,Y` = absolute indexed by Y (note/table index).
`(zp),Y` = zero-page indirect Y (sequence pointer walk).
`??` = wildcard byte (relocation-variable address).

## 1. Vibrants/Laxity — the original Laxity editor

### Fragment 1: Frequency write (note-on path)

```asm
18           CLC
7D ?? ??     ADC abs,X        ; accumulate freq (slide delta)
0A           ASL A            ; x2 for word-aligned table
A8           TAY              ; Y = note index * 2
B9 ?? ??     LDA abs,Y        ; freq_table_hi[note]
48           PHA
B9 ?? ??     LDA abs,Y        ; freq_table_lo[note]  (adjacent table, same Y)
AC ?? ??     LDY abs          ; Y = voice_stride (0, 7, or 14)
99 01 D4     STA $D401,Y      ; voice_N_freq_lo
68           PLA
99 00 D4     STA $D400,Y      ; voice_N_freq_hi
```

**Inference:** The `CLC / ADC abs,X` before the note load = per-voice slide accumulator.
The freq table is TWO adjacent tables (hi and lo byte tables indexed by same Y).
Voice stride via LDY abs → Y=0/7/14 for voices 1/2/3.

Writes per frame per voice (note-on): $D400+Y (freq hi), $D401+Y (freq lo).

### Fragment 2: Control register write + duration advance

```asm
FE ?? ??     INC abs,X        ; advance duration counter (INC because counting up to limit?)
BD ?? ??     LDA abs,X        ; load control/waveform byte
99 04 D4     STA $D404,Y      ; voice_N_control (gate, waveform, test, ring, sync)
4C ?? ??     JMP (normal path)
BD ?? ??     LDA abs,X        ; reload (gate-off path)
29 ??        AND #imm         ; mask to clear gate bit
F0 ??        BEQ ...
A9 ??        LDA #imm         ; hardcoded gate-off waveform
99 04 D4     STA $D404,Y      ; voice_N_control (gate-off)
```

**Inference:** `FE` = INC abs,X = duration counting UP (not decrement like Hubbard DEC).
Two paths for $D404 write: normal waveform byte (with gate), and gate-off value.
The `AND #imm / BEQ` before the second `99 04 D4` = masking and branching on gate bit.

Writes per frame per voice: $D404+Y (control register), once per note event.

### Fragment 3: Tempo / 4× DEC duration counters

```asm
A9 ??        LDA #imm         ; reload value (tempo)
8D ?? ??     STA abs          ; reset tempo counter
60           RTS
A2 ??        LDX #N           ; X = voice index (2 for voice 3 down to 0)
CE ?? ??     DEC abs          ; decrement counter 1 (voice N duration)
10 ??        BPL (active)
CE ?? ??     DEC abs          ; decrement counter 2 (effect 1?)
CE ?? ??     DEC abs          ; decrement counter 3 (effect 2?)
CE ?? ??     DEC abs          ; decrement counter 4 (effect 3?)
AD ?? ??     LDA abs
8D ?? ??     STA abs
```

**Inference:** 4 DEC abs counters per voice in a nested BPL cascade = nested speed counters.
This is the SAME structure as Hubbard '85's nested DEC/BPL but with 4 levels instead of 2.
Outer counter = note duration; inner 3 = effect counters (vibrato, arp, slide?).

### Fragment 4: ADSR nibble handling

```asm
C9 ??        CMP #imm         ; compare
B0 ??        BCS ...
29 ??        AND #imm         ; mask nibble (e.g., #$0F or #$F0)
48           PHA
A9 ??        LDA #imm         ; attack value
9D ?? ??     STA abs,X        ; store to per-voice ADSR cache
68           PLA
0A 0A        ASL A / ASL A    ; shift low nibble up (×4) for decay position?
9D ?? ??     STA abs,X        ; store shifted value
4C ?? ??     JMP
29 ??        AND #imm         ; mask other nibble
```

**Inference:** ADSR is stored in split nibbles in the player state. PHA/PLA to save one nibble
while writing the other. `0A 0A` (×2 ASL) = shift ×4 — for positioning in the ADSR byte.
This implies the Vibrants/Laxity format encodes attack+decay in a single byte (hi/lo nibble)
and sustain+release in another, same as standard SID ADSR register layout.

Writes: $D405+Y (ATK/DEC), $D406+Y (SUS/REL) — inferred, not directly visible in fragment 4.

### Fragment 5: Filter sweep → $D416

```asm
AD ?? ??     LDA abs          ; load filter cutoff current value
18           CLC
79 ?? ??     ADC abs,Y        ; add sweep step (Y = voice or filter voice index)
8D ?? ??     STA abs          ; save new cutoff
8D 16 D4     STA $D416        ; write filter cutoff hi byte
2C ?? ??     BIT abs          ; test direction flag
70 ??        BVS ...          ; branch if overflow (V flag = direction bit in status byte?)
D9 ?? ??     CMP abs,Y        ; compare to limit
90 ??        BCC ...          ; branch if below limit
```

**Inference:** Direct `STA $D416` (filter cutoff hi). The `BIT abs / BVS` pattern = the BIT
instruction copies bit 6 of the memory byte into the V flag — so bit 6 of the direction-flag
byte = filter sweep direction. `CMP abs,Y / BCC` = lower clamp. Presumably an upper clamp
follows (not in signature). This is the ONLY filter fragment visible — the Vibrants/Laxity
filter model writes ONLY $D416 (cutoff hi), not $D415 (cutoff lo).

## 2. Laxity_NewPlayer_V21 — minimal fragment

```asm
99 04 D4     STA $D404,Y      ; control register write (shared with Vibrants/Laxity)
BD ?? ??     LDA abs,X        ; load per-voice duration/state
C9 FF        CMP #$FF         ; end-of-sequence sentinel
F0 ??        BEQ (next_pattern)
4C ?? ??     JMP (active note)
DE ?? ??     DEC abs,X        ; decrement duration
BD ?? ??     LDA abs,X        ; reload duration
D0 ??        BNE (still active)
4C ?? ??     JMP (load next note)
```

**Inference:** `99 04 D4` shared with Vibrants/Laxity = same voice-stride Y layout.
Duration model: DEC abs,X, check zero → advance. $FF = sequence end. Note duration is
COUNT-DOWN to zero (unlike Vibrants/Laxity which uses INC + BPL limit).

## 3. JCH_NewPlayer — key structural writes per version

### Hard-restart init (V0x fragment — present in ALL versions)

```asm
98           TYA
99 00 D4     STA $D400,Y      ; zero all SID regs (Y walks 0..24)
C8           INY
C0 19        CPY #$19         ; 25 registers = $D400..$D418
D0 F8        BNE loop
A9 88        LDA #$88
8D 04 D4     STA $D404        ; voice 1 control = $88 (test+gate)
8D 0B D4     STA $D40B        ; voice 2 control = $88
8D 12 D4     STA $D412        ; voice 3 control = $88
A9 ??        LDA #imm
8D 05 D4     STA $D405        ; voice 1 ATK/DEC
8D 0C D4     STA $D40C        ; voice 2 ATK/DEC
(AND)
8D 13 D4     STA $D413        ; voice 3 ATK/DEC
A9 ??        LDA #imm         ; (sustain/release value)
```

**Init write sequence confirmed:** 
1. Zero $D400–$D418 (25 regs, loop)
2. $D404/$D40B/$D412 = $88 (hard-restart pulse)
3. $D405/$D40C/$D413 = attack/decay value
4. $D406/$D40D/$D414 = sustain/release value (implied)

This is the JCH "hard restart" that sidplay documentation praises.

### Base fragment 4: Master vol + voice data copy

```asm
A2 03        LDX #3           ; 3 voices
B9 ?? ??     LDA abs,Y        ; load voice data byte 1
3D ?? ??     AND abs,X        ; mask with per-voice mask
9D ?? ??     STA abs,X        ; store masked result
CA           DEX
D0 F4        BNE loop
B9 ?? ??     LDA abs,Y        ; load freq lo
9D ?? ??     STA abs,X        ; store (freq lo path)
B9 ?? ??     LDA abs,Y        ; load freq hi
9D ?? ??     STA abs,X        ; store (freq hi path)
C8 C8        INY INY          ; advance Y by 2 (2 bytes per note entry)
E8           INX
E0 03        CPX #3
D0 ED        BNE loop         ; 3 voices
A9 0F        LDA #$0F
8D 18 D4     STA $D418        ; master volume = $0F (every frame!)
```

**Key structural write:** `STA $D418` with $0F = master volume written EVERY frame.
This is the JCH equivalent of the Hubbard master_vol_every_frame knob.

### Version evolution in SID-register write terms

| Version | New register writes discovered |
|---------|-------------------------------|
| V1 | ADSR nibble split (PHA/PLA, `29 0F / 29 F0`) |
| V2 | Master vol accumulation (`6D ?? ?? 8D 18 D4`) — ADSR into vol? |
| V3 | Filter mode `8D 12 D4` = $D412; sentinel $FD (loop) |
| V4 | New command sentinels $7E/$7F |
| V5 | Wave/pulse table advance (`FE ?? ?? D0` × 2) |
| V6 | ZP indirect sequence pointer `B1 ??` |
| V7 | Outer 3-voice DEC/BPL loop restructured |
| V8 | Gate-off `C9 7F / A9 00 9D` (control=$00) |
| V10 | Explicit rest note: gate-off + `BC / 99 04 D4` direct write |
| V11 | Multi-subtune support (`D9 ?? ?? D0` Y-indexed compare) |
| V12 | Integrated wave-table advance with gate-off |
| V14 | Filter select: `AD ?? ?? F0 09 AD` = conditional filter enable |
| V20 | Tempo counter `CE BPL` (song timing) |

## 4. SidFactory_II/Laxity — modern driver

```asm
C8           INY              ; advance sequence position
B1 ??        LDA (zp),Y       ; fetch next byte from sequence
C9 FF        CMP #$FF         ; end-of-sequence?
D0 04        BNE not_end
C8           INY              ; skip $FF
B1 ??        LDA (zp),Y       ; fetch loop target byte
A8           TAY              ; Y = loop target position
98           TYA
; (AND with bitmask here)
C9 7E        CMP #$7E         ; command byte?
F0 ??        BEQ handle_cmd
18           CLC              ; start freq calculation
```

**Inference:** Sequence byte parsing:
- $FF = end-of-sequence: next byte is loop target (pattern jump offset)
- $7E = embedded command (tie note? effect trigger?)
- Any other value = note byte → CLC before freq calc

`B1 ??` (LDA (zp),Y) = the ZP indirect walk pattern, same family as JCH V6+.
The `INY` before the read = pointer is BEFORE the next byte (Y advances then reads).

This matches SF2 user manual: order list = `[transpose_byte][sequence_number]`, sequences
are walked with an advancing pointer; $FF + jump-byte = loop marker.

## Summary: Per-Frame Write Model

### Vibrants/Laxity (per voice per frame):
1. $D400+Y / $D401+Y (freq hi/lo) — note-on only, or every frame with slide
2. $D404+Y (control register) — every note event
3. $D416 (filter cutoff hi) — every frame (if filter sweep active)
4. (Implied) $D405+Y/$D406+Y (ADSR) — on note-on
5. (Implied) $D407+Y/$D408+Y, $D40E+Y/$D40F+Y — for voices 2/3 (same pattern)

The `FE` (INC abs,X) duration model means duration counts UP to a per-note limit value,
not DOWN to zero (opposite of Hubbard DEC model).

### JCH_NewPlayer (per frame, all versions):
1. $D418 = $0F every frame (base fragment 4)
2. $D400/$D401 / $D407/$D408 / $D40E/$D40F (freq, via B9/9D pairs in base frag 4)
3. $D404/$D40B/$D412 (control, via `99 04 D4` in V10+ direct or base frag)
4. $D405/$D40C/$D413 (ADSR, nibble-split, V1+)
5. $D412 (filter mode, V3+)
6. (Inferred) $D406/$D40D/$D414 (SUS/REL, nibble-split)

Duration model: DEC abs,X, BPL (counting DOWN, BMI = expired) in V3+; earlier versions
use SEC/SBC (V1: `38 FD ?? ??` = SEC SBC abs,X).

### SidFactory_II:
1. Sequence walk via ZP indirect `B1 ??`
2. $FF = loop; $7E = embedded command
3. Register writes determined by the specific driver version (11.xx)
4. SF2 project files (.sf2) contain all musical data; the driver is a separate binary

---

## Open questions (not resolvable from signatures alone)

1. **Vibrants/Laxity pulse width:** No `$D402/$D403` or `$D409/$D40A` visible in signatures.
   Does the original Laxity editor have a pulse-width sweep? The 5 fragments cover freq,
   control, filter, ADSR, and duration — pulse is conspicuously absent. Possible that PW
   is static per-instrument and the signature fragments happen not to capture the PW write.

2. **Vibrants/Laxity voice stride:** `AC ?? ??` = LDY abs loads the stride. Is this set
   to a fixed value at voice-dispatch time, or does it vary per-call? This affects whether
   the voice loop is a single subroutine called 3× or inlined 3× (affecting frame structure).

3. **JCH V2 `6D ?? ?? 8D 18 D4`:** ADC abs + STA $D418. Is this a master-vol fade
   (accumulate from zero) or a per-frame volume sum (sum of voice volumes)? The surrounding
   context (after ADSR nibble handling) suggests it's ADSR-related accumulation.

4. **Laxity_NewPlayer_V21 single-fragment:** Only one fragment signature. The full player
   must have more structure (freq, ADSR, filter at minimum) — the short signature was chosen
   for disambiguation only. A full disassembly is needed for the complete write model.

5. **Vibrants/JO:** Is Poul-Jesper Olsen's engine related to the Laxity editor (fork? copy?
   independent development within Vibrants)? The `BC ?? ?? B1 ??` (LDY abs,X + LDA (zp),Y)
   combined access = more sophisticated than Laxity's `AC ?? ?? 99` stride model, suggesting
   JO developed his own player independently.
