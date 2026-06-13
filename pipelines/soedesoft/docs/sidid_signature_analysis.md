# SoedeSoft / Soundmaster — sidid Signature Analysis

**Provenance:** Grepped from (read-only):
- `tmp/dmc_hunt/player-id/config/sidid.cfg`  (lines 1812-1820)
- `tmp/dmc_hunt/sidid/sidid.cfg`              (lines 1775-1783)
- `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg`  (lines 1709-1717)

All three files carry identical SoedeSoft blocks.
Date: 2026-06-13.

---

## Raw sidid.cfg block

```
SoedeSoft
D0 03 BD ?? ?? 9D ?? ?? 60
B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9

(Soundmaster_V1.0)
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C

(Soundmaster_V3.1)
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60

(Soundmaster_V3.2)
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ??
7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

(`??` = wildcard byte, `END` / no-connector = implicit AND in sidid.)

---

## Interpretation: root signature

```
SoedeSoft
  line 1: D0 03 BD ?? ?? 9D ?? ?? 60
  line 2: B9 ?? ?? 4A 4A 4A 4A 9D ?? ?? B9 ?? ?? 0A 0A 0A 0A 9D ?? ?? B9
```

**Line 1 disassembly (static, no addresses):**
```
BNE +3        ; D0 03  — skip if non-zero (e.g. subtune loop guard)
LDA abs,X    ; BD ?? ??
STA abs,X    ; 9D ?? ??
RTS           ; 60
```
This is a conditional store — a common `if (counter != 0) table[x] = src[x]`
pattern. Likely a voice-state or effect-flag update with early-out.

**Line 2 disassembly (nibble-split idiom — THE key fingerprint):**
```
LDA (abs),Y  ; B9 ?? ??   — load byte from table indexed by Y
LSR A         ; 4A         \
LSR A         ; 4A          |  >> 4 → high nibble → low nibble
LSR A         ; 4A          |
LSR A         ; 4A         /
STA abs,X    ; 9D ?? ??   — store high nibble (e.g. waveform)

LDA (abs),Y  ; B9 ?? ??   — load same or adjacent byte
ASL A         ; 0A         \
ASL A         ; 0A          |  << 4 → low nibble → high nibble
ASL A         ; 0A          |
ASL A         ; 0A         /
STA abs,X    ; 9D ?? ??   — store low nibble shifted up (e.g. pulse or vol)

LDA (abs),Y  ; B9 ?? ??   — (continues)
```

The `4A 4A 4A 4A` / `0A 0A 0A 0A` pair is the SoedeSoft engine's
signature **nibble-split**: instrument data is packed one byte per voice
parameter where the HIGH nibble and LOW nibble encode two different
fields.  The player unpacks them into SID registers by:
- `>> 4` (four `LSR A`) → upper nibble extracted as 0x0N
- `<< 4` (four `ASL A`) → lower nibble rotated to 0xN0

This pattern is relocation-invariant (no absolute addresses in the
matched bytes) so it fires at any load address. It is the definitive
SoedeSoft fingerprint and does NOT appear in the three sub-variant
signatures — those test for later, finer structural differences.

---

## Sub-variant (Soundmaster_V1.0)

```
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C
```

**Disassembly:**
```
STA abs,X    ; 9D ?? ??   — store to voice table
LDA abs,X    ; BD ?? ??   — load something
BNE +??      ; D0 ??      — conditional branch
CLC           ; 18
LDA (abs),Y  ; B9 ?? ??   — load note/pitch byte
ADC abs,X    ; 7D ?? ??   — add (pitch slide / transpose)
STA (abs),Y  ; 99 ?? ??   — store result
STA $D400,Y  ; 99 00 D4   — write voice frequency LO to SID
LDA (abs),Y  ; B9 ?? ??   — load hi byte
ADC #??      ; 69 ??      — add carry + immediate
STA (abs),Y  ; 99 ?? ??   — store
STA $D401,Y  ; 99 01 D4   — write voice frequency HI to SID
JMP abs      ; 4C ??      — loop / next voice
```

**Key characteristics:**
- Uses `ADC abs,X` (7D) for **pitch addition** — i.e. a running accumulator
  on a base pitch.  This implies a simple additive frequency-slide effect.
- Writes both frequency bytes (`$D400+Y`, `$D401+Y`) via `STA (zp),Y`.
- The `D0 ??` guard before the `18/ADC` block suggests frequency update
  is skipped when a counter reaches zero (note duration / effect gate).
- This is the **earliest Soundmaster play routine** still recognised by sidid.

---

## Sub-variant (Soundmaster_V3.1)

```
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

**Disassembly:**
```
LDA #??      ; A9 ??      — load immediate (e.g. waveform byte, or 0=silence)
STA abs,X    ; 9D ?? ??   — store to voice state table
JMP abs      ; 4C ?? ??   — jump (voice-loop or effect handler)
LDA abs,X    ; BD ?? ??   — load freq lo from table
STA $D400    ; 9D 00 D4   — write to SID freq lo
LDA abs,X    ; BD ?? ??   — load freq hi from table
STA $D401    ; 9D 01 D4   — write to SID freq hi
RTS           ; 60
```

**Key characteristics:**
- Simpler: no pitch-slide ADC, just direct `LDA abs,X / STA $D4xx`.
- The `LDA #?? / STA / JMP` prefix is probably a note-trigger or
  waveform-load preamble.
- Freq writes are at fixed addresses `$D400`, `$D401` (absolute, with X
  index implied by the `9D` opcode + `00 D4` low byte).
- This corresponds to a **stripped-down V3 play core** — pitch slides
  removed or handled elsewhere.

---

## Sub-variant (Soundmaster_V3.2)

```
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ??
7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

**Disassembly:**
```
LDA #??      ; A9 ??      — load immediate
STA abs,X    ; 9D ?? ??
JMP abs      ; 4C ?? ??   — loop head
CLC           ; 18
LDA abs,X    ; BD ?? ??   — load freq lo from table
ADC abs,X    ; 7D ?? ??   — add pitch delta
STA abs,X    ; 9D ?? ??   — store back
LDA abs,X    ; BD ?? ??   — load freq hi
ADC abs,X    ; 7D ?? ??   — add carry + hi-delta
STA abs,X    ; 9D ?? ??   — store back
LDA abs,X    ; BD ?? ??   — load final freq lo
STA $D400    ; 9D 00 D4
LDA abs,X    ; BD ?? ??   — load final freq hi
STA $D401    ; 9D 01 D4
RTS           ; 60
```

**Key characteristics:**
- Pitch-slide is back: `CLC / ADC abs,X` for both lo and hi bytes,
  result stored back, then the modified value written to SID.
- This is a **two-pass frequency update**: accumulate slide into the
  working table, then copy result to SID.
- Structurally: V3.1 base + pitch-slide layer added back (different
  from V1.0's `B9/99` indirect addressing — V3.2 uses `BD/9D` absolute).
- The `A9 ?? / 9D ?? ?? / 4C ?? ??` prefix is shared with V3.1 and is
  likely the note-on trigger / waveform write that precedes the
  frequency handler.

---

## Version taxonomy from sidid + HVSC population

| sidid label        | Play offset from init | HVSC count | Note |
|--------------------|----------------------|------------|------|
| (none — root only) | +6 (0x0006)          | 319        | SoedeSound V1.0 (1988) — earliest; init=play+6 |
| (none — root only) | +3 (0x0003)          | 151        | Short-dispatch variant; init/play often at same page |
| Soundmaster_V1.0   | +262 (0x0106)        | 163        | V1.0 pitch-slide engine |
| (none / Vx)        | +221 (0x00DD)        | 99         | Intermediate variant (init_lo=0x29) |
| (none / Vx)        | +223 (0x00DF)        | 78         | Intermediate variant (init_lo=0x27) |
| (none)             | -41 (0xFFD7)         | 60         | play=page+0x00, init=page+0x29; player jumps backwards |
| Soundmaster_V3.1   | +3 or other          | mixed      | V3.1 — direct freq write, no slide in main sig |
| Soundmaster_V3.2   | +3 or other          | mixed      | V3.2 — pitch-slide with abs,X addressing |

**Note:** sidid does NOT emit sub-variant labels for the majority of
SoedeSoft tunes — the three sub-variant patterns are secondary signatures
that only fire when the root match is confirmed AND the additional bytes
are present.  The "offset+6" dominant cluster (319 tunes) is all root-
only matches with no sub-variant tag.

---

## The `play<init` layout (offset -0x29)

60 tunes have `init_addr = base+0x29` and `play_addr = base+0x00`.
This means the PSID header's play vector points to the PAGE START
(not a JSR-through-vector), while the init vector is 0x29 bytes into
the engine block.  This layout is consistent with early SoedeSoft where:
- The player loop is placed at page+0x00 and entered directly by the VBI.
- The init code is at page+0x29 (after the player).
- The play entrypoint IS the beginning of the data/code segment.

This is distinct from the 0x0106 / 0xDD / 0xDF clusters where init and
play are in "normal" order (init first, play second in address space).

---

## The CreaMD outlier cluster (large offsets)

8 tunes by CreaMD (`MUSICIANS/C/CreaMD/`) have init in the $7C–$86
range and play at $9106 (init_lo=0xe0, offset ≈ 3000–5000 bytes).
Rudolf Stember's Western_Contest.sid (15 subtunes) has an extreme
offset of +7819.  These are likely **multi-song containers** or
heavily customised derivations where the Soundmaster engine is embedded
deeper in the binary and the play routine is in a different page.
They still match the root SoedeSoft nibble-split pattern.

---

## Embedded ASCII signature

The `"88 SOEDESOFT-"` ASCII string in the data area is NOT used by
sidid for matching (sidid works on code bytes only).  It is present as
a human-readable watermark in the editor's data output.  The hyphen
suffix suggests the string continues — possibly the version number
follows (e.g. `"88 SOEDESOFT-V1.0"`).  This string would provide
a secondary classification signal if future tools scan for it directly.
