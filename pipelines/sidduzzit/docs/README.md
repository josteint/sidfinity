# SID Duzz'It (SDI) — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

SID Duzz'It (SDI), by **Geir Tjelta (GT)** + **Glenn Rune Gallefoss (6R6/GRG)** of
**SHAPE** (Norwegian scene), 1996-2014 (V2.1.7). ~934 HVSC tunes
(`Geir_Tjelta/SIDDuzz'It`), 0 migrated. **Fully open source.**

A six-cluster sweep ran 2026-06-13 (gather+summarise scope, on sonnet — no RE;
`siddump`/disasm deferred to migration as OPENs). The player source, the 65 KB
official format doc, and the manual were all gathered and kept in `docs/src/`.

## Start here

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist + the OPEN items.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` model (as the source describes it).
3. **`github_source_and_format.md`** — format summary from the player asm + docs.
4. **`csdb_manual.md`** — the Psylicium manual (prose: effects, program tables).
5. **`src/`** — the upstream player + docs kept in-repo (`SRC_SDI21-N50.asm`,
   `SDI.2.1.6-docs.txt`, …). See `src/README.md`.

## Engine model

- **Player API** (assembled $1000): `init`=$1000 (X=subtune 0-$1F), `play`=$1003,
  `fadeout`=$1006 (A=level), `speedplay`=$1009 (multispeed, sound-only). ZP $FE/$FF.
- **4 voices**: 1-3 = music, **voice 4 = "conductor"** (tempo / transpose / filter).
- **Instruments**: 10 **column-major** arrays (`z0..z9`: wf-prg ptr, AD, SR,
  gate-timeout, vib-prg, pulse-prg, filt-prg, band/res, detune hi/lo); 32 direct
  (`$00-$1F`) + 16 arpeggio-only (`$20-$2F`) = 48.
- **Program tables**: waveform = a bytecode state machine (cmds `$FF` jump / `$FE`
  delay / `$FD` ADSR / `$FB` multipulse / `$FA` repeat / `$F0-$F7` filter / `$EB-$EE`
  pulse / `$E2-$E7` noise) over parallel waveform+note columns; pulse 4-byte, filter
  4-byte (+ "filter-frame" mode), vibrato 3-byte. Gate-timeout (`z3`) encodes 8
  hard/soft-restart variants + timeout frames.
- **Sequencer**: FX+note pairs; FX `$00-$1F`=instrument, `$21-$3F`=glide, `$40-$6F`=
  arpeggio, `$70-$7F`=ADSR, `$20`=filter toggle. **4 tracks** (3 voices + conductor).

## ⚠ The key complication: ~25 `rem_*` assembly flags

The player is **compile-time configurable**: ~25 `rem_*` flags strip unused
routines, so a tune's exported SID **only contains code+data for the effects it
actually uses**. Consequence: the **music-data region and table bases are NOT at
fixed offsets** — they shift per flag-set and must be located by **dataflow tracing
per tune** (read the table base from `lda tbl-1,y` operands), exactly like the FC
standard-player and DMC/HardTrack. The editor memory map in `research.md`
($3000/$5000/$E000…) is the *editor's* RAM layout, not the exported SID's.

## Versions, timing, census

- **V1.x ↔ V2.x are binary-incompatible** (V1 uses NTSC-derived freq tables, V2
  PAL; a V1→V2 converter shipped but was buggy). HVSC is overwhelmingly **V2 at
  $1000**. The single sidid signature is **version-agnostic** (V1.x–V2.1.7 all match).
- **Multispeed** via `$1009 speedplay` (sound-only between full frames; PAL raster
  split = 312/speed). **OPEN:** whether the PSID speed bit is set per tune → flat
  Mode-1 vs `--writelog-per-irq` verdict; resolve with a header survey at migration.
- **Census (`hvsc84.db`, read-only):** 934 tunes, all `load_addr=0` (load in data
  prefix), `pipeline=NULL`. **609 canonical** (`init=$0FFF` 1-byte stub→$1000 with
  `play=$1003` = 480, or direct `init=$1000` = 129); **325 relocated** (e.g. the
  `$E8FF`/`$E903` cluster = 71). **16 RSID** (`play=0` — digi/echo overlays).
  95% single-subtune.

## ⚠ Sibling Geir Tjelta engines are SEPARATE (don't conflate)

The `Geir_Tjelta/*` sidid family has several distinct engines; only `SIDDuzz'It`
is this target. **`SIDSys` (1989-90)** is the *predecessor* player (different note
model: `C9 C0 / 29 3F` range vs SDI's `C9 80 / 29 7F` bit-mask) — separate engine.
**`Echo`** is a `$D418`-sampling delay-echo *post-processor wrapper* (RSID, `play=0`),
not a standalone player. **`Comptech-X`** is a 2019+ private X-Ample player. Lineage:
JCH inspired GRG → SDI, but SDI is an **independent lineage** (an editor for Geir
Tjelta's player), **not a JCH fork**.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan + OPENs | `spec_extraction_plan.md` | `github_source_and_format.md` |
| Per-frame write model | `spec_write_model.md` | — |
| Format from source + docs | `github_source_and_format.md` | `csdb_manual.md` |
| Manual (prose) | `csdb_manual.md` | — |
| Versions / releases | `archive_version_history.md` | `csdb_releases.md`, `forum_csdb_release_comments.md` |
| Authors / lineage | `forum_lineage_and_relationships.md` | `archive_authors_pages.md` |
| sidid family taxonomy | `sidid_family_taxonomy.md` | `deepsid_sdi_notes.md` |
| Population / DeepSID | `deepsid_sdi_notes.md` | — |
| Forum/Usenet (mostly gaps) | `forum_comp_sys_cbm_and_lemon64.md` | `forum_scene_technical_notes.md` |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- **Full open source + official 65 KB docs + manual**, kept in `docs/src/`.
- Player API, instrument/program-table/sequencer encodings, the conductor track,
  the `rem_*` compile-time-flag model, version lineage, sidid taxonomy, census.

## What remains (migration — OPENs, deferred from this gather-only sweep)

- **Locate the music-data region + table bases by dataflow** per tune (flag-set
  dependent) — the central extraction task; reuse the FC/DMC operand-tracing approach.
- **Fingerprint the `rem_*` flag set** per tune (which effects are compiled in).
- **Confirm the per-frame write order** + glide `$D404` sequence + the `z7`
  band/res access (`,x` vs `,y`) via `siddump --writelog`/`--pc-trace` on a canary.
- **PSID speed-bit survey** → flat-Mode-1 vs per-IRQ verdict for the multispeed subset.
- Decide V1.x scope (separate, NTSC, binary-incompatible — likely a later pass).
- Canary: a canonical `init=$0FFF/$1000` V2 tune (e.g. `MUSICIANS/V/V-12/Remember.sid`).

## Top leads

1. The dead `home.eunet.no/~ggallefo/sdi/` page (Wayback) — V0.98–V1.801 changelogs.
2. **SIDSys V4.1 source** (CSDb #33644) — diff vs SDI to map the SIDSys→SDI evolution.
3. V1.x player source (on the V1.801 / V1 D64s) — the separate V1 format, if it's pursued.
4. Lemon64 t=31585 ("SDI and SID files", PSID ripping) + t=67248 (editor comparison) — 503'd, retry.
