# Provenance log — JCH NewPlayer research sweep (2026-06-13)

Roll-up of sources attempted across the six-cluster sweep. Per-file provenance
headers carry exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| codebase64 `jch_20.g4_player_file_format` | direct (raw DokuWiki export) | NP20.G4 table map + AA/BB sequence grammar (thin, by author's admission) |
| CheeseCutter `player_v4.acme` (+ `src/ct/base.d`, `dump.d`) | local read `tmp/dmc_hunt/CheeseCutter/` (+ github theyamo/CheeseCutter) | NP21.G4 player source: setsid write model, effect chain, HR, tables |
| SID Factory II `converter_jch.cpp` (+ driver_info.h) | local read `tmp/dmc_hunt/sidfactory2/SIDFactoryII/` | maintained NP20.gX packed-binary parser + version marker `$0fee` |
| HVSC binary `Odkin/Wild.sid` (load=$1000) | local decode | ground-truth packed layout; surfaced init-rebased seq pointers |
| local `sidid.cfg` ×3 (`tmp/dmc_hunt/{sidid,player-id/config,DeepSID/utility/sidid_100}`) | local read (read-only) | full JCH_NewPlayer V1–V20 + relatives signature block |
| `pipelines/dmc/docs/research.md` | local read (read-only) | DMC→JCH sibling cross-reference |
| chordian.net (JCH timeline), C64-Wiki, VGMPF, carol6502 guide | direct | lineage, version dates, NP21 community format guide |
| `hvsc84.db` | read-only (`mode=ro`) | census: JCH_NewPlayer 3611 (+ Laxity 313, Glover 67, …) |

## Attempted but blocked

| Source | Status |
|---|---|
| **CSDb (csdb.dk)** | **503, Retry-After 3600** all session (curl + WebFetch + noname mirror) — release notes reconstructed from snippets |
| Lemon64 threads (t=10351, t=63546) | 503 |
| forum64.de 145999, chipmusic.org 3753 | 403 |
| theyamo.kapsi.fi/ccutter (CC reference guide, about.html) | 401 |
| comp.sys.cbm (Google Groups) | bodies JS-gated (subjects/snippets only) |

## Unfetched leads (see README "Top leads")

CSDb id=165426 (NP20.g2 docs), id=100406 / getinternalfile 97829 (NP22-25 manual
`.doc`), id=26563/20112 (NP21); `vibrants.dk/files.htm` (JCH native source);
`JCH Editor-docs.prg` (zimmers, 14,269 B); CheeseCutter full $00–$08 effect
routines; archive.org `d64_JCH_Editor_v3.04`; per-variant counts via local
`sidid -m` over HVSC.

## Note

All six agents honored the no-git / write-scoped / read-only-DB constraints
(the `research-player` skill's hardened agent-constraints block, added after the
soundmonitor-sweep incident — see `.claude/memory/feedback_subagents_no_git.md`).
No tracked file outside the docs dir was touched.
