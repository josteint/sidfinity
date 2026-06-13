---
source_url: local: pipelines/gmc/docs/research.md + local: pipelines/dmc/docs/ (research.md, tnd_dmc_tutorial.txt, dmc_sector_commands.md, dmc_v5_format_notes.md, README.md) + local: pipelines/dmc/v4/disassembly.s + local: .claude/memory/project_dmc.md
fetched_via: in-repo synthesis (no external fetch required for this document)
fetch_date: 2026-06-13
author: sidfinity research wave (Claude, 2026-06-13)
content_date: 2026-06-13
reliability: DOCUMENTED where sourced from DMC research + TND tutorial; INFERRED where extrapolated from the GMC→DMC kinship; OPEN where no confirmed byte-level fact exists
---

# GMC Extraction Plan

GMC (Game Music Creator) by Balazs Farkas (Brian) / Graffity, Hungary, ~1990.
Direct predecessor to DMC V4 (Demo Music Creator, 1991).  ~446 HVSC SIDs.
No public source.  CSDb release #7268.  SIDId tags: GMC/Superiors (V1.0),
GMC_V2.0/Superiors.

---

## 1. Fixed anchors (DOCUMENTED or high-confidence)

These facts appear in the HVSC research note (pipelines/gmc/docs/research.md)
and/or are cross-confirmed by the DMC/TND/sidid literature:

| Anchor | Fact | Confidence |
|--------|------|------------|
| Entry init | $1000 | DOCUMENTED (research.md, same as DMC V4) |
| Entry play | $1003 | DOCUMENTED (research.md, same as DMC V4) |
| Hierarchy | Two-level: Tracks → Sectors (≤8 tunes/file) | DOCUMENTED (research.md) |
| Sound (instrument) size | 16 bytes each | DOCUMENTED (research.md: "indexed via 4× ASL A = ×16") |
| Sound indexing | 4× ASL A shifts instrument# → byte offset into instrument block | DOCUMENTED (research.md) |
| Sector step fields | DUR, SND, APM, GLD, HLD, CONT, END | DOCUMENTED (research.md field names) |
| Track transpose | tracks reference sectors with transpose controls | DOCUMENTED (research.md) |
| Predecessor relationship | GMC is the direct predecessor of DMC V4 | DOCUMENTED (TND tutorial, DMC research.md line 23) |
| Max subtunes | ≤8 | DOCUMENTED ("≤8 tunes/file", research.md) |

The 4× ASL is the only multiply-by-N instruction visible in the HVSC research
note and is unusual: DMC V4 uses 11-byte instruments (×11 is done with a
sequence of ADC/clc; the stride encoded in the player changes between versions).
GMC's 16-byte stride is cleaner (power-of-2 shift).

---

## 2. GMC↔DMC structural correspondence (DOCUMENTED + INFERRED)

Both engines are by the same author; GMC predates DMC V4 by ~1 year.  The TND
tutorial explicitly confirms kinship: "The predecessor of DMC is the GMC –
Game Music Creator, written by Brian of Graffity too.  You will find some
similar elements in that editor too."

### 2a. Structural elements that CARRY OVER with high confidence (INFERRED)

The DMC V4 pipeline machinery — established in SIDfinity via the Zaks canary
— provides a rich set of likely-to-transfer concepts.  Each is labelled with
the canonical DMC source:

| GMC concept (research.md) | DMC V4 equivalent | Transfer confidence |
|---------------------------|-------------------|---------------------|
| Sectors (pattern sequences) | Sectors ($7F = end) | High — same author, same term |
| Tracks (orderlists per voice) | Track orderlists ($FF=loop, $FE=end) | High |
| DUR field | $80-$BF duration prefix (AND $3F = ticks) | High |
| SND field | $60-$7B instrument-select prefix (AND $1F) | High |
| GLD field | $C0-$DF glide/slide (mode+speed nibbles) | High |
| CONT / tie | $7D SWITCH (gate-mask toggle) | High |
| END | $7F sector terminator | High |
| Transpose in track | $80-$9F / $A0-$BF per DMC; GMC likely similar | Medium |
| Speed + master-vol in tune table | Tune-table bytes 6 + 7 (DMC V4) | High |
| Freq table (96 notes, LO/HI split) | $1647/$16A7 in DMC V4 | High — same tuning range expected |
| Wave table (ctrl + freq parallel arrays) | $19D7/$1A27 in DMC V4 | High |
| Filter definitions | 16-byte filter def block (DMC V4) | High — same filtering model |
| Hard-restart (test-bit method) | Frame-1 $08→ctrl then real AD/SR | Medium — may be present or simplified |
| Sector pointer table at file end | lo[] then hi[] parallel arrays | High |

### 2b. Known GMC DIFFERENCES from DMC V4 (DOCUMENTED)

| Feature | GMC | DMC V4 |
|---------|-----|--------|
| Sound record size | **16 bytes** (power-of-2, shifted by 4× ASL) | 11 bytes (irregular stride) |
| APM field | Present in sector steps (amplitude/modulation) | No APM-named field; VOL is $F0-$FF |
| HLD field | Present in sector steps (hold duration) | Folded into FX flag $10 "holding" |
| Entry points | $1000 init / $1003 play | Same (may be true for both) |
| Version split | V1.0, V2.0 | V4.0, V4.3, V5, V7 |

The APM and HLD fields are GMC-specific names that have no direct DMC V4
equivalent, though their EFFECTS likely map onto DMC mechanisms.  Their exact
byte encoding is OPEN.

### 2c. Features OPEN (not in research.md; need disasm)

- Whether the per-note vibrato depth table (a FIXED-address code+data
  overlap region in DMC V4 at $1888-$18E7) is present and at what address.
- Whether the dual-effect ($40 half-rate slide) exists.
- Whether the cymbal ($80 FX flag) and drum-abs-freq ($01 FX flag) are present.
- Whether the global frame parity byte ($1019 in DMC V4) exists.
- Whether the "filter claim" single-owner model is present.
- Whether VOL override ($F0-$FF in DMC V4) exists, or is replaced by APM.

---

## 3. Open list — byte-level facts needing a disassembly

Every item below requires `seed_disassembly.py` on a canary SID + annotation
before the extraction can be coded.  Each is annotated with the migration-phase
trace (where to look in the DMC pipeline for guidance).

### OPEN-1: Exact sector byte packing for all 7 field types

**What we know:** the sector step stores DUR, SND, APM, GLD, HLD, CONT, END
(research.md).  These cover notes, instrument-select, duration, amplitude,
glide, hold, tie, and terminator.

**What we need:** the byte ranges for each field — equivalent to the DMC V4
dispatch table in `disassembly.s` header ("SECTOR BYTE DISPATCH").

**V1.0 vs V2.0 nibble-split difference:** the sidid signature distinguishes
V1.0 from V2.0; this may reflect a re-encoding of some field (analogous to
the way DMC family-2 shifted the sector terminator from $7F to $FF — see
`project_dmc.md` family-2 note).

**Migration trace:** disassemble from sector-dispatch code; look for the CMP
opcode chain that dispatches each byte range (in DMC V4 this was `sub_11E6`
checking $7F, with the main voice loop testing ranges via BCS/BCC chains).
Then cross-reference with `pipelines/dmc/v4/disassembly.s` sector-dispatch
section as a template for annotation.

### OPEN-2: Sound definition 16-byte layout

**What we know:** 16 bytes each, indexed by 4× ASL.

**DMC V4 parallel:** 11 bytes — AD($D405), SR($D406), PW-init, PW-speed×3,
PW-base/filter-index, vibrato, wave-ptr, FX-flags.  The extra 5 bytes in GMC
are UNKNOWN.  Candidates: (a) more PW speed phases; (b) APM and HLD are stored
IN the instrument record (not as sector-step prefixes); (c) additional FX bits.

**Migration trace:** in the player, find the note-init path (the code that
loads the instrument record into per-voice RAM) via `STA` to voice-state vars.
Map each byte to its function by following its value to the SID write.

### OPEN-3: Track/transpose encoding

**What we know:** tracks reference sectors with transpose.

**DMC V4 parallel:** track bytes $00-$7F = sector number, $80-$9F = down-
transpose 0-31 (then next byte is sector), $A0-$BF = up-transpose 0-31,
$FE = voice end (freewheels), $FF = loop.

**OPEN:** whether GMC uses the same 5-bit $8x/$Ax split, or a different
encoding (e.g. sign+magnitude byte, 4-bit split, or a separate transpose byte
BEFORE the sector byte as in some early editors).

**Migration trace:** find the track dispatcher (`JMP/JSR` on track-byte branch
chains); check if the same $80/$A0 discriminator bits appear.

### OPEN-4: V1.0 vs V2.0 differences

**What we know:** two sidid signatures exist.  HVMEC lists GMC V1.0, V1.6,
V2.0.  The signatures differ.

**OPEN:** which byte-level encodings changed between versions.  Candidates
from the DMC precedent: sector terminator value, instrument record layout,
track-transpose encoding, or tune-table stride.

**Migration trace:** sidid `.cfg` byte patterns for the two GMC signatures
are the starting point — they reveal which opcode sequence differs.  With
`seed_disassembly.py` on one V1.0 and one V2.0 canary, diffing the two
dispatch regions will isolate the change.

### OPEN-5: Tune/song table format

**What we know:** ≤8 tunes/file; speed is present (inferred from DUR timing
model); similar to DMC V4's 8-byte tune records.

**OPEN:** byte count per tune record, field order (especially whether
master-vol is byte 6 or 7, and whether speed is here or in the player).

**Migration trace:** find the tune-select entry point (the code reached via
`+$1D` in DMC V4); follow the LDA/STA pairs that load per-voice track
pointers and the speed/volume globals.

### OPEN-6: APM (amplitude/modulation) field exact semantics

**What we know:** field is named in research.md.  In DMC V4 the analogous
mechanism is VOL override ($F0-$FF in sector = sustain-nibble override) and
master-vol in the tune record.

**OPEN:** whether APM sets the SID master volume, the voice sustain, or a
per-step modulation depth.  Whether it is a sector-step prefix (like DUR/SND)
or inline.

**Migration trace:** find the SID $D418 write path in the player; identify
which player variable drives the volume bits.

### OPEN-7: HLD (hold) field exact semantics

**What we know:** field is named in research.md.  In DMC V4 "holding" is an
FX flag (bit $10) in the instrument record, not a sector-step field.

**OPEN:** whether HLD is a standalone sector-step command (like DMC V4's
SWITCH/$7D), or whether it is a duration modifier that extends a note beyond
its DUR count.

**Migration trace:** find the sector-step branch that loads/uses HLD; trace
the value into the duration counter or gate-mask logic.

### OPEN-8: Sector pointer table location and format

**What we know:** by analogy with DMC V4, expect lo[] then hi[] parallel
byte arrays at the end of the binary.

**OPEN:** whether the sector pointer table is at the very end (as in DMC V4),
or at a fixed offset, or at a packer-patched operand location.

**Migration trace:** dataflow from the sector-dispatch code — find the LDA
abs,Y that loads the sector data pointer; the operand is the sector-ptr-lo
table address (same as DMC V4 operand sites $1103/$1108).

### OPEN-9: Whether packer-patches table operands (same as DMC V4)

**What we know:** DMC V4 uses packer-patched absolute operands for all table
addresses except the two fixed freq tables.  This is the KEY EXTRACTION
FINDING for DMC.

**OPEN for GMC:** if GMC's packer follows the same convention, extraction
must use dataflow over the operand sites, not fixed offsets.

**Migration trace:** probe 10+ HVSC GMC SIDs: check whether the instrument
table, wave table, and sector-ptr addresses are constant or vary across
members.  If they vary → packer-patches; same dataflow approach as DMC.

### OPEN-10: SID filter presence and model

**OPEN:** whether GMC has the same "first voice that claims the filter wins"
model as DMC V4 (filter $1720 claim flag), or a simpler fixed-voice routing.

---

## 4. Where the DMC pipeline machinery transfers

The SIDfinity DMC V4 pipeline lives in `pipelines/dmc/v4/` (extract) +
`pipelines/dmc/composer_asm.py` (our composer engine).  The following
components transfer directly to GMC migration:

| DMC component | Transfer to GMC |
|---------------|-----------------|
| `pipelines/dmc/v4/factory.py` | Factory pattern: masked-identity compare + operand-consistency probe. Clone and adapt for GMC sidid sig. |
| Dataflow operand extraction | Apply the same "find STA $D4xx, walk A's predecessors" recipe (per `feedback_dataflow_over_heuristics.md`) to the GMC player. |
| Sector decoder loop (path-resolved with loop-unroll cycle detection) | Port to GMC once sector byte ranges are known (OPEN-1). The loop architecture is the same. |
| USF schema blocks (wave_freq, gate_mode, pwm, vibrato, slide, filter) | Most are reusable; APM/HLD will add at most 1-2 new USF fields (subject to schema-addition discipline). |
| `pipelines/dmc/composer_asm.py` | Our OWN composer; the write-model (see spec_write_model.md) determines how much to reuse vs clone. |
| `tools/dmc_family_batch.py` | Generalise (or clone) for GMC-family wide-batch rollout. |
| `tools/regression.py` DMC section | Add a GMC section when the first canary verifies. |
| `verify_all` / `compare_instruction_stream` | No change needed; verification tooling is format-agnostic. |
| Trichotomy init path | GMC's init will differ from our universal-reset init → apply `init_style='universal_reset'` + `mode='trichotomy'` comparison as for FC/Adrenalin. |

---

## 5. Canary SID selection

Recommended approach (following the FC + DMC V4 playbook):

1. Query `hvsc84.db` for GMC SIDs:
   ```python
   import sqlite3
   db = sqlite3.connect('hvsc84.db')
   rows = db.execute(
       "SELECT path, title, songlength_s FROM sids "
       "WHERE engine LIKE 'GMC%' "
       "ORDER BY songlength_s DESC LIMIT 20"
   ).fetchall()
   ```
2. Choose a single-subtune, medium-length (30-120 s) tune with no CI/speed
   complications as the first canary.
3. `seed_disassembly.py` on that canary → annotate `pipelines/gmc/v1/disassembly.s`
   (or `pipelines/gmc/v2/` if it is a V2.0 member).
4. Answer OPENs 1-10 above before any extraction code.

---

## 6. Pipeline structure (proposed)

Following the DMC V4 precedent:

```
pipelines/gmc/
├── docs/                  ← this doc + spec_write_model.md + future RE_NOTES.md
├── v1/                    ← V1.0 engine (sidid "GMC/Superiors")
│   ├── disassembly.s      (seed via tools/seed_disassembly.py; hand-annotate)
│   ├── config.py
│   ├── factory.py
│   └── extract/
│       ├── engine_model.py
│       └── to_usf.py
└── v2/                    ← V2.0 engine (sidid "GMC_V2.0/Superiors"), if format differs
    └── ...
```

Whether V1.0 and V2.0 need separate extract dirs depends on the answer to
OPEN-4.  If the only difference is a single opcode (like DMC's family-2
sector terminator $FF vs $7F), a single extract path with a `version` flag
suffices.

The composer (`pipelines/gmc/composer_asm.py` or integration into
`pipelines/composer.py`) can be deferred until the first canary verifies — the
DMC composer at `pipelines/dmc/composer_asm.py` is the direct model.

---

## 7. Verification approach

- **Primary:** `verify_all` (write-log frame-by-frame, Mode 1).
- **Comparator:** `compare_instruction_stream` flat-prefix (drop init,
  compare play stream).
- **Init style:** `init_style='universal_reset'` with
  `compare_instruction_stream(mode='trichotomy')` — same as FC standard and
  Adrenalin (see `feedback_init_trichotomy.md`).
- **PSID speed bit:** query each SID's PSID header `speed` field.  Most GMC
  tunes are expected to be VBlank (speed=0); if any are CIA-timed use
  `siddump --writelog-per-irq` path.
  OPEN: whether any GMC SIDs use multispeed (DMC V4 has a CIA-multispeed
  bucket; GMC may have single-speed variants only).

---

## Leads to follow

See `spec_write_model.md` § "Leads to follow" for additional leads.
