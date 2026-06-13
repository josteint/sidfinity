# Provenance log — SID Duzz'It research sweep (2026-06-13)

Gather+summarise sweep (sonnet, no-RE scope). Per-file provenance headers carry
exact URLs.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| SourceForge `Sid_Duzz_It_v2.1.7-shape` release (D64s in the zip) | curl + D64 walk + PETSCII decode | player asm (`SRC_SDI21-N50`/`SPD50`), `SDI.2.1.6-docs.txt` (65 KB), note tables, release notes → kept in `docs/src/` |
| Psylicium PDF manual (CSDb #153760) | curl + pdftotext | prose manual: effects, program tables, sequencer → `docs/src/sdi_217_manual.txt` |
| CSDb release pages (19, 1996-2017) + SHAPE group #142 | curl (Firefox UA; WebFetch 503'd) | version history, release notes, comments |
| local `sidid.cfg` ×3 (+ `.nfo`) | local read (read-only) | the Geir_Tjelta family taxonomy (SIDDuzz'It vs SIDSys/Comptech-X/Echo) |
| `hvsc84.db` | read-only (`mode=ro`) | census: 934; init/play layout (609 canonical / 325 relocated); 16 RSID |
| DeepSID, VGMPF, Recollection, chipflip | direct | labelling, lineage (JCH→GRG→SDI, independent), the Echo $D418 trick |

## Attempted but blocked

| Source | Status |
|---|---|
| SourceForge raw curl (some files) | blocked — used the release-zip D64s instead |
| Lemon64 threads (t=31585, t=67248) | 503, Retry-After 3600 |
| chipmusic.org SDI threads (19378, 10911) | 403 |
| forum64.de thread 46876 | 403 |
| comp.sys.cbm | no SDI content (distributed via Norwegian BBS/scene, not Usenet) |
| `home.eunet.no/~ggallefo/sdi/` + `shape.scene.org` | dead / ECONNREFUSED (try Wayback) |

## Deferred to migration (OPENs, NOT run — gather-only scope)

`siddump --writelog`/`--pc-trace` on a canary (write order, glide sequence, music-
data start); the `rem_*` flag-set fingerprint; PSID speed-bit survey; the `z7`
access pattern; V1.x format recovery.

## Note

This was the first sweep under the rescoped skill: subagents on **sonnet**,
**gather+summarise only** (no `siddump`/py65/disasm — RE-dependent facts became
OPENs). Source kept in `docs/src/`, scratch in `tmp/sidduzzit_research/`. All
agents honored the no-git / read-only-DB constraints; the concurrent DMC session's
files were left untouched.
