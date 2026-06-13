# SID-Wizard (Hermit) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

SID-Wizard, by **Hermit (Mihály Horváth)** of SIDRIP Alliance, 2012-2022
(V1.0 RC → V1.92). **WTF-license, fully open source.** ~1,048 HVSC tunes
(`Hermit/SidWizard_V1.x`), 0 migrated. Supports 1/2/3/4-SID.

A six-cluster sweep ran 2026-06-13. Outcome: **the most complete source picture
in the campaign** — the entire player is open (`player.asm`, `exporter.asm`,
`SWM-spec.src`, Hermit's own 31 KB `ChangeLog.txt`), plus a 27-page author-written
manual (a prose format spec), full version history, and four decoded HVSC binaries.

## Start here (canonical, source-grounded)

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist + OPEN items.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` model (Mode-1 target).
3. **`github_exporter_layout.md`** — the **extraction target**: what `exporter.asm`
   produces at $1000 (jump table, version string, embedded SWM header, data behind
   self-modified pointer tables).
4. **`github_player_writemodel.md`** + **`github_swm_format.md`** — the player loop
   + the SWM format from `SWM-spec.src`.
5. **`csdb_hermit_site_manual.md`** — the 1.4 manual: every musical-byte *semantic*
   (table command codes, the full FX catalogue, multispeed thresholds, HR types).

## Scope & census (read before any migration)

`hvsc84.db`: 1,048 tunes. **PSID version is a perfect chip-count proxy**: v2→1010
(1SID), v3→29 (2SID), v4→9 (3SID), no 4SID.
- **In-scope target = the 1010 single-SID tunes** (the $D400-$D418 verdict).
  Primary slice: `v2 AND init=$1000` = **739** tunes; the rest are relocated
  ($0FB8/$0C00/$E000/$A000…) or deferred-init layouts.
- **Exclude the 38 multi-SID tunes** — they write extra chips ($D420/$D440/$D460+);
  discriminator is `psid_version≥3` **or** the `_2SID`/`_3SID` filename suffix
  (DeepSID itself keys off the suffix). Add to `tools/excluded_sids.json` at
  migration time.

## ⚠ Verification mode: flat Mode-1 for the main slice

Despite SID-Wizard's CIA-multispeed *capability* (and the exporter's CIA-default
source), **real HVSC exports are overwhelmingly vblank**: PSID `speed=0` for
992/1048; only **56** set bit 0 (CIA multispeed). So the 739-tune primary slice
is **flat `siddump --writelog` (Mode-1)**; the 56 CIA/multispeed tunes use
`--writelog-per-irq` (Trap C). Init is a clean universal reset (`$D400-$D417`
descending clear, `$D418=$0F`) → the **init-trichotomy** comparator applies directly.

## Per-frame write model

Voices dispatched **V3→V2→V1**, **filter ($D415-$D417) last**, then `$D418`.
Two flush implementations (driver-dependent):
- **Ghost/multi-SID builds**: the fixed `COMMONREGS` loop — per voice **SR, AD,
  Freq-lo, Freq-hi, PW-lo, PW-hi, Waveform** (writes never skipped → held notes
  re-emit every frame).
- **Lean 1-SID builds**: alias `SIDG = SID` and write `$D4xx` incrementally with a
  **driver-variant-dependent** note-start order (e.g. AD,SR,Freq,CTRL vs
  Freq-hi,SR,AD,CTRL) — sparser (writes on change). The driver variant
  (SWM header `$13`) is recoverable from the author-info `N/M/L/E/B` tag.
Hard-restart from the instrument control byte (bits 0-3): HR-ADSR loaded 1-2
frames before gate-on; Normal vs Staccato (test-bit). Multispeed = MULPLY
(`framespeed` IRQs/frame; intermediate ticks advance instrument tables only).

## Exported binary layout (the extraction target)

`[PSID v2/3 header][load $1000][CIA-starter (multispeed only)][player code][MUSICDATA]`.
At load: a **jump table** — `init`=+0 (subtune in A), single-speed `play`=+3,
multispeed=+6, volume=+9 — then an ASCII `"SID-WIZARD <ver>"` string, then an
**embedded native SWM header** (`"SWM1"`/`"SWMS"`, ~load+$20: counts, DRIVERTYPE,
TUNING, FSPEED). **Critical:** the playable data is NOT tightly concatenated after
the header — `exporter.asm` re-lays it out behind the player's **self-modified
pointer tables**, computed per (driver, version). **The exact pointer-table
offset map per `(version, drivertype)` is the one blocking unknown** (see OPEN).

## Versions

Two eras: **C64 player V1.0 (2012) → V1.8 (2021)** evolved (this is where the
per-version sidid sigs come from); **V1.9+ (2022-26)** is the cross-platform PC
editor — the C64 player is essentially frozen, and V1.92's "4SID" is a WebSID
export-header feature, not player logic. Verifier-relevant per-version deltas
(source-confirmed, → config knobs):

| Knob | Change |
|---|---|
| `hr_adsr_order` | AD-then-SR (≤V1.7) → **SR-then-AD at V1.8** (r390) |
| `init_writes_d418` | full `$D400-$D418` clear (≤V1.4) → **$D418 dropped at V1.5** |
| `singlespeed_export` | plain PSID (no CIA) from V1.4 |
| `ghost_register_coverage` | grew V1.0→V1.2; always-on for multi-SID, Extra-only for mono |
| `driver_variant` | light/medium/normal/extra → +bare (V1.5) → +SWP (V1.7) → +demo (V1.8) |

SWM magic `SWM1`/`SWMS` is **frozen across all versions** (SWM2 was planned, never
shipped); obsolete header bytes ($06/$07/$11/$12) must not be read. The exported
player embeds `" SID-WIZARD <ver> "` as an in-binary version stamp (when not stripped).

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan + OPEN | `spec_extraction_plan.md` | `github_exporter_layout.md` |
| Per-frame write model | `spec_write_model.md` | `github_player_writemodel.md`, `forum_player_internals_gotchas.md` |
| SWM format | `github_swm_format.md` | `csdb_hermit_site_manual.md` |
| Format/FX semantics (manual) | `csdb_hermit_site_manual.md` | — |
| Version history + diffs | `archive_version_history.md` | `archive_version_player_diffs.md`, `csdb_releases.md` |
| Multi-SID write map | `forum_multisid_writemap.md` | `sidid_variant_taxonomy.md` |
| sidid taxonomy / census | `sidid_variant_taxonomy.md` | `deepsid_labelling.md`, `forum_versions_and_drivers.md` |
| Releases / Pouet / Wayback | `csdb_releases.md` | `csdb_pouet.md`, `archive_wayback_pages.md` |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- **Full open source** (player + exporter + SWM-spec + ChangeLog) and the prose
  manual — every byte's meaning is documented.
- Per-frame write model, hard-restart, multispeed, driver variants, init.
- Version history + the write-order/init/format deltas → config knobs.
- Census + the 1SID-vs-multiSID scope boundary.

## What remains (migration, not research)

- **Close the pointer-table offset map** — the single blocking unknown. Seed
  `pipelines/sidwizard/<engine>/disassembly.s` for one tune per (version,
  drivertype) and tabulate `{seq,pat,inst,chord,tempo,subtune}` bases. Canary:
  `MUSICIANS/H/Hermit/Magyar_Nepzenek.sid` (1SID, $1000).
- **Recover the lean-emitter + table-stepping source** (large `player.asm` was
  truncated by the raw fetch) via byte-range fetch / SourceForge viewvc.
- **Reconcile DrvType naming** (editor.asm 0=NORMAL/1=MID/2=LIGHT/3=EXTRA/4=BARE
  vs SWM-spec light/medium/full/extra/bare/demo).
- **Exclude the 38 multi-SID tunes** (`tools/excluded_sids.json`) for the 1SID pass.

## Top leads

1. **SourceForge SVN viewvc** for the full `player.asm` bodies + pre-V1.4 layout
   (the 1.0/1.2 byte diffs); GitHub raw truncates the large file.
2. **Full 1.5/1.7/1.8 manuals** (CSDb `getinternalfile`) + the plaintext 1.8 manual
   (`raw.githubusercontent.com/M64GitHub/sid-wizard/.../SID-Wizard-1.8-UserManual.txt`)
   — resolve the orderlist `$B0..$FD` vs `$F0..$FD` dispatch difference.
3. **cRSID** (Hermit's own portable replayer) — an independent reference to
   cross-validate the write stream.
4. **CSDb release pages** (Cloudflare-gated this run; WebFetch's AI path worked for V1.92).
