# Digitalizer — research docs index

Player family: **Digitalizer**, by **Olav Mørkrid** ("OFF" / "Omega Supreme",
Panoramic Designs, Norway). Editor versions V2.2 (1989) → V3.5 (1995). The 6502
player source is **NOT public** — this sweep reconstructs the format from the
recovered V3.0 help text, the sidid signatures, and the documented descendant
format **SID Duzz' It (SDI)**.

HVSC #84 footprint (our DB engine classification): **542 `Digitalizer_V2.x` + 77
`Digitalizer_V3.0` = 619 SIDs**. (The sidid databases additionally tag 38 SIDs as
`Olav_Moerkrid` — see the variant note below; in our corpus those fall under the
Digitalizer_* engine strings.) Heaviest user: **Blues Muz' / Glenn Gallefoss**
(150+ tunes), Norwegian scene.

Research sweep date: **2026-06-13**. Two waves of parallel sonnet agents
(CSDb · archive.org/author · GitHub/sidid · forums · SDI-proxy · ancestor/variants).
GATHER-only — no RE, no siddump/py65. The 6502-level RE is the migration phase.

## TL;DR for the migration phase

- **No source, no parser, no format spec exists in open source.** The only
  open-source knowledge is the **sidid signatures** (decoded in
  `github_sidid_signature.md`). Everything else is reconstructed.
- **The single recovered primary document** is Olav's own **V3.0 help file**
  (`src/digitalizer_v3.0_instructions.txt`, PETSCII→ASCII by 6R6, June 1992). It
  gives the editor's three modes and the **sequence byte encoding** — the most
  load-bearing artifact we have.
- **SDI (SID Duzz' It) is the format proxy.** SDI's own manual states it was
  "built on ideas from the JCH/Vibrants editor, Olav Mørkrid/Panoramic
  'Digitalizer' editor and Geir Tjelta/Shape 'SID Systems'", and the **DTZ2SDI**
  converter turns Digitalizer V3.x data into SDI. SDI is fully documented
  (`sdi_format_spec.md`), so its data model bounds Digitalizer's — but SDI also
  *added* features (see the reliability split in `sdi_digitalizer_mapping.md`).
- **It's a tracker + integrated digi player.** A 4-bit sample player writes
  `$D418` with `STA $01` banking (`OmegaSupreme_Digi` signature). Expect digi
  alongside the synth voices.

## Format facts we are confident about

### Sequence byte encoding (V3.0, from Olav's help file — `src/digitalizer_v3.0_instructions.txt`)
A single packed byte stream mixing notes + commands:
- `$00–$1F` — set instrument (32 instruments)
- `$20–$3F` — set arpeggio (32 arpeggios)
- `S1–SF` — sustain add
- `R0–RF` — release / attack + gate
- `$00–$7F` — portamento rate (with a P-declare)
- note values; tie flag (bit 0 only: pulse/filter tie)
- end-of-sequence sentinel — **`$7F` vs `$FF` is unresolved** between the two
  sidid databases (cadaver uses `$7F`, WilfredC64 uses `$FF`); likely version-
  dependent. OPEN.

### Instrument model
Per-instrument **sub-tables: waveform, pulse, filter, arpeggio**, plus **two
speed parameters**. Filter table first appears in **V3.0** — V2.2 / V2.8 have
wave/pulse/arpeggio but **no filter** (HVMEC version comparison). The SDI
descendant uses **10 parallel byte arrays** per instrument (AD, SR, gate-timeout,
vibrato ptr, pulse ptr, filter ptr, band/resonance, detune hi/lo, waveform ptr) —
a likely superset of Digitalizer's field set.

### Architecture / versions
- **V2.x** — relocatable (wildcard `STA $D4xx` addresses in the signature),
  common load addresses $1000 / $9000. Variables around page 3 ($0334–$03A4).
- **V3.0** — partly **fixed-address** (signature embeds absolute $033A/$033D/$0340
  in the stack page); a digi/sample clipping loop (`$80`/`$C0`/`$3F` thresholds).
  Variable speed divider at $033D (1×/2×/3×).
- **V3.5** — a **re-assembly/rewrite by GRG + Kjell Nordbø** ("Newplayer 3.5",
  F1/F3 play/stop vs F7/F5 earlier). **No own sidid entry** → V3.5 HVSC tunes
  almost certainly match the `Digitalizer_V3.0` signature. OPEN: confirm.
- **Ancestor** — Olav admits copying **Stein Pedersen's "Prosonix Music Editor" /
  "SteinTronic"** ("vi kaller det herming" = "we call it imitation"). Stein was a
  fellow Panoramic member. The Prosonix sidid variants use a `$C0/$E0` sentinel
  range vs Digitalizer's `$7F/$FF` — the clearest format divergence.

## File index

### Format / proxy (read these first for the migration)
- `src/digitalizer_v3.0_instructions.txt` — **PRIMARY**: Olav's V3.0 help text.
- `sdi_format_spec.md` — byte-level SDI v2.1 format (instrument arrays, all
  program tables, sequence/tracker layout, player entry points). The proxy spec.
- `sdi_effect_reference.md` — per-effect SDI → `$D400–$D418` register writes per tick.
- `sdi_digitalizer_mapping.md` — **inferred Digitalizer↔SDI field mapping with an
  explicit "safe to assume vs SDI-only" reliability split.** Read before trusting
  any SDI fact for Digitalizer.
- `src/sdi_2.1.6_docs_summary.md` — verbatim SDI manual excerpts.

### Signatures / detection
- `github_sidid_signature.md` — all sidid entries decoded (V2.x, V3.0,
  Olav_Moerkrid ×2, OmegaSupreme_Digi, Panorama) with byte-level meaning.
- `src/sidid_signatures_raw.txt` — verbatim signature blocks (cadaver + WilfredC64).
- `github_player_detection.md` — survey of every open-source tool's Digitalizer handling.
- `variants_player_families.md` — **resolves the 6 sidid entries**: `Olav_Moerkrid`
  detects the tracker sequence-player; `Digitalizer_V*` detect the digi/sample
  code; `OmegaSupreme_Digi` the 4-bit `$D418` digi; `Panorama` a voice dispatcher.

### Versions / lineage
- `csdb_release_notes.md` / `csdb_version_differences.md` — all 7 releases +
  recovered keyboard/command reference + version deltas.
- `variants_ancestor_prosonix.md` — the Prosonix/SteinTronic ancestor + JCH influence.
- `archive_documentation.md` — V3.5 instrument-editor field names + column headers
  extracted from disk-image strings; DTZ2SDI provenance correction.
- `archive_author_trail.md` / `archive_scene_notes.md` — author/scene context.
- `forum_discussion.md` / `forum_technical_notes.md` — forum/diskmag/HVMEC notes.
- `github_parser_notes.md` — structural inferences + binary download locations.
- `csdb_leads_to_follow.md` — wave-1 lead list (largely chased in wave 2).

## What we have (quality assessment)

| Need | Status |
|---|---|
| Sequence byte encoding | **GOOD** — from Olav's own V3.0 help file (sentinel byte OPEN) |
| Instrument sub-table set (wave/pulse/filter/arp) | **GOOD** — help file + V3.5 field names + SDI proxy |
| Per-effect → SID register behavior | **PROXY-ONLY** — documented for SDI; must verify against Digitalizer binary |
| sidid signatures / version discrimination | **SOLVED** — byte-exact |
| Digi/sample path | **KNOWN to exist** (4-bit `$D418`, `STA $01` banking); exact model OPEN |
| Version lineage (V2.2→V3.5 + ancestor) | **SOLVED** |
| Byte-level on-disk layout (table offsets, order list) | **NOT SOLVED** — needs RE (no spec exists) |

## Open items (defer to migration/RE phase — each is a disasm/extraction trace)

1. **Disassemble a V3.0 player** (e.g. `MUSICIANS/B/Blues_Muz/Solitaire.sid`,
   `Saviour.sid`, `Nibbleman.sid`) to recover the authoritative on-disk layout:
   table base offsets, order-list/sequence pointer scheme, instrument array
   addresses. This is the single highest-value RE task — no online spec exists.
2. **Extract + read the DTZ2SDI converter** (CSDb #237762, `.d64` in
   `tmp/digitalizer_research/DTZ2SDI.zip`). Its Digitalizer-READ routines document
   the exact V3.x field layout, and its SDI-WRITE side is already specced here.
   Needs a D64 tool (vice/c1541) to extract the PRG, then disasm.
3. **Resolve the end-of-sequence sentinel** `$7F` vs `$FF` (version-dependent).
4. **Confirm V3.5 player identity** — do HVSC V3.5 tunes match the V3.0 signature
   byte-for-byte, or did the GRG "Newplayer 3.5" diverge?
5. **Digi/sample exact model** — sample rate, packing, how the digi voice
   interleaves with the 3 synth voices, banking timing.
6. **Per-effect register write formulas** — portamento/glide rate→Δfreq, vibrato
   delay/width/rate, pulse + filter program stepping, gate/hard-restart sequence.
   Confirm against the binary; SDI gives the shape, not the exact Digitalizer values.
7. **Olav_Moerkrid vs Digitalizer_V2.x scope** — confirm whether the 38
   `Olav_Moerkrid`-tagged tunes are a meaningfully different engine for our purposes.
8. **(Low priority) Prosonix/SteinTronic** ancestor format — only if V2.x RE stalls.

All Open items are confined to binaries we already hold (619 HVSC SIDs + the
downloaded editor/converter images) and are the proper subject of the
`disassembly.s` + extractor step. Nothing further is fillable from online sources —
the search space (CSDb, archive.org, GitHub, forums, diskmags) is exhausted.

## Suggested first migration target

A **V3.0** Blues Muz' tune (filter table present, fixed-address player → easier to
anchor). Disassemble it alongside the SDI spec as a Rosetta stone; cross-check
table semantics against `sdi_format_spec.md` + `sdi_digitalizer_mapping.md`.
