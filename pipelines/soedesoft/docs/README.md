# SoedeSoft / Soundmaster — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

SoedeSoft / Soundmaster, by **Jeroen Soede** (player/driver) + **Michiel Soede**
(editor/music) — Dutch twins, subgroup of **Fire-Eagle**, 1988-1989. ~929 HVSC
tunes (`SoedeSoft`), 0 migrated. **Closed engine — no public source.**

A six-cluster sweep ran 2026-06-13 (gather+summarise, on sonnet). Despite being
closed, the translated German V3.1 manual yielded a solid song-data model; the
byte-level binary layout stays OPEN for the migration phase (a closed engine —
expected). JC64dis ships a `SoundMaster1.dis` analysis profile as a disasm bootstrap.

## Start here

1. **`csdb_manual_de.md`** — the translated German Soundmaster V3.1 manual: the
   full song-data model + sound structure + effects (the richest source).
2. **`spec_extraction_plan.md`** — honest closed-engine plan: fixed anchors + a
   clearly-marked OPEN list (byte offsets needing a disasm).
3. **`spec_write_model.md`** — per-frame `$D400-$D418` model (DOCUMENTED vs
   INFERRED vs OPEN, explicitly labelled).
4. **`sidid_signature_analysis.md`** + **`population_census.md`** — variant sigs + the layout clusters.

## Engine model (from the V3.1 manual)

- **Hierarchy**: Song → **Block** → **Step** → **Bar**. 3 voices in parallel.
  Each step assigns a bar# + per-track transpose; each block adds a second
  transpose layer + a per-track sound-number offset (`s1/s2/s3` — the same bar
  can sound different timbres per block).
- **Note byte**: octave + chromatic semitone + sound# (`$00-$2F` = 48 sounds) +
  bit `$40` (transpose-off) + bit `$80` (portamento).
- **Sound** (2-3 parts): waveform bytes (`$D404`) + optional arp/wave table ptr
  block; ADSR + pulse start/sweep + vibrato + delay/portamento + filter
  start/sweep; an interleaved arp+wave table (`$7F` = "current note"; `$81`
  waveform + `$7F` = a Hubbard-style drum tick).
- **Effects**: arpeggios, wave patterns (waveform cycling), PWM, filter modulation.
  "Nothing ripped — from scratch."
- **Entry**: +$0 (JMP init) / +$3 (JMP play); standalone `SYS $6000`. Player
  ~884 bytes; vars at page 3 (`$0333-$039D`); per-voice indexed `STA $D4xx,X`
  (X=0/7/14); embedded ASCII sig `"88 SOEDESOFT-"`; VBlank/50 Hz.

## Versions

SoedeSoft (group) = **SoedeSound Editor** (product screen name) = **Soundmaster**
(scene release) — *the same software*. **V1.0** (1988/89; editor); **V3.1** (1989,
public, via Magic Disk 64 — the German PDF manual); **V3.2** (Fire-Eagle internal).
**V2.x gap** unexplained. sidid distinguishes V1.0 / V3.1 / V3.2 by the freq-write
loop: V3.2 adds a `CLC/ADC abs,X` portamento accumulation that V3.1 lacks; V1.0 uses
indirect (`B9/99`) writes. The DeepSID `soedesoft.py` classifier is a *pure sidid
reformatter* (emits only those 3 sub-labels; HVSC stores engine-level only). Amiga
successor = "SoundMaster Professional"; the modern SIDmaster Reason plugin
reimplements the engine (authoritative effect list).

## Census & verification (`hvsc84.db`, read-only)

929 tunes, all **PSID v2, VBlank/50 Hz** → flat **Mode-1** verdict (PSID speed-bit
survey is an OPEN to confirm). 96.8% single-subtune. **8 init→play offset clusters**;
dominant `init=$6000 / play=$6006` (309) = the V3.1 canonical batch and the primary
migration target. The clusters differ by init-preamble length — which cluster maps
to which version/cluster needs the embedded-sig scan (OPEN).

## ⚠ Closed engine — byte layout is OPEN

No public source and no human-readable disassembly. **JC64dis (`ice00/jc64`) ships
`doc/example/SoundMaster1.dis`** — Ian Coog's binary analysis profile, the best
disasm bootstrap. The manual gives *semantics*; the exact binary table offsets
(bar-row packing, sound-record byte layout, the arp+wave table encoding, var-area
assignments) require a disassembly **during migration** — recorded as OPENs with
traces, not RE'd here.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Format model (manual) | `csdb_manual_de.md` | `forum_sidpreservation_trackers.md` |
| Extraction plan + OPENs | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | `sidid_signature_analysis.md` |
| sidid sigs / variants | `sidid_signature_analysis.md` | `forum_sidid_signatures.md`, `deepsid_classifier.md` |
| Population / clusters | `population_census.md` | — |
| Versions / naming | `forum_naming_and_versions.md` | `archive_version_history.md`, `csdb_releases.md`, `forum_csdb_releases.md` |
| Authors / interview | `archive_authors_pages.md` | `forum_remix64_interview.md`, `forum_vgmpf_wiki.md` |
| Tooling (closed; JC64dis profile) | `github_tools_survey.md` | — |
| Leads | `forum_leads_to_follow.md` | (per-doc "Leads to follow") |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- The **song-data model + effect set** (from the translated manual + interview).
- Version taxonomy + naming + the sidid V1.0/V3.1/V3.2 freq-loop deltas.
- Census (929; 8 layout clusters; VBlank; the $6000 V3.1 primary batch).
- Confirmed closed-source; identified the JC64dis profile as the disasm bootstrap.

## What remains (migration — OPENs, deferred from this gather-only sweep)

- **Disassemble a canary** (seed `disassembly.s`) to pin the byte layout: bar-row
  packing, sound-record offsets, the arp+wave table encoding, var-area assignments,
  the per-frame write order — bootstrap with the JC64dis `SoundMaster1.dis` profile.
- **Embedded-sig version scan** + map the 8 layout clusters to V1.0/V3.1/V3.2.
- **PSID speed-bit survey** (expected VBlank → flat Mode-1; confirm).
- **Digi outliers**: a few large files (17-32 KB: `Magic_Drums`, `Magnetic_Fields`,
  `Let_It_Be`, …) likely embed PCM — check whether the engine has a built-in digi
  path or these need a separate route.
- Canary: a canonical `init=$6000` V3.1 tune.

## Top leads

1. **`soundmaster3.1.prg`** editor (CSDb #90307 getinternalfile 87430) — disasm the
   actual editor binary to resolve the byte-layout OPENs without a SID canary.
2. **`SoundMaster1.dis`** (`ice00/jc64`) — extract/load Ian Coog's annotation profile.
3. **`Soundmaster_V3_1_Docs.prg`** (CSDb #90307) — the in-program docs, maybe extra detail.
4. **Michiel Soede** (soedesoft.com, active) — could resolve the V2.x gap + format internals.
