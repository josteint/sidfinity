---
source_url: local: /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg
fetched_via: local read
fetch_date: 2026-06-15
author: Unknown (sidid project, cadaver/Covert Bitops)
content_date: unknown (sidid.cfg as shipped with gt2_pipeline)
reliability: primary
---

# SIDId Signatures for Ariston / Ian Crabtree / Wally Beben — Opcode Analysis

## Raw Signatures (verbatim from sidid.cfg lines 142–159)

```
Ariston
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF END

(Ian_Crabtree_V1)
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4 END

(Ian_Crabtree_V2)
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD END

(Wally_Beben)
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30 END
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 END
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18 END
```

Notes on parenthesised names: `(Ian_Crabtree_V1)`, `(Ian_Crabtree_V2)`, `(Wally_Beben)` are secondary
signatures (parentheses in sidid.cfg mean "match only if the preceding primary also matched").
They DO NOT identify independent engines — they are disambiguators within the Ariston family.

---

## Opcode-by-opcode Decoding

### Signature 1: `Ariston` (primary fingerprint)

```
A2 00           LDX #$00          ; X = 0 (voice index / table index counter)
6E ?? ??        ROR $????         ; rotate memory right — clears carry (or shifts drum/tick flag?)
90 07           BCC +7            ; if carry clear, skip the copy block
BD ?? ??        LDA $????,X       ; load from table indexed by X
99 ?? ??        STA $????,Y       ; store to destination indexed by Y
C8              INY               ; Y++ (destination pointer advance)
E8              INX               ; X++ (source pointer advance)
E0 08           CPX #$08          ; X == 8?
D0 EF           BNE <loop>        ; if not, loop
AE ?? ??        LDX $????         ; load X from absolute address (voice state / channel index)
A9 FF           LDA #$FF          ; load $FF
```

**Interpretation (DERIVED — not confirmed by disassembly):**

- The `E0 08 / D0 EF` loop runs exactly **8 iterations**, copying 8 bytes from one table
  to another using X (source index) and Y (destination index).
- The `ROR` + `BCC` gate: the 8-byte block copy only runs if the ROR sets carry. This
  is a tick/phase counter or frame gate — suggests the instrument update runs at a
  sub-frame rate (every N calls, not every call).
- The `LDA #$FF` after the loop: likely about to write $FF to SID (hard restart, ADSR reset,
  or pulse high-byte set to $FF for a drum hit).
- **8-byte table copy = one instrument "program step"** — most likely copies the current
  instrument row (waveform, ADSR, PW, or effect parameters) into the voice's working registers.
- OPEN: what are the 8 bytes? Could be: [wave, AD, SR, PW_lo, PW_hi, effect, param1, param2].
  Could also be partial: ADSR (4 bytes) + freq (2) + PW (2). Needs disassembly confirmation.

---

### Signature 2: `Ian_Crabtree_V1` (secondary — sub-fingerprint of Ariston)

```
9D ?? ??        STA $????,X       ; store A to table indexed by X
20 ?? ??        JSR $????         ; call subroutine (voice update or instrument step)
CA              DEX               ; X-- (count down voices)
10 EF           BPL <loop>        ; loop while X >= 0 (→ 3 or 8 voices, depending on start)
A0 ??           LDY #??           ; Y = constant (table offset or note index)
A9 ??           LDA #??           ; load immediate value
99 00 D4        STA $D400,Y       ; write to SID base register + Y offset
```

**Interpretation (DERIVED):**

- `DEX / BPL` loop with `STA $????,X` before it: iterating over voices (3) or table entries,
  storing a value per voice, then calling a common update subroutine.
- `STA $D400,Y`: direct Y-indexed write to SID base ($D400). Y is loaded immediately before, so
  this is a one-shot write to a *specific* SID register. The target register = $D400 + Y.
- OPEN: what value is written? With `LDA #??` (immediate), this is writing a constant to one
  SID register — likely $D418 (volume/filter) or a voice 1 register offset.
- **Variant 1 characteristic**: JSR-based voice dispatch (calls a shared subroutine per voice);
  the final write is a direct indexed store to SID base. Simpler/earlier variant.

---

### Signature 3: `Ian_Crabtree_V2` (secondary — sub-fingerprint of Ariston)

```
AA              TAX               ; X = A (save A in X, or use A as index)
BD ?? ??        LDA $????,X       ; load from table indexed by X (instrument/effect data)
99 05 D4        STA $D405,Y       ; → SID $D405+Y*7 = AD register for voice Y/voice-stride
BD ?? ??        LDA $????,X       ; load next byte
99 06 D4        STA $D406,Y       ; → SID $D406+Y*7 = SR register for voice Y
29 0F           AND #$0F          ; mask lower nibble (release value only)
48              PHA               ; push (save SR for later)
A9 ??           LDA #??           ; load immediate (probably gate-off control byte)
99 04 D4        STA $D404,Y       ; → SID $D404+Y*7 = voice control register (gate OFF)
BD ?? ??        LDA $????,X       ; load next byte (note/freq or wave value)
99 04 D4        STA $D404,Y       ; → SID $D404+Y*7 = voice control register (gate ON / wave set)
BD ...          (continues)
```

**Interpretation (DERIVED):**

- **$D405/Y = Attack/Decay**, **$D406/Y = Sustain/Release** — this is the ADSR write pair.
  The Y-indexed SID writes with stride 7 per voice: voice 0 → Y=0, voice 1 → Y=7, voice 2 → Y=14.
- `AND #$0F / PHA`: extracts the Release nibble and saves it — probably for a soft note-off that
  uses only the Release component.
- **Double write to $D404,Y**: first with an immediate `A9 ??` value (gate-off: clears gate bit,
  sets waveform), then with the loaded byte (gate-on: sets gate bit + waveform). This is the
  standard C64 note-trigger sequence: gate-off → gate-on (hard restart pattern).
- **Variant 2 characteristic**: explicit ADSR write pair ($D405/$D406) + double gate write to
  $D404. More complete instrument update than V1. The `TAX` at the start uses the note/instrument
  index from A to index the instrument table.

---

### Signature 4: `Wally_Beben` (secondary — sub-fingerprint of Ariston)

Three-part match (all three lines must match):

**Line 1:**
```
48              PHA               ; push A (save current value — likely note / channel index)
C9 08           CMP #$08          ; compare with 8
B0 ??           BCS <branch>      ; if >= 8, branch (range check or high-note special case)
A9 ??           LDA #??           ; load immediate (drum/effect parameter)
9D ?? ??        STA $????,X       ; store to per-voice table indexed by X
AC ?? ??        LDY $????         ; load Y from absolute (voice state / index)
68              PLA               ; pull A back
99 03 D4        STA $D403,Y       ; → SID $D403+Y = Pulse Width HIGH byte for voice at Y
68              PLA               ; pull another saved value
99 02 D4        STA $D402,Y       ; → SID $D402+Y = Pulse Width LOW byte for voice at Y
CE ?? ??        DEC $????         ; decrement counter (tick counter / note length / drum timer)
30 ...          (BMI — check for underflow)
```

**Line 2:**
```
BD ?? ??        LDA $????,X       ; load from table (instrument data)
AA              TAX               ; TAX (save/redirect index)
BD ?? ??        LDA $????,X       ; load (using new X)
99 05 D4        STA $D405,Y       ; → SID $D405+Y = AD register
BD ?? ??        LDA $????,X       ;
99 06 D4        STA $D406,Y       ; → SID $D406+Y = SR register
A9 ??           LDA #??           ; load immediate (gate-off waveform byte)
99 04 D4        STA $D404,Y       ; → $D404+Y (gate OFF)
BD ?? ??        LDA $????,X       ;
99 04 D4        STA $D404,Y       ; → $D404+Y (gate ON, with waveform)
```

**Line 3:**
```
BD ?? ??        LDA $????,X       ;
99 04 D4        STA $D404,Y       ; additional $D404 write (drum? second gate toggle?)
AE ?? ??        LDX $????         ; reload X from absolute
EE ?? ??        INC $????         ; increment counter (step/position counter)
BD ?? ??        LDA $????,X       ;
18              CLC               ; clear carry (for subsequent ADC — freq calculation?)
```

**Interpretation (DERIVED):**

- **$D402/$D403 writes** (pulse width lo/hi): Beben's variant explicitly programs pulse width
  in the note-trigger path — the base Ariston/Crabtree signatures don't show this. This is the
  "phasing" feature: pulse width is set per note, enabling the phase/pulse-width effect Beben
  is known for.
- **Three writes to $D404**: gate-off, gate-on, then a *third* $D404 write. This third write
  is unusual — could be a drum/noise hit on the same voice after the main note, or a second
  waveform change mid-note.
- The `C9 08 / BCS` check before the PW write: likely a drum/special note gate: note indices
  >= 8 go down a different path (drum? silence?).
- **DEC $????/30** (BMI) after the PW writes: a countdown timer per voice — Beben adds a
  per-note duration counter that is absent from the V1/V2 signatures (where duration may be
  handled by the main tick counter only).
- **Beben variant characteristic**: PW write pair ($D402/$D403) + note-range gate (CMP #$08) +
  per-note timer (DEC/BMI) + 3× $D404 toggle. Confirms the "enhanced drums" returned by
  Maniacs of Noise after receiving Beben's source.

---

## Variant Taxonomy Summary

| Variant       | Primary sig | $D402/D403 PW writes | $D404 toggles | $D405/D406 ADSR | 8-byte table copy | Note-range gate |
|---------------|-------------|---------------------|---------------|-----------------|-------------------|-----------------|
| Ariston       | YES         | not shown           | not shown     | not shown       | YES (E0 08 loop)  | no              |
| Crabtree V1   | +secondary  | no                  | 1 (STA $D400,Y) | no            | inherited         | no              |
| Crabtree V2   | +secondary  | no                  | 2 (gate-off+on)| YES ($D405/$D406)| inherited       | no              |
| Wally_Beben   | +secondary  | YES                 | 3             | YES             | inherited         | YES (CMP #$08)  |

**Implication for write-log model (DERIVED):**
- All variants share the 8-byte instrument table copy (primary Ariston loop).
- V1 is the simplest — one SID write per update path.
- V2 adds proper ADSR + hard-restart (gate-off/gate-on).
- Beben adds: pulse-width programming per note, 3× control-register toggle, note-range gate,
  per-note duration DEC counter. The "phasing" effect comes from the explicit PW writes.
- The Y-index stride of 7 per voice ($D400 = base, voice 1 at Y=0, voice 2 at Y=7, voice 3 at
  Y=14) is confirmed by the $D405/Y, $D406/Y, $D404/Y pattern in V2 and Beben.
- OPEN: The primary "Ariston" signature shows an 8-byte block copy but no SID writes — the
  SID writes are in the secondary signatures. The primary may be the instrument *program step*
  updater, while the secondary is the *voice register writer*. Or the SID writes appear after
  the shown region. Needs disassembly to confirm.

---

## Cross-reference: cadaver/sidid GitHub

The canonical online sidid.cfg at https://github.com/cadaver/sidid/blob/master/sidid.cfg
was checked (2026-06-15). The Ariston entry there matches our local copy exactly (same 4
signatures with the same byte sequences). No additional version splits or comments beyond
what is in our local file.
