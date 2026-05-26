# Rob Hubbard Research — Index and Summary

Research date: 2026-04-21

---

## Files in This Directory

| File | Source | Quality | What It Contains |
|------|--------|---------|-----------------|
| `chacking5_player_source.md` | C=Hacking #5 (McSweeney, 1993) | PRIMARY | Full annotated disassembly of Monty on the Run player. Speed counter, note format, instrument format, all effects. The definitive reference. |
| `siddecompiler_parser_notes.md` | Galfodo/SIDdecompiler on GitHub | PRIMARY | C++ Rob Hubbard ripper — binary patterns used for data structure detection, note duration formula, instrument parsing code |
| `sidid_signatures_format_spec.md` | cadaver/sidid sidid.cfg | PRIMARY | Byte signatures for all driver variants: Rob_Hubbard, Rob_Hubbard_Digi, Paradroid/HubbardEd, Giulio_Zicchi, Bjerregaard |
| `forum_discussions.md` | chipmusic.org, lemon64.com, VGMPF | SECONDARY | Fourth channel for tempo control, Wizball 200Hz multispeed, IK double-tempo section, composer histories |
| `version_differences.md` | Multiple sources synthesized | SECONDARY | Feature timeline, per-song speed tables, nested counters, CIA multispeed, variant differences |
| `provenance_log.md` | This research session | META | All URLs attempted with status, leads not yet followed |

---

## Key Findings

### 1. Speed Counter — THE FORMULA

**Frames per note = (note_length_bits + 1) × (resetspd + 1)**

Where:
- `note_length_bits` = first note byte AND $1F (bits 0-4, values 0-31)
- `resetspd` = speed counter reset value (stored in player binary, typically 0-7)

At `resetspd=1` (Monty on the Run): a max-length note ($1F) = 32 ticks × 2 frames = 64 frames ≈ 1.28 sec at 50Hz.

**Source:** C=Hacking #5, confirmed by be6502 assembly, confirmed by SIDdecompiler formula.

### 2. Speed Counter Mechanism

```assembly
dec speed        ; counts down
bpl mainloop     ; skip note work if still positive
lda resetspd     ; reload default
sta speed
; ... note work for all 3 channels
```

The `dec speed` fires every frame. Note work fires every `resetspd+1` frames.

### 3. Three Tiers of Speed Control

| Tier | Mechanism | Detectability | Affects |
|------|-----------|--------------|---------|
| Single global `resetspd` | Static value in binary | Easy — our find_speed() | All songs, constant |
| Per-song speed table | LDA table,X / STA resetspd in init | Easy — our find_speed() detects it | Per-subtune |
| Nested outer/inner counter | Two DEC/BPL stacked | Medium — our Pass 3 | Effective speed modified |
| Fourth channel tempo | In-song data track modifies resetspd | Hard — requires runtime analysis | Mid-song tempo change |
| CIA multispeed | Interrupt timer 2x/4x/8x | SID header speed bits | Entire song plays faster |

### 4. No "Phase 2/3/4" Nomenclature

The "Phase 2/3/4" terminology does NOT apply to Rob Hubbard's driver. It was found to
describe a different composer's drivers (likely Laxity). Rob Hubbard's driver evolved
incrementally with no formal version numbering. Use "early/advanced/digi" instead.

### 5. What Existing Tools DON'T Handle

- **SIDdecompiler**: Detects data structures correctly but `m_SpeedDivider` initialization
  is not visible in the code — likely hardcoded or from a separate pass.
- **No existing tool** handles the fourth channel tempo control or CIA multispeed in
  a static parser. These require runtime emulation.

### 6. Fourth Channel — CRITICAL GAP

Multiple sources confirm a "fourth channel for filter/tempo/speed table control."
This is NOT the same as CIA multispeed. It's likely:
- A 4th data track in the song structure (next to the 3 voice tracks)
- Parsed similarly to a note pattern, but containing control commands
- Commands would include: set resetspd, set filter cutoff, set filter resonance/enable

**This explains IK's "double tempo" section** — a fourth-channel command fires mid-song
to change `resetspd` from e.g. 1 to 0, halving the frame count per tick.

**We need to investigate:** which SIDs have a 4th track pointer and what format it uses.

### 7. CIA Multispeed

From the Lemon64 WAR forum: Wizball runs at 200Hz (4x speed).
From the SID header: `speed` field bit N = 1 means CIA timer drives subtune N (not VBI).
Our pipeline currently does not detect or compensate for CIA multispeed in Hubbard songs.
This is a SEPARATE issue from the `resetspd` speed counter.

---

## Gaps Remaining

### High Priority
1. **Fourth channel format** — need to inspect actual Hubbard SIDs with multiple subtunes
   that have mid-song tempo changes (IK, Delta, Last V8) to find the 4th track pointer
   and decode its format.

2. **CIA multispeed song list** — which Hubbard SIDs in HVSC have CIA timer flag set?
   Run: `for f in data/C64Music/MUSICIANS/H/Hubbard_Rob/*.sid: check speed header bits`

3. **Nested counter correction** — our current formula `(inner + outer) // 2` is a guess.
   Need to verify against a known-correct song. The correct formula may be `inner + outer`
   (outer fires every `outer_imm+1` frames and skips the inner, so effective rate is
   reduced by a factor related to both).

### Medium Priority
4. **Paradroid/HubbardEd format** — ZP $FC pointer, different flag bits. Need to find
   which HVSC songs match this signature and test our decompiler against them.

5. **ACE 2 player format** — late 1987 driver with arpeggio tables and table-driven PWM.
   Our decompiler doesn't handle these yet.

6. **Bjerregaard stack-based write** — may affect our instrument address detection patterns.

### Low Priority
7. **Giulio Zicchi** — structurally very similar to main driver, likely works already.

8. **Rob_Hubbard_Digi** — PCM playback via volume register; out of scope for USF conversion.

---

## Recommended Next Steps for rh_decompile.py

1. Read SID header `speed` field to detect CIA multispeed, skip those songs or flag them
2. Search for 4th track pointer in multi-song init code (BD lo hi patterns near the 3-track loader)
3. If 4th track found, scan it for speed-change commands and apply them to build a speed map
4. Test nested counter formula against IK (known double-tempo section)
