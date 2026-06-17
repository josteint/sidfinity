# SidWinder research — provenance log

Every URL/source attempted in the 2026-06-17 research-player sweep, with status.
Future waves: check here before re-fetching.

## PRIMARY — source archive (the grail; recovered)

| Source | Status |
|--------|--------|
| `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip` (333 KB, V01.23 GPL) | **FETCHED + extracted.** Player/packer/editor asm + docs committed under `docs/src/`; full tree in `tmp/sidwinder_research/`. |
| `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html` | fetched — confirmed the ZIP listing. |
| funet mirror (`ftp.funet.fi /pub/cbm/c64/audio/editors/`) | same archive, mirror of zimmers. |

## CSDb / scene DBs

| Source | Status |
|--------|--------|
| `https://csdb.dk/release/?id=66494` (SIDwinder V01.22) | fetched — release notes, attribution. |
| `https://csdb.dk/release/?id=101758` (V01.23 / Plus4 GPL) | fetched. |
| `https://csdb.dk/release/?id=99574` (PCH "Enhanced", 2011) | noted; format-compat not confirmed (lead). |
| `https://csdb.dk/release/?id=253271` (Genesis Project "SIDwinder V0.2", 2025) | fetched — **NAME COLLISION, unrelated**. |
| `https://plus4world.powweb.com/software/SIDwinder_V01_23` | fetched — best online format description. |
| Demozoo Natural Beat | fetched — historical colour only. |
| Pouet.net | searched — no SidWinder listing. |
| Predecessors #8709 Naturality, #5075 Harmony, #99142 Taki's Music Analyzer | NOT fetched (low value — source in hand). |

## GitHub / open-source tools

| Source | Status |
|--------|--------|
| `https://github.com/cadaver/sidid` (sidid.cfg) | fetched — SidWinder signature (committed to `docs/src/`). |
| `https://github.com/WilfredC64/player-id` | fetched — identical signature, no extra detail. |
| `https://github.com/RobertTroughton/SIDwinder` (2025, Raistlin) | fetched — **unrelated modern analyzer**, flagged. |
| SIDFactory II / CheeseCutter / GoatTracker / DeepSID / libsidplayfp / VICE | searched — **no SidWinder format parser anywhere**; only the sidid label. |

## Archive.org / Wayback

| Source | Status |
|--------|--------|
| `http://www.sch.bme.hu/~takinb` (Taki homepage, ~2000) | Wayback checked — historical only. |
| archive.org "sidwinder" items | searched — source ZIP (zimmers) is the canonical copy. |
| `ftp://c64.rulez.org/...`, `ftp://ftp.padua.org/...` Natural_Beat dirs | listed via Wayback — no extra source beyond the ZIP. |

## Forums / wikis / Usenet / HVSC docs

| Source | Status |
|--------|--------|
| Codebase64 wiki | searched — **no SidWinder page**. |
| Lemon64 | auth-walled. Forum64.de | HTTP 403. c64-wiki.de | no page. |
| comp.sys.cbm via Google Groups (2000–2016) | searched — threads found, no format internals. |
| DeepSID (deepsid.chordian.net) | fetched — inherits sidid label, no extra tech. |
| HVSC `hvsc84/DOCUMENTS/*` + STIL | grepped — **no mention** of sidwinder/natural beat/taki. |
| YouTube "SIDWinder v1.24 sub030 Enhanced" (Draxish fork) | noted — no binary/source located (lead). |
