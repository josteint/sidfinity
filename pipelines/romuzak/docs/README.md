# RoMuzak — research docs index

Player family: **RoMuzak**, by **Oliver Blasnik** ("ROM" / DOS-era "R0M"),
Germany, published by **Digital Marketing**. Versions **V6.2 → V6.3 (1989)** and
**V7.94 → V7.96 (March 1990)**. Embedded signature string `ROMUZAK89` /
`** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!!`.

HVSC #84 footprint (our DB): **569 `RoMuzak_V6.x` + 22 `RoMuzak_V7.x` = 591 SIDs**.
Predominantly German scene. Heaviest users: Kai Lehmann (Ass It, 55), Markus Raab
(Sony, 26), Stefan Hartwig (23), Thomas Detert (21).

Research sweep date: **2026-06-13/14**. Two waves of parallel sonnet agents
(CSDb · archive.org/author · GitHub/sidid · forums · wave-2 leads). GATHER-only —
no RE, no siddump/py65. The 6502-level RE is the migration phase.

## TL;DR — the big win

The **complete author's editor manual `ROMUZAK.DOC`** (29.9 KB, German, covers
V6.2 + V7.9x) was recovered from the VacSID zip → `src/romuzak_doc_vacsid_bundle.txt`.
This is a **primary format spec** and changes RoMuzak from "no docs" to "well
specified at the field/command level." The only material gap is the **binary byte
VALUES** for the sector-command dispatch thresholds (mnemonics are in the manual;
numeric opcodes live in the player code → RE phase).

There is **no public source and no open-source parser** for RoMuzak — the manual +
the sidid signatures are the whole external knowledge base.

## Format facts we are confident about (from ROMUZAK.DOC + sidid)

### Memory map / entry points (V6.x, default load $8000; V7.96 at $7000)
- `+$0000` JMP init · `+$0003` JMP play · `+$0006`/+$FF stop · `+$0009` `ROMUZAK89` string
- `+$0012` three 2-byte per-voice pattern pointers
- `+$0018` instrument parameter block (~136 bytes): per-instrument ADSR, waveform,
  pulse width, filter, vibrato/portamento
- `+$00A2` standard frequency table (96 entries, identical across all V6.x tunes)
- `+$0202` player code (~2636 bytes)
- Zero page used: **$F8–$FB only** (per the manual). Voice writes via `STA $D4xx,Y`,
  Y ∈ {0,7,14}. VBlank / 50 Hz.

### Track (sequence) byte semantics — FC-compatible ranges
RoMuzak's track bytes deliberately mirror **C64 Future Composer V1.0** ("Future
Composer 0.18") so it can convert FC songs:
- `$00–$3F` / `$40–$7F` / `$80–$BF` — same partitioning as FC V4.1 track bytes
- `$C0–$FB` — **sound-transpose** range (RoMuzak addition over FC V1.0)
- `$FC` — goto (RoMuzak addition)
See `wave2_fc_inheritance.md` for the field-by-field FC↔RoMuzak comparison.

### Sector / pattern commands (V7.9x — 21 commands, from the manual)
`VDL ARP REL PNT ECH ASS HGD PSW FDR VOL FST FAD FSW LCY SPD RES :xx . GOTOxx ->`
(volume, ADSR/release, pulse, echo, vibrato/portamento, filter sweep, fade, loop,
speed, etc.) — `wave2_vacsid_manual.md` lists each with its documented meaning.
**OPEN:** the numeric byte that selects each command (dispatch thresholds) — RE.

### Instrument bytes B0–B7
B0–B3 byte-compatible with FC; **B6** = PW-vibrato (FC used it for arpeggio);
**B7** = bit flags, remapped vs FC (FC's filter-enable bit0 → RoMuzak drum-enable
bit0 — the source of the documented "~90% sound conversion" mismatch). Drum table:
2×16 bytes, `$FF` end.

### Version differences
- **V6→V7 note encoding** (from sidid): V7 inserts `PHA` + `AND #$07` before the
  note→freq multiply — V7 packs octave/flags into the upper bits and masks low 3
  bits before the freq-table lookup; V6 used the raw note byte. (`github_sidid_signature.md`)
- **V7.96 dual-player layout** (observational): V7.96 SIDs appear to embed BOTH a
  V6.3 sub-player and a V7.96 sub-player with a top init dispatcher — confirm in RE.
- Known V6.3 bug: "first note sometimes muted" on looping/multi-voice songs.

## File index

### Format / spec (read first for migration)
- `src/romuzak_doc_vacsid_bundle.txt` — **PRIMARY**: the full author manual (German).
- `wave2_vacsid_manual.md` — structured English synthesis of the manual: all 21
  sector commands, B7 flag semantics, drum table, entry points, zero-page map.
- `wave2_fc_inheritance.md` — **FC V1.0 ↔ RoMuzak field mapping** (track bytes,
  instrument bytes, the lossy FC-arp→Echo conversion), bounding RoMuzak's data
  model from the FC side. Cross-referenced against our local `future_composer/docs/`.
- `github_sidid_signature.md` + `src/sidid_romuzak_blocks.txt` — decoded V6.x/V7.x
  signatures (the note-dispatch routine) + version discriminator.

### Versions / detection / structure
- `csdb_version_differences.md` — V6.3 vs V7.96 (load addr, note encoding, bug).
- `github_parser_notes.md` — confirms NO public parser; player characteristics.
- `github_fc_relationship.md` — FC-conversion details + C64-vs-Amiga FC caveat.
- `wave2_skull_disasm_thread.md` — the c64scene.pl (skull) RE thread: per-voice
  subroutine structure, ~20 raster/channel, copyright-validation routine (addr OPEN).

### Author / scene / provenance
- `csdb_release_notes.md` / `csdb_forum_discussion.md` — releases, ROM's Fix SFX
  editor, composers, STIL notes.
- `archive_author_trail.md` / `archive_documentation.md` / `archive_scene_notes.md`
  — Blasnik career, Digital Marketing catalogue, VacSID bundling, cracks.
- `forum_discussion.md` / `forum_technical_notes.md` — forum/diskmag aggregation,
  business address, V7.96 dual-player observation.
- `src/vacsid_v159_doc.txt`, `src/vacuum_nfo_mekka_prerelease.txt` — VacSID docs.

## What we have (quality assessment)

| Need | Status |
|---|---|
| Memory map / entry points / freq table offset | **GOOD** — manual + sidid + research.md |
| Track/sequence byte semantics | **GOOD** — manual + FC-compat ranges |
| Instrument byte layout (B0–B7) + drum table | **GOOD** — author manual |
| Sector/pattern command SET (mnemonics) | **GOOD** — 21 commands from manual |
| Sector command numeric DISPATCH bytes | **OPEN** — RE (manual gives mnemonics only) |
| Per-effect → SID register behavior (exact) | **PARTIAL** — semantics known, exact write formulas RE |
| sidid signatures / version discrimination | **SOLVED** — byte-exact |
| V7.96 dual-player layout | **OBSERVED** — confirm in RE |
| Version lineage / author / scene | **SOLVED** |

## Open items (defer to migration/RE phase — each is a disasm trace)

1. **Disassemble a V6.3 player** (e.g. `GAMES/M-R/Riddles_and_Stones.sid`,
   `MUSICIANS/H/Hartwig_Stefan/Double_Sphere.sid`) to recover the **numeric
   dispatch bytes** for the 21 sector commands and the exact per-effect SID-write
   formulas. The manual gives the command SET; only the binary gives the opcodes.
2. **V7 note-byte encoding** — confirm the octave/flag packing implied by `AND #$07`.
3. **V7.96 dual-player layout** — confirm the two embedded sub-players + dispatcher,
   and which one actually plays.
4. **Copyright-validation routine** address (skull stripped it in 2009 but no hex
   was preserved) — locate so it can be ignored during extraction.
5. **Drum table + arpeggio data binary layout** in the instrument/sound table.
6. **V6 vs V7 saved-file binary structure** delta (load address aside).
7. (Optional) verbatim c64scene.pl post text via `curl` for any hex skull mentioned.

All Open items are confined to the 591 HVSC binaries we already hold and are the
proper subject of the `disassembly.s` + extractor step. The online search space
(CSDb, archive.org, GitHub, German forums, diskmags) is exhausted; the author's
manual was the last major external artifact and it has been recovered.

## Suggested first migration target

A **V6.3** tune (the dominant 569-SID bulk, $8000 load, raw note bytes — simpler
than V7's packed encoding). Disassemble it with `ROMUZAK.DOC` open as the spec:
the manual's command mnemonics + the FC-compat track-byte ranges give a near-
complete Rosetta stone; only the numeric dispatch table needs recovering.
