---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-15
author: Cadaver (Lasse Öörni) and contributors; Vibrants/JO signatures may have different author
content_date: cumulative 1989-2020
reliability: primary
---

# SIDId Signatures — Vibrants/Laxity, Vibrants/JO, JCH_OldPlayer

All signatures fetched verbatim from the cadaver/sidid GitHub repository.
These are reloc-invariant play-routine fingerprints — they wildcard address bytes (??)
but keep SID I/O literal bytes.

---

## 1. `Vibrants/Laxity` (5 OR-lines, any one sufficient)

```
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4 END
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4 END
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D END
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29 END
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90 END
```

### Disassembly analysis (inferred from opcodes)

**LINE 1 — 16-bit frequency table write:**
```
18        CLC
7D ?? ??  ADC abs,X       ; add voice offset to table index (16-bit freq calc)
0A        ASL A           ; ×2 (2 bytes per note in freq table)
A8        TAY             ; Y = byte offset into freq table
B9 ?? ??  LDA abs,Y       ; load freq high byte from table
48        PHA             ; push freq high to stack
B9 ?? ??  LDA abs,Y       ; (next Y = Y+1? or same Y?) — this may be a different load
AC ?? ??  LDY abs         ; load Y from absolute (another index?)
99 01 D4  STA $D401,Y     ; write freq HI to D401+voice_offset
68        PLA             ; pull freq high back
99 00 D4  STA $D400,Y     ; write freq LO to D400+voice_offset
```
Note: $D401 is written BEFORE $D400 here. This is freq-write order HIGH-before-LOW,
distinguishing this engine from the NP21 freq write (which does freqlo first at D400+o).

**LINE 2 — sequence/control byte decode and gate write:**
```
FE ?? ??  INC abs,X       ; increment sequence pointer
BD ?? ??  LDA abs,X       ; load current sequence byte
99 04 D4  STA $D404,Y     ; write control/gate to $D404+voice_offset
4C ?? ??  JMP abs         ; jump (to advance or next voice)
BD ?? ??  LDA abs,X       ; reload from sequence
29 ??     AND #imm        ; mask (range check on command byte)
F0 ??     BEQ +N          ; branch if zero
A9 ??     LDA #imm        ; load immediate (preset waveform?)
99 04 D4  STA $D404,Y     ; write gate=0 to $D404 (gate off)
```
This is the per-frame ctrl-register write plus a sequence-decode branch. The `29 ??; F0 ??;
A9 ??` suggests: AND sequence byte with mask, if result=0 (branch), write immediate value
to $D404 — this appears to be the "gate off" path (matching $00 gate-off writes via a preset
waveform byte).

**LINE 3 — timer/speed init with multi-counter DEC loop:**
```
A9 ??     LDA #imm
8D ?? ??  STA abs         ; initialize some register
60        RTS             ; early-RTS (this may be at start of init?)
A2 ??     LDX #imm        ; init loop counter
CE ?? ??  DEC abs
10 ??     BPL +N          ; loop on 1st counter
CE ?? ??  DEC abs
CE ?? ??  DEC abs
CE ?? ??  DEC abs
AD ?? ??  LDA abs
8D ?? ??  STA abs
```
Four separate `DEC abs` counters decrement separately with BPL boundary. This is a multi-tempo
or multi-counter system (compare: the JCH_NewPlayer single `speedcnt` vs Vibrants/Laxity's
apparent 4-counter speed system). The four decrements suggest 4 independent counters —
possibly per-voice speed + one global, or a 4-part tempo subdivision.

**LINE 4 — command nibble dispatch:**
```
C9 ??     CMP #imm        ; threshold compare
B0 ??     BCS +N          ; branch if carry set (byte >= threshold = different type)
29 ??     AND #imm        ; mask low/high nibble
48        PHA
A9 ??     LDA #imm
9D ?? ??  STA abs,X       ; store one decoded field
68        PLA
0A        ASL             ; ×2
0A        ASL             ; ×4
9D ?? ??  STA abs,X       ; store another decoded field (×4 = pointer into 4-byte table?)
4C ?? ??  JMP abs
29 ??     AND #imm        ; continues to next masking operation
```
The `PHA; LDA; STA; PLA; ASL; ASL; STA` pattern splits a byte into two parts:
lower half → direct store, upper half × 4 → table index. This is consistent with a
byte encoding that packs two parameters (e.g. instrument number in high nibble = index×4,
command/effect in low nibble).

**LINE 5 — filter cutoff write ($D416):**
```
AD ?? ??  LDA abs          ; load current filter value (running accumulator)
18        CLC
79 ?? ??  ADC abs,Y        ; add sweep increment from table[Y]
8D ?? ??  STA abs          ; save updated filter value
8D 16 D4  STA $D416        ; write to filter cutoff HI
2C ?? ??  BIT abs          ; test flags
70 ??     BVS +N           ; branch on overflow (boundary/direction flip)
D9 ?? ??  CMP abs,Y        ; compare to limit
90 ??     BCC +N           ; branch if below limit
```
$D416 (filter cutoff HIGH byte) is written every frame via an ADC-accumulation loop
with a BVS overflow check and a CMP/BCC limit check. This suggests the filter sweep
is a 2-direction sweep with direction flip at BVS (overflow) and range clamping via CMP.
Note: $D417 (routing + resonance) and $D418 (volume + filter type) are NOT in these
signatures — they may be written only on initialization or on specific filter-change events.

---

## 2. `Vibrants/JO` (10 OR-lines)

A related but distinct player engine. JO is a different scener from Vibrants group
(likely "Jo" — possibly Joachim). This engine shares the V-indexed absolute addressing
style with Vibrants/Laxity but has different sequence semantics.

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

### Key features of Vibrants/JO from signatures

- `BC ?? ??; B1 ??` = `LDY abs,X; LDA (zp),Y` — double-indirect sequence read (pointer
  in zero-page indexed by Y). This is a more complex sequence fetch than Vibrants/Laxity's
  direct indexed read.
- `C9 F0; D0 ??; C8; B1 ??; 18; 7D ?? ??` — `CMP #$F0; BNE; INY; LDA(zp),Y; CLC; ADC abs,X`
  — frequency calculation with $F0 as a special sentinel.
- `C9 FF; D0 ??; A9 00; 9D ?? ??; DE ?? ??; D0 ??; A9 01; 9D ?? ??; FE` — the $FF
  end-of-sequence sentinel pattern, with gate-off/gate-on writes.
- `C9 60; 90 ??; 38; E9 60` — range check + subtract $60 (octave transposition?).
- `A2 02; BC ?? ??; A9 00; 99 05 D4; 99 06 D4; A9 08; 99 04 D4; CA; 10 ??; 60` — reset
  loop: X=2, LDY abs,X, STA $D405,Y; STA $D406,Y; LDA #8; STA $D404,Y; DEX; BPL; RTS —
  this is an INIT routine that resets all 3 voices: AD=0, SR=0, ctrl=$08 (test bit set).
- `30 03; 4C ?? ??; A9 00; 9D ?? ??; A9 08; 99 04 D4; 98; 48; A0 00; BD` — BMI skip,
  gate-off ($A9 00; STA), test bit ($A9 08; STA $D404,Y), TYA, PHA, LDY #0.

The `$08` test-bit write (LINE 9 + LINE 10) identifies Vibrants/JO as a hard-restart
engine: the test bit ($08 = bit3 of $D404) is set during the restart window.

---

## 3. `JCH_OldPlayer` (1 OR-line)

```
48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D ?? ?? 68 18 6D ?? ?? 8D ?? ?? 68 END
```

Disassembly:
```
48        PHA
18        CLC
4A        LSR A      ; ÷2
4A        LSR A      ; ÷4
4A        LSR A      ; ÷8
4A        LSR A      ; ÷16
29 07     AND #$07   ; mask to 3 bits (0-7 = 8 octaves)
0A        ASL A      ; ×2
0A        ASL A      ; ×4
0A        ASL A      ; ×8  (= note_within_octave × 8)
48        PHA
0A        ASL A      ; ×16
8D ?? ??  STA abs    ; store freq fragment
68        PLA
18        CLC
6D ?? ??  ADC abs    ; add to computed freq (16-bit build-up)
8D ?? ??  STA abs    ; store result
68        PLA        ; pull original back
```

This is a **frequency calculation from a packed note byte** using nibble extraction
+ bit shifts to compute a frequency value. The sequence LSR×4 + AND #$07 + ASL×3
is consistent with a packed byte format where:
- Bits 7-4 = octave (LSR×4 → 0-15 range, masked to 0-7)
- Bits 3-0 = semitone within octave (retrieved by PHA + AND after the high nibble processing)

The ADC abs + STA pattern builds the freq value in stages, consistent with a
lookup table approach where the note is split across table offsets.

This is JCH composing IN the Laxity player format (1988-1989), before JCH wrote
his own player. This signature therefore reveals Laxity's original note encoding:
a packed single-byte note format where octave and semitone are nibble-packed,
decoded via successive shifts and masks.

---

## 4. Population data

From `hvsc84.db` (read-only, 2026-06-14, per `cluster_sidid_discrimination.md`):

| Engine | HVSC #84 count |
|--------|---------------|
| `Vibrants/Laxity` | 179 SIDs |
| `Vibrants/JO` | (in HVSC, count unknown — not queried this session) |
| `JCH_OldPlayer` | (in HVSC, count unknown — primarily historical; JCH's early tunes) |

For `Vibrants/Laxity`:
- Canonical: init=$1000, play=$1006 (81% of 179)
- 10 multi-subtune entries (much higher fraction than NP21's 1.9%)
- Play offset +$06 = 6-byte dispatch table {init, play, mplay}

---

## 5. Migration implications

1. **The Vibrants/Laxity player is not NP21**: The two engines share a family ancestor
   (JCH learned from Laxity's player) but have completely different binary layouts, play
   offsets, and SID write models. Do NOT use the NP21.G4 extractor for Vibrants/Laxity.

2. **No public format documentation exists**: The sidid.cfg signatures are the primary
   source for understanding the binary layout. The disassembly of at least one representative
   HVSC tune is required before implementing the extractor.

3. **16-bit freq table write model differs from NP21**: Vibrants/Laxity writes D401 BEFORE
   D400 (hi before lo); NP21 writes D400 before D401 (lo before hi, via setsid).

4. **Filter on $D416 only**: The signature shows STA $D416 (filter cutoff HI), NOT $D417
   (routing) or $D418 (vol/filter-type). The filter routing may be static (init only) or
   encoded differently.

5. **Multi-counter speed**: The 4×CE-10-pair pattern in LINE 3 suggests a more complex
   speed/tempo system than NP21's single `speedcnt`. Possibly per-voice independent speeds
   or a 4-part tempo subdivision for multispeed effects.
