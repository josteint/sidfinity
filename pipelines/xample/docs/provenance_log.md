# Provenance log — X-Ample / Compotech research sweep (2026-06-13)

Gather+summarise sweep (sonnet, no-RE scope). Per-file provenance headers carry
exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| Compotech V2.1 D64 (CSDb #122614) + Parsec V5.1 (#10744) + Compotech 1992 (#130599) | curl + D64 directory listing | the **annotated V3.2 TurboAss player source SEQ** + editor inventory |
| CSDb releases + group page #245 + sceners | curl (Firefox UA) | version/editor history, member roster, comments |
| Remix64 / Atlantis Prophecy interviews (Schneider, Detert) | direct | authorship (4 contributors), lineage, XTracker=SoNiC |
| c64-wiki.de, VGMPF, DeepSID | direct | group history, labelling |
| local `sidid.cfg` ×3 | local read (read-only) | the 7 X-Ample sub-variant sigs + Comptech-X |
| `hvsc84.db` | read-only (`mode=ro`) | census: 380; layout groups A/B/C/exotic; 1 RSID; 0 confirmed digi |

## Attempted but blocked / negative

| Source | Status |
|---|---|
| Docs2Compotech / Parsec-info | crunched C64 viewers — text needs runtime emulation (deferred) |
| xap64.de (X-Ample history site) | ECONNREFUSED (try Wayback) |
| Lemon64 / forum64.de | 503 / not fully reachable |
| comp.sys.cbm | negative (no X-Ample format discussion) |
| GitHub format-aware parser | none exists (closed; libsidplayfp/ChiptuneSAK/JC64dis have no X-Ample handling) |

## Deferred to migration (OPENs — NOT run, gather-only scope)

Song-data byte layout (patterns/sequences/instruments) via `seed_disassembly.py`
on a canary (bootstrap: the annotated V3.2 source + the Compotech V2.1 D64);
confirm Layout A≡B (one extractor); XTracker V4.1x format-vs-dispatch diff;
per-variant every-frame $D416/$D418 quirk; exclude X-Ample_Digi (Mode-2) + the
RSID Hawkeye_II; confirm the 11 CIA SoNiC tunes are Mode-1-per-IRQ.

## Note

Gather-only/sonnet sweep under the rescoped skill (add-only — `research.md`
intact). No `siddump`/disasm run; D64 fetches stayed in `tmp/xample_research/`;
the concurrent DMC session's files (incl. shared `src/usf/*`) were left untouched.
**Correction recorded**: a sweep agent lumped the unrelated `Reflextracker`
engine (137 RSID tunes) into an X-Ample "family" count — it is a separate engine.
