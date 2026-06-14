# CheeseCutter 2.x — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

CheeseCutter, an open-source (GPL) D-language cross-platform SID tracker by
**Timo Taipalus ("Abaddon")** of Triad (later co-dev Ruk). 302 HVSC #84 tunes
tagged `CheeseCutter_2.x`; 0 migrated. Default export: load=$1000, init=$1000,
play=$1003. Full source is locally checked out (read-only) at
`tmp/dmc_hunt/CheeseCutter/`.

## ⚠ The player is an evolved JCH NP21.G4 — see the JCH/Laxity corpus first

CheeseCutter's native export player is `src/c64/player_v4.acme` ("Based on JCH NP
21.G4 by Laxity/VIB"). **The per-frame `$D400-$D418` write model + effect chain are
already documented** in [`pipelines/jch_newplayer/docs/github_cheesecutter.md`](../../jch_newplayer/docs/github_cheesecutter.md)
and [`pipelines/laxity_newplayer/docs/cluster_np21_effect_routines.md`](../../laxity_newplayer/docs/cluster_np21_effect_routines.md).
The "CheeseCutter / NP21+ runtime" column in the JCH two-encoding table **is** this
format (4-byte pulse/filter rows, column-major instruments, `$bf` sequence end-mark).
Read those for the effect semantics. This corpus is the **CheeseCutter-specific
delta**: the export data packing, the per-tune player variability, version diffs, 2SID.

## File index

| Topic | File | Reliability |
|---|---|---|
| Export data layout + `.ct` format + variable INSNO + effect stripping | `cluster_native_player_and_export.md` | primary (D source) |
| ↳ key D-source excerpts | `src/base_d_structs.d`, `src/build_d_dumpOptimized.d`, `src/dump_d_dumpData.d` | primary |
| 4 sidid sub-variants + 2SID stereo write model | `cluster_versions_and_2sid.md` | primary |
| Release timeline + scene + HVSC corpus shape | `cluster_history_and_scene.md` | secondary |

## What's solved — the migration-critical deltas

**The exported SID is assembled fresh per tune, NOT pre-linked** (`build.d::dumpData`):
the `player_v4.acme` source is text-substituted with per-tune `INCLUDE_*` defines,
merged with song data as ACME `!byte`/`!word`, and re-assembled. Consequences the
extractor MUST handle:

- **Variable `INSNO` (per-tune)** — `INSNO = numInstr+1` (highest instrument actually
  referenced +1), NOT always 48. Every `INS_SR`/`INS_HR`/... offset scales with it.
  Probe per-tune (instrument-block size / 8 columns, or disassemble the player). **The
  single most important extractor detail.**
- **Per-tune effect stripping (`dumpOptimized`)** — 15 `INCLUDE_*` flags; any effect
  routine not used by the tune is not assembled, so **the player byte image (and size)
  varies per tune** (this is also why sidid sub-sigs are present/absent per tune).
  `INCLUDE_CMD_SET_WAVE` (`$06`) is **always FALSE** (never present in any CC export).
  **`INCLUDE_FILTER=FALSE`** ⇒ no `$D415/$D416/$D417` writes at all (~half of tunes).

**Data section order** (runtime, after player code): `arp1, arp2, filttab, pulstab,
inst0..inst7, seqlo/seqhi, cmd1/cmd2/cmd3, songsets, track{N}_{V} orderlists, s00..sNN
sequences, chord, chordindex`. No `$0fa0` pointer table in exports (editor-only).
- **songsets**: 8 bytes/subtune = 3×2-byte track ptrs + 1 speed + 1 voicemask (hardcoded `7`).
- **sequence end-mark `$bf`** (NOT NP20's `$7f`); note+command uses raw `$60-$bf` + cmd byte; bare notes `$00-$5e`.
- **`.ct` on-disk**: zlib blob; header at decompressed offset 65536 (`ver, clock, multiplier,
  sidModel, fppres, songspeeds[32] if ver≥6, highlight if ver>10`); titles/labels/orderlists
  at fixed high offsets. (`.ct` is the editor format; HVSC ships the assembled `.sid`.)

**Four sidid sub-signatures — NOT mutually exclusive** (one binary can match several;
sidid picks by cfg order). For the pipeline, **all single-SID variants share ONE player
architecture and ONE extraction code path**:

| sidid label | fingerprints | HVSC | note |
|---|---|---|---|
| `2.0-2.2` | flat voicon init | **0** | pre-2012, none survived in HVSC |
| `2.3-2.4` | subinit1 tail | **4** | ordering artifact (cfg lists it before 2.5+) |
| `2.5+` | chord dispatch `CMP #$A0/AND #$1F` | **184** | present only if `INCLUDE_CHORD=TRUE` |
| `2SID` | `STA $D415 … STA $D435` | **6** | PSID v3, 2nd SID at $D420 |
| parent `2.x` only | all above stripped | **108** | 2.5+ player w/ chord stripped |

**2SID stereo write model** (9 PSID-v3 tunes by LMan/Scarzix/Steel; agent disassembled
`Auxillary_Love_2SID.sid`): **6 voices**, voice table `{$00,$07,$0E,$20,$27,$2E}` —
voices 0-2→SID1 ($D400), 3-5→SID2 ($D420); loop X=5→0. Per-voice write order identical
to single-SID (freqlo,freqhi,SR,AD,PWlo,PWhi,ctrl). Filter once/frame interleaved
`$D415,$D435,$D416,$D436,$D417,$D437,$D418,$D438`. Init zeros both chips in one LDX#$18
loop. All 2SID tunes: PAL/8580/speed=0/VBI. **This needs a 6-voice write-stream verdict**
(the stereo branch `v2.9-beta-3-stereo` was never merged to master).

**Timing**: 1× tunes `speed=0` (VBI); multispeed `speed=0xffffffff` (CIA, timer
`$4cc7/multiplier`) → the Trap-C `--writelog-per-irq` path.

**Release timeline** (player-string anchors): 0-series 2011 (JCH-compat) → 2.x 2012
(JCH dropped, `.ct` format, 3-byte cmd table) → 2.5.0 2013 (multispeed, wave program) →
2.7.1 2015 (`cc4.03`, first GitHub tag) → 2.8.0 2015 (`cc4.04`, stereo beta) → 2.9.0
2017 (`cc4.07`, last Abaddon release) → 2.10 2026 (SDL2, no format change). **Exported
SIDs carry no version string** — version is inferred from player byte image, not read.

## Corpus shape (302 tunes)

92.7% single-subtune; 208/302 at default $1000 base; 9 PSID-v3 (2SID); mean songlength
~2.85 min; peak 2015–2017; LMan+Scarzix ≈ 35% of corpus. **Two groups to audit before
migration**: 25 LMan tunes with init=$080D/play=0 (may not be standard CC exports) and
4 early Abaddon tunes at $0FED.

## What remains (migration-phase RE, not research)

- **Disassemble one standard CC export** (`seed_disassembly.py`) to: read per-tune INSNO,
  confirm which `INCLUDE_*` are set (→ which effect routines present), and confirm the
  exported data-section base offsets. The 2.5+/parent group (292 tunes) is the main path.
- **6-voice 2SID write-stream verdict** for the 9 PSID-v3 tunes (separate from the
  single-SID path).
- **Audit the $080D/play=0 LMan group (25) + $0FED group (4)** — confirm they're CC
  exports vs misclassified before counting them in scope.
- `fppres` field purpose unknown; per-tune chord-table/tempo breakspeed boundary.
- Leverage the DMC/JCH pipelines — same NP21 table + hard-restart machinery.

## Top leads (if migration needs more; CSDb 503 / Wayback / changelog-401 this session)

1. **GitHub `theyamo/CheeseCutter`** tags `v2.7.1…v2.9.0` — diff `player_v4.acme` across
   `cc4.03/4.04/4.07` to enumerate the exact per-version player byte differences.
2. The **`v2.9-beta-3-stereo`** branch — the only place 2SID export is implemented;
   confirm the PSID-v3 header + 6-voice layout against the 9 HVSC tunes.
3. CC changelog site (401) + CSDb release pages (503) — retry for v2.3–2.6 feature dates.

Full provenance in each file + `provenance_log.md`.
