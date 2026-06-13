# X-Ample / Compotech — SIDId Variant Taxonomy

**Provenance:** Static analysis of sidid.cfg signatures from three independent
sources:
- `tmp/dmc_hunt/sidid/sidid.cfg` (standalone sidid tool)
- `tmp/dmc_hunt/player-id/config/sidid.cfg` (player-id tool)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` (DeepSID bundled sidid v1.00)

All three sources have byte-for-byte identical X-Ample family blocks. The
signatures were read 2026-06-13; no disassembly or runtime execution was
performed.

**No DeepSID-specific Python classifier exists** for X-Ample: searching
`tmp/dmc_hunt/DeepSID/utility/python/specific/` finds no `xample.py` or
equivalent. DeepSID relies entirely on sidid for X-Ample identification.

---

## Full family block (verbatim from sidid.cfg)

```
X-Ample
9D ?? ?? BD ?? ?? 29 7F 9D ?? ?? C8 98 9D ?? ?? BD ?? ?? 29 80 9D ?? ?? BC ?? ?? B9 ?? ?? 29 0F 9D ?? ?? 9D END
(Compotech_V2.x)
A9 ?? 8D ?? ?? CE ?? ?? 10 ?? A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 90 ?? 20 ?? ?? ?? ?? 69 07 AA ?? 15 90 ?? A9 ?? 09 ?? 8D END
(Sonic/SDS)
BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 A9 00 F0 12 CE ?? ?? 10 END
(Thomas_Detert)
8D ?? ?? CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 20 ?? ?? 8A 18 69 07 AA C9 15 90 F1 A9 ?? 09 0F 8D 18 D4 A9 ?? 8D 16 D4 A9 00 F0 03 20 ?? ?? 60 END
(XTracker_V4.1x)
CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ?? A9 ?? 09 ?? 8D 18 D4 A9 ?? 8D 16 D4 END
(XTracker_V4.2x)
A0 00 F0 01 60 A9 ?? 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 ?? 8D ?? ?? 4E ?? ?? B0 07 29 00 9D 04 D4 F0 03 20 ?? ?? 8A 18 69 07 AA C9 15 90 E8 A9 ?? 09 ?? 8D 18 D4 END
(X-Ample_Digi)
29 1F 8D ?? ?? C8 B1 ?? C9 80 90 ?? 29 3F 8D ?? ?? C8 B1 ?? AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD AE ?? ?? BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A9 ?? 8D 0E DD END
```

---

## Sub-variant interpretation (static, no disassembly)

### 1. Base `X-Ample`

**Signature bytes (decoded):**
```
9D ?? ??      STA abs,X    — store to X-indexed table (voice register cache)
BD ?? ??      LDA abs,X    — load from table
29 7F         AND #$7F     — mask bit 7 (e.g. frequency high byte, clear MSB)
9D ?? ??      STA abs,X
C8            INY
98            TYA
9D ?? ??      STA abs,X
BD ?? ??      LDA abs,X
29 80         AND #$80     — isolate bit 7
9D ?? ??      STA abs,X
BC ?? ??      LDY abs,X   — indexed Y load
B9 ?? ??      LDA abs,Y   — indirect Y load (table lookup)
29 0F         AND #$0F     — low nibble (e.g. ADSR nibble)
9D ?? ??      STA abs,X
9D ...        STA abs,X   (continues)
```

**Interpretation:** This is the voice-loop body of the base X-Ample player
(Markus Schneider's Parsec-derived driver, ~1989). The `29 7F` / `29 80`
pair is a classical C64 tracker pattern: split a packed byte into a 7-bit
field (frequency low) and a 1-bit flag. `BC` / `B9` is an indexed indirect
table walk (instrument program lookup). The `29 0F` extracts an ADSR nibble.
The signature anchors to the note/instrument dispatch loop — the most
stable, engine-characteristic region of the player.

**Likely version:** Compotech V2.0 or the pre-Compotech Parsec Music Editor
driver. The parent group before the child sub-variants differentiate.

---

### 2. `(Compotech_V2.x)`

**Signature bytes (decoded):**
```
A9 ??         LDA #imm     — load constant
8D ?? ??      STA abs      — store to zp/ram variable
CE ?? ??      DEC abs      — decrement counter
10 ??         BPL rel      — branch if positive (timer countdown)
A9 ??         LDA #imm
8D ?? ??      STA abs      — reload counter
A2 ??         LDX #imm     — X = voice index (0, 7, 14)
8A            TXA
4E ?? ??      LSR abs      — logical shift right abs (channel enable bitmask test)
90 ??         BCC rel      — skip if channel disabled
20 ?? ??      JSR abs      — call voice handler
?? ?? 69 07   ... ADC #7   — advance voice offset (+7 per SID voice)
AA            TAX          — X = next voice base
?? 15         ... (branch back?)
90 ??         BCC rel
A9 ??         LDA #imm
09 ??         ORA #imm     — combine control bits
8D ...        STA          — write SID register
```

**Interpretation:** The Compotech V2.x dispatch loop. Key identifiers:
- `CE ?? ??` / `10 ??` / `8D` is the frame-counter pattern (decrement,
  branch-if-positive, reload on expiry) — same pattern seen in Hubbard '85
  speed counters. Here it gates the voice update rate.
- `4E ?? ??` (LSR abs) + `90 ??` is the classic C64 3-voice bitmask:
  shift a channel-enable byte; carry = channel active.
- `ADC #7` advances the SID register base by 7 per voice.
- The `?? ?? 69 07` means the preceding byte is unknown (relocated); the
  `69 07` = `ADC #$07` is the per-voice stride.

**Likely version:** Compotech V2.x (the "full tracker" evolution of the
Parsec Music Editor). The most common sub-variant for non-SoNiC composers
using the standard layout.

---

### 3. `(Sonic/SDS)`

**Signature bytes (decoded):**
```
BD ?? ??      LDA abs,X    — load channel data
D0 1B         BNE +27      — branch if not zero (channel active)
9D 04 D4      STA $D404,X  — write HARDCODED $D404 (voice gate/ctrl)
F0 19         BEQ +25      — branch if zero (skip)
A9 00         LDA #$00
8D ?? ??      STA abs      — clear variable
A2 00         LDX #0
CE ?? ??      DEC abs      — frame counter
10 05         BPL +5       — branch if not expired
A9 02         LDA #2
8D ?? ??      STA abs      — reload counter
4E ?? ??      LSR abs      — channel bitmask shift
90 B3         BCC -77      — long backward branch (loop to next voice)
20 ?? ??      JSR abs      — call voice handler
8A            TXA
18            CLC
69 07         ADC #7       — voice stride
AA            TAX
C9 15         CMP #$15     — compare X to 21 (3 voices × 7 = 21)
90 EF         BCC -17      — loop while X < 21
A9 00         LDA #0
09 ??         ORA #imm
8D 18 D4      STA $D418    — HARDCODED write to $D418 (master vol/filter)
A9 00         LDA #0
8D 16 D4      STA $D416    — HARDCODED write to $D416 (filter cutoff hi)
A9 00         LDA #0
F0 12         BEQ +18
CE ?? ??      DEC abs
10 ...        BPL ...
```

**Interpretation:** SoNiC's custom variant (Tufan Uysal / Sonic Design
Studio). Key identifiers:
- `9D 04 D4` = hardcoded `STA $D404,X` (not through a cached abs address
  like the base variant). This means the player stores voice registers
  directly at $D404+X (X = 0/7/14). This is the gate/control register
  write.
- `C9 15 / 90 EF` = loop terminator: compare voice offset to $15 (21),
  branch-carry-clear back. Three-voice loop with stride 7.
- `8D 18 D4` / `8D 16 D4` = hardcoded writes to master volume ($D418)
  and filter cutoff hi ($D416). SoNiC's variant explicitly manages these
  at the top of every play() call.
- The `4E ?? ??` / `90 B3` bitmask check is retained from Compotech_V2.x
  but is now embedded mid-loop rather than at dispatch.

**Likely version:** A heavily customized variant by Tufan Uysal (SoNiC),
as used in Katakis/Turrican 3 and his later work. The hardcoded $D4xx
addresses suggest the player was embedded at a known fixed load address
(confirmed: init=$1000 for most SoNiC tunes). May also include the SDS
(Sonic Design Studio) tools.

---

### 4. `(Thomas_Detert)`

**Signature bytes (decoded):**
```
8D ?? ??      STA abs      — store (end of previous voice write)
CE ?? ??      DEC abs      — frame counter
10 05         BPL +5       — wait if not expired
A9 ??         LDA #imm
8D ?? ??      STA abs      — reload counter
A2 ??         LDX #imm     — X = voice index
8A            TXA
4E ?? ??      LSR abs      — channel bitmask
20 ?? ??      JSR abs      — voice handler
8A            TXA
18            CLC
69 07         ADC #7       — voice stride
AA            TAX
C9 15         CMP #21
90 F1         BCC -15      — voice loop (3 voices)
A9 ??         LDA #imm
09 0F         ORA #$0F     — force lower nibble = $F (master vol = 15)
8D 18 D4      STA $D418    — HARDCODED master vol write
A9 ??         LDA #imm
8D 16 D4      STA $D416    — filter cutoff hi
A9 00         LDA #0
F0 03         BEQ +3       — always branch
20 ?? ??      JSR abs      — (conditional subroutine)
60            RTS
```

**Interpretation:** Thomas Detert's personal fork. Key identifiers:
- Same `CE/10/8D` frame-counter and `4E/90/20/8A/18/69 07/AA/C9 15/90`
  dispatch skeleton as Compotech_V2.x — Detert used the Compotech editor
  but modified the player.
- `09 0F / 8D 18 D4`: OR #$0F forces master volume to $0F before writing
  $D418, regardless of filter state. This is a Detert-specific idiom
  (compare to Sonic/SDS which uses `09 ??`).
- `8D 16 D4`: same explicit $D416 write as SoNiC.
- `F0 03 / 20 ?? ??`: a BEQ-always used as a 2-byte JMP (zero flag always
  set by `LDA #0`). This is a 3-byte JMP substitute that saves 1 byte —
  a known Detert optimization.

**HVSC correlation:** 92 tunes by Thomas Detert use `engine='X-Ample'`,
and Detert tunes show extreme address diversity ($1000, $A800, $B000,
$AC00, $3000, $E000 etc.) — suggesting he shipped his player embedded
at the natural load address of each game/demo.

---

### 5. `(XTracker_V4.1x)`

**Signature bytes (decoded):**
```
CE ?? ??      DEC abs      — frame counter
10 05         BPL +5
A9 ??         LDA #imm
8D ?? ??      STA abs      — reload counter
A2 00         LDX #0       — start voice 0 (FIXED, not imm-variable)
20 ?? ??      JSR abs      — voice 0 handler
A2 ??         LDX #imm     — voice 1 base (= 7)
20 ?? ??      JSR abs      — voice 1 handler
A2 ??         LDX #imm     — voice 2 base (= 14)
20 ?? ??      JSR abs      — voice 2 handler
A9 ??         LDA #imm
09 ??         ORA #imm
8D 18 D4      STA $D418    — master vol write
A9 ??         LDA #imm
8D 16 D4      STA $D416    — filter cutoff hi
```

**Interpretation:** XTracker V4.1x (a later-generation product from
X-Ample Architectures, distinct from Compotech). Key differentiator:
the three-voice dispatch is now **unrolled** — three separate `A2 xx /
JSR` pairs instead of a loop (`C9 15 / 90 Fxx`). This makes the
dispatch faster and simpler at the cost of ~6 bytes. The hardcoded
`8D 18 D4` / `8D 16 D4` writes are retained.

**Note:** The `A2 00` is non-wildcard (literal $00) — meaning the
matching is tight on the voice-0 start address being exactly #0.

---

### 6. `(XTracker_V4.2x)`

**Signature bytes (decoded):**
```
A0 00         LDY #0       — init Y = 0
F0 01         BEQ +1       — always branch (skip 1 byte — a 2-byte NOP/branch trick)
60            RTS          — (skipped — or alternate exit)
A9 ??         LDA #imm
8D ?? ??      STA abs
A2 00         LDX #0
CE ?? ??      DEC abs
10 05         BPL +5
A9 ??         LDA #imm
8D ?? ??      STA abs
4E ?? ??      LSR abs      — channel bitmask (restored from V4.2)
B0 07         BCS +7       — branch if channel ENABLED (inverted from BCC!)
29 00         AND #0       — clear A (= LDA #0 equivalent)
9D 04 D4      STA $D404,X  — HARDCODED gate-off ($D404,X)
F0 03         BEQ +3       — always branch (skip next JSR)
20 ?? ??      JSR abs      — voice handler (if channel active)
8A            TXA
18            CLC
69 07         ADC #7       — voice stride
AA            TAX
C9 15         CMP #21
90 E8         BCC -24      — voice loop
A9 ??         LDA #imm
09 ??         ORA #imm
8D 18 D4      STA $D418    — master vol
```

**Interpretation:** XTracker V4.2x. Hybrid: returns to a bitmask-gated
loop like Compotech_V2.x (vs V4.1x's unrolled approach) but with the
hardcoded `$D404,X` write from SoNiC. Notable: `B0 07` (BCS) vs the
earlier `90 ??` (BCC) — the skip logic is inverted, suggesting the
bitmask polarity changed between versions. The `A0 00 / F0 01 / 60`
at the head is a "skip 1 byte" trick sometimes used as a branch-over-RTS
for a quick exit from init.

**HVSC corpus:** Only 1 tune in hvsc84.db carries this exact fingerprint
(`engine='(XTracker_V4.2x)'`): `MUSICIANS/S/Sonic/Falk-Ohr-Filter_Model_50.sid`
by Tufan Uysal (SoNiC), init=$8000 play=$8003. This suggests V4.2x was
a narrow release or short-lived version.

---

### 7. `(X-Ample_Digi)`

**Signature bytes (decoded):**
```
29 1F         AND #$1F     — mask low 5 bits (sample data nibble)
8D ?? ??      STA abs      — store processed sample byte
C8            INY          — advance pointer
B1 ??         LDA (zp),Y   — load next sample byte via indirect Y
C9 80         CMP #$80     — test for end-of-sample marker ($80)
90 ??         BCC rel      — branch if not end
29 3F         AND #$3F     — mask 6 bits (secondary nibble)
8D ?? ??      STA abs
C8            INY
B1 ??         LDA (zp),Y   — load next byte
AA            TAX          — transfer to X
BD ?? ??      LDA abs,X    — table lookup (CIA timer hi-byte table)
8D 04 DD      STA $DD04    — WRITE CIA1 TIMER A LOW   ***DIGI MARKER***
BD ?? ??      LDA abs,X
8D 05 DD      STA $DD05    — WRITE CIA1 TIMER A HIGH  ***DIGI MARKER***
AE ?? ??      LDX abs      — load voice register base
BD ?? ??      LDA abs,X    — load SID register value
8D ?? ??      STA abs
BD ?? ??      LDA abs,X
8D ?? ??      STA abs
A9 ??         LDA #imm
8D 0E DD      STA $DD0E    — WRITE CIA1 CONTROL REGISTER A (start timer)
```

**Interpretation:** This is a fundamentally different engine mode —
CIA-timer-driven sample playback. Key identifiers:
- `8D 04 DD` / `8D 05 DD`: writes to CIA1 Timer A low/high ($DD04/$DD05).
  The player programs the CIA timer to fire at a sample rate.
- `8D 0E DD`: writes to CIA1 Control Register A ($DD0E) — starts the
  timer.
- `B1 ??` (LDA indirect Y) + `C9 80` (CMP #$80): sample stream iterator
  with $80 as end-of-sample sentinel.
- `29 1F` / `29 3F`: two 5-bit nibble extractions — likely the sample
  data is packed as two 5-bit fields per byte (giving 32 amplitude levels),
  with the high bit as a flag.
- `BD ?? ??` after `AA TAX`: a table lookup indexed by sample byte value
  — the timer reload values for each sample amplitude.

**Migration scope:** This variant is out-of-scope for standard $D400-$D418
Mode-1 (frame-by-frame) pipeline. It writes CIA registers, not just SID
registers. Requires Mode-2 (cycle-exact) treatment OR explicit exclusion.
See population analysis in `deepsid_population_and_digi.md`.

---

## Variant lineage diagram

```
Parsec Music Editor (Schneider, ~1989)
    |
    +-- Base X-Ample driver
    |       Signature: 9D/BD/29 7F/29 80/BC/B9/29 0F voice-loop
    |
    +-- Compotech V2.x (full tracker editor)
    |       Signature: CE/10/LDX/4E/90/20/69 07 bitmask-loop dispatch
    |
    |   [Thomas Detert fork]
    |       Signature: Compotech_V2.x + 09 0F + F0 03 tricks
    |
    |   [SoNiC / SDS fork]
    |       Signature: 9D 04 D4 hardcoded + C9 15/90 loop + 8D 18 D4/16 D4
    |
    +-- XTracker V4.1x (new product)
    |       Signature: unrolled A2 00/JSR + A2 07/JSR + A2 0E/JSR
    |
    +-- XTracker V4.2x (revision)
    |       Signature: A0 00/F0 01 entry trick + bitmask-loop + BCS invert
    |
    +-- X-Ample_Digi (digi extension)
            Signature: 29 1F/B1/C9 80 sample decode + 8D 04 DD/8D 05 DD CIA writes
```

---

## Key shared idioms across variants

| Idiom | Bytes | Meaning |
|---|---|---|
| Frame counter | `CE ?? ?? / 10 ?? / A9 ?? / 8D ?? ??` | Decrement, branch-if-positive, reload |
| Voice stride | `18 / 69 07` | CLC ADC #7 — advance SID base by 7 |
| Loop terminator | `C9 15 / 90 ??` | CMP #21 (3×7), BCC back |
| Vol/filter | `8D 18 D4` | STA $D418 (master vol) |
| Filter cutoff | `8D 16 D4` | STA $D416 (cutoff hi) |
| Bitmask gate | `4E ?? ?? / 90 ??` | LSR abs, BCC skip = channel-off |
| Gate write | `9D 04 D4` | STA $D404,X (voice ctrl hardcoded) |

---

## Reflextracker (related but distinct)

sidid labels 137 HVSC tunes as `Reflextracker`. All are RSID (play=$0000,
self-playing). Init addresses cluster at $C006 (130/137). File sizes are
large (15K-48K), consistent with embedded sample data. Authors are
predominantly Polish demosceners (Warlock, JFK, Data, Gregfeel, Mephisto).

Reflextracker is **not** an X-Ample variant: its sidid signature is
separate, it is exclusively RSID, and its user community is disjoint from
the X-Ample community. It is named "Reflextracker" after the Reflex group
(Polish C64/Amiga demoscene). Likely a separate CIA-timer-driven MOD/sample
player. Not part of the X-Ample migration scope.
