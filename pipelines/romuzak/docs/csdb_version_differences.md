---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg, https://csdb.dk/webservice/?type=release&id=17814&depth=2, https://csdb.dk/webservice/?type=release&id=17819&depth=2, https://www.vgmpf.com/ (multiple pages), pipelines/romuzak/docs/research.md (pre-existing project data)
fetched_via: direct
fetch_date: 2026-06-13
author: synthesis from multiple sources
content_date: 1989–2026
reliability: secondary (inferred from signatures + scene sources; no source code or manual)
---

# RoMuzak Version Differences: V6.x vs V7.x

## Known versions

| Version | CSDb ID | Release date | Load address | Signature file / distributor |
|---------|---------|--------------|--------------|------------------------------|
| V6.3 | #17814 | 1989 (exact month unknown) | $8000 | Cracked by Cosmos/Antitrack, imported by Apa-Soft |
| V7.96 | #17819 | 1990-03-15 | $7000 | Original release by ROM; found embedded in VacSID V0.88 |

**Also mentioned in in-binary documentation string:** versions V6.2, V7.94, and V7.96 are noted in
"German documentation included" referenced by CSDb V7.96 comments. This implies there are at least
three intermediate versions: V6.2 → V6.3 → (possibly V7.x iterations) → V7.94 → V7.96.

**Embedded signature string (V6.3):**
```
** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!!
```
and a compact machine-readable tag at +$0009:
```
ROMUZAK89
```
(The "89" suffix likely encodes the year 1989, common in demo-era software.)

---

## Machine-level differences: sidid.cfg byte signatures

Both versions share the same core note-dispatch loop but differ in the note byte handling:

### V6.x detection pattern
```
C9 ??        ; CMP #imm   — check for rest/tie sentinel in note byte (raw)
F0 ??        ; BEQ rel    — branch if rest/tie
0A           ; ASL A      — note_byte × 2
8D ?? ??     ; STA abs    — store intermediate result
0A           ; ASL A      — intermediate × 2 (now ×4)
6D ?? ??     ; ADC abs    — add stored value (→ ×3 total, or ×2 + ×1 depending on pattern)
AA           ; TAX        — result → X (freq table index)
A0 00        ; LDY #$00   — Y = 0 (voice 0 channel select or initial index)
```

### V7.x detection pattern
```
C9 ??        ; CMP #imm   — same sentinel check
F0 ??        ; BEQ rel    — branch if rest/tie
48           ; PHA        — push raw note byte  ← NEW IN V7
29 07        ; AND #$07   — mask to low 3 bits  ← NEW IN V7
0A           ; ASL A      — masked_value × 2
8D ?? ??     ; STA abs    — store
0A           ; ASL A      — × 2 more
6D ?? ??     ; ADC abs    — add stored → freq table index
AA           ; TAX
A0           ; LDY #imm   — (next byte not captured by sidid; probably #$00)
```

### Interpretation of the V7 change

The key new instructions in V7 are `PHA` (push A) + `AND #$07` (keep low 3 bits only) inserted
BEFORE the frequency-table multiply.

**V6 note encoding:** the raw note byte is used directly as the freq-table index multiplied. This
implies the note byte is essentially a 1-byte note index (0–N), with the sentinel value checked
first.

**V7 note encoding:** the low 3 bits are extracted from the note byte BEFORE the freq-table
multiply. The upper bits (bits 3–7) are saved on the stack (PHA) and presumably read back after
the freq lookup to extract additional information (effect type, instrument number, or octave).

This is the classic "packed note byte" pattern: V7 packs both the semitone (low 3 bits = 0–7,
one octave of semitones in some encoding) and metadata (upper 5 bits) into a single byte, whereas
V6 used the full byte as a raw note index.

**Consequences for USF format:**
- V6 notes: single-byte note index → maps directly to freq table entry (up to 96 entries per
  research.md). The sentinel value checked by CMP is the rest/tie marker.
- V7 notes: packed byte. Low 3 bits = semitone (0–7). Upper bits: likely octave field or
  combined octave+effect. The PHA/AND pattern means the original full byte is still available
  on the stack for a second decode pass.

**OPEN (RE needed):** Confirm the upper-bit layout in V7 packed notes. Standard C64 note packing
usually uses: bits[6:4] = octave (0–7), bits[2:0] = semitone (0–6 or 0–11). `AND #$07` would then
give semitone mod 8, with octave in bits[6:4] = the full byte >> 4 after PHA/PLA.

---

## Load address difference: $8000 (V6.3) vs $7000 (V7.96)

- V6.3 loads at $8000 (confirmed by research.md and sidid notes)
- V7.96 loads at $7000 (confirmed by CSDb V7.96 comment: "SYS 28672" = SYS $7000)

This is a significant change: $8000 is the BASIC ROM bank start, while $7000 is safely in RAM
below $8000. Moving to $7000 frees the player from BASIC ROM banking concerns and gives
approximately 4 KB more address space below the load point before colliding with I/O at $D000.

**OPEN (RE needed):** Whether the 1 KB gap between $7000 (V7 load) and $8000 (V6 load) is used
for additional data in V7 — i.e., whether V7's binary is larger than V6's.

---

## Feature differences implied by scene sources

### ROM's Fix bundled with V6.3 only
From VGMPF ROM's Fix page:
> "ROM's Fix is a sound effects editor that came with RoMuzak V6.3."

ROM's Fix is separately described as being released "between May and August 1989." This implies
it was a companion tool shipped alongside the V6.3 editor disk, not integrated into the editor itself.
No reference mentions ROM's Fix bundling with V7.96 — it may have been dropped, integrated, or
kept as a separate product.

### German documentation covering V6.2, V7.94, V7.96
The CSDb V7.96 page notes "German documentation included covering versions 6.2, V7.94, and V7.96."
This implies the V7.96 disk shipped with a text document describing all three version milestones —
a changelog/manual that covers:
- What changed from V6.2 to V7.94
- What changed from V7.94 to V7.96
This document is the highest-priority text to extract from the disk image. It would reveal the
exact feature additions in V7.

**OPEN (disk image needed):** Extract the documentation text file from the V7.96 D64/ZIP and read it.
The Archive.org D64 may be the cracked V6.3 disk; the VacSID ZIP (csdb.dk/getinternalfile.php/36832/vacsid.zip)
contains V7.96 and should be the target.

### Note encoding change (V7 packed bytes)
Described under machine-level differences above. The `AND #$07` + `PHA` pattern in V7 sidid
signature is the most concrete known difference between versions. Affects: note data layout,
orderlist byte width, possibly instrument numbering.

### Known bug: "first note sometimes muted"
From VGMPF Tube Madness (C64) page:
> "Tracks 2–4 suffer under RoMuzak's most common bug, namely the first note sometimes being muted."
And from VGMPF Clik Clak (C64) page:
> "The looping songs suffer under its most common bug, namely the first note sometimes being muted."

This bug is described as present in V6.3 songs. It is labelled "RoMuzak's most common bug" —
implying it is a well-known defect across multiple V6.x tunes, and that it affects looping songs
and multi-track songs especially. Whether it was fixed in V7.x is unknown.

**Likely cause (hypothesis, RE needed):** On loop-restart or song start, the per-voice pattern
pointer is not reset to the correct offset, causing the player to read the first note's data one
cycle early or with an off-by-one in the instrument/note byte interpretation. The result is a
silenced (muted) first note on affected voices.

---

## Summary table

| Feature | V6.3 | V7.96 |
|---------|------|-------|
| Load address | $8000 | $7000 |
| Note byte encoding | raw index (full byte) | packed (low 3 bits = semitone before freq multiply) |
| ROM's Fix bundled | Yes | Unknown |
| German documentation | Not confirmed | Yes (covers V6.2, V7.94, V7.96) |
| First-note mute bug | Confirmed present | Not documented |
| Known commercial users | Multiple (see csdb_forum_discussion.md) | Not documented |
| CSDb type | C64 Crack (circulated cracked) | C64 Tool (original release by author) |
| Release context | Cracked by Cosmos; commercial original | Uploaded 2021 from VacSID V0.88 |
| Embedded signature | `ROMUZAK89` + verbose banner | Unknown (may be `ROMUZAK90` or same) |

---

## Leads to follow

- **OPEN (RE needed):** Determine exact byte layout of V7 packed note: is it octave×8 + semitone,
  or semitone + (instrument | octave in upper bits)?
- **OPEN:** Extract and read the German documentation file from the V7.96 disk image (VacSID ZIP).
  This is the only known written changelog covering V6.2 → V7.94 → V7.96.
- **OPEN:** Whether ROM's Fix was updated or dropped in V7. The Archive.org "Analyser/Play
  Construction Kit" disk image may be a separate V6.x companion disk (different from the main
  editor disk).
- **OPEN:** Whether the "first note muted" bug was fixed in V7. Checking a V7.96 SID from HVSC
  (if any exist as HVSC entries rather than DEMOS/UNKNOWN) against a V6.3 SID of the same tune
  would reveal this.
- **OPEN:** Confirm whether V7.96 was the final version or if later versions exist (V7.x > 7.96
  not documented anywhere found).
- **OPEN:** The sidid pattern for V7 ends with `A0` (LDY #imm, partial — the immediate byte is
  not captured). This means the detection window closes before capturing the Y-register value.
  The actual Y value would tell us whether voice 0 is addressed as Y=0 (consistent with V6) or
  some other value. RE of V7.96 binary will confirm.
