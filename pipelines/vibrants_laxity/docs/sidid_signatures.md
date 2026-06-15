---
source_url: local: /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg
fetched_via: local read
fetch_date: 2026-06-15
author: Lasse Oorni (cadaver) + contributors
content_date: unknown (local copy), github master confirmed identical signature set
reliability: primary
---

# SIDId Signatures — Vibrants/Laxity Family

Full extraction of all SIDId signature blocks for the Laxity/Vibrants/JCH family,
verbatim from the local sidid.cfg.  The github cadaver/sidid master (1923 lines) has
the same signatures; our local copy (2335 lines) has some additional non-family entries
but no extra family entries.

## Cross-reference: engine counts in hvsc84.db

| SIDId name               | HVSC #84 count |
|--------------------------|----------------|
| JCH_NewPlayer            | 3611           |
| SidFactory_II/Laxity     | 377            |
| Laxity_NewPlayer_V21     | 313            |
| Vibrants/Laxity          | 179            |
| Vibrants/JO              | 130            |
| JCH_Protracker           | 94             |
| Glover_NewPlayer_V21     | 67             |
| SidFactory/Laxity        | 39             |
| JCH_OldPlayer            | 32             |
| (Dane_NewPlayer)         | 5              |
| JCH_DigiPlayer           | 4              |
| 256bytes/Laxity          | 2              |
| **TOTAL**                | **4853**       |

---

## 1. 256bytes/Laxity (line 16)

```
4A 4A A8 88 88 30 07 46 FC 66 FB END
```

**Structure notes:** Very short (11 bytes). `4A 4A` = two LSR A; `A8` = TAY; `88 88` = DEY DEY;
`30 07` = BMI; `46 FC 66 FB` = LSR $FC / ROR $FB — this is a bitshift loop, not a standard
3-voice player. Likely a 256-byte intro player with no full instrument engine.

---

## 2. Vibrants/Laxity (lines 2038-2043)

**CSDb ref:** https://csdb.dk/release/?id=122333
**Author:** Thomas Egeskov Petersen (Laxity)
**HVSC count:** 179

```
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4 END
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4 END
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D END
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29 END
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90 END
```

### Per-fragment structure analysis

**Fragment 1** (freq/note write):
```
18          CLC
7D ?? ??    ADC abs,X          ; freq accumulate (for slide/vibrato?)
0A          ASL A              ; shift for note
A8          TAY                ; Y = note index
B9 ?? ??    LDA abs,Y          ; load freq high byte from table
48          PHA                ; save freq hi
B9 ?? ??    LDA abs,Y          ; load freq low byte (different table)
AC ?? ??    LDY abs            ; load aux (pulse width? voice offset?)
99 01 D4    STA ($D401),Y      ; write freq LOW to voice N freq lo ($D401/$D408/$D40F)
68          PLA                ; restore freq hi
99 00 D4    STA ($D400),Y      ; write freq HIGH to voice N freq hi ($D400/$D407/$D40E)
```
Key insight: `Y` offsets into $D400 so voice 1 = Y=0 ($D400/$D401), voice 2 = Y=7 ($D407/$D408),
voice 3 = Y=14 ($D40E/$D40F). The `99 01 D4` / `99 00 D4` pair = freq lo/hi writes for current voice.

**Fragment 2** (control register + duration advance):
```
FE ?? ??    INC abs,X          ; duration counter advance
BD ?? ??    LDA abs,X          ; load waveform/control byte
99 04 D4    STA ($D404),Y      ; write control reg to voice N ($D404/$D40B/$D412)
4C ?? ??    JMP ...            ; branch
BD ?? ??    LDA abs,X
29 ??       AND #imm           ; mask (gate? test bit?)
F0 ??       BEQ ...
A9 ??       LDA #imm           ; hardcoded waveform value
99 04 D4    STA ($D404),Y      ; write control reg (gate-off path)
```
`99 04 D4` = voice-Y control register write. Two paths: normal and gate-off.

**Fragment 3** (tempo / duration counters — 4 voice counters):
```
A9 ??       LDA #imm           ; reset value
8D ?? ??    STA abs            ; store
60          RTS
A2 ??       LDX #N             ; voice loop counter
CE ?? ??    DEC abs            ; decrement counter 1
10 ??       BPL (stay)         ; if not expired...
CE ?? ??    DEC abs            ; decrement counter 2
CE ?? ??    DEC abs            ; decrement counter 3
CE ?? ??    DEC abs            ; decrement counter 4
AD ?? ??    LDA abs
8D ?? ??    STA abs
```
Four `CE` decrements = 4 per-voice duration/effect counters, nested BMI structure.
This confirms: per-voice speed counters, similar to Hubbard nested DEC/BPL.

**Fragment 4** (instrument envelope):
```
C9 ?? B0 ?? 29 ?? 48    ; compare, branch, mask ADSR nibble, push
A9 ??       LDA #imm           ; ADSR value
9D ?? ??    STA abs,X          ; store to voice state
68          PLA
0A 0A       ASL A / ASL A      ; shift for table index
9D ?? ??    STA abs,X
4C ?? ??    JMP ...
29 ??       AND #imm           ; mask other nibble
```
ADSR/envelope handling: nibble-split encode (attack+decay hi/lo nibbles).

**Fragment 5** (filter / $D416):
```
AD ?? ??    LDA abs            ; load filter cutoff
18          CLC
79 ?? ??    ADC abs,Y          ; add sweep value (filter sweep?)
8D ?? ??    STA abs            ; store new cutoff
8D 16 D4    STA $D416          ; write to $D416 (Filter Cutoff Hi byte)
2C ?? ??    BIT abs            ; test bits
70 ??       BVS ...            ; branch on overflow (direction flip?)
D9 ?? ??    CMP abs,Y          ; compare to limit
90 ??       BCC ...            ; branch if below
```
`8D 16 D4` = direct write to $D416 (filter cutoff hi). Filter sweep with direction-flip
pattern similar to PWM logic. The `BIT`/`BVS`/`CMP`/`BCC` structure = clamp or
direction-reversal for the sweep.

---

## 3. Laxity_NewPlayer_V21 (line 1116)

**CSDb ref:** https://csdb.dk/release/?id=26563 (NP21.g4 final, Jan 2006, Maniacs of Noise + Vibrants)
**Author:** Thomas Egeskov Petersen (Laxity)
**HVSC count:** 313

```
99 04 D4 BD ?? ?? C9 FF F0 ?? 4C ?? ?? DE ?? ?? BD ?? ?? D0 ?? 4C END
```

**Structure notes:**
```
99 04 D4    STA ($D404),Y      ; write control reg (gate, waveform)
BD ?? ??    LDA abs,X          ; load duration/counter
C9 FF       CMP #$FF           ; compare to $FF sentinel (note end / loop marker)
F0 ??       BEQ ...            ; branch if note exhausted
4C ?? ??    JMP ...            ; continue
DE ?? ??    DEC abs,X          ; decrement duration counter (INC = advance forward)
BD ?? ??    LDA abs,X          ; reload
D0 ??       BNE ...            ; if not zero, stay in note
4C ?? ??    JMP ...            ; next note
```
Duration counter: `DE` (DEC abs,X) = decrements. `$FF` sentinel = end-of-sequence marker
(same as JCH NewPlayer family). The `99 04 D4` / `DE` / `C9 FF` pattern is the per-voice
note-advance kernel — a direct ancestor of JCH's V1 through V21 loop.

---

## 4. SidFactory/Laxity (lines 1742-1743)

**CSDb ref:** https://csdb.dk/release/?id=39519
**Author:** Thomas Egeskov Petersen (Laxity)
**Released:** 2006 (SID Factory 0.5 Alpha 1, Sep 2, 2006)
**HVSC count:** 39

```
A9 ?? 4C ?? ?? A9 ?? 9D ?? ?? A9 ?? 9D ?? ?? BD ?? ?? A8 29 02 D0 ?? 4C ?? ?? 98 29 FD 9D END
```

**Structure notes:**
```
A9 ??       LDA #imm           ; load immediate
4C ?? ??    JMP ...            ; (indirect dispatch?)
A9 ??       LDA #imm
9D ?? ??    STA abs,X          ; store to per-voice state
A9 ??       LDA #imm
9D ?? ??    STA abs,X          ; another per-voice state write
BD ?? ??    LDA abs,X          ; load voice state byte
A8          TAY                ; Y = index
29 02       AND #$02           ; test bit 1 (direction / gate flag?)
D0 ??       BNE ...            ; branch if set
4C ?? ??    JMP ...
98          TYA                ; restore A
29 FD       AND #$FD           ; clear bit 1 (direction reset)
9D ?? ??    STA abs,X          ; write back
```
Multi-state control byte with bit-flag manipulation. `29 02 / D0 / 29 FD` = toggle pattern
for a direction or enable flag. Very different from V21 — SidFactory was a fresh rewrite.

**SidFactory key features** (from CSDb release page):
- Dynamic multispeed switching
- Tempo table
- Portamento (added in Driver 5.02)
- Parallel instrument and slide
- Pointer configuration to various tables from within voices
- Pattern editing 8 steps at a time

---

## 5. SidFactory_II/Laxity (lines 1745-1746)

**CSDb ref:** https://csdb.dk/release/?id=210571
**Author:** Thomas Egeskov Petersen (Laxity), Jens-Christian Huus (JCH), Michel de Bree, Thomas Jansson
**Released:** 2020 (ongoing)
**HVSC count:** 377

```
C8 B1 ?? C9 FF D0 04 C8 B1 ?? A8 98 AND C9 7E F0 ?? 18 END
```

**Structure notes:**
```
C8          INY                ; advance pointer
B1 ??       LDA (zp),Y         ; load byte from sequence pointer (indirect Y)
C9 FF       CMP #$FF           ; end-of-sequence sentinel
D0 04       BNE ...            ; not end
C8          INY                ; advance past $FF
B1 ??       LDA (zp),Y         ; load loop target
A8          TAY                ; Y = new sequence position
98          TYA
AND         ...                ; (AND with something — AND is the mnemonic text)
C9 7E       CMP #$7E           ; compare to $7E (command marker?)
F0 ??       BEQ ...            ; branch if command
18          CLC
```
`B1 ??` (LDA (zp),Y) = indirect-Y sequence read — the sequencer walks through data via
a zero-page pointer. `$FF` = end-of-sequence / loop marker. `$7E` = embedded command byte
(tie note? instrument change? — compare with JCH's `C9 FD`, `C9 FE`, `C9 7E` markers).
This is the innermost note-fetch loop of the SF2 driver.

---

## 6. Vibrants/JO (lines 2045-2055)

**Author:** Poul-Jesper Olsen (JO) of Vibrants
**HVSC count:** 130

```
C9 80 D0 ?? BC ?? ?? C8 B1 END
29 7F DD ?? ?? D0 ?? A9 ?? 9D ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 F0 D0 ?? C8 B1 ?? 18 7D ?? ?? 9D ?? ?? C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? DE ?? ?? D0 ?? A9 01 9D ?? ?? FE END
BC ?? ?? B1 ?? C9 60 90 ?? 38 E9 60 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? D0 ?? 9D ?? ?? FE END
B9 ?? ?? 85 ?? DE ?? ?? ?? ?? BC ?? ?? B1 ?? C9 END
A2 ?? CE ?? ?? 10 ?? AD ?? ?? 8D ?? ?? EE ?? ?? EE ?? ?? EE END
C9 D0 90 ?? E9 D0 0A 0A 0A 9D END
A2 02 BC ?? ?? A9 00 99 05 D4 99 06 D4 A9 08 99 04 D4 CA 10 ?? 60 END
30 03 4C ?? ?? A9 00 9D ?? ?? A9 08 99 04 D4 98 48 A0 00 BD END
```

**Structure notes:** JO is a different Vibrants author (not Laxity). The `BC ?? ??` (LDY abs,X)
+ `B1 ??` (LDA (zp),Y) = indexed-indirect sequence access per voice, similar to SF2.
`$C9 FF D0 / A9 00 9D / DE / D0 / A9 01 9D` = note-end detection, gate-off ($D404→$08 gate-off),
duration decrement, restart. `A9 00 99 05 D4 / 99 06 D4 / A9 08 99 04 D4` = init: PW=$0000,
control=$08 (gate-off noise? or just waveform reset), voice 3 first (`CA 10 ??` = DEX/BPL
countdown from 2).

---

## 7. JCH_NewPlayer (lines 925-975) — base + sub-versions V1–V20, V0x, Dane

**CSDb ref:** https://csdb.dk/release/?id=14037 (JCH Editor V3.04 20G4, 1991)
**Author:** Jens-Christian Huus (JCH)
**HVSC count (all sub-versions combined):** 3611 + 94 (Protracker) + 32 (OldPlayer) = ~3737

### JCH_NewPlayer base (4 required fragments, ALL must match):

```
4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 48 29 10 END
A2 00 B9 ?? ?? 9D ?? ?? ?? ?? ?? B9 ?? ?? 9D ?? ?? ?? ?? ?? C8 C8 E8 E0 03 D0 END
B1 ?? 30 ?? F0 ?? C9 7E F0 END
AD ?? ?? F0 26 A2 03 B9 ?? ?? 3D ?? ?? 9D ?? ?? CA D0 F4 B9 ?? ?? 10 13 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? C8 C8 E8 E0 03 D0 ED A9 0F 8D END
```

Base fragment 1: `48 29 E0 C9 80 D0 / 68 48 29 10` — push A, mask top 3 bits (command type),
compare to $80 (high command range), branch. This is the command dispatch — top 2 bits
select note / instrument / control.

Base fragment 2: `A2 00 B9 ?? ?? 9D ?? ?? ... C8 C8 E8 E0 03 D0` — X=0 voice loop, LDA (abs,Y)
STA (abs,X) copy loop, C8 C8 E8 (INY INY INX) = 2-byte-per-voice step, E0 03 = 3 voices.

Base fragment 3: `B1 ?? 30 ?? F0 ?? C9 7E F0` — LDA (zp),Y (sequence byte read via ZP pointer),
BMI (note with duration bit set), BEQ (sequence-end $00), CMP #$7E BEQ (tie note marker).

Base fragment 4: `AD ?? ?? F0 26 A2 03 B9 ?? ?? 3D ?? ?? 9D ?? ?? CA D0 F4 B9 ?? ?? 10 13 ...
C8 C8 E8 E0 03 D0 ED A9 0F 8D` — filter enable check ($F0 26), 3-voice loop writing
envelope/wave data (`B9 LDA abs,Y` + `3D AND abs,X` + `9D STA abs,X`), then voice
copy loop (`B9 / 9D` ×2 pairs for freq lo/hi), C8 C8 E8 step, `A9 0F 8D` = master
vol $0F write to $D418.

### Version sub-signatures (only ONE needs to match alongside the base):

**(JCH_NewPlayer_V1):**
```
BC ?? ?? B9 ?? ?? 48 29 0F 9D ?? ?? 68 29 F0 4A 4A 9D ?? ?? 9D ?? ??
A9 00 9D ?? ?? 38 FD ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? B9 ?? ?? 48 29 F0 9D ?? ??
68 29 0F 9D ?? ?? B9 ?? ?? 9D ?? ?? B9 ?? ?? 48 29 F0 C9 10 D0 END
```
`BC` (LDY abs,X) + `B9` (LDA abs,Y) = indexed sequence access. `29 0F / 29 F0` = ADSR nibble split
(attack/decay nibbles). `4A 4A` = ASL×2 for table index. `38 FD ?? ??` = SEC / SBC abs,X = duration
subtraction. `C9 10 D0` = compare to $10 (gate-off threshold?).

**(JCH_NewPlayer_V2):**
```
38 FD ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? E0 00 D0 ?? B9 ?? ?? 48 29 0F F0 ??
0A 8D ?? ?? 8D ?? ?? 68 29 F0 18 6D ?? ?? 8D 18 D4 END
```
`E0 00 D0` = voice loop done check. `29 0F F0 / 0A / 8D / 8D / 29 F0 18 6D ?? ?? 8D 18 D4` =
note handling with `6D 18 D4` = ADC $D418 = ADD to master volume!  Vibrato accumulation
into $D418? No — this is ADSR combined into master vol byte write. `18 D4` = $D418 direct write.

**(JCH_NewPlayer_V3):**
```
DE ?? ?? 30 ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? 4C ?? ??
C9 FD D0 ?? A9 00 8D ?? ?? 8D 12 D4 4C ?? ??
BD ?? ?? 85 ?? BD ?? ?? 85 ?? 4C END
```
`DE` = DEC abs,X = duration decrement. `30 ??` = BMI (expired). `C9 FD D0` = CMP #$FD branch
(loop/restart sentinel $FD). `8D 12 D4` = STA $D412 = write to Filter/Mode register!
V3 adds filter mode control. `C9 FD` / `C9 FE` / `C9 FF` are the 3-sentinel system
(loop = $FD, rest = $FE, end = $FF).

**(JCH_NewPlayer_V4):**
```
4C ?? ?? 48 29 E0 C9 80 D0 ?? 68 29 1F 38 E9 0C 0A 9D ?? ?? C8 D0 ?? 68 A9 00 9D ??
?? F0 ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? A0 00 B1 ?? 30 ?? F0 ?? C9 7E F0 ?? C9 7F END
```
`29 1F 38 E9 0C 0A` = mask lower 5 bits, subtract $0C (octave offset?), ASL (×2 for
freq table). `C9 7E / C9 7F` = two new command sentinels in V4 vs V3.

**(JCH_NewPlayer_V5):**
```
C9 FF D0 ?? BD ?? ?? 9D ?? ?? 85 ?? BD ?? ?? 9D ?? ?? 85 ?? 4C ??
?? 29 7F 0A 9D ?? ?? FE ?? ?? D0 ?? FE ?? ?? D0 ?? A8 B9 ?? ?? 85 END
A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? FE ?? ?? A5 ?? 9D ?? ?? A5 ?? 9D ?? ?? 4C ??
?? 48 29 E0 C9 C0 D0 END
```
`FE ?? ?? D0 / FE ?? ?? D0` = INC abs,X BNE × 2 pairs = TWO independent increment-and-
continue steps (wave table and pulse table advance?). `29 7F 0A` = strip bit 7, ASL.
`C9 C0 D0` = compare $C0 (new command range). V5 adds wave/pulse table pointers.

**(JCH_NewPlayer_V6):**
```
C9 FF D0 ?? BD ?? ?? 9D ?? ?? 85 ?? BD ?? ?? 9D ?? ?? 85 ?? A0 00 B1 ?? 10 ??
C9 FF F0 ?? 29 7F 0A 9D ?? ?? FE ?? ?? D0 ?? FE END
```
`A0 00 B1 ?? 10` = LDY #0, LDA (zp),Y, BPL — sequence pointer now via ZP indirect
(switched from abs,Y to (zp),Y mode). `C9 FF F0` = end sentinel. Two `FE / D0` = still
two-table advance.

**(JCH_NewPlayer_V7):**
```
A2 02 CE ?? ?? 10 ?? A9 01 8D ?? ?? F0 ?? 4C ?? ?? BD ?? ?? F0 ?? C9 03 D0 ??
BD ?? ?? 85 ?? BD ?? ?? 85 ?? A0 00 B1 ?? C9 FF END
```
`A2 02 CE ?? ?? 10 ??` = X=2, DEC abs,X BPL — 3-voice outer loop (X=2,1,0) with
DEC/BPL. `C9 03 D0` = compare $03 (voice count check). `A9 01 8D` = LDA #1 STA = set
flag. `A0 00 B1 ?? C9 FF` = ZP indirect note read + $FF end check. V7 = multivice loop
restructured.

**(JCH_NewPlayer_V8):**
```
B1 ?? C9 7F D0 ?? A9 00 9D ?? ?? BD ?? ?? 18 69 01 9D ?? ?? 85 ??
BD ?? ?? 69 00 9D ?? ?? 85 ?? A0 00 B1 ?? C9 FF END
```
`C9 7F D0 / A9 00 9D` = CMP #$7F, not equal → play; else gate-off ($00 to control reg).
`18 69 01 / 69 00` = ADC #1 / ADC #0 — with-carry note/freq increment. V8 adds
pattern-advance / frequency-increment logic.

**(JCH_NewPlayer_V9):** (two sub-fragments)
```
A2 02 CE ?? ?? 10 ?? AD ?? ?? 8D ?? ?? D0 ?? BD ?? ?? D0 ?? 4C ?? ??
BD ?? ?? F0 ?? DE ?? ?? 4C ?? ?? BD AND B1 ?? C9 7F D0 ?? A9 00 9D ?? ??
A8 BD ?? ?? 18 69 01 9D ?? ?? 85 ?? BD ?? ?? 69 00 9D ?? ?? 85 ?? B1 ?? C9 FF END
A2 02 CE ?? ?? 10 ?? A9 ?? 8D ?? ?? D0 ?? BD ?? ?? F0 ?? DE ?? ?? 4C ?? ??
BD ?? ?? 9D ?? ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? A0 00 98 END
```
Two alternate sub-fragments in V9 (detected by AND/OR logic). `A0 00 98` = LDY #0 TYA
= clear A via Y. `AD ?? ?? 8D ?? ??` = copy-absolute (song position?). `DE` decrement.

**(JCH_NewPlayer_V10):**
```
B1 ?? C9 FF D0 ?? BD ?? ?? 9D ?? ?? BD ?? ?? 9D ?? ?? C9 FE D0 ?? A9 00 9D ??
?? BC ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? F0 ?? 4C ?? ?? BD ?? ?? 29 FE END
A2 02 CE ?? ?? 10 ?? A9 02 8D ?? ?? AD ?? ?? D0 ?? BD ?? ?? F0 ?? DE ?? ?? 4C ??
?? BD ?? ?? 9D ?? ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? A0 00 98 9D ?? ?? B1 ?? 10 ??
29 7F END
```
`C9 FE D0 / A9 00 9D / BC ?? ?? 99 04 D4` = $FE sentinel = rest/tie note, gate-off
sequence, then `BC` (LDY abs,X) `99 04 D4` (STA ($D404),Y) = direct voice control
register write. `29 FE` = AND #$FE = clear gate bit. V10 = explicit rest-note handling.

**(JCH_NewPlayer_V11):**
```
8A A8 BD ?? ?? F0 ?? D9 ?? ?? D0 ?? 8D ?? ?? BC ?? ?? B9 ?? ?? 29 F0 C9 F0 D0 ??
AD ?? ?? 9D ?? ?? 4C ?? ?? DE ?? ?? 4C ?? ?? BD END
```
`8A A8` = TXA TAY — copy voice counter to Y. `D9 ?? ?? D0` = CMP abs,Y BNE — Y-indexed
comparison (subtune or voice table?). `29 F0 C9 F0 D0` = mask top nibble, compare $F0
(special command range). V11 adds multi-subtune support.

**(JCH_NewPlayer_V12):**
```
A2 02 BD ?? ?? D0 03 4C ?? ?? BD ?? ?? F0 08 A9 00 9D ?? ?? 4C ?? ?? BD ?? ?? C9 01
D0 05 FE ?? ?? D0 06 DE ?? ?? 4C ?? ?? BD ?? ?? 9D ?? ?? BD ?? ?? 85 ?? BD END
```
`C9 01 D0 05 FE / D0 06 DE` = compare 1, not equal, INC abs (wave table?), BNE continue;
DEC abs (duration). `F0 08 A9 00 9D` = if zero, gate-off ($00 → control). V12 = tighter
wave-table advance / gate-off integration.

**(JCH_NewPlayer_V13):**
```
A2 02 BD ?? ?? C9 02 D0 ?? BC ?? ?? B9 ?? ?? BC ?? ?? 99 ?? ?? BC ?? ?? B9 ?? ??
BC ?? ?? 99 ?? ?? A9 09 99 ?? ?? CA 10 D9 A5 ?? 48 A5 ?? 48 END
```
`C9 02 D0` = compare $02 (voice/channel count check). `BC / B9 / BC / 99 × 2 pairs` =
doubled copy via indexed LDY/LDA/STA (freq lo + hi per voice). `A9 09 99 ?? ??` =
LDA #$09 STA (wave table?). `CA 10 D9` = DEX BPL loop. `A5 48 A5 48` = ZP push pairs
(saving voice pointers). V13 = 2-byte-per-voice frequency copy loop.

**(JCH_NewPlayer_V14):**
```
A2 02 BD ?? ?? C9 02 D0 ?? BC ?? ?? B9 ?? ?? BC ?? ?? 99 ?? ?? BC ?? ?? B9 ?? ??
BC ?? ?? 99 ?? ?? AD ?? ?? F0 09 AD AND 98 9D ?? ?? B1 ?? 10 0F 0A 9D ?? ?? FE ??
?? D0 03 FE ?? ?? C8 B1 ?? A8 END
```
`AD ?? ?? F0 09 AD` = load absolute, branch if zero, load next absolute — filter check.
`98 9D` = TYA STA abs,X = store Y (voice index). `B1 ?? 10 0F 0A 9D` = ZP indirect read,
BPL skip (note bit), ASL (×1), STA abs,X. `FE D0 / FE` = dual INC-continue. V14 adds
filter select logic.

**(JCH_NewPlayer_V15):**
```
A2 02 A5 ?? 48 A5 ?? 48 BD ?? ?? D0 03 4C AND BD ?? ?? F0 19 DD ?? ?? D0 0E A9 00
9D ?? ?? BD ?? ?? BC ?? ?? 99 ?? ?? DE ?? ?? 4C END
```
`A5 ?? 48 A5 ?? 48` = ZP push ZP push (save two ZP voice pointers on stack). `DD ?? ??
D0 0E` = CMP abs,X BNE (compare with previous note — tie-note check?). `A9 00 9D` = 
gate-off. V15 = stacked voice pointer saves, tie-note detection.

**(JCH_NewPlayer_V17):**
```
A5 ?? 48 A5 ?? 48 A2 02 BD ?? ?? D0 03 4C ?? ?? BD ?? ?? D0 03 4C ?? ?? C9 02 F0 06
DE ?? ?? 4C END
```
V16 skipped in sidid (no V16 signature). `C9 02 F0 06 DE` = CMP #2, BEQ, DEC — 3-way
counter (0/1/2). Two `BD D0 03 4C` guards = voice active checks. V17 = re-ordered
outer/inner loops.

**(JCH_NewPlayer_V18):**
```
A5 ?? 48 A5 ?? 48 BD ?? ?? D0 03 4C ?? ?? BD ?? ?? 30 17 BD ?? ?? F0 59 DD ?? ?? D0
26 A9 ?? 9D END
```
`30 17` = BMI (if note has sign bit set = some flag). `F0 59` = BEQ +89 (long branch =
skip-ahead). `DD D0 26` = CMP BNE +38. `A9 ?? 9D` = LDA imm STA abs,X = new instrument.
V18 = larger branches, long-range tie / instrument-change logic.

**(JCH_NewPlayer_V19):**
```
4C ?? ?? DE ?? ?? 4C ?? ?? DE ?? ?? BD ?? ?? 85 ?? BD ?? ?? 85 ?? A0 00 98 9D ?? ??
B1 ?? 10 0F END
```
Two `DE 4C / DE` pairs + two `BD 85` pairs + `A0 00 98 9D / B1 10 0F` = two parallel
duration decrements, two ZP pointer loads, `TYA 9D` voice save, ZP indirect note read.
V19 = parallel dual-channel decrement step.

**(JCH_NewPlayer_V20):**
```
48 A5 ?? 48 CE ?? ?? 10 1D AD ?? ?? 8D ?? ?? C9 02 B0 13 AC ?? ?? B9 ?? ?? 8D ?? ??
CE ?? ?? 10 05 A9 END
```
`CE ?? ?? 10 1D` = DEC BPL +29 — tempo counter with 30-tick range. `AD 8D` = load-store
absolute (song position counter?). `C9 02 B0 13` = CMP #2 BCS — subtune/speed comparison.
`AC ?? ?? B9 ?? ?? 8D` = LDY abs + LDA abs,Y + STA abs = indexed song lookup. V20 = final
production version (JCH's "last standard player on C64", May 1991 per chordian timeline).

**(JCH_NewPlayer_V0x):**
```
98 99 00 D4 C8 C0 19 D0 F8 A9 88 8D 04 D4 8D 0B D4 8D 12 D4 A9 ?? 8D 05 D4 8D 0C D4 AND
8D 13 D4 A9 END
```
Init/reset sequence: `98 99 00 D4 C8 C0 19 D0 F8` = TYA STA ($D400),Y INY CPY #$19 BNE =
clear $D400–$D418 (25 registers). `A9 88 8D 04 D4 8D 0B D4 8D 12 D4` = LDA #$88 STA $D404
STA $D40B STA $D412 = set all 3 voice control regs to $88 (test-bit + gate = hard-restart).
`8D 05 D4 8D 0C D4 AND 8D 13 D4` = AD hi = $00 for all 3 voices. This is the JCH hard-restart
init pattern — "V0x" = common init present across ALL versions.

**(Dane_NewPlayer):**
```
30 03 4C ?? ?? 4C ?? ?? BD ?? ?? 85 02 BD ?? ?? 85 03 A0 00 98 9D ?? ?? B1 02 10 0F 0A 9D END
0A 8D ?? ?? EE ?? ?? D0 ?? EE ?? ?? 4C END
```
`85 02 / 85 03` = hardcoded ZP addresses $02/$03 (vs JCH's wildcards) — Dane uses fixed
ZP voice pointer. `B1 02` = LDA ($02),Y = indirect through fixed $0002. `EE ?? ?? D0 / EE`
= INC abs BNE + INC — dual-table advance (same as JCH V5+ pattern). Dane variant from 2011
(NP22-25) is NP-family but with hardcoded ZP base.

---

## 8. Glover_NewPlayer_V21 (line 743)

```
B9 ?? ?? 85 ?? 29 F0 C9 20 F0 ?? B0 ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? A5 ?? 29 0F 9D ?? ?? A9 ?? 9D END
```

**HVSC count:** 67
**Structure notes:** `B9` (LDA abs,Y) = table read. `29 F0 C9 20 F0` = mask top nibble,
compare $20, BEQ = waveform $20 = pulse-only test. `B0 ??` = BCS. `9D` pair = STA abs,X
×2 (freq lo + hi). `29 0F / 9D` = lower nibble mask + store (ADSR nibble). `A9 ?? 9D` =
immediate STA (hardcoded envelope byte). Glover uses V21 player but with hardcoded
instrument starts.

---

## 9. JCH_OldPlayer (line 977)

```
48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D ?? ?? 68 18 6D ?? ?? 8D ?? ?? 68 END
```

**HVSC count:** 32
**Structure notes:** `PHA 18 4A×4 29 07` = push, CLC, LSR×4, AND #$07 = extract 3-bit
note/octave field. `0A×3` = ASL×3 = ×8 (table index). `48 0A 8D` = PHA ASL STA (pulse?).
`68 18 6D ?? ?? 8D ?? ?? 68` = PLA CLC ADC abs STA abs PLA (accumulate + store — freq
addition). OldPlayer (1987) = simpler nibble-field format without sequences.

---

## 10. JCH_Protracker (line 980)

```
8D ?? ?? AD ?? ?? 8D 18 D4 60 A2 02 BD ?? ?? C9 02 D0 2C BC ?? ?? B9 ?? ?? BC ?? ??
99 05 D4 BC ?? ?? B9 ?? ?? BC ?? ?? 99 06 D4 AD ?? ?? F0 09 AD ?? ?? 99 04 D4 END
```

**HVSC count:** 94
**Structure notes:** `8D 18 D4` = STA $D418 (master volume). `60` = RTS (init complete).
`A2 02 BD ?? ?? C9 02 D0 2C` = X=2, LDA abs,X, CMP #$02 BNE — 3-voice loop. `BC B9 BC 99 05 D4` =
LDY abs,X + LDA abs,Y + LDY abs,X + STA ($D405),Y = PW lo write! `99 06 D4` = STA ($D406),Y
= PW hi write. `AD ?? ?? F0 09 AD ?? ?? 99 04 D4` = filter check then control write ($D404).
JCH_Protracker = NP family player focused on pulse-width + control; likely a compact variant.

---

## 11. JCH_DigiPlayer (line 922)

```
D0 ?? AD ?? ?? F0 ?? A0 00 8C ?? ?? B1 ?? 4A 4A 4A 4A 18 END
```

**HVSC count:** 4
**Structure notes:** `AD ?? ?? F0 ??` = LDA abs BEQ = digi pointer check. `A0 00 8C ?? ??` =
LDY #0, STY abs = reset digi position. `B1 ?? 4A 4A 4A 4A 18` = LDA (zp),Y then 4× LSR +
CLC = extract 4-bit sample nibble. This is the digi sample nibble-extract loop.

---

## Comparison: local sidid.cfg vs cadaver/sidid github master

| Metric | Local | Github |
|--------|-------|--------|
| Total lines | 2335 | 1923 |
| Vibrants/Laxity signatures | IDENTICAL | IDENTICAL |
| JCH_NewPlayer sub-versions | V1–V20, V0x, Dane | Same set |
| SidFactory/Laxity | Same | Same |
| SidFactory_II/Laxity | Same | Same |
| Extra entries local | Yes (non-family) | — |

Local copy is a superset of the github version. No new Laxity/JCH family entries were
found in github that our local copy lacks.
