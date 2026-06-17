# David Whittaker research — provenance log

> Sweep of 2026-06-17 was **interrupted by the session token limit** (caused by
> recursive sub-agent fan-out, since fixed in the skill). Most cluster agents
> never wrote their summaries, so this log is sparse. A clean re-run should
> treat almost everything below as still-to-do.

## Salvaged

| Source | Status |
|--------|--------|
| `Whittaker_David_Panther.asm` ("Reversed by dmx87"), annotated ACME disassembly of *Panther* (1986 Mastertronic) | **RECOVERED** to `docs/src/`. **Origin URL NOT captured** before the agent was killed — re-discover it (likely a dmx87 GitHub repo / SID-disasm collection that may hold MORE Whittaker tunes). |

## Attempted but lost to the kill (re-do on re-run)

| Cluster | Status |
|--------|--------|
| CSDb + Pouet (scener page, driver releases, version history) | launched, no summary written. |
| GitHub + tools (libsidplayfp / VICE / DeepSID detection; dmx87 repo) | launched, no summary written. |
| Archive.org + Wayback (interviews, MML workflow, cross-platform port docs) | launched, no summary written. |
| Forums + wikis (Codebase64 / Lemon64 / Forum64 / AtariAge / comp.sys.cbm) | launched, no summary written. |
| HVSC docs + SIDId + DeepSID (**variant/signature count** = # driver versions) | launched, no summary written. **Highest-value gap.** |
| Disassemblies + tech articles (more dmx87 tunes, scene-mag articles) | launched, no summary written. |

## Known local leads (cheap, not yet read)

- `hvsc84/DOCUMENTS/Update00.hvs`, `Update02.hvs`,
  `Update_Announcements/20020817.txt`, `Update_Announcements/20240630.txt` —
  all grep-match "whittaker"; read for reclassification / variant notes.
- `src/sidid.py` + the sidid signature DB (cadaver/sidid, WilfredC64/player-id)
  — extract every `David_Whittaker` / `Whittaker` signature variant.
