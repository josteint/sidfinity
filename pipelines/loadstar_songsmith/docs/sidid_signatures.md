---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-14
author: cadaver (Covert Bitops)
content_date: unknown (file continuously updated; fetched 2026-06-14)
reliability: primary
---

# Loadstar SongSmith — sidid Byte Signatures

## Sources

- **cadaver/sidid** — https://github.com/cadaver/sidid  
  The authoritative C64 playroutine identity scanner. `sidid.cfg` is the master
  signature database, fetched raw from
  `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg`.

- **WilfredC64/player-id** — https://github.com/WilfredC64/player-id  
  A Rust re-implementation of sidid that ships its own `config/sidid.cfg`.
  Independently confirmed to carry the same four SongSmith entries (signatures
  are byte-for-byte identical to cadaver's copy). Format documented in
  `doc/Signature_File_Format.txt` (V2.0).

- **sidid.nfo** (cadaver) — `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo`  
  References the CSDb Songsmith entry https://csdb.dk/release/?id=122855 as the
  authoritative REFERENCE for this player entry. No individual contributor for
  these signatures is named in the nfo.

Raw signature blocks are saved verbatim in:
`pipelines/loadstar_songsmith/docs/src/sidid_loadstar_songsmith_signatures.txt`

---

## Signature Format Primer

Each entry in `sidid.cfg` (V2 format):
- **Name line**: identifier string, no spaces (e.g. `Loadstar_SongSmith_v2`)
- **Pattern line(s)**: space-separated hex bytes; `??` = wildcard (any byte);
  `END` = explicit terminator; `&&` = skip-to-next-match (V2 only)
- Multiple pattern lines under the same name = alternative patterns (OR logic):
  the tune is tagged if ANY line matches.
- Wildcards replace relocated zero-page addresses, absolute-address operands,
  and other variable fields, while preserving SID I/O register references
  ($D400–$D418 operands are kept literal where they appear).

---

## Four Detected Variants

### 1. `Loadstar_SongSmith_v1`

```
B1 F9 E6 F9 D0 02 E6 FA C9 19 90 11 C9 1D 90 END
```

**Decoded (6502 assembly):**

```
B1 F9       LDA ($F9),Y       ; indirect-Y load from pointer at $F9/$FA
E6 F9       INC $F9           ; increment low byte of pointer
D0 02       BNE +2            ; branch if no carry
E6 FA       INC $F9+1==$FA    ; increment high byte of pointer  [NOTE: typo in opcode — should be INC $FA]
C9 19       CMP #$19          ; compare A to 25
90 11       BCC +17           ; branch if below (note-range low limit?)
C9 1D       CMP #$1D          ; compare A to 29
90 ??       BCC +?            ; branch if below (END terminates here: next byte masked)
```

This is a fundamentally different code structure from v2/v3/unversioned. The
`($F9),Y` indirect-Y addressing + inline INC ZP + dual range-compare pattern
is characteristic of a very simple note-lookup or data-stream-read loop.

**Key distinctions from v2/v3:**
- No `38 E9 xx 0A` (SEC, SBC #, ASL A) preamble.
- No `8D 00 D4` / `8D 01 D4` (STA $D400, STA $D401) writes in signature.
- Likely a much earlier/simpler player with different data layout.
- Fixed ZP pointers $F9/$FA — these are concrete (not wildcarded), meaning this
  variant is NOT relocated.

### 2. `Loadstar_SongSmith_v2`

```
38 E9 01 0A A8 B9 90 C2 8D 00 D4 C8 B9 90 C2 8D 01 D4
A0 ?? B1 ?? 8D ?? ?? 18 A5 ?? 69 ?? 85 ?? A5 ?? 69 ?? 85 ??
AD ?? ?? 8D 04 D4 CE ?? ?? AD END
```

**Decoded (6502):**

```
38          SEC
E9 01       SBC #$01          ; voice/note index arithmetic
0A          ASL A             ; ×2 (word-table index)
A8          TAY               ; Y = table index
B9 90 C2    LDA $C290,Y       ; load freq-lo from fixed freq table at $C290
8D 00 D4    STA $D400         ; write to SID V1 freq-lo
C8          INY
B9 90 C2    LDA $C290,Y       ; load freq-hi from same table
8D 01 D4    STA $D401         ; write to SID V1 freq-hi
A0 ??       LDY #nn           ; immediate Y (voice/offset)
B1 ??       LDA (??),Y        ; indirect-Y
8D ?? ??    STA abs           ; store to SID register
18          CLC
A5 ??       LDA zp            ; 16-bit pointer add
69 ??       ADC #imm
85 ??       STA zp
A5 ??       LDA zp
69 ??       ADC #imm
85 ??       STA zp
AD ?? ??    LDA abs
8D 04 D4    STA $D404         ; write to SID V1 control register
CE ?? ??    DEC abs
AD          [END — next byte masked]
```

**Key signature markers:**
- Freq table is at **fixed absolute address $C290** (concrete, not wildcarded).
  This means v2 is NOT relocated (loads at a specific address with the table at
  $C290). This is the primary v2 discriminator.
- Note arithmetic: `SEC / SBC #$01 / ASL` = `(note - 1) * 2` → word-table index.
- Writes `$D400` (freq-lo), `$D401` (freq-hi), `$D404` (voice 1 control).
- 16-bit pointer arithmetic (CLC/ADC/STA pair) for data pointer advance.
- `DEC abs` at end = probably a duration/tick counter decrement.

### 3. `Loadstar_SongSmith_v3`

```
38 E9 ?? 0A A8 B9 ?? ?? 8D 00 D4 C8 B9 ?? ?? 8D 01 D4
AD ?? ?? 8D 04 D4 A0 ?? B1 ?? 8D ?? ??
18 A5 ?? 69 ?? 85 ?? A5 ?? 69 00 85 ?? CE ?? ?? AD END
```

**Differences from v2:**
- `E9 ??` (SBC #??) — the subtract constant is wildcarded; v2 had `E9 01` (SBC #1
  concrete). This allows versions that subtract a different offset before the ×2
  multiply.
- Freq table address wildcarded (`B9 ?? ??`) — v3 can be RELOCATED. This is the
  key structural advance.
- `$D404` write moved earlier in the sequence (before indirect-Y load in v3,
  after it in v2).
- The 16-bit pointer increment has `69 00` (ADC #0, i.e. carry propagation only)
  for the high byte, rather than `69 ??` — the high byte of the pointer step is
  zero (data is organized as a flat array within a page).
- Otherwise the same conceptual flow: note→freq table→SID registers→data ptr
  advance→duration DEC.

### 4. `Loadstar_SongSmith` (unversioned)

```
38 E9 ?? 0A A8 B9 ?? ?? 8D 00 D4 C8 B9 ?? ?? 8D 01 D4
AD ?? ?? 8D 04 D4 EE ?? ?? AC ?? ?? B1 ?? 8D ?? ??
EE ?? ?? CE ?? ?? AD END
```

**Differences from v3:**
- After `8D 04 D4` (STA $D404): uses `EE ?? ??` (INC abs) + `AC ?? ??` (LDY abs)
  instead of `A0 ?? B1 ??` (LDY #imm / LDA (zp),Y). The data pointer is now an
  absolute address incremented via INC, and Y is loaded from an absolute address
  rather than being an immediate — a slightly different data-read architecture.
- Two `EE ?? ??` (INC abs) instructions instead of the 16-bit CLC/ADC pointer
  arithmetic: simpler byte-at-a-time pointer increment.
- `AC ?? ??` (LDY abs) — Y loaded from absolute (likely voice-state RAM).

This variant reads data via absolute INC + LDY abs rather than a ZP indirect
pointer — a distinct data-stream model from v2/v3.

---

## Version Discrimination Summary

| Variant | Freq table addr | SBC operand | Data ptr model | Reloc? |
|---------|----------------|-------------|----------------|--------|
| v1 | n/a (different arch) | n/a | ZP indirect ($F9/$FA), fixed | No |
| v2 | $C290 (fixed) | #$01 (fixed) | ZP indirect + 16-bit CLC/ADC | No |
| v3 | wildcarded | wildcarded | ZP indirect + 16-bit CLC/ADC, high-step=0 | Yes |
| unversioned | wildcarded | wildcarded | ABS indirect (INC abs + LDY abs) | Yes |

The four HVSC engine names map to:
- `Loadstar_SongSmith_v1` — very early/simple architecture, fixed ZP $F9/$FA
- `Loadstar_SongSmith_v2` — second-gen, fixed freq table at $C290
- `Loadstar_SongSmith_v3` — third-gen, relocated, same data model as v2
- `Loadstar_SongSmith`    — latest (or parallel branch), relocated, different data-read arch

OPEN (RE needed): The relationship between the unversioned tag and v1/v2/v3 is
unclear. The unversioned entry might be an earlier catchall or a fourth
independent version. Checking HVSC SIDs tagged "Loadstar_SongSmith" (unversioned)
vs "Loadstar_SongSmith_v3" will clarify whether one supersedes the other.

---

## Leads to Follow

- **Disassemble a v1 SID** to understand the full play loop: the 15-byte v1
  signature is very short and could match multiple unrelated engines if the
  pattern isn't unique — worth running sidid on the whole Loadstar SongSmith HVSC
  corpus to see which v-tag hits which files.
- **Disassemble v2 at $C290 origin** — the freq table at a fixed address is a
  strong anchor to reconstruct the load map.
- **Confirm unversioned vs v3** — are they mutually exclusive across the HVSC
  corpus? Or does one SID trigger both?
- **Joe Garrett / Alan Gardner** (precursor songmaker authors per comp.sys.cbm
  thread for Loadstar #168) — did their earlier tool ship in Loadstar issues
  27/28 (as hinted in the #168 thread: "reverse-engineer the song codes from
  LS #27-28")? Could v1 correspond to that earlier tool?
