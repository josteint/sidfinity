# Provenance log — Soundmonitor research sweep (2026-06-13)

Roll-up of sources attempted across the six-cluster research-player sweep, so a
future wave doesn't re-fetch. Per-file provenance headers carry exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| 64'er Magazin 10/1986 (`archive.org/details/64er_1986_10`, `_djvu.txt`) | direct | Hülsbeck's manual + 24-register table + memory map + demo patches (PRIMARY) |
| Local JC64dis `tmp/jc64/doc/example/SoundMonitor_shades.dis` (+ Rockmonitor2/5) | local read + gzip/DataInputStream decode | full hand-annotated disasm: labels, table addrs, per-$D4xx comments |
| namelessalgorithm blog | Wayback `web/2id_/` (live site 404/403) | RE corroboration; editor UI semantics |
| CSDb release #59929 | curl (Firefox UA; WebFetch 503'd) | version map, downloads, comments |
| Editor disk `Soundmonitor_v1.0_1986-10_Chris_Huelsbeck.d64` (archive.org) | direct + Python D64 walker | `vendor/SOUND-MONITOR.prg` |
| `github.com/ice00/jc64` (JC64dis), `cadaver/sidid`, `WilfredC64/player-id` | raw | sidid signatures + ~20 variant taxonomy |
| Local `tmp/dmc_hunt/.../sidid.cfg` (3 identical copies) | local read (read-only) | the `Soundmonitor` signature block (no `tools/sidid.cfg` in-repo) |
| HVSC binaries + `siddump --writelog` | local | empirical per-frame write model |
| C64-Wiki, VGMPF, de.wikipedia, Pouet | direct | lineage + name-collision warnings |
| comp.sys.cbm (Google Groups) | direct | lineage posts (bodies JS-gated; subjects/snippets only) |
| `hvsc84.db` | read-only (`mode=ro`) | census: 3625 Soundmonitor + 11 Chris_Huelsbeck |

## Attempted but blocked

| Source | Status |
|---|---|
| forum64.de threads 60587 / 145999 | 403 (needs browser; top remaining forum lead) |
| Lemon64 t=15402 | 503 (Retry-After 3600s) |
| web.archive.org (from some agents' env) | intermittently unreachable |
| JITT64 SourceForge SVN | no `svn`/network in sandbox |

## Incident note

A research agent ran `git restore hvsc84.db` (misdiagnosing a pre-existing
working-tree modification as its own read-only touch), reverting the live DB to
the last committed state and undoing an `engine_docs` doc-state bump. Recovered
by re-running `tools/apply_engine_docs.py`. Future agent prompts must forbid all
`git` mutations and any write to tracked files outside the docs dir.

## Unfetched leads

64'er 10/1986 exact line ranges (README lead #1); zimmers FTP SM-Relocator.prg +
rockmonitor-2/3/4.prg; CSDb Rockmonitor V5 #10632; forum64.de (retry);
per-variant counts via a `sidid -m` HVSC pass.
