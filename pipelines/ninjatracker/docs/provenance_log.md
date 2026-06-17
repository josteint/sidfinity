# Provenance log — NinjaTracker research sweep (2026-06-16)

Every source attempted, with status. Future waves: don't re-fetch these.

## Fetched successfully (all six clusters completed)
| URL / source | status | yielded |
|---|---|---|
| cadaver.github.io / Covert Bitops distribution | OK | **player source** nt2play_v204.s (V2), ntplay_v1.s (V1), editor/songdata/var defs, both readmes → `src/` |
| GT2NT2 converter source (gt2nt2.c) | OK | **binary-format ground truth** (writes NT2) → `src/gt2nt2.c` |
| github.com (localhost/NinjaTracker fork; cadaver tools) | OK | mirror of player source; confirmed canonical dist is cadaver.github.io |
| github.com/cadaver/sidid (sidid.cfg) | OK | NinjaTracker_V1.x + V2.x signature blocks → `src/sidid_signatures.txt` |
| csdb.dk/release/?id=7206 (+ release list) | OK | V1.0 (2002) … V2.04 (2013, #119721) history; converter releases (#7833, #115448, #152424) |
| local: hvsc84/MUSICIANS/**/*.sid (111 NinjaTracker) | OK | PSID-header survey, V1/V2 clusters, play=init+3, two play=$0000 data-only |
| local: hvsc84/DOCUMENTS/ (STIL, Musicians) | OK | composer/STIL notes |
| Lemon64 / forum threads (V2.0) | OK | table/pattern encodings, hard-restart sequence |
| Wayback Machine (Covert Bitops history) | OK | release/changelog, doc text, V1 readme/nfo |

## Confirmed available (no gaps)
- Full player source for BOTH versions + the format-writing converter + distribution
  docs are all saved under `docs/src/`. No reverse-engineering required to spec the format.

## Notes
- V1 and V2 are distinct engines (sidid signatures share no bytes; V2 is a full rewrite).
- Some `src/` files appear twice (un-prefixed = github/dist cluster, `archive_*` = archive
  cluster) — independent fetches with distinct provenance headers; un-prefixed are canonical.
- Raw downloads / PSID-header dump retained under `tmp/ninjatracker_research/` (~3 MB,
  gitignored scratch).
