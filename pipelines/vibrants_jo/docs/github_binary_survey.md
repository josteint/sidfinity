---
source_url: local: hvsc85/MUSICIANS/J/JO/ (HVSC #84 local corpus)
fetched_via: local read
fetch_date: 2026-06-16
author: Poul-Jesper Olsen (JO)
content_date: 1988-2026
reliability: primary
---

# Vibrants/JO Player — Binary Survey from HVSC Corpus

## Corpus Summary

Engine tag in hvsc84.csv: `Vibrants/JO`
Total SIDs: 130
- MUSICIANS/J/JO/: 106 files (JO's own compositions)
- MUSICIANS/D/DRAX/Worktunes/Worktune_in_JOs_player.sid: DRAX tune in JO's engine
- MUSICIANS/H/HJE/: ~23 files (Hans Jürgen Ehrentraut)

## PSID Header Fields

- Magic: PSID
- Version: 2 throughout
- Speed: 0x00000000 throughout (VBI / 50 Hz, PAL)
- Songs: usually 1; some multi-subtune (Amok_Title has at least subtune 1/2)

Author field examples:
- "Jesper Olsen (JO)"
- "Hans Jürgen Ehrentraut (HJE)"
- "Thomas Mogensen (DRAX)"

Released field examples:
- "1988-89 Amok Sound Dept."
- "1988 Amok Sound Dept."
- "1989 Jesper Olsen"
- "1990-91 Vibrants"

## Load / Init / Play Addresses

The player is fully relocatable. Observed load addresses span: $0800 – $F000.
No fixed canonical base address.

Common init-to-load offsets:
- init == load (player starts directly with init)
- init == load + 3 (3-byte header before init: either a JMP dispatch or small data table)
- init == load + 6 (6-byte header)

Common play-to-init relationship:
- play == init + 3 (most common: both via a 3-byte JMP table at top)
- play == init + 6
- Some tunes have play < init (play entry first in memory)

## Code Size Distribution (106 JO/ SIDs)

- Minimum: 635 bytes (Grid)
- Maximum: 6705 bytes
- Average: ~2966 bytes
- Typical: 2000–3500 bytes

This places the player skeleton at roughly 600–1000 bytes (player code) + song data.

## Layout Observations from Representative Samples

### Grid.sid — 635 bytes, Load=$1000, Init=$1169, Play=$1000

The play() entry is at the very start of the load address.
Init is near the END of the binary at +$169.

Play at $1000:
```
A2 02    LDX #$02
C6 75    DEC $75      ; decrement frame counter (zero page $75)
10 04    BPL $+6      ; branch if not underflowed
...
```
Three-voice loop structure: X = 2, 1, 0 iterates all voices.

Init at $1169:
```
A2 3A    LDX #$3A     ; 58 voice register slots (0-57)
A9 00    LDA #$00
95 40    STA $40,X    ; zero-page voice state starting at $40
9D 00 D4 STA $D400,X  ; SID register reset
CA       DEX
10 F6    BPL loop
A9 1F    LDA #$1F
8D 18 D4 STA $D418    ; master vol = $0F, filter off
60       RTS
```
Zero-page voice state base: **$40** (likely $40-$77 for 3 voices × ~20 bytes each).
SID base: $D400 (standard).

### Airwolf_Theme.sid — 2769 bytes, Load=$1000, Init=$1003, Play=$1009

Dispatch table at top:
```
$1000: 00 00 00     (3 pad bytes)
$1003: 4C 1B 1A    JMP $1A1B    ; init jumps into high range
$1006: 00 00       (2 pad bytes)
$1009: 4C 77 12    JMP $1277    ; play dispatches into middle range
```
Data and/or instrument tables appear between $100C and $1276.
Player engine code starts at $1277.

The B9 ?? ?? pattern (sig 6: LDA abs,y followed by DE and BC) confirmed at code
offsets consistent with an instrument/note-fetch subroutine.

Sig 10 (`30 03 4C`) confirmed at file offset $6FB → $17FB (load $1000 + $7FB).

### Amok_Title.sid — 3864 bytes, Load=$1000, Init=$1000, Play=$1003

Multi-subtune (song selector logic at start):
```
$1000: 4C 0A 18    JMP $180A    ; init jumps to high end (player init code)
$1003: 4C 15 10    JMP $1015    ; play dispatches to $1015
$1006: data...                   ; per-subtune table (e.g.: 01 02 04 00...)
```
Play at $1015 reads a subtune state byte and dispatches accordingly.

High-end code confirmed at $180A (near end of $1000 + 3864 = $1F18).
Data (song tables, instrument data) appears in the lower region $1006–$17FF.

## Key Structural Inferences from sidid Signatures

(Decoded from the raw 6502 opcodes in the signatures — see src/sidid_vibrants_jo_signatures.txt)

1. **Three-voice loop**: `A2 02 ... CA 10 ?? 60` pattern (sig 9) = DEX loop for voices 2/1/0.
2. **Indirect table access**: `BC ?? ?? B1 ??` = LDY abs,x / LDA (zp),y — pointer-indirect note/command fetch.
3. **Command sentinels in note stream**:
   - $F0 = some command byte (pattern end? instrument?)
   - $FF = sequence end / restart
   - $60 = note offset threshold (notes stored as offset-from-$60 or similar)
   - $80 = note boundary marker or high-note flag
   - $D0 = instrument-select command: `CMP #$D0 / BCC / SBC #$D0 / ASL / ASL / ASL` → instr_index × 8
4. **Gate-off pattern**: LDA #0 → STA $D405,y, STA $D406,y; LDA #8 → STA $D404,y (test bit = gate off).
5. **INC $D4xx,x patterns** (`FE ?? ?? FE ?? ??`): repeated INC operations, possibly advancing sequence pointers stored in SID-adjacent zero page or RAM.
6. **DE ?? ??** (`DE` = DEC abs,x) combined with `FE` (INC abs,x) = pointer management in zero-page or RAM tables.

## Zero-Page Layout Clues

From Grid.sid init:
- $40: voice 0 state block start (LDX #$3A → STA $40,X covers down to $40)
- $75: per-voice frame counter (DEC $75 in play loop)
- Loop: X from $3A ($58) down to $00 → ZP $40 to $7A (58 bytes of state)

Three voices × ~19 bytes each in zero page starting at $40.

## Note/Command Encoding Hypothesis

From the sidid signatures:
- Values < $60: likely raw note indices (0–95, covering ~8 octaves at 12 notes/octave)
- Values $60–$7F: ?? (could be extended notes or early commands)
- Bit 7 set ($80–$FF): command bytes
  - $80: some gate or boundary command
  - $D0+: instrument select (index = (byte - $D0) * 8)
  - $F0: sequence command or block terminator
  - $FF: end-of-sequence / loop

This is inferred from the sidid signature byte values only. Verification requires disassembly.

## Version / Variant Evidence

No sidid version variants seen (only one [Vibrants/JO] block, no V1/V2/V3 distinction).
The wide address-range variation is relocation, not versioning.
The HJE tunes use the same engine (same sidid match) but were composed after JO joined Vibrants.
