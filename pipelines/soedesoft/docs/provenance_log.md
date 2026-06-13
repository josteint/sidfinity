# Provenance log — SoedeSoft / Soundmaster research sweep (2026-06-13)

Gather+summarise sweep (sonnet, no-RE scope). Per-file provenance headers carry
exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| German V3.1 PDF manual (CSDb #90307, getinternalfile 115254) | curl (Firefox UA) + pdftotext | translated song-data model + sound structure + effects |
| CSDb releases #10735 / #90307 / #91649 / #117086 / #117095 + scener #5983 | curl | version history, naming, comments (Fred, DRAX) |
| Remix64 Michiel Soede interview + VGMPF Jeroen Soede | direct | authorship (Jeroen=player/Michiel=editor), Fire-Eagle, "nothing ripped" |
| SID Preservation (Xiny6581) | direct | recalled note/pattern byte-format fragment |
| local `sidid.cfg` ×3 + `DeepSID/.../soedesoft.py` | local read (read-only) | SoedeSoft + V1.0/V3.1/V3.2 sigs; the classifier is a pure sidid reformatter |
| `hvsc84.db` | read-only (`mode=ro`) | census: 929; 8 init→play clusters; $6000 dominant; all PSID v2 VBlank |
| `ice00/jc64` repo listing | direct | `doc/example/SoundMaster1.dis` profile exists (Ian Coog) |

## Attempted but blocked / negative

| Source | Status |
|---|---|
| Wayback Machine (soedesoft.com snapshots) | blocked to the fetcher |
| Lemon64 / chipmusic.org | 503 / 403 |
| forum64.de | not directly searched (German community — a gap) |
| comp.sys.cbm | zero SoedeSoft hits (negative) |
| GitHub format-aware parser | none exists (closed engine; libsidplayfp/ChiptuneSAK/sid2midi engine-blind) |

## Deferred to migration (OPENs — NOT run, gather-only scope)

Byte-level layout (bar packing, sound-record offsets, arp+wave table, var-area)
via `seed_disassembly.py` on a canary (bootstrap with the JC64dis `SoundMaster1.dis`
profile); the embedded-sig version scan; the PSID speed-bit survey; the digi-outlier
check.

## Incident note

A subagent **deleted the tracked `research.md`** (constraint violation — agents
must only ADD `{cluster}_*.md`, never delete/overwrite existing files). The
orchestrator restored it from HEAD (scoped `git checkout HEAD -- …research.md`,
no impact on the concurrent DMC session). Source fetches stayed in
`tmp/soedesoft_research/`; no other tracked file was touched.
