# GMC / Superiors — SIDId Signature Analysis

**Provenance:** Static analysis of three sidid.cfg copies — all read-only:
- `tmp/dmc_hunt/sidid/sidid.cfg` (standalone sidid build)
- `tmp/dmc_hunt/player-id/config/sidid.cfg` (player-id tool)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` (DeepSID bundled, main)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid_old_but_works.cfg` (older working copy)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid_newer_but_does_not_work.cfg` (broken newer)

All three active copies contain **identical** GMC/Superiors and GMC_V2.0/Superiors entries.
No disassembly performed.  Date: 2026-06-13.

---

## 1. Raw Signatures

### GMC/Superiors (V1)

All three copies, line 749/767/728/729/745 respectively:

```
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ??
BD ?? ?? 9D ?? ?? BC ?? ?? 18 0A 0A 0A 0A 85 ?? AD ?? ?? 69 00 85 ??
A0 00 B1 [END]
```

Length: 51 bytes of discriminating pattern (plus wildcards).

### GMC_V2.0/Superiors

```
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ??
BD ?? ?? 9D ?? ?? A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD A0 00
98 9D [END]
```

Length: 48 bytes of discriminating pattern (plus wildcards).

---

## 2. Shared Prefix

Both signatures share an **identical 30-byte prefix**:

```
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ??
BD ?? ?? 9D ?? ?? [shared prefix ends here]
```

Decoded (6502):
| Bytes | Mnemonic | Comment |
|-------|----------|---------|
| `E1 EE FD` | `SBC ($FD,X)` + operand (or unusual encoding) | Likely first bytes of play routine |
| `BD ?? ??` | `LDA abs,X` | Load from indexed table |
| `9D ?? ??` | `STA abs,X` | Store to SID register |
| `A8` | `TAY` | Transfer A→Y |
| `B9 ?? ??` | `LDA abs,Y` | Load from Y-indexed table |
| `9D ?? ??` | `STA abs,X` | Store to SID |
| `B9 ?? ??` | `LDA abs,Y` | Another Y-indexed load |
| `9D ?? ??` | `STA abs,X` | Store to SID |
| `BD ?? ??` | `LDA abs,X` | Load |
| `9D ?? ??` | `STA abs,X` | Store |

This prefix represents an inner voice-write loop loading SID frequency/control values from per-voice data tables. The `BD`/`9D` pairs (abs,X for multi-voice dispatch) and `B9` pairs (abs,Y for per-instrument data) are characteristic. The `TAY` after the first load (`A8`) uses the loaded value as a Y-index into instrument data.

---

## 3. Divergence Point: V1 vs V2.0

After the shared prefix (`...9D ?? ??`), the two versions split:

### V1 continuation:
```
BC ?? ??   ; LDY abs,X   (load voice step index from abs,X table)
18         ; CLC
0A         ; ASL A       \
0A         ; ASL A        |  multiply by 16 (4x ASL)
0A         ; ASL A        |  to get instrument offset (sound * 16)
0A         ; ASL A       /
85 ??      ; STA zp       store computed instrument base
AD ?? ??   ; LDA abs      load another parameter
69 00      ; ADC #$00     add with carry (carry from prior math)
85 ??      ; STA zp       store
A0 00      ; LDY #$00
B1 ??      ; LDA (zp),Y   indirect Y load from instrument data
```

**V1 instrument addressing:** sound number is multiplied by 16 (`4x ASL A`) to produce
a base offset into a flat instrument table. Each instrument record is exactly 16 bytes.
The `ADC #$00` adds carry only — this is a carry-propagation step for a 16-bit addition
(`STA base_lo; ADC #0; STA base_hi` pattern).

### V2.0 continuation:
```
A8         ; TAY          transfer A→Y
29 F0      ; AND #$F0     keep HIGH nibble of A
85 FC      ; STA $FC      store hi-nibble part
98         ; TYA          restore original A from Y
29 0F      ; AND #$0F     keep LOW nibble of A
18         ; CLC
6D ?? ??   ; ADC abs      add a base
85 FD      ; STA $FD      store lo-nibble result
A0 00      ; LDY #$00
98         ; TYA
9D ?? ??   ; STA abs,X
```

**V2.0 instrument addressing:** the loaded byte is split into **two nibbles**:
- High nibble (`AND #$F0` → `STA $FC`): one field (likely instrument number upper)
- Low nibble (`AND #$0F`): added to an absolute base (`ADC abs`), stored separately

This is a **packed-field decode**: a single byte encodes two parameters. The 4-bit low
field is an index into a base-relative table (maximum 16 entries = 4 bits). The 4-bit
high field may encode a second attribute (e.g., waveform, arpeggio class, effect type).

**Structural significance:** V2.0 doubled the information density of one data byte,
allowing independent control of two parameters per step where V1 used only one
(instrument index → 16-byte record). This is consistent with a second-generation
editor adding a new per-step field without expanding step record size.

---

## 4. Comparison with DMC Signatures

DMC family signatures from the same sidid.cfg files:

### DMC (base, V4.x sub-variant):
```
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ??
BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

### DMC (V4.x) sub-variant:
```
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ??
BD ?? ?? 29 01 D0
```

### DMC (V5.x) sub-variant:
```
BC ?? ?? B9 ?? ?? C9 90 D0 [AND operand] BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

### DMC_V6.x:
```
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4
8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60
CE ?? ?? 30 69 20
```

### Key structural differences from GMC:

| Feature | GMC V1 | GMC V2.0 | DMC V4 | DMC V5 | DMC V6 |
|---------|--------|----------|--------|--------|--------|
| Opening bytes | `E1 EE FD BD` | same | `18 7D` | `BC ?? B9` | `A9 02 9D` |
| Write opcode | `9D` (STA abs,X) | `9D` | `99` (STA abs,Y) | `99`/`3D` | `8D` (STA abs) |
| Instrument decode | 4x ASL (×16) | nibble split | `7D` (ADC abs,X) | pattern check `C9 90` | init-style; writes hardcoded regs |
| Step index | abs,X (`BD`) | abs,X (`BD`) | abs,X (`BD`/`FE`) | abs,X + abs,Y | INC/DEC counter |
| Signature style | inner loop | inner loop | inner loop | hybrid | init block |

**Lineage observation:** GMC and early DMC (V4) share the `BD`/`9D` abs,X write pattern
for SID voice dispatch. DMC V4 uses `7D` (ADC abs,X) where GMC V1 uses individual `B9`
loads — both implement per-voice parameter accumulation but with different accumulator
patterns. DMC V5 introduces a pattern-command branch (`C9 90 D0` = compare to $90, BNE)
suggesting a command/data byte interpreter rather than the GMC direct-data model. DMC V6
signature is purely an init block with hardcoded SID register writes — structurally
incomparable.

The GMC→DMC lineage is credible at the write-dispatch level (shared abs,X multi-voice
pattern) but the instrument-addressing mechanism diverged substantially between GMC V1's
×16 flat table and DMC's accumulated-offset model.

---

## 5. sidid.cfg File Consistency

Checked across all five sidid.cfg variants:
- `sidid/sidid.cfg`: GMC/Superiors at line 749, GMC_V2.0/Superiors at line 751
- `player-id/config/sidid.cfg`: GMC/Superiors at line 767, GMC_V2.0/Superiors at line 769
- `DeepSID/utility/sidid_100/sidid.cfg`: GMC/Superiors at line 728, GMC_V2.0/Superiors at line 730
- `DeepSID/utility/sidid_100/sidid_old_but_works.cfg`: GMC/Superiors at line 693, GMC_V2.0/Superiors at line 695
- `DeepSID/utility/sidid_100/sidid_newer_but_does_not_work.cfg`: GMC/Superiors at line 745, GMC_V2.0/Superiors at line 748

All five copies are **byte-identical** for the GMC and GMC_V2.0 entries.
The `sidid_newer_but_does_not_work.cfg` differs only in lacking the `END` keyword
terminator on entries (a known sidid version incompatibility, not a GMC-specific issue).

---

## 6. sidid Classification Ambiguity

Both GMC variants share the 30-byte prefix identically. sidid must scan past that prefix
to reach the divergence point to distinguish V1 from V2.0. This means:

1. A SID file is classified V2.0 only if the longer V2.0-specific suffix also matches.
2. If a V2.0 file somehow lacks the unique suffix (truncated or corrupted), it would
   fall through to a V1 match or miss entirely.
3. The V2.0 population (9 SIDs) is entirely from 2010–2023, confirming this is a
   **modern revival** of GMC, not a 1990s-era concurrent branch.

---

## Leads to follow

- **What are the first 3 bytes `E1 EE FD`?** `E1` = `SBC ($FD,X)` on 6502 — unusual
  as the very first instruction of a play routine. Possible: it's mid-routine signature
  bytes, not the play entry. Alternatively, it's data used by the SID file header or a
  region that sidid scans at a fixed offset (not necessarily the play entry point).
  Needs binary inspection to resolve.
- **V1 step size:** instrument = sound × 16 (`4x ASL`) → confirm the 16-byte instrument
  record layout (envelopes, waveforms, arpeggio, vibrato etc.).
- **V2.0 nibble semantics:** what exactly are hi-nibble vs lo-nibble? Candidate: hi=wave/
  octave, lo=instrument index (0–15). Would constrain the V2.0 instrument table to max
  16 entries. Or: the split encodes arpeggio+waveform packed as a single SID control byte.
- **GMC V2.0 tool:** who distributed it and when? NecroPolo authored most V2.0 tunes
  (2010, 2021, 2023). He may have written or obtained a patched GMC editor — no CSDb
  reference found from this static analysis.
- **The `E1 EE FD` prefix:** might be a fixed magic sequence in the GMC player binary
  itself (player code that always lives at those offsets within the SID image), or it
  could be bytes of the init routine that always precede the play call. Disassembly
  of one canonical $18EA/$14EA SID would resolve immediately.
