# Provenance log — GMC / Game Music Creator research sweep (2026-06-13)

Gather+summarise sweep (sonnet, no-RE scope). Per-file provenance headers carry
exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| CSDb #7268 + GMC tool releases (V1.0/V1.6/V2.0/Fenek/Wacek) + scener #367 | curl (Firefox UA) | version history, credits, comments, GMC→DMC succession |
| Tehernapló interview (Brian, 2013, Hungarian) | direct | author/scene history, "Superiors"=SAD label, GMC's origin |
| in-repo DMC docs (`pipelines/dmc/docs/`, `.claude/memory/project_dmc.md`) | local read (read-only) | the GMC↔DMC structural correspondence + DMC-pipeline reuse map |
| local `sidid.cfg` ×3 | local read (read-only) | GMC/Superiors V1 (×16 ASL) + GMC_V2.0 (nibble-split) sigs; DMC comparison |
| `hvsc84.db` | read-only (`mode=ro`) | census: 455 (446 V1 + 9 V2.0); layout clusters; 4 RSID |
| HVMEC, scene.hu, DeepSID, Demozoo | direct | editor-binary archive, Hungarian-scene context, labelling |

## Attempted but blocked / negative

| Source | Status |
|---|---|
| Wayback Machine | blocked to the fetcher (candidate URLs noted) |
| Lemon64 | 503 |
| comp.sys.cbm | zero GMC hits (negative — Eastern-European-scene tool) |
| GitHub format-aware parser | none exists (closed; libsidplayfp/ChiptuneSAK/sid2midi engine-blind; no JC64dis GMC profile) |

## Deferred to migration (OPENs — NOT run, gather-only scope)

Byte-level layout (sector packing, 16-byte sound-def, track/transpose, APM/HLD
semantics, V1↔V2.0 nibble diff) via `seed_disassembly.py` on a canary — bootstrap
with the HVMEC editor binaries + Fenek's reimplementation. PSID speed-bit survey.
**Reuse the DMC pipeline** for the actual migration.

## Note

Gather-only/sonnet sweep under the rescoped skill (now with the "only ADD files"
rule — `research.md` was left intact this time). No `siddump`/disasm run; source
fetches stayed in `tmp/gmc_research/`; the concurrent DMC session's files were
read-only-referenced (for the lineage) and left untouched.
