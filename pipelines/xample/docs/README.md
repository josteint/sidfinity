# X-Ample / Compotech — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

X-Ample / Compotech, by **Markus Schneider** (driver) + **Helge Kozielek** +
**Mario van Zeist** (speed optim.) + **Joachim Fräder** (editor UI) — **X-Ample
Architectures, Germany** (1988-1997, via CP-Verlag). ~380 HVSC tunes (`X-Ample`),
0 migrated. Closed source, **but** an annotated player source ships on disk (below).

A six-cluster sweep ran 2026-06-13 (gather+summarise, on sonnet). Famous tunes:
Thomas Detert's game music (Turrican 3, Katakis, Gordian Tomb).

## Start here

1. **`csdb_manual.md`** — the **annotated V3.2 TurboAss player source** (an
   integration-reference SEQ on the Compotech V2.1 D64, CSDb #122614), summarised:
   VBI loop, 3-voice bitmask, the effect routines, the SFX block format.
2. **`spec_extraction_plan.md`** — plan + the multi-variant layout groups + OPENs.
3. **`spec_write_model.md`** — per-frame `$D400-$D418` model (3-voice, +7 stride).
4. **`sidid_variant_taxonomy.md`** — the 7 sub-variants, statically decoded.

## Engine model (from the V3.2 source)

VBI-driven; player iterates **3 voices via a bitmask**, per-voice subroutine,
**7-byte voice blocks** ($D400 / $D407 / $D40E). Effect routines (named in the
source): vibrato, portamento/glide, arpeggio, drum (wave-table), pulse sweep,
filter sweep, pseudo-echo (tremolo), **true echo** ("Echtes Echo"), fade,
velocity ("Anschlagsdynamik"). SFX block: 4-byte entries `[voice-bitmask][blk1]
[blk2][blk3]`, `$FE,$01,$00` terminator. The byte-level *song-data* layout
(patterns/sequences/instruments) is **OPEN** — the source on disk is the player,
not a data-format spec; RE during migration.

## Lineage & variants (likely ONE data format, multiple editors)

Schneider's driver (~1989) → **Parsec Music Editor V5.1** (1989) → **Compotech V1**
(1992) / **V2.1** (1995). Then **XTracker V3.1 / V4.1x / V4.2x** by **Tufan Uysal
(SoNiC)** — a *separate author* (X-Ample had disbanded by 1996), with the **XTracker
V3.1 player byte-identical to Compotech V2.1** (CSDb-confirmed). Plus personal forks
`Thomas_Detert` and `Sonic/SDS`, and a 2019 `Comptech-X` (Geir Tjelta + Schneider —
links to the `sidduzzit`/Geir-Tjelta family). sidid sub-variants: base `X-Ample`,
`Compotech_V2.x`, `Sonic/SDS`, `Thomas_Detert`, `XTracker_V4.1x` (unrolled 3×JSR
dispatch vs the bitmask loop), `XTracker_V4.2x` (1 tune), `X-Ample_Digi`.

**Implication for migration:** most non-Digi variants likely share one data format
(V3.1≡V2.1 confirmed) → probably **one extractor + per-variant write-quirk flags**
(e.g. Detert/SoNiC write `$D416`/`$D418` every frame; a DMC-style `*_every_frame`
knob). XTracker V4.1x's dispatch change is the main thing to verify (format change
unconfirmed — OPEN).

## ⚠ Scope flags

- **`X-Ample_Digi`** = CIA2-NMI sample playback (`$DD04/$DD05/$DD0E`) → **Mode-2
  (cycle-exact), out of the standard `$D400-$D418` scope**. **0 confirmed** in HVSC;
  the RSID `Hawkeye_II.sid` (Schneider, `play=$0000`) is the candidate. Defer/exclude.
- **11 CIA-timed SoNiC tunes** are music-CIA (tempo) → the **Mode-1 per-IRQ** path
  (`--writelog-per-irq`), NOT digi. Confirm during migration.
- **`Reflextracker` (137 tunes) is a SEPARATE engine** (Polish demoscene, all RSID,
  `play=$0000`) — *not* X-Ample. Don't conflate (a sweep agent mistakenly lumped it
  into a "combined family" count). It's its own `LITTLE` family.

## Census (`hvsc84.db`, read-only)

380 `X-Ample` (+1 `XTracker_V4.2x`); 379 PSID / 1 RSID; all `psid_version=2`,
`load_addr=$0000`; 757 subtunes (avg ~2). Layout groups:

| Group | Count | init/play | Status |
|---|--:|---|---|
| A | 192 (51%) | init=BASE, play=BASE+3 | primary target |
| B | 118 (31%) | init=BASE+3, play=BASE | likely same player, flipped header convention |
| C | 16 | init=BASE, play=BASE+6 | OPEN (Detert; 2×JMP stub?) |
| exotic | 53 | various (incl. Merken $116C/$09D1) | defer |

A+B ≈ 82% — the first target. **Hypothesis to confirm at migration**: A and B are
the same player binary with the PSID init/play fields swapped → one extractor.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Player source (V3.2, annotated) | `csdb_manual.md` | `archive_version_history.md` |
| Extraction plan + layout groups | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | — |
| sidid variant taxonomy | `sidid_variant_taxonomy.md` | `github_editor_lineage.md` |
| Family relationships (XTracker=SoNiC) | `forum_family_relationships.md` | `forum_xtracker_by_sonic.md` |
| Digi / CIA mode | `forum_digi_cia_mode.md` | `deepsid_population_and_digi.md` |
| Releases / editors | `csdb_releases.md` | `forum_csdb_releases.md`, `archive_version_history.md` |
| Authors / scene | `archive_authors_scene.md` | `forum_wiki_group_history.md`, `forum_dev_interviews.md` |
| Tooling (closed) / negatives | `github_parsers_survey.md` | — |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- The **player architecture + effect set** (from the annotated V3.2 source on disk).
- The variant taxonomy + the **one-data-format hypothesis** (XTracker V3.1 ≡ Compotech V2.1).
- Authorship/lineage (incl. XTracker = SoNiC, separate; Comptech-X ↔ Geir Tjelta).
- Census + layout groups + the digi/Reflextracker scope clarifications.

## What remains (migration — OPENs, deferred from this gather-only sweep)

- **Disassemble canaries** to pin the song-data byte layout (patterns/sequences/
  instruments) — bootstrap with the annotated V3.2 source + the Compotech V2.1 D64.
- **Confirm A≡B** (one extractor) and whether **XTracker V4.1x** changed the data
  format (vs just the dispatch). Per-variant write-quirk flags (Detert/SoNiC every-frame $D416/$D418).
- **Exclude** `X-Ample_Digi`/`Hawkeye_II` (Mode-2) + confirm the 11 CIA SoNiC tunes are Mode-1-per-IRQ.
- Canary: `MUSICIANS/S/Sonic/4k_Intro_windows_95_mix.sid` (small, Layout A, $1000/$1003).

## Top leads

1. **Compotech V2.1 D64** (CSDb #122614) — vendor the annotated V3.2 player SEQ + extract a canary's data section.
2. **XTracker V4.13 D64** (CSDb #82320) — for the `XTracker_V4.1x` dispatch/format diff + SoNiC demo SIDs as canaries.
3. **Parsec Music Editor V5.1** (CSDb #10744) — the pre-Compotech player the base `X-Ample` sig anchors to.
4. **xap64.de** (X-Ample history homepage, ECONNREFUSED) via Wayback; **Markus Schneider** (CSDb #6003, active) for format details.
