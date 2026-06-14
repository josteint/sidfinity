# Provenance log — Laxity NewPlayer V21 research sweep (2026-06-14)

Every URL / source attempted this sweep, fetched or failed. Future waves: don't
re-fetch fetched-OK rows. Scope note: this sweep is the **V21 delta** on top of the
already-`OK` `jch_newplayer` corpus (2026-06-13) — that corpus' provenance log
covers the shared base (CheeseCutter, SF2 converter_jch, codebase64 spec, DeepSID).

## Phase 1 — local (orchestrator)

| Source | Status | Notes |
|---|---|---|
| `pipelines/laxity_newplayer/docs/research.md` | read | pre-existing stub; NP21.G4 overview |
| `pipelines/jch_newplayer/docs/` (full corpus) | read | confirmed V21 ≡ NP21.G4 = the JCH oracle |
| `tools/engine_docs.json`, `tools/build_sid_db.py` | read | family mapping + prior state |
| `hvsc84.db` (read-only) | queried | 313 V21 / 3611 JCH / 179 Vibrants-Laxity / 377 SF2 |

## Phase 2 — cluster agents

### NP21 effect routines (cluster_np21_effect_routines.md)
| Source | Status | Notes |
|---|---|---|
| `tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme` (local checkout, 1764 lines) | read in full | THE oracle; verbatim copy → `src/player_v4_acme_full.asm` |
| github.com/theyamo/CheeseCutter | referenced | upstream of the local checkout (GPL) |

### Laxity variants & releases (cluster_laxity_variants_and_releases.md)
| Source | Status | Notes |
|---|---|---|
| csdb.dk/release/?id=26563 (NP21.G4 Final) | 503 / Wayback | canonical G4, 2006-01-16 |
| csdb.dk/release/?id=33785 (NP21.G5) | 503 / Wayback | G5, 2006-05-09; Byte-C HR change |
| csdb.dk/release/?id=20112 (NP21.b4 beta) | 503 / Wayback | first NP21 artefact, 2005-08 |
| csdb.dk/release/?id=101622 (NP21.G6 / Samar) | snippet only | independent Polish fork, not Laxity |
| carol6502.neocities.org/c6_ccutter_guide | fetched | CheeseCutter user guide — `$Ax` Laxity-restart naming |
| vibrants.dk, funet `Vibrants/Laxity/`, DeepSID Laxity | partial | lineage / authorship cross-check |

### SIDId discrimination (cluster_sidid_discrimination.md)
| Source | Status | Notes |
|---|---|---|
| `tools/sidid.cfg` (local, read-only) | read | V21 / Glover / Vibrants-Laxity / SF2 signatures |
| `tmp/dmc_hunt/player-id/config/sidid.cfg` (local) | read | 2nd independent copy — byte-identical |
| `hvsc84.db` (read-only) | queried | 313 V21 corpus stats (load/init/play, subtunes, authors) |

## Failures / blocked (retry later)
- **CSDb (csdb.dk) — 503 all session** for direct release-page fetches; Wayback
  fallbacks used where available. Retry the 4 release IDs above for native asm +
  embedded READMEs (migration-phase, if needed).
- **`psid_speed`** not in `hvsc84.db` — CIA/multispeed fraction of V21 unknown without
  PSID-header parsing.
