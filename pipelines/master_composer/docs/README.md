# Master Composer — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

Master Composer, by **Paul Kleimeyer / Access Software Inc.** (US commercial),
1983-1984, $39.95 — "the first popular C64 music editor." ~1,019 HVSC tunes
(11th-largest family), 0 migrated. Source not public, **but the engine is now
fully decoded**: a local JC64dis hand-annotation + the identical-across-files
player + ground-truthing against real binaries (`siddump`) closed the format.

A six-cluster sweep ran 2026-06-13. Two agents independently decoded the
JC64dis project and cross-checked every address against `Maniac.sid` + the
write-log — they agree on the core structure.

## Start here (canonical, disassembly-grounded)

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist + OPEN items.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` model, with the CIA census.
3. **`github_jc64dis_local_disasm.md`** — the decoded local JC64dis annotation
   (22 routine labels + per-`$D4xx`-write comments), cross-named onto a real binary.
4. **`src/Maniac_seed_disasm.s`** + `src/jc64dis_labels.txt` — the kept disasm.

## Engine model

Simple, **no effect engine** (no vibrato/arp/PWM in the base player). Three tiers:
- **Pages** (≤23, played sequentially; each = a block range).
- **Blocks** (≤64): a block applies a **16-register full SID snapshot** via
  `outTimbre` (+$0AA) — V1/V2/V3 AD,SR,PW-lo,PW-hi + `$D417` + `$D418` +
  `$D415`/`$D416`. Like switching instruments. Waveform/gate is **not** in the
  snapshot — it's applied per-note.
- **Bars** (≤127): ≤16 notes at 16th-note resolution. Note byte: `$00`=rest,
  `$01-$63`=freq index (96-entry table), **`$64`=gate-off/release**. Each pitched
  note does a gate retrigger (`$D404` written twice: `AND #$FE` then `ORA #$01`).
Bar durations live in a separate table; an inner `blockSpeed` divisor sets tempo.

## ⚠ Corrections to `research.md` (now authoritative)

- **CIA-timed, NOT VBlank.** PSID `speed=$1` for **996/1019** tunes (only 23
  VBlank). The player programs CIA-1 Timer A per-block. → verification uses
  **`siddump --writelog-per-irq`** (the CIA per-`play()` path), not the flat one.
- **Table bases are dataflow-derived per file**, not fixed offsets. There are
  **≥2 player relocations/variants** (e.g. `Maniac.sid` vs `Star_Trek_II.sid`,
  both load $7580, sidid at different offsets) → the extractor must read the
  table bases from code operands (`outTimbre`/`setTimer`/`setAddr`), DMC/HardTrack
  style. (One member's grounded map, for reference: freq-lo +$301, freq-hi +$360,
  16 block-param tables at +$3D1 stride $40 (1-based), bar durations +$3D0, page
  tables +$A51/+$A69, note data ≈+$AC0 as 64-byte measure records — but **do not
  hardcode these**; they shift per variant.)
- **The "decaying hum" bug is real at the byte level**: `gateOff` reads `$D412`
  but writes `$D404` for V3, so V3 keeps sounding after the last page; `stopSound`
  doesn't clear `$D418`/waveform. Reproduce only if verification runs past song
  end (it usually loops within the window). NB: HVSC #80+ rips may carry a
  Prg2Sid 1.15 end-of-tune *patch* — diff a pre-#80 vs #80+ rip to see if the
  binary is patched or pristine.

## Variant taxonomy (one engine + add-on)

- **`Master_Composer` + `(Patrick_Payne)` = the SAME player.** The two sidid
  signatures are adjacent per-voice slices of one contiguous play routine
  (co-occur a constant ~53 bytes apart in every file; Payne never appears alone).
  Patrick Payne is a *composer who used the editor*, not a fork. **One extract path.**
- **`(Lope_Pulse_Sweep)` (~20 files)** — a real external 16-bit PW-sweep add-on
  (accumulator `$02AA/$02AB`) absent from the vanilla player → its own effect/config
  at migration time (the only sub-signature that changes the write stream).
- **`TFMX/MasterComposer` (5 files)** — a genuinely separate engine (Playboy & Sir
  Tippitt, 1990, derived from Hülsbeck's Starball; zero-page-indirect note fetch).
  Name collision — **exclude** from any Access-Master-Composer migration.
- Variant scan over 1019: ~984 vanilla (head+Payne), 19 +Lope, 13 relocated/packed
  outliers, ~2 head-only.

## Census (`hvsc84.db`, read-only)

1019 tunes, all `psid_version=2`, `load_addr=$0000` (real load in the data
prefix), `pipeline=NULL`. init=$7580 = 751 (74%); **`play−init = +7` holds for
962/1019 (94%)** — the strongest structural marker. 166 distinct inits
(relocations $4122/$4073/$1A73/$17E3/…); 18 RSID with own-IRQ (`play=$0000`).
996 are `speed=$1` (per-IRQ verdict); 1003 single-subtune.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan + OPEN | `spec_extraction_plan.md` | `github_jc64dis_local_disasm.md` |
| Per-frame write model + CIA census | `spec_write_model.md` | `forum_sidid_fingerprints.md` |
| Decoded local disasm | `github_jc64dis_local_disasm.md` | `src/Maniac_seed_disasm.s` |
| sidid signatures / variants | `sidid_signature_analysis.md` | `github_sidid_signatures.md`, `forum_namecollision_payne.md` |
| Population / DeepSID | `deepsid_master_composer.md` | (census in `sidid_signature_analysis.md`) |
| Manual / disk / preservation | `archive_manual_and_disk.md` | `csdb_manual.md`, `archive_provenance_preservation.md` |
| Releases / history | `csdb_releases.md` | `csdb_history.md`, `forum_community_lemon64_csdb.md` |
| HVSC bugs / hum | `forum_hvsc_docs.md` | `forum_vgmpf_wiki.md` |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- The engine is **fully decoded** (local JC64dis annotation + 2 independent
  ground-truthed disasms): the page/block/bar model, `outTimbre` snapshot, the
  note codec, freq tables, CIA dispatch, and the hum bug.
- Variant taxonomy + the name-collision resolutions (Payne / Lope / TFMX).
- Census + the per-IRQ verification routing.

## What remains (migration, not research)

- **Dataflow-derive the table bases per file** (≥2 variants; DMC/HardTrack-style
  operand tracing) — do NOT hardcode the nominal offset map.
- **Vanilla first** (~985 files, ONE config gated on the head signature +
  `play−init=+7`); then a **`(Lope_Pulse_Sweep)`** PW-sweep config (~20 files);
  **exclude** the 5 `TFMX/MasterComposer` + audit the relocated/RSID outliers.
- Confirm freq-table index range, bar-duration semantics, and the song-end policy
  (finite "stop"+hum vs content loop). Canary: `Kleimeyer_Paul/Maniac.sid`
  (the JC64dis reference; clean $7580).

## No public manual

No scanned printed manual survives online (confirmed via a Lemon64 request thread
+ absent archive.org item). The only usage doc is the in-program **"H" help screen**
inside the editor `.d64`. This doesn't block us — the player is small, effect-free,
and now fully RE'd from the disasm. Companion tool **Music Translator V1.2** (ships
with the 1985 ICG crack) is a format converter worth a look for the on-disk byte layout.

## Top leads

1. **Music Translator V1.2** (CSDb, on `Mastercomposer-ICG.d64`) — a converter that
   encodes the song-data byte format more legibly than the player.
2. **Prg2Sid 1.15** (CSDb #235041) — the HVSC #80 hum-bug patch; diff pre-/post-#80
   rips to learn whether HVSC binaries are patched or pristine.
3. **Editor `.d64`** (archive.org `d64_Master_Composer_v1.0_19xx_Playboy`, or CSDb
   #128699/#31047) — dump the "H" help screen + confirm the St/Pm/Tu column model.
4. **Second-variant disasm** (`Poole_Chris/Star_Trek_II.sid`) — confirm the
   dataflow-base extractor generalizes across relocations.
