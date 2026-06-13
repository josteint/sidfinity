---
source_url: local: pipelines/dmc/docs/research.md, dmc_sector_commands.md, fingerprint_census.md, dmc4_editor_2025.md, dmc4editor_embedded_player_notes.md, dmc_v5_format_notes.md; local: pipelines/gmc/docs/research.md, sidid_signature_analysis.md, spec_write_model.md; web: https://csdb.dk/release/?id=7268, https://csdb.dk/group/?id=193, https://hvmec.altervista.org/blog/?p=1256, https://hvmec.altervista.org/blog/?p=1265, https://hvmec.altervista.org/blog/?p=1272, https://csdb.dk/release/?id=44814, https://demozoo.org/sceners/1711/, https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: READ-ONLY on all local DMC/GMC files; web via WebFetch/WebSearch
fetch_date: 2026-06-13
author: SIDfinity research wave (Claude, 2026-06-13); underlying texts by Brian/Graffity, Richard Bayliss/TND, The Syndrom, Logan/Slackers, Fenek/Protovision, cadaver/sidid
content_date: 1990–2026
reliability: HIGH for DMC V4 data (annotated disassembly + TND tutorial + DMC 4 Editor 1.1 binary confirmed); MEDIUM for GMC specifics (editor keyboard maps from HVMEC confirmed; byte-level details INFERRED from sidid signatures + kinship; unmarked where INFERRED or OPEN)
---

# GMC → DMC Lineage: Shared Foundations and Divergences

This file documents what GMC (Game Music Creator, 1990) and DMC (Demo Music
Creator, 1991+) share versus where they differ, so the GMC migration can reuse
the DMC pipeline machinery wherever the formats align.

The source of truth for DMC V4 is `pipelines/dmc/v4/disassembly.s` (annotated)
and the confirmed corrections in `pipelines/dmc/docs/research.md` (marked
2026-06-12).  GMC facts derive from: (A) the HVMEC keyboard maps for V1.0 and
V2.0 (editor-side evidence); (B) the sidid.cfg opcode signatures (player-side
evidence, analysed in `sidid_signature_analysis.md`); (C) structural inference
from authorship identity (both by Brian/Graffity) and the "grandfather" framing
cited independently by Fenek (CSDb #44814) and the TND tutorial.

---

## 1. Author and Lineage Summary

Both tools were created by **Balázs Farkas ("Brian") of Graffity**, a Hungarian
C64 group founded October 1990.  The release sequence from the CSDb Graffity
group page (id=193):

| Tool | CSDb ID | Date | Notes |
|------|---------|------|-------|
| Digieditor V1.3 | 44465 | 1990 | sample editor (pre-GMC) |
| **GMC V1.0** | 7268 | Dec 8, 1990 | "Superiors Game Music Creator System V1" |
| **GMC V1.6** | 98639 | Dec 1990 | editor + beta music |
| **DMC V1.2** | 2598 | Feb 4, 1991 | first DMC; also credited to Brian/Graffity |
| DMC V2.0 | 10757 | 1991 | |
| DMC V3.0 | 98640 | 1991 | |
| **DMC V4.0** | 2596 | Sep 1991 | dominant player (5401 HVSC SIDs) |
| DMC V4.05 | 2597 | 1992 | |
| DMC V5.0 | 2594 | 1993 | 8-byte instruments; different branch |
| DMC V5.1 Package | 2599 | 1994 | |
| DMC V5.1+ Package | 2600 | 1994 | |
| DMC 4.0 Professional | 2603 | 1995 | |
| DMC Relocator | 10758 | 1991 | |

**Key timeline fact:** GMC V1.0 (Dec 8, 1990) and DMC V1.2 (Feb 4, 1991) are
only ~8 weeks apart.  DMC V1.2 is effectively GMC's immediate successor, with
the same author, same year, and a renamed "Demo" vs "Game" focus.

**Third-party characterisations (verbatim/paraphrase):**
- Fenek (CSDb #44814, 2006): "GMC is a music editor by Graffity, a grandfather
  to DMC."  He "disassembled the player and recreated the editor."
- HVMEC comment (from sidid.nfo context): "The predecessor of DMC is the GMC –
  Game Music Creator, written by Brian of Graffity too. You will find some
  similar elements in the GMC editor too, but the following DMC versions are
  more improved."
- CSDb GMC V1.0 comment (verbatim): "They should have called this tool DMC V1.0"
  — implying the tools were seen as near-equivalent by contemporaries.

**Brian's Demozoo credits (id=1711):** 103+ releases 1989–2025.  Tools:
DigiEditor V1.3 (1990), GMC V1.0 (1990), DMC V1.2 (1991), DMC V4.0 (1991),
Eqaleditor V1, Notemaker.  No confirmed GMC source-code release ever.

---

## 2. Shared Architecture: Two-Level Tracks → Sectors

Both GMC and DMC share the same two-level data hierarchy: a **Track** (orderlist
of sector references) drives three independent **Voices**; each voice steps
through **Sectors** (variable-length note sequences with per-step commands).

### Track level — command vocabulary
Confirmed for both (editor keyboard maps from HVMEC V1.0 and V2.0; DMC V4
confirmed from TND tutorial + binary):

| Command | GMC V1.0 key | GMC V2.0 key | DMC V4 |
|---------|--------------|--------------|--------|
| Insert sector ref | `S` | SHIFT+RETURN→Sector ed | byte $00–$3F |
| Transpose down | `–` | `–` | byte $80–$8F (AND $0F = semitones) |
| Transpose up | `+` | `+` | byte $A0–$AF |
| End marker | `SHIFT+E` | `SHIFT+E` | `$FE` (deactivate voice) |
| Stop | `C=+E` | `SHIFT+S` | `$FF` (loop to beginning) |
| Exchange tracks | `SHIFT+X` | `SHIFT+X` | N/A (editor only) |
| Set tune (0–7) | `SHIFT+T` | `SHIFT+T` | subtune select |

**Conclusion:** track-level structure is functionally identical.  GMC and DMC
both use 8 subtunes (0–7) per file, with per-voice track data addressed via a
tune pointer table.

### Sector level — command vocabulary
Both use per-step commands mixing note bytes with control commands:

| Command | GMC name | DMC V4 name | Correspondence |
|---------|----------|-------------|----------------|
| Duration | `DUR` (CTRL+D / C=+D) | `DUR.xx` ($80–$9F, AND $1F) | IDENTICAL concept; byte encoding OPEN for GMC |
| Sound/instrument | `SND` (CTRL+S / C=+S) | `SND.xx` ($60–$7B, AND $1F) | IDENTICAL concept |
| Glide | `GLD` (CTRL+G / C=+G) | `GLD.xy` ($A0–$BF, mode+speed nibbles) | IDENTICAL concept; encoding may differ |
| Volume/amplitude | `APM` (CTRL+A / C=+A) | `VOL.0x` ($C0–$DF inferred) | LIKELY SAME: sustain-nibble override |
| Hold | `HLD` (CTRL+H / C=+H) | no direct equivalent | GMC-SPECIFIC; maps to `holding` FX flag |
| Tie/legato | `CONT` (present in GMC research.md) | `SWITCH` ($7D, toggles gate mask) | SAME MECHANISM |
| End of sector | `\` key in V1/V2 | `END!` ($7F) | IDENTICAL concept |
| Gate off | not documented for GMC | `-GATE-` ($7E) | OPEN for GMC |

**Key GMC-specific field: APM.**  The HVMEC keyboard maps confirm GMC has `APM`
where DMC V4 has `VOL`.  The field name "APM" (amplitude/pitch modulation?) is
not decoded from any binary source, but the analogous position in the command
set (after DUR and SND, before GLD and HLD) and the sustain-override semantic
in DMC strongly suggests APM controls per-note amplitude — i.e. the sustain
nibble override (→ $D406).  Whether "pitch modulation" is ALSO encoded in the
same byte (high nibble?) is OPEN.

**Key GMC-specific field: HLD.**  Present in the keyboard map; absent from DMC
V4's sector command set.  DMC's "HOLDING FX" (instrument flag bit $10) controls
whether the gate stays until duration ctr == 1 before hard-restart.  GMC's HLD
may be a per-step override of this, or a separate hold-duration value.  OPEN.

**NOTE on V2.0 command keys:** GMC V2.0 changed from `CTRL+x` to `C=+x` for
sector commands (HVMEC V2.0 keyboard map shows `CTRL+D/S/A/G/H`); V1.0 used
`C=+D`, `C=+S`, etc.  The semantic meaning appears unchanged.

---

## 3. Entry Points: Identical

Both GMC and DMC share:
- **Init:** `$1000` (A = subtune number)
- **Play:** `$1003` (called each VBlank IRQ, ~50 Hz PAL)

These match the HVSC PSID header for both families and are confirmed in
`research.md` (GMC) and `dmc4editor_embedded_player_notes.md` (DMC V4).

The DMC V4 player binary at $1000 opens with:
```
+$00: JMP $101D   ; init
+$03: JMP $1085   ; play
```
GMC is expected to have the same jump-table layout at the canonical $1000 base
(the sidid.cfg signatures locate the GMC player at a fixed internal offset).

---

## 4. Sound / Instrument Format

### GMC V1: 16 bytes per instrument
Confirmed by the sidid.cfg signature analysis (`sidid_signature_analysis.md`):
the GMC V1 player computes the instrument base offset as `sound_number × 16`
via four consecutive `ASL A` instructions.  This gives 16 bytes per instrument
(not the 11 bytes of DMC V4).

The 16-byte record layout is OPEN — no first-party documentation found.
Inferred structure based on DMC V4's 11-byte record + available GMC field names:
- Bytes 0–1: AD/SR (ADSR envelope, same as DMC V4 bytes 0/1)
- Bytes 2–5: PW fields (GMC likely has PW speed/limit similar to DMC V4 bytes 2–5)
- Bytes 6+: vibrato, wave table pointer, effect flags, possibly arpeggio or GMC-specific
- 5 extra bytes vs DMC V4: may encode APM/HLD per-instrument defaults or extended fields

### GMC V2.0: packed nibble field (different from V1 and DMC)
The V2.0 sidid signature shows a fundamentally different instrument decode:
one data byte is split into high nibble and low nibble and stored separately
(as `$FC` and `$FD`), suggesting V2.0 uses a packed-byte scheme where a single
step byte encodes two 4-bit fields (e.g. instrument index + waveform, or
effect class + speed).  This is a divergence from both GMC V1 and DMC V4.

### DMC V4: 11 bytes per instrument
Confirmed fields (from annotated disassembly, corrected 2026-06-12):
| Byte | Field | Corrected content |
|------|-------|-------------------|
| 0 | AD | → $D405 |
| 1 | SR | → $D406 |
| 2 | PW | hi nib = PW bound A (EOR $0F = bound B); lo nib = PW hi initial |
| 3 | PW1 | Pulse speed nibbles, phase 0/1 |
| 4 | PW2 | Pulse speed nibbles, phase 2/3 |
| 5 | PW3 | Pulse speed nibbles, phase 4/5 |
| 6 | PW/Filt | hi nib = PW step base; lo nib = filter def index |
| 7 | Vib1 | vibrato delay frames (hi nib × 8) / width (lo nib) |
| 8 | Vib2 | vibrato ramp limit |
| 9 | Wave | wave table start index |
| 10 | FX | effect flags (drum/no-filt-reset/no-pulse-reset/no-gate/holding/filter-en/dual/cymbal) |

**Reuse assessment for GMC extractor:** bytes 0–1 (AD/SR) and bytes 9–10
(wave ptr / fx flags) are almost certainly present in the GMC 16-byte record
in the same role.  The 5 additional bytes in GMC's record may carry HLD
semantics or extended arpeggio data.  The DMC V4 extractor's instrument
parsing should be cloned as a starting point and extended for the 5 extra bytes
rather than rewritten.

### DMC V5: 8 bytes per instrument (separate branch — different extractor)
DMC V5 uses 8 bytes per instrument (AD, SR, WV, PU, FL, V1, V2, V3) with
programmable 2-byte tables.  This is a different branch and does NOT apply to
GMC or DMC V4.

---

## 5. Sector Byte Encoding: Differences

### DMC V4 (CONFIRMED from binary + editor + TND):
| Range | Command |
|-------|---------|
| $00–$5F | Note (96 notes, 8 octaves × 12) |
| $60–$7B | Instrument select (SND, AND $1F) |
| $7C | Soft-start toggle |
| $7D | SWITCH (gate-mask toggle for tie/legato) |
| $7E | -GATE- (gate off, full step) |
| $7F | END of sector |
| $80–$9F | DUR (AND $1F = ticks) |
| $A0–$BF | GLD.xy (glide: bit4=mode, lo-nibble=speed) |
| $C0–$DF | VOL.0x (sustain override, inferred by elimination) |
| $E0–$FF | Unknown/unused in V4 |

### GMC (OPEN — byte encoding not confirmed from any source)
The HVMEC command names (DUR, SND, APM, GLD, HLD, CONT, END) map to 7 distinct
command classes plus notes.  Whether GMC uses the same byte-range layout as DMC
or a different allocation is **OPEN** — the only current constraint is that note
values must cover 96 entries and that the GMC V1 player uses the sector bytes
directly as indices (inferred from the `B9` abs,Y loads in the sidid signature).

**Hypothesis (needs binary confirmation):** GMC may use an encoding similar to
DMC V4 but with APM replacing VOL and HLD occupying the "soft-start" slot or
the upper $E0–$FF range.  Alternatively, GMC may prefix commands differently
since it has one more command type than DMC V4.

---

## 6. Player Write Pattern (SID Registers)

### Shared: abs,X multi-voice dispatch

Both GMC V1 and DMC V4 use `BD ?? ?? 9D ?? ??` (LDA abs,X / STA abs,X) pairs
for multi-voice SID writes.  This confirms both use the same paradigm of
indexing SID register addresses by voice (X = voice offset 0/7/14).

### DMC V4 confirmed per-frame write order:
```
for voice in [V1, V2, V3]:
    $D400/07/0E  freq LO
    $D401/08/0F  freq HI
    $D402/09/10  PW LO
    $D403/0A/11  PW HI
    $D404/0B/12  ctrl
global:
    $D416  filter cutoff (written every frame)
    $D417  resonance + route (written every frame)
$D418  volume: written only at init + note-init of filter-using instruments
```

### GMC V4 expected write order (INFERRED, OPEN):
Based on shared authorship and two-level architecture, the GMC write order is
expected to match DMC V4.  The sidid signature confirms GMC writes freq (via
B9/9D abs,Y pairs) and ctrl bytes (via the flag/mask path).  Whether filter
($D416/$D417) and volume ($D418) are written every frame or conditionally is
OPEN until disassembly.

---

## 7. Hard Restart

DMC V4 uses the test-bit method:
1. Note-fetch frame: $08→ctrl, $0F→AD, $0F→SR.
2. Frame 2: real AD/SR, full freq/PW/ctrl.
3. Gate on ≥3 frames; then gate-mask $FE (non-holding) or gate until dur==1 (holding).

GMC is INFERRED to use the same method (shared era, shared author, contemporary
"modern testbit" practice).  The HLD command is the main GMC-specific feature
that would affect gate timing.

---

## 8. Wave Table

### DMC V4 (CONFIRMED):
- 1 byte per entry: ctrl value (bits 4–7 = waveform, bits 0–3 = gate+sync+ring+test).
- Special: any value ≥ $90 = jump back (value – $90) positions.
- Gate bit ANDed with global gate mask before writing to $D404.
- Parallel freq table: 1 byte per entry = semitone offset.

### GMC (INFERRED):
- Expected 1 byte per entry (same era; V5's 2-byte entry was an evolution).
- Jump-back mechanism likely present (standard in the era).
- Gate masking for tie/CONT: expected (sidid signature shows mask-AND in player).

---

## 9. Filter

### DMC V4 (CONFIRMED):
- 6-step envelope with R, T, cutoff, RT (loop), ST (stop), S1–S6 (direction),
  X1–X6 (duration/magnitude pairs).
- Filter definition table at fixed offset in the binary.
- Written to $D416 (cutoff, every frame) and $D417 (res+route).
- $D418 mode bits set at note-init of filter-using instruments.

### GMC (INFERRED):
- GMC V1.0 was noted in the CSDb comments as "really solid to work with and it
  is really good at producing some really twisted filtering."  This suggests
  filter support is present and effective.
- OPEN: whether GMC's filter envelope uses the same 6-step parametric format
  as DMC V4 or a simpler model.

---

## 10. Tune Pointer / Subtune Table

### DMC V4 (CONFIRMED, corrected 2026-06-12):
8 bytes per subtune (0–7): lo(V1), hi(V1), lo(V2), hi(V2), lo(V3), hi(V3),
speed, master_vol.

All 8 bytes active (the "6 + 2 padding" claim was wrong).

### GMC (INFERRED):
The HVMEC keyboard map shows "SHIFT+T = Set tune (0–7)", confirming 8 subtunes.
The same 8-byte layout (3 voice pointers + speed + vol) is expected; the GMC
research.md entry says "Up to 8 tunes per file."  OPEN: whether speed/vol are
combined differently.

---

## 11. SIDid Signatures: Structural Divergence Point

The sidid.cfg signatures (full analysis in `sidid_signature_analysis.md`) confirm:

**Shared 30-byte prefix** (GMC V1 and V2.0 both open with this):
```
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ??
BD ?? ?? 9D ?? ??
```
This is a SID-write inner loop (LDA/STA pairs, abs,X and abs,Y indexed).

**After the shared prefix:**
- GMC V1: `BC ?? ?? 18 0A 0A 0A 0A 85 ?? ...` — load voice index (LDY abs,X),
  then 4× ASL to compute instrument base (sound × 16).
- GMC V2.0: `A8 29 F0 85 FC 98 29 0F 18 6D ?? ??` — TAY, split byte into
  hi/lo nibbles, add base address.  Packed-field decode.

**DMC V4 opening:** `18 7D ?? ?? 99 ?? ??` — completely different (uses ADC
abs,X + STA abs,Y).  NOT a fork from GMC's inner loop; these are independent
reimplementations of the same musical concept by the same author.

**Implication for migration:** the GMC extractor is NOT a simple fork of the
DMC V4 extractor; the binary layout and player code are structurally distinct.
The USF schema (data model) can be shared/reused; the extraction and composition
code needs its own routines for the GMC-specific instrument record (16 bytes)
and the different sector command encoding.

---

## 12. HVSC Population

From the HVSC census (hvsc84.db, `engine LIKE 'GMC%'`):
- **~446 GMC SIDs** (sidid classification; see `pipelines/gmc/docs/research.md`).
- GMC V1.0 canonical (majority).
- GMC V2.0/Superiors: 9 SIDs (modern revival 2010–2023, all by NecroPolo).

From `fingerprint_census.md` for DMC:
- 10,676 DMC SIDs total; GMC is ~4% of that count.

---

## 13. What the GMC Migration CAN Reuse from the DMC Pipeline

| Component | Reuse potential | Notes |
|-----------|----------------|-------|
| `verify.py` / `verify_cycle.py` | **Full reuse** — the write-log verification machinery is engine-agnostic | Just supply the GMC SID pair |
| USF schema types (notes, envelopes, sectors, tracks, subtunes) | **Full reuse** — same musical model | |
| Tune pointer table extractor | **High** — 8-byte layout expected identical | Confirm speed/vol byte positions |
| Freq table extractor | **High** — 96-entry PAL 16-bit split table expected | Confirm from binary |
| Wave table extractor | **High** — 1-byte per entry, jump-back ≥$90, same era | Confirm jump-back encoding |
| Vibrato extractor | **Medium** — delay+width model expected | confirm byte packing vs DMC V4's 2-byte scheme |
| Glide extractor | **Medium** — mode+speed scheme confirmed in DMC V4; GMC likely same | |
| Filter extractor | **Medium** — step-envelope concept shared; exact byte layout OPEN | |
| Instrument extractor | **Low** — 16 bytes vs 11; must handle 5 extra bytes | Clone DMC's bytes 0–8, extend for 5 unknowns |
| Sector command decoder | **Low** — different byte ranges; APM/HLD not in DMC V4 | Write from scratch; reuse classification logic |
| PW extractor | **Medium** — 6-phase nibble model may match (DMC V4 has PW1–PW3) | |
| `composer.py` routines | **High for existing effects** — all shared effects (freq/PW/vibrato/glide/filter/wave) use same composer emitters | APM/HLD may need new or adapted emitters |
| Hard-restart test-bit logic | **Full reuse** — same method expected | |

---

## 14. What Must Be Built Fresh for GMC

1. **Instrument record parser** (16 bytes vs 11 — extend the DMC extractor).
2. **Sector command byte decoder** (APM, HLD, CONT byte ranges OPEN; must be
   determined from the GMC player binary disassembly).
3. **APM effect composer emitter** (if APM encodes pitch modulation beyond
   sustain override, a new USF field may be needed — apply
   `feedback_schema_addition_discipline.md` discipline before adding).
4. **HLD effect handler** (per-step hold gate extension; likely maps to the
   existing `holding` FX flag but may need a duration override).
5. **GMC-specific canary selection and annotation** (run `seed_disassembly.py`
   on a canonical V1.0 SID to get the skeleton; annotate the header before
   coding the extractor).

---

## Leads to Follow

1. **Confirm the sector command byte ranges** — the single highest-value next
   step.  Download any GMC V1.0 SID from HVSC and run `seed_disassembly.py`
   with `--range` covering the init+play routine.  The sector dispatcher will
   show the branch table for DUR/SND/APM/GLD/HLD/CONT/END.

2. **Confirm 16-byte instrument layout** — a `siddump --memwatch` probe at
   the instrument base address during a note-init frame will show which bytes
   the player reads and what SID registers they go to.  This pins bytes 2–15
   of the GMC instrument record.

3. **APM semantics** — does it write to $D406 (sustain), $D418 (volume), or
   both?  Run `tools/effect_chain_profiler.py` on a GMC SID with APM steps.

4. **HLD semantics** — does it extend gate duration (a count) or set a flag?
   Compare a sector with HLD vs without, using `siddump --writelog`.

5. **V2.0 nibble decode** — what are the two packed fields?  NecroPolo's
   V2.0 tunes in HVSC are the only corpus.  Compare byte values in V2.0 sector
   data against note/instrument/effect patterns.

6. **HVMEC binary download** — `hvmec.altervista.org/blog/?p=1256` (GMC V1.0)
   and `?p=1272` (GMC V2.0) carry the editor binaries as zip downloads.  The
   player can be carved from the editor (same technique as
   `dmc4editor_embedded_player_notes.md`).
