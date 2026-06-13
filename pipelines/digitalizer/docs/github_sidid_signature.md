---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (primary); https://raw.githubusercontent.com/WilfredC64/player-id/main/config/sidid.cfg (secondary)
fetched_via: direct
fetch_date: 2026-06-13
author: cadaver (Lasse Ööyrni); WilfredC64 (Wilfred Bos)
content_date: ongoing (cadaver/sidid last commit visible; WilfredC64/player-id maintained 2024+)
reliability: primary
---

# Digitalizer — sidid.cfg Signature Blocks

## Source: cadaver/sidid (https://github.com/cadaver/sidid)

The canonical SID playroutine identity scanner. Signatures contributed by
Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos, and cadaver.
sidid.cfg is ~4,200+ lines covering hundreds of C64 music players.

### Entry 1 — Digitalizer_V3.0 (cadaver/sidid, ~line 1078)

```
Digitalizer_V3.0

FE 3A 03 B1 FB C8 C9 80 90 22 C9 C0 B0 1E 69 80 9D 3D 03 9D 40 03 C9 3F D0 0C FE 3A 03 B1 FB C8 END
```

Single-pattern, 32-byte exact (no wildcards). All bytes fixed. `END` terminates.

**Byte breakdown (hex → decimal):**
```
FE 3A 03  → INC $033A      (16-bit index increment at absolute $033A)
B1 FB     → LDA ($FB),Y   (indirect indexed load via ZP $FB)
C8        → INY
C9 80     → CMP #$80      (compare with $80 — sample midpoint / MSB flag)
90 22     → BCC +$22      (branch if below $80)
C9 C0     → CMP #$C0      (compare with $C0)
B0 1E     → BCS +$1E      (branch if >= $C0)
69 80     → ADC #$80      (add $80 — sign-extend or bias)
9D 3D 03  → STA $033D,X   (store to indexed absolute — output buffer)
9D 40 03  → STA $0340,X   (store to second location — two channels?)
C9 3F     → CMP #$3F      (range check $3F)
D0 0C     → BNE +$0C      (skip if not $3F)
FE 3A 03  → INC $033A     (repeat of the opening bytes — confirms loop structure)
B1 FB     → LDA ($FB),Y
C8        → INY
```

**Structural interpretation (OPEN — needs RE):**
- `$033A` is an absolute counter/index, not relocatable — this is a fixed-load-address engine
- `$FB`/`$FC` is a ZP pointer to sample/pattern data
- Double-store to `$033D` and `$0340` suggests stereo or two-voice output buffer
- `$C0` and `$80` boundary checks are sample amplitude clipping/bias logic
- The signature repeats `FE 3A 03 B1 FB C8` — it spans a loop body that executes twice in sequence
- **The V3.0 signature identifies a DIGI/sample playback routine, not a tracker sequence engine.** The bytes describe sample-reading and DAC-writing logic.
- OPEN: What is at $033A through $0340? What is the player load address?

### Entry 2 — Digitalizer_V2.x (cadaver/sidid, ~line 1083)

```
Digitalizer_V2.x

9D ?? ?? 0A 90 ?? B9 END
```

7-byte pattern with two wildcard pairs. Short and loose.

**Byte breakdown:**
```
9D ?? ??  → STA $????,X    (indexed absolute store — output to variable address)
0A        → ASL A          (arithmetic shift left — amplitude scaling)
90 ??     → BCC +??        (branch on no carry — conditional skip)
B9        → LDA $????,Y    (absolute indexed by Y — table lookup)
```

**Structural interpretation (OPEN — needs RE):**
- `STA $????,X` + `ASL A` + `BCC` + `LDA $????,Y`: consistent with a sample output loop
- The wildcard addresses mean the player IS relocatable (unlike V3.0)
- Very short signature — high false-positive risk; cadaver uses it as a fallback
- OPEN: Does this match V2.2, V2.5, V2.7, V2.8 all? Or only some?

---

## Source: WilfredC64/player-id (https://github.com/WilfredC64/player-id/main/config/sidid.cfg)

This is a maintained fork/derivative. The Digitalizer entries **match cadaver's exactly**:

```
Digitalizer_V3.0
FE 3A 03 B1 FB C8 C9 80 90 22 C9 C0 B0 1E 69 80 9D 3D 03 9D 40 03 C9 3F D0 0C FE 3A 03 B1 FB C8 END

Digitalizer_V2.x
9D ?? ?? 0A 90 ?? B9 END
```

No additional version entries (no V2.2, V2.5, V2.7, V2.8, V3.5 discrete entries).

---

## Related entries in sidid.cfg — same author / era

### Olav_Moerkrid (cadaver/sidid)

A SEPARATE player identity — NOT named "Digitalizer" but attributed to Olav Mørkrid.
This is either a different tool or a sub-component (possibly the Olav_Moerkrid entry
detects the PLAYER ROUTINE embedded in music SIDs, while Digitalizer_V* detects the
EDITOR TOOL CODE).

**cadaver/sidid version:**
```
Olav_Moerkrid

29 80 60 DE ?? ?? ?? ?? ?? 20 ?? ?? 18 BD ?? ?? 7D ?? ?? 8D ?? ?? BD ?? ?? 7D ?? ?? 8D ?? ?? A4 END
B9 ?? ?? 49 01 29 01 F0 ?? BD END
F6 0C C8 B1 FC 30 0F C9 7F D0 E5 END
```

Three separate pattern lines before END — sidid.cfg `AND` semantics: all three must
match (each after a forward scan) for the signature to fire. Details:

**Pattern A:** `29 80 60 DE ?? ?? ...`
```
29 80     → AND #$80       (mask bit 7)
60        → RTS
DE ?? ??  → DEC $????,X    (indexed decrement — counter/envelope step)
...
20 ?? ??  → JSR $????      (subroutine call)
18        → CLC
BD ?? ??  → LDA $????,X    (load from indexed table)
7D ?? ??  → ADC $????,X    (add from indexed table — freq accumulator)
8D ?? ??  → STA $????      (store freq to SID register)
BD ?? ??  → LDA $????,X
7D ?? ??  → ADC $????,X
8D ?? ??  → STA $????      (second SID write — likely hi freq byte)
A4 ??    → LDY $??         (load Y from ZP)
```

**Pattern B:** `B9 ?? ?? 49 01 29 01 F0 ?? BD`
```
B9 ?? ??  → LDA $????,Y    (table lookup by Y)
49 01     → EOR #$01       (toggle bit 0 — gate bit flip)
29 01     → AND #$01       (isolate bit 0 — gate)
F0 ??     → BEQ +??        (branch if gate=0)
BD        → LDA $????,X... (load next parameter)
```

**Pattern C:** `F6 0C C8 B1 FC 30 0F C9 7F D0 E5`
```
F6 0C     → INC $0C,X      (ZP-indexed increment — voice state byte at $0C+X)
C8        → INY
B1 FC     → LDA ($FC),Y    (ZP pointer $FC indirect indexed)
30 0F     → BMI +$0F       (branch if negative — sentinel check)
C9 7F     → CMP #$7F       (compare $7F — end-of-pattern or tie marker)
D0 E5     → BNE -$1B       (loop back)
```

**WilfredC64/player-id version** (slightly different Pattern A):
```
Olav_Moerkrid

98 18 7D ?? ?? A8 B9 ?? ?? C9 FF D0 ?? BD ?? ?? 18 E9 02 9D
BC ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 DE ?? ?? D0 ?? BC ?? ?? B9 ?? ?? 29 0F 0A
4A 4A 4A 4A 85 ?? BD ?? ?? 38 E5 ?? 9D ?? ?? BD ?? ?? E9 00
```

These patterns differ significantly between cadaver and Wilfred — Wilfred's version
detects a different revision of the same player. The bytes suggest:
- `99 01 D4` = `STA $D401,Y` — SID write (pulse hi)
- `99 00 D4` = `STA $D400,Y` — SID write (freq lo)
- `4A 4A 4A 4A` — four LSR A = divide by 16 (envelope/speed step)
- `C9 FF` — compare with $FF end-of-sequence marker
- `38 E5 ??` — SEC + SBC ZP (delta calculation)

### Oeyvind_Jergan (cadaver/sidid)

Another Norwegian scener's player, included for completeness (may be a collaborator
or contemporary):

```
Oeyvind_Jergan

A2 78 A9 00 9D 34 03 CA 10 F8 A2 17 9D 00 D4 CA 10 FA A9 0F 8D
A2 ?? 0A 0A 0A 18 0A 85 FE 90 01 E8 86 FF AE ?? ?? AD ?? ?? 9D ?? ?? AD ?? ?? 9D ?? ?? A9 00 9D
```

Pattern A start: `A2 78 A9 00 9D 34 03 CA 10 F8` = `LDX #$78 / LDA #$00 / STA $0334,X / DEX / BPL` — clear $02BC..$0333 (a 120-byte zeroing loop). `A2 17 9D 00 D4 CA 10 FA` = `LDX #$17 / STA $D400,X / DEX / BPL` — clear all 24 SID registers.

### Panorama (cadaver/sidid and WilfredC64)

Likely the Panoramic Designs player (Olav's personal release player, distinct from
the tracker editor detection):

```
Panorama

AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? 29 01 D0
```

Pattern interpretation:
```
AD ?? ??  → LDA $????       (load absolute — voice active flag?)
D0 03     → BNE +3          (skip next)
4C ?? ??  → JMP $????       (jump to next voice — skip if inactive)
[repeated 3x for 3 voices]
AD ?? ??  → LDA $????
29 01     → AND #$01        (test bit 0 — gate bit or flag)
D0        → BNE ...
```

This is a 3-voice gate/skip loop. Each voice checks an activity flag; if nonzero,
it jumps to the next-voice handler. The final `29 01` isolates bit 0.
OPEN: Is this the RELEASE player or a separate Panoramic tool?

---

## sidid Scanning Mechanics (from sidid.c)

Relevant to understanding what "matches at offset X" means:

1. **No fixed offset scanning** — `identifybytes()` scans the ENTIRE file buffer linearly from byte 0.
2. **Multiple pattern lines** (for Olav_Moerkrid's 3 patterns) use `AND` semantics:
   - After matching pattern A ending at position P, the scanner continues from P searching for pattern B, etc.
   - `??` = wildcard (any byte).
   - `END` = match success.
3. **For Digitalizer_V3.0**: the 32-byte pattern has NO wildcards — exact match anywhere in the file.
4. **Player name is a non-hex, non-keyword token** — first non-hex token after the previous `END` starts a new entry.
5. **Signature file format:** whitespace-separated tokens; hex pairs, `??`, `AND`, `END`, or player-name strings.

---

## Version Coverage Summary

| sidid label     | Covers                    | Wildcards | Confidence |
|-----------------|---------------------------|-----------|------------|
| Digitalizer_V3.0 | V3.0 only (fixed addresses) | none      | high (32 bytes exact) |
| Digitalizer_V2.x | V2.2, V2.5, V2.7?, V2.8? | 2 pairs   | low (7 bytes, short) |
| Olav_Moerkrid    | Olav's player in music SIDs | many     | medium-high (3 chained patterns) |
| Panorama         | Panoramic Designs release player? | many | medium |

**No V3.5 entry exists** in either cadaver/sidid or WilfredC64/player-id.

---

## Leads to follow

- OPEN: The V3.0 signature has fixed absolute addresses ($033A, $033D, $0340, ZP $FB).
  This strongly implies V3.0 loads at a fixed address. RE needed: what is that load address?
- OPEN: Does `$033A`/`$033D`/`$0340` indicate the player loads into $0300-$03FF (C64 stack page)?
  The SID address space starts at $D400; `$033A`/`$033D`/`$0340` are in the stack page.
- OPEN: `$FB`/`$FC` ZP pointers appear in both Digitalizer_V3.0 and Olav_Moerkrid Pattern C
  (`B1 FC`) — this is the same ZP pair used across versions. Likely the sample/pattern data pointer.
- OPEN: V3.5 was co-coded by 6R6 and Kjell Nordbo of Blues Muz' — is there a SEPARATE
  "Blues_Muz_Player" signature in sidid.cfg that might cover V3.5-generated SIDs?
- OPEN: "Olav_Moerkrid" vs "Digitalizer_V*" — are these two distinct detection targets
  (one for the tracker's own init code in music SIDs, one for the editor binary itself)?
- OPEN: The Wilfred vs cadaver Olav_Moerkrid pattern discrepancy — different revision?
  The Wilfred version has explicit SID register writes ($D400/$D401), making it the player
  routine. The cadaver version has no $D4xx addresses visible — possible it's the editor code.
- SOURCE TO FETCH: sidid.nfo binary (45.2KB) contains the full player/editor database
  with author/year/CSDB links — includes the Digitalizer V2.x and V3.0 entries with
  CSDB release IDs 33646 and 33649.
