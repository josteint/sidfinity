---
source_url: multiple — see per-section citations below
fetched_via: WebFetch + WebSearch
fetch_date: 2026-06-13
author: synthesised from primary sources (sidid.cfg, CSDb, sidid.nfo)
content_date: 1989–2026
reliability: primary (sidid.cfg byte signatures, CSDb release metadata); secondary (interpretations)
---

# Digitalizer — TASK 2: Three player variants and sidid tag families

## Summary of findings

sidid.cfg (cadaver) contains SIX entries attributable to Olav Mørkrid's work:

1. `Digitalizer_V2.x` — detects V2.x editor binary or its player code
2. `Digitalizer_V3.0` — detects V3.0 sample/digi playback loop (fixed load address)
3. `Olav_Moerkrid` — detects the sequence/tracker player engine in music SIDs (cadaver variant)
4. `Olav_Moerkrid` (WilfredC64 variant) — a DIFFERENT pattern for a different player revision
5. `OmegaSupreme_Digi` — detects the 4-bit digi-to-$D418 playback routine
6. `Panorama` — detects a 3-voice gate/skip dispatch loop (Panoramic Designs release player)

**Key finding:** `Olav_Moerkrid` in sidid.cfg is NOT a separate product — it is a
composer/author attribution tag, placed alphabetically in the O-section of sidid.cfg
(between `Oeyvind_Jergan` and `OmegaSupreme_Digi`). It detects the tracker sequence
player engine embedded in music SIDs compiled with Digitalizer. The distinction from
`Digitalizer_V*` is that `Olav_Moerkrid` fires on the runtime play routine, while
`Digitalizer_V*` may fire on the editor code or sample-handling code.

**V3.5 sidid coverage:** V3.5 (1995, 6R6 re-assembly of V3.0) has NO dedicated
sidid entry. V3.5-generated SIDs will match `Digitalizer_V3.0` if the player
code was preserved, or potentially nothing if 6R6 replaced the player.

---

## 1. Complete sidid.cfg signature inventory (Olav Mørkrid / Digitalizer)

All from https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
(WebFetch 2026-06-13)

### 1a. Digitalizer_V2.x

```
Digitalizer_V2.x
9D ?? ?? 0A 90 ?? B9 END
```

- 7-byte pattern with 2 wildcard pairs (loose match)
- `9D ?? ??` = STA $????,X → RELOCATABLE (wildcard address)
- `0A` = ASL A (amplitude scale)
- `90 ??` = BCC (conditional branch)
- `B9` = LDA $????,Y (start of table read)
- sidid.nfo: Author = Olav Mørkrid, Released 1989, CSDb id 33646
- OPEN: Does this match V2.2, V2.5, V2.7, V2.8 uniformly, or only some?

### 1b. Digitalizer_V3.0

```
Digitalizer_V3.0
FE 3A 03 B1 FB C8 C9 80 90 22 C9 C0 B0 1E 69 80 9D 3D 03 9D 40 03 C9 3F D0 0C FE 3A 03 B1 FB C8 END
```

- 32-byte pattern, NO wildcards (high confidence)
- Contains ABSOLUTE addresses: $033A, $033D, $0340 → FIXED load address
- ZP pointer: $FB (and $FC) for data read
- Byte breakdown:
  - `FE 3A 03` = INC $033A (absolute index counter)
  - `B1 FB` = LDA ($FB),Y (indirect-indexed read via ZP $FB)
  - `C8` = INY
  - `C9 80 90 22` = CMP #$80 / BCC (below-midpoint check)
  - `C9 C0 B0 1E` = CMP #$C0 / BCS (above-max check)
  - `69 80` = ADC #$80 (bias/sign-extend)
  - `9D 3D 03` = STA $033D,X (first output buffer write)
  - `9D 40 03` = STA $0340,X (second output buffer write — two channels)
  - `C9 3F D0 0C` = CMP #$3F / BNE (special-case check)
  - then the 6-byte opener repeats → loop structure
- INTERPRETATION: This is a SAMPLE/DIGI playback routine, NOT the tracker engine.
  The $80/$C0 boundary checks are standard 1-bit/4-bit sample amplitude logic.
  The double STA suggests stereo or two-voice digi output.
- sidid.nfo: Author = Olav Mørkrid, Released 1992, CSDb id 33649

### 1c. Olav_Moerkrid (cadaver/sidid)

```
Olav_Moerkrid
29 80 60 DE ?? ?? ?? ?? ?? 20 ?? ?? 18 BD ?? ?? 7D ?? ?? 8D ?? ?? BD ?? ?? 7D ?? ?? 8D ?? ?? A4 END
B9 ?? ?? 49 01 29 01 F0 ?? BD END
F6 0C C8 B1 FC 30 0F C9 7F D0 E5 END
```

Three chained patterns (all three must match in sequence):

**Pattern A:** `29 80 60 DE ?? ...`
- `29 80` = AND #$80 → mask bit 7 (flag/envelope test)
- `60` = RTS
- `DE ?? ??` = DEC $????,X → indexed counter decrement (envelope/duration step)
- `20 ?? ??` = JSR → subroutine call
- `18 BD ?? ?? 7D ?? ?? 8D ?? ??` = CLC + LDA $,X + ADC $,X + STA → frequency accumulate-and-write
- This pattern repeats for both frequency bytes → two SID freq writes (lo+hi) per voice

**Pattern B:** `B9 ?? ?? 49 01 29 01 F0 ?? BD`
- `B9 ?? ??` = LDA $????,Y → table read
- `49 01` = EOR #$01 → toggle bit 0 (gate bit flip)
- `29 01` = AND #$01 → isolate bit 0
- `F0 ??` = BEQ → skip if gate=0
- Gate toggle logic (note-on / note-off handling)

**Pattern C:** `F6 0C C8 B1 FC 30 0F C9 7F D0 E5`
- `F6 0C` = INC $0C,X → ZP-indexed increment of voice state byte at ZP+$0C+voice (!)
- `C8` = INY
- `B1 FC` = LDA ($FC),Y → indirect-indexed read via ZP $FC (sequence data pointer)
- `30 0F` = BMI → branch if negative byte (special command dispatch)
- `C9 7F` = CMP #$7F → compare with $7F (end-of-pattern sentinel)
- `D0 E5` = BNE → loop back

**KEY FORMAT FACTS from Pattern C:**
- ZP $FC = sequence/pattern data pointer (pair $FB/$FC confirmed across V3.0 and here)
- INC $0C,X implies voice state counters live at ZP$0C, $0D, $0E (for voices 0, 1, 2)
- Sentinel $7F = end-of-pattern marker (cadaver version)
- Negative bytes ($80+) = special command bytes (effect/instrument dispatch)

**Position in sidid.cfg:** Between `Oeyvind_Jergan` and `OmegaSupreme_Digi` — confirms
this is an AUTHOR attribution entry (O-section alphabetically), not a product name.
Author-attributed entries in sidid detect player routines embedded in music SIDs by
that composer, regardless of which editor produced them.

### 1d. Olav_Moerkrid (WilfredC64/player-id — DIFFERENT pattern)

```
Olav_Moerkrid
98 18 7D ?? ?? A8 B9 ?? ?? C9 FF D0 ?? BD ?? ?? 18 E9 02 9D END
BC ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 DE ?? ?? D0 ?? BC ?? ?? B9 ?? ?? 29 0F 0A END
4A 4A 4A 4A 85 ?? BD ?? ?? 38 E5 ?? 9D ?? ?? BD ?? ?? E9 00 END
```

Key differences from cadaver's pattern:
- `C9 FF` = CMP #$FF → sentinel is $FF, not $7F (DIFFERENT song data encoding)
- `99 01 D4` = STA $D401,Y → SID pulse-hi write visible (player routine confirmed)
- `99 00 D4` = STA $D400,Y → SID freq-lo write visible
- `4A 4A 4A 4A` = four LSR A → divide by 16 (4-bit step / ADSR scaling)
- `29 0F` = AND #$0F → 4-bit nibble extraction
- No `F6 0C` / `B1 FC` → different ZP layout in this revision

OPEN: The $7F vs $FF sentinel discrepancy is format-significant. One possibility:
- Cadaver's pattern detects a V2.x-era player (using $7F)
- Wilfred's pattern detects a V3.x-era player (using $FF)
or vice versa. RE of the disk images would resolve this.

Source: `docs/src/sidid_signatures_raw.txt` (already in this docs directory, primary)

### 1e. OmegaSupreme_Digi

```
OmegaSupreme_Digi
85 01 A0 00 B1 FB 4A 4A 4A 4A 8D 18 D4 A9 END
```

- `85 01` = STA $01 → C64 bank-switching register write (!)
- `A0 00` = LDY #0
- `B1 FB` = LDA ($FB),Y → read from ZP $FB pointer (same $FB as V3.0 digi signature)
- `4A 4A 4A 4A` = four LSR A → 4-bit right-shift (4-bit sample)
- `8D 18 D4` = STA $D418 → SID master volume register = DAC output for digi playback
- `A9` = LDA #imm (next immediate value load)

This is UNAMBIGUOUSLY a 4-bit digi-to-$D418 player. Key facts:
1. `STA $01` implies banking — the sample data may be in ROM-banked RAM ($A000–$BFFF
   or $E000–$FFFF). The bank switch takes effect immediately on next fetch.
2. ZP $FB is used here AND in V3.0 signature (`B1 FB`) AND in Pattern C (`B1 FC`) —
   $FB/$FC is the consistent song/sample data pointer pair across all player variants.
3. Handle "Omega Supreme" = Olav Mørkrid's early scene handle.

sidid.nfo: Author = Olav Mørkrid (Omega Supreme). No CSDb link or year in the nfo entry.

### 1f. Panorama

```
Panorama
AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? D0 03 4C ?? ?? AD ?? ?? 29 01 D0 END
```

Pattern structure (3× repeated):
- `AD ?? ??` = LDA $???? → load voice-active flag (absolute)
- `D0 03` = BNE +3 → skip if nonzero (voice is active)
- `4C ?? ??` = JMP $???? → jump to next voice handler (skip inactive voice)

Then:
- `AD ?? ??` = LDA $????
- `29 01` = AND #$01 → test bit 0 (gate bit or trigger flag)
- `D0` = BNE ...

**Interpretation:** 3-voice dispatch loop. Each voice checks an activity flag; inactive
voices are skipped via JMP. Final AND #$01 tests the gate/trigger. This is a play()
dispatcher, not a data format — it is the player routine's main loop structure.

**Relationship to Digitalizer:** The name "Panorama" in sidid.cfg plausibly means
"Panoramic Designs" (the group's internal shortened name). This may detect the player
routine embedded in SIDs released by Panoramic Designs as standalone music demos,
as opposed to SIDs compiled with the Digitalizer tracker editor tool.

OPEN: Does "Panorama" fire on the same SIDs as "Olav_Moerkrid" or different SIDs?
If different, it may be a standalone release player (a simpler player used in intros
and demos) vs. the full tracker player (Olav_Moerkrid).

---

## 2. What the HVSC sidid tags actually count

From the task description: HVSC84 contains:
- `Digitalizer_V2.x` — 542 SIDs
- `Digitalizer_V3.0` — 77 SIDs
- `Olav_Moerkrid` — 38 SIDs (a SEPARATE count from Digitalizer_V*)
- `Panorama` — 0 SIDs in HVSC84

### Interpretation of the 38 `Olav_Moerkrid` SIDs

The `Olav_Moerkrid` sidid tag fires SEPARATELY from `Digitalizer_V*`. Possible explanations:

**Hypothesis A (most likely): The 38 SIDs use Olav's player but NOT the standard
Digitalizer editor output.** These could be:
- Music SIDs written by Olav for his own demos (hand-assembled or using an earlier
  editor version before V2.2)
- SIDs where only Pattern A/B/C match but the V2.x/V3.0 sample routine patterns do not
- A different generation of the player (pre-V2.2, i.e. 1987–1988 era)

**Hypothesis B:** The `Digitalizer_V*` signatures target the SAMPLE/DIGI portion of
the engine (V2.x has a sample loop; V3.0 definitely does from the $80/$C0 checks).
Meanwhile `Olav_Moerkrid` targets the TRACKER/SEQUENCE portion. If a SID file only
contains one portion, it matches only one tag. The 542 `Digitalizer_V2.x` SIDs likely
contain BOTH the tracker AND sample code, giving full identification.

**Hypothesis C:** The 38 may be false positives (the 7-byte V2.x signature is very
loose). OPEN: run sidid on the 38 `Olav_Moerkrid` SIDs to see if they also match
`Digitalizer_V2.x` or not.

**What it is NOT:** The `Olav_Moerkrid` tag is NOT a different product/editor — it
is an author attribution. The alphabetical placement and the naming convention
(person's name vs product name) in sidid.cfg is definitive. Compare: `Oeyvind_Jergan`
(before), `OmegaSupreme_Digi` (after) — all are person-attributed player codes.

---

## 3. V3.5 sidid coverage — gap analysis

### The problem

V3.5 (1995, CSDb id 33650) was co-coded by 6R6 (Glenn Davanger, Blues Muz'/SHAPE) and
Kjell Nordbo. It is described by 6R6 as "a re-assembled hack of v3.0 with alot of new
functions." No `Digitalizer_V3.5` entry exists in either cadaver/sidid or WilfredC64/player-id.

### How V3.5 SIDs get classified in HVSC84

Three possible outcomes for a V3.5-generated SID:

**Case 1: Player code unchanged from V3.0.** If 6R6 only changed editor features
(new patterns/effects/UI) but left the player routine binary identical, V3.5 SIDs
will match `Digitalizer_V3.0` (32-byte exact match). The 77 `Digitalizer_V3.0` SIDs
in HVSC84 include V3.5-compiled SIDs in this case.

**Case 2: Player code modified.** If 6R6 changed the player routine (new opcodes, new
addresses), the 32-byte V3.0 pattern breaks. The SID would then:
- Match `Olav_Moerkrid` (if the sequence player Pattern C survived)
- Match nothing (if the pattern was sufficiently changed)
- Potentially match a Blues Muz' / SHAPE player entry (if 6R6 substituted his own engine)

**Case 3: Different player altogether.** The DTZ2SDI converter (CSDb id 237762) converts
Digitalizer V3.x format TO SID Duzz' It (SDI) format. SDI is 6R6's own C64 music format
(released 2014). This converter implies the formats are INCOMPATIBLE. But the existence
of the converter also suggests V3.5 SIDs use DIGITALIZER format output (not SDI),
because the converter is needed to migrate FROM Digitalizer TO SDI.

**Verdict (OPEN):** Most likely V3.5 SIDs match `Digitalizer_V3.0` (Case 1) — the
re-assembly preserved the player binary code, and "new functions" were in the editor
UI + feature set. The 77 `Digitalizer_V3.0` SIDs likely include both V3.0 and V3.5
produced material. RE confirmation needed.

---

## 4. V3.0 internal name: "v2.9(FF)"

The V3.0 zip (CSDb id 33649) contains an editor with internal version string "v2.9(FF)".
The CSDb community labeled it V3.0. The "(FF)" suffix is unexplained but possibly means:
- "Final" release (a common scene convention: "FF" = final final)
- A hex value in Olav's internal versioning (v2.9 = decimal 2.9; FF = no relation)

**Implication for player detection:** A SID file compiled with "V3.0" (= V2.9-FF) would
carry whatever player code 6R6 then re-assembled for V3.5. If the player binary is
byte-for-byte identical, the sidid pattern fires. If the re-assembly introduced any
change at the 32 fixed bytes of the V3.0 signature, it does not.

---

## 5. Version → sidid tag mapping (synthesised)

| Version | Year | sidid match (likely) | Confidence |
|---------|------|-----------------------|------------|
| V2.2 | 1989 | `Digitalizer_V2.x` + `Olav_Moerkrid` | medium (V2.x sig is short) |
| V2.5 | 1989 | `Digitalizer_V2.x` + `Olav_Moerkrid` | medium |
| V2.7 | ~1989–91 | `Digitalizer_V2.x` + `Olav_Moerkrid` | medium |
| V2.8 | 1991 | `Digitalizer_V2.x` + `Olav_Moerkrid` | medium |
| V3.0 | 1992 | `Digitalizer_V3.0` + `Olav_Moerkrid` | high (V3.0 sig exact) |
| V3.5 | 1995 | `Digitalizer_V3.0` (Case 1) or nothing | OPEN |
| Olav demos | 1987–88? | `Olav_Moerkrid` only | medium |
| Release intros | various | `Panorama` (?) | OPEN |

The 38 HVSC `Olav_Moerkrid`-only SIDs are likely:
- Pre-V2.2 music SIDs (before the Digitalizer sample routine was added), OR
- SIDs where the sample code was stripped (player-only output), OR
- A different generation of the player with the seq engine matching but not the V2.x sample loop

---

## 6. The "3-pattern player using ZP $FC/$FD + INC $0C" description

The task description identifies the `Olav_Moerkrid`-tagged player as "a SEPARATE
3-pattern player using ZP $FC/$FD + INC $0C." This description aligns precisely
with Olav_Moerkrid Pattern C from cadaver/sidid:

- `F6 0C` = INC $0C,X → matches "INC $0C"
- `B1 FC` = LDA ($FC),Y → matches "ZP $FC" (and $FD is likely the high byte of the pointer pair)
- "3-pattern" = the three chained match patterns in sidid.cfg

But this IS the Digitalizer player routine — it is not a different product. The
task description's "SEPARATE 3-pattern player" refers to the fact that sidid uses
THREE separate byte-pattern lines to identify it (chained match), not that there
are three distinct player products.

The $FC/$FD ZP pair is the sequence-data pointer. Pattern A uses `BD ?? ??` (LDA abs,X)
for frequency table reads; Pattern C uses `B1 FC` (LDA (FC),Y) for sequence reads.
Both pointers may co-exist: $FB/$FC for sample data and $FC/$FD for seq data, or
$FB = seq pointer lo, $FC = seq pointer hi.

OPEN: RE of the player to determine exact ZP memory map.

---

## Leads to follow

1. **RE the `Olav_Moerkrid` 38 SIDs vs `Digitalizer_V*` overlap.** Run sidid on all
   `Olav_Moerkrid`-tagged SIDs from HVSC84 and check which also match `Digitalizer_V2.x`
   or `Digitalizer_V3.0`. The non-overlapping subset is the pre-V2.2 or stripped-player
   population.

2. **V3.5 player code identity.** Disassemble one V3.5-generated SID (from HVSC84) and
   check whether the 32-byte V3.0 signature sequence appears at any offset. Confirm
   Case 1 (identical player) or Case 2 (modified player).

3. **$7F vs $FF sentinel discrepancy.** cadaver's Olav_Moerkrid Pattern C uses `CMP #$7F`;
   Wilfred's uses `CMP #$FF`. RE a V2.x SID and a V3.x SID to determine which sentinel
   each version uses. This would allow dating the format change.

4. **`Panorama` target population.** Run sidid on all HVSC84 SIDs and collect
   `Panorama` matches (HVSC84 count = 0 per task description, but Panorama IS in
   sidid.cfg). Either: (a) the signature does not fire on any HVSC84 SID, meaning
   these were never submitted to HVSC; or (b) the count is from an older HVSC.
   Check: does the `Panorama` entry fire on any Olav Mørkrid HVSC SID?

5. **`OmegaSupreme_Digi` STA $01 banking.** Identify which C64 bank the digi player
   reads from. The `STA $01` value determines the bank configuration. If $01 is set
   to $35 (ROM+IO enabled → RAM at $A000/$E000 banked out), the samples are in RAM
   above $8000. If $37 (all RAM), samples are standard RAM. This determines sample
   buffer placement.

6. **Blues_Muz_Player in sidid.cfg.** Check whether a `Blues_Muz_Player` or `SDI`
   entry exists in sidid.cfg. If it does and fires on V3.5 SIDs, that would confirm
   Case 2 (6R6 substituted his own engine in V3.5).

7. **sidid.nfo for Olav_Moerkrid and Panorama.** The sidid.nfo file (45.2 KB binary)
   was not parseable via WebFetch for the Olav_Moerkrid and Panorama entries — the
   model only retrieved Digitalizer_V*.x entries. Fetch and grep the raw bytes of
   sidid.nfo for "Panorama" and "Olav" to get any year/CSDb-link metadata.
