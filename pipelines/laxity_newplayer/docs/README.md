# Laxity NewPlayer V21 — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

Laxity NewPlayer V21, by **Thomas Egeskov Petersen ("Laxity")** of Vibrants /
Maniacs of Noise. 313 HVSC #84 tunes tagged `Laxity_NewPlayer_V21`; 0 migrated.
Canonical entry: load=$1000, init=$1000, play=$1003 (92% of the corpus).

## ⚠ Read this first: this is NOT a separate engine from JCH NewPlayer

`Laxity_NewPlayer_V21` **is NP21.G4** — the exact player whose released source
(CheeseCutter's `player_v4.acme` = *"Based on JCH NP 21.G4 by Laxity/VIB"*) is the
canonical oracle for the already-`OK` **`jch_newplayer`** family. The V21 string is
just a distinct SIDId top-level name for the same 21-series player core.

**→ The canonical player-source / format / write-model corpus lives in
[`pipelines/jch_newplayer/docs/`](../../jch_newplayer/docs/README.md). Read its
README + `spec_write_model.md` + `github_cheesecutter.md` first.** The 21-series
column is the row labelled "Laxity continuation: NP21.G4 / G5 / B6" there.

This `laxity_newplayer/docs/` corpus is the **Laxity-V21-specific delta** on top
of the JCH base: the full NP21 effect routines (the JCH README's open lead #3),
the sidid discrimination, and the 21-series sub-variant taxonomy.

## File index (this corpus — the V21 delta)

| Topic | File | Reliability |
|---|---|---|
| **Full NP21 effect/command routines** (the write oracle) | `cluster_np21_effect_routines.md` | primary |
| ↳ verbatim player source | `src/player_v4_acme_full.asm` | primary |
| **SIDId discrimination** (V21 vs JCH vs Glover vs Vibrants/Laxity vs SF2) | `cluster_sidid_discrimination.md` | primary |
| **21-series sub-variants & releases** (G4/G5/B6, Q, Samar G6, SF2 lineage) | `cluster_laxity_variants_and_releases.md` | secondary |
| first-pass overview (pre-sweep; minor errors corrected below) | `research.md` | tertiary |

## What's solved (the migration foundation)

**Per-frame write model (Mode-1 target)** — from `player_v4.acme`, read in full:
- Per-voice write order: **D400, D401, D406 (SR), D405 (AD), D402, D403, D404 (ctrl)**
  — **SR-before-AD is the JCH/Laxity fingerprint.** Voices V3→V2→V1, then once/frame
  D417 (filter-init rows only), D415, D416, D418. No separate gate-edge/testbit write.
- **`tsync` 3-frame hard-restart state machine** fully decoded (2→1 = HR frame gate
  `$fe` wave-only; 1→0 = intermediate; 0→`$ff` = gate-on).
- **4 hard-restart types** with exact per-frame writes: `$0x` (3-frame, no ADSR/wave
  force), `$4x` (soft, wave not forced), `$8x` (normal HR: AD←cmd2[0], SR←inst byte6),
  **`$Ax` = "Laxity restart"** (AD UNCHANGED, SR←inst byte6) — the G5-era addition
  that names the engine.
- **All 9 super-table effect commands** decoded (slide ±, hi-fi vibrato semitone-scaled
  with feel ramp, lo-fi vibrato ×4, set-offset/detune, set-ADSR, portamento with
  immediate-parse-at-nextnote, stop) — bytes read + per-frame algorithm each.
- **Super-high inline sequence commands** ($40–$ff) decoded incl. nibble-patch ADSR.
- **Pulse/filter row formats** (4-byte NP21 rows; 10-bit filter sweep; nibble-reversed
  direct pulse) and **wave-table column-B semantics** ($01–$0f delay, $10–$df ctrl,
  $e0–$ef ctrl $00–$0f).

**SIDId signatures** (byte-identical across two independent `sidid.cfg` copies):
- `Laxity_NewPlayer_V21` anchors on `STA $D404,Y` + `CMP #$FF` (seq-end) + `DEC abs,X`
  (duration dec) — keyed on the **play-routine shape**, not a version string / reloc.
- `Glover_NewPlayer_V21` (67 SIDs) — same generational era, different super-table
  dispatcher (`AND #$F0; CMP #$20`); a separate front-end fork.
- `Vibrants/Laxity` (179) — older Laxity engine, play at init+$06, anchored on D401/D400
  freq + D416 filter. `SidFactory_II/Laxity` (377) — separate modern engine.

**Sub-variant taxonomy**: G4 (CSDb 26563, 2006-01-16, canonical) → G5 (33785,
2006-05-09; narrow change — instrument **Byte C hi-nibble**, introduces `$Ax` Laxity
restart) → B6 (Abaddon's CheeseCutter input label). Table format (4-byte rows, 48
column-major instruments) unchanged G4→G5. **No NP21.Q** — multispeed machinery is
present (`MULTISPEED`, CIA `$4cc7`, `mplay` at base+$06) but Laxity never shipped a
Q-named build; the Q-series is JCH's NP20 era. `NP21.G6` (CSDb 101622) is **Samar
Productions**, an independent fork, not Laxity.

**Corpus shape** (313 V21 tunes): 92% at $1000/$1003; 98% single-subtune; all PSID v2
bar 1 RSID. Authorship is extremely concentrated — DRAX (166, 53%) + G-Fellow (92,
29%) = 83%; Laxity himself authored only 4 (he built the engine for others).

## `research.md` corrections (carried from the JCH sweep + this one)

- Instrument **byte 6 = HR-SR**, NOT "unused".
- HR-AD is global (super-table row 0 / cmd2[0]), HR-SR is per-instrument.
- The `$Ax` "Laxity restart" is a G5 addition (instrument Byte C hi-nibble selects mode).

## What remains (migration-phase RE, not research)

These are deliberately deferred to the migration phase (`disassembly.s` + extractor),
which redoes the byte-exact decode properly:

- **Disassemble one V21 tune** to confirm: packed-vs-runtime data encoding for V21
  (V21 is the 4-byte-table / 48-instrument side per the JCH two-encoding split — but
  confirm whether HVSC V21 binaries ship packed like NP20 or in runtime layout),
  seq-pointer rebasing at init, relocation base, transpose zero-point.
- **CIA/multispeed fraction** of the 313 V21 tunes — `hvsc84.db` has no `psid_speed`
  column; parse PSID headers or `siddump --writelog-per-irq` the suspects (DRAX/G-Fellow).
- The DMC pipeline (`pipelines/dmc/`) is a sibling — hard-restart + programmable-table
  machinery may partly transfer.

## Top leads (only if migration needs more; all CSDb-503-blocked this session)

1. **CSDb #26563** (NP21.G4 Final) download — may contain Laxity's **native 6502 asm**
   (vs CheeseCutter's D reimplementation) + a README.
2. **NP21.G5 Final.zip** (CSDb #33785) — embedded player docs / Byte-C HR detail.
3. **NP21.G6 / Samar** (CSDb #101622) — confirm whether it hits the V21 SIDId signature.
4. Local SIDId `-m` re-run — split the 3611 `JCH_NewPlayer` by V-number for a real
   V1..V21 histogram (the DB stores only the coarse label).

Full provenance in each file + `provenance_log.md`.
